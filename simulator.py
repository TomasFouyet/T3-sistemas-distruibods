from __future__ import annotations
import json
import re
import os
from models import TransactionState, DELETE_SENTINEL
from transaction import Transaction
from server import Server


class Simulator:
    def __init__(self, test_path: str):
        self.test_path = test_path
        self.validation: str = "forward"
        self.servers: dict[str, Server] = {}
        self.server_names_set: set[str] = set()
        self.db: dict[str, str] = {}
        self.transactions: dict[str, Transaction] = {}
        self.logs: list[str] = []
        self.step_counter: int = 0
        self.committed_history: list[tuple[int, str, set[str]]] = []

    @staticmethod
    def _strip_jsonc_comments(raw: str) -> str:
        return re.sub(r"//.*", "", raw)

    def load(self):
        with open(self.test_path, encoding="utf-8") as f:
            raw = f.read()
        clean = self._strip_jsonc_comments(raw)
        data = json.loads(clean)

        self.validation = (data.get("VALIDATION") or "").strip().lower()
        servers = data.get("SERVERS", [])
        self.servers = {name: Server(name) for name in servers}
        self.server_names_set = set(servers)    
        self.db = dict(data.get("DATA", {}))
        self.transactions_script: list[str] = list(data.get("TRANSACTIONS", []))

    def _get_or_create_transaction(self, transaction_id: str) -> Transaction:
        if transaction_id not in self.transactions:
            self.transactions[transaction_id] = Transaction(id=transaction_id)
        return self.transactions[transaction_id]

    def _abort_transaction(self, transaction: Transaction):
        if transaction.state in {TransactionState.ABORTADA, TransactionState.CONFIRMADA}:
            return
        transaction.state = TransactionState.ABORTADA
        for s in self.servers.values():
            s.release(transaction.id)

    def _finalize_commit(self, transaction: Transaction):
        for var in transaction.write_set:
            val = transaction.local_db.get(var, None)
            if val == DELETE_SENTINEL:
                self.db.pop(var, None)
            elif val is not None:
                self.db[var] = val

        transaction.state = TransactionState.CONFIRMADA
        transaction.commit_step = self.step_counter
        for s in self.servers.values():
            s.release(transaction.id)

        self.committed_history.append((transaction.commit_step, 
                                      transaction.id, set(transaction.write_set)))

        written = set(transaction.write_set)
        if not written:
            return
        for other in self.transactions.values():
            if other.state in {TransactionState.EN_PREPARACION, TransactionState.ABIERTA}:
                accepted_somewhere = any(
                    s.has_accepted(other.id) for s in self.servers.values()
                )
                if accepted_somewhere and (other.read_set & written):
                    self._abort_transaction(other)

    def _conflict_read_write(self, A_read: set[str], A_write: set[str],
                             B_read: set[str], B_write: set[str]) -> bool:
        return bool((A_write & B_read) or (B_write & A_read))

    def _cc_forward_reject(self, cand: Transaction) -> bool:
        for other in self.transactions.values():
            if other.id == cand.id:
                continue
            if other.state in {TransactionState.ABIERTA, TransactionState.EN_PREPARACION}:
                if self._conflict_read_write(
                    cand.read_set, cand.write_set, other.read_set, other.write_set
                ):
                    return True
        return False

    def _cc_backward_reject_and_abort(self, cand: Transaction) -> bool:
        if cand.begin_step < 0:
            return False
        for commit_step, _, wset in self.committed_history:
            if commit_step >= cand.begin_step and (wset & cand.read_set):
                self._abort_transaction(cand)
                return True
        return False

    def _twopc_reservation_reject(self, server: Server, cand: Transaction) -> bool:
        for rec in server.accepted.values():
            if rec.id == cand.id:
                continue
            if self._conflict_read_write(
                cand.read_set, cand.write_set, rec.read_set, rec.write_set
            ):
                return True
        return False

    def _query_read_commit(self, var: str):
        val = self.db.get(var, None)
        self.logs.append(val if val is not None else "NULL")

    def _query_read_possible_values(self, var: str):
        possible: set[str] = set()
        if var in self.db:
            possible.add(self.db[var])
        for transaction in self.transactions.values():
            if transaction.state in {TransactionState.ABIERTA, 
                                     TransactionState.EN_PREPARACION}:
            
                if var in transaction.write_set:
                    val = transaction.local_db.get(var, None)
                    if val is not None and val != DELETE_SENTINEL:
                        possible.add(val)
        self.logs.append(json.dumps(list(possible)))

    def _cmd_begin(self, transaction_id: str):
        transaction = self._get_or_create_transaction(transaction_id)
        if transaction.state != TransactionState.ABIERTA or transaction.begin_step >= 0:
            return
        transaction.begin_step = self.step_counter

    def _cmd_read(self, transaction_id: str, var: str):
        transaction = self._get_or_create_transaction(transaction_id)
        if transaction.is_final() or transaction.begin_step < 0:
            return
        if transaction.state == TransactionState.EN_PREPARACION:
            transaction.state = TransactionState.INVALIDA
            return

        exists_local = var in transaction.local_db and \
                              transaction.local_db[var] != DELETE_SENTINEL

        exists_global = var in self.db
        if not exists_local and not exists_global:
            transaction.state = TransactionState.INVALIDA
            return

        transaction.read_set.add(var)

    def _cmd_write(self, transaction_id: str, var: str, val: str):
        transaction = self._get_or_create_transaction(transaction_id)
        if transaction.is_final() or transaction.begin_step < 0:
            return
        if transaction.state == TransactionState.EN_PREPARACION:
            transaction.state = TransactionState.INVALIDA
            return

        if val == "DELETE":
            transaction.local_db[var] = DELETE_SENTINEL
        else:
            transaction.local_db[var] = val
        transaction.write_set.add(var)

    def _cmd_can_commit(self, transaction_id: str, server_name: str):
        transaction = self._get_or_create_transaction(transaction_id)
        if transaction.is_final() or transaction.begin_step < 0:
            return
        if server_name not in self.server_names_set:
            return
        server = self.servers[server_name]

        if server.has_accepted(transaction.id):
            return

        if self.validation == "backward":
            if self._cc_backward_reject_and_abort(transaction):
                return

        if self._twopc_reservation_reject(server, transaction):
            return

        server.accept(transaction)
        transaction.accepted_servers.add(server_name)
        if transaction.state == TransactionState.ABIERTA:
            transaction.state = TransactionState.EN_PREPARACION

    def _cmd_abort(self, transaction_id: str):
        transaction = self._get_or_create_transaction(transaction_id)
        if transaction.is_final() or transaction.begin_step < 0:
            return
        self._abort_transaction(transaction)

    def _cmd_commit(self, transaction_id: str):
        transaction = self._get_or_create_transaction(transaction_id)
        if transaction.is_final() or transaction.begin_step < 0:
            return

        if self._cc_backward_reject_and_abort(transaction):
            return

        cond2_ok = transaction.state != TransactionState.INVALIDA
        total = len(self.servers)
        quorum = (total // 2) + 1
        cond1_ok = len(transaction.accepted_servers) >= quorum

        if cond1_ok and cond2_ok:
            self._finalize_commit(transaction)
        else:
            pass

    def run(self):
        self.load()
        for raw in self.transactions_script:
            self.step_counter += 1
            line = raw.strip()
            if not line:
                continue

            if line.startswith("C;"):
                parts = line.split(";", 2)
                if len(parts) < 3:
                    continue
                _, qtype, arg = parts[0], parts[1], parts[2]
                if qtype == "READ_COMMIT":
                    self._query_read_commit(arg)
                elif qtype == "READ_POSSIBLE_VALUES":
                    self._query_read_possible_values(arg)
                continue

            parts = line.split(";", 2)
            if len(parts) < 2:
                continue
            transaction_id, cmd = parts[0], parts[1]
            args = parts[2] if len(parts) == 3 else None

            if cmd != "BEGIN":
                transaction = self._get_or_create_transaction(transaction_id)
                if transaction.begin_step < 0 and cmd not in {"BEGIN"}:
                    continue

            if cmd == "BEGIN":
                self._cmd_begin(transaction_id)
            elif cmd == "READ":
                if args is not None:
                    self._cmd_read(transaction_id, args)
            elif cmd == "WRITE":
                if args is not None and "," in args:
                    var, val = args.split(",", 1)
                    self._cmd_write(transaction_id, var, val)
            elif cmd == "CAN_COMMIT":
                if args is not None:
                    self._cmd_can_commit(transaction_id, args)
            elif cmd == "COMMIT":
                self._cmd_commit(transaction_id)
            elif cmd == "ABORT":
                self._cmd_abort(transaction_id)

        self._emit_results()

    def _emit_results(self):
        base_name = os.path.basename(self.test_path)
        name_txt = os.path.splitext(base_name)[0] + ".txt"
        out_dir = "logs"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, name_txt)

        lines: list[str] = []
        lines.append("##LOGS##")
        if len(self.logs) == 0:
            lines.append("No hay logs")
        else:
            lines.extend(self.logs)

        lines.append("##DATABASE##")
        if len(self.db) == 0:
            lines.append("No hay datos")
        else:
            for k, v in self.db.items():
                lines.append(f"{k}={v}")

        by_state: dict[TransactionState, list[str]] = {
            TransactionState.ABIERTA: [],
            TransactionState.ABORTADA: [],
            TransactionState.CONFIRMADA: [],
            TransactionState.EN_PREPARACION: [],
            TransactionState.INVALIDA: [],
        }
        for transaction in self.transactions.values():
            by_state[transaction.state].append(transaction.id)

        lines.append("##STATS##")
        def j(lst: list[str]) -> str:
            return json.dumps(lst)

        lines.append(f'ABIERTA={j(by_state[TransactionState.ABIERTA])}')
        lines.append(f'ABORTADA={j(by_state[TransactionState.ABORTADA])}')
        lines.append(f'CONFIRMADA={j(by_state[TransactionState.CONFIRMADA])}')
        lines.append(f'EN_PREPARACION={j(by_state[TransactionState.EN_PREPARACION])}')
        lines.append(f'INVALIDA={j(by_state[TransactionState.INVALIDA])}')

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
