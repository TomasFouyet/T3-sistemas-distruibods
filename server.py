from __future__ import annotations
from models import AcceptedRecord
from transaction import Transaction


class Server:
    def __init__(self, name: str):
        self.name = name
        self.accepted: dict[str, AcceptedRecord] = {}

    def has_accepted(self, transaction_id: str) -> bool:
        return transaction_id in self.accepted

    def accept(self, transaction: Transaction):
        self.accepted[transaction.id] = AcceptedRecord(
            transaction_id=transaction.id,
            read_set=set(transaction.read_set),
            write_set=set(transaction.write_set),
        )

    def release(self, transaction_id: str):
        self.accepted.pop(transaction_id, None)
