from __future__ import annotations
import dataclasses
from models import TransactionState


@dataclasses.dataclass
class Transaction:
    id: str
    state: TransactionState = TransactionState.ABIERTA
    begin_step: int = -1
    commit_step: int = -1
    local_db: dict[str, str] = dataclasses.field(default_factory=dict)
    read_set: set[str] = dataclasses.field(default_factory=set)
    write_set: set[str] = dataclasses.field(default_factory=set)
    accepted_servers: set[str] = dataclasses.field(default_factory=set)

    def tx_finalizada(self) -> bool:
        estados_finales = {
            TransactionState.CONFIRMADA,
            TransactionState.ABORTADA,
            TransactionState.INVALIDA
        }
        return self.state in estados_finales
