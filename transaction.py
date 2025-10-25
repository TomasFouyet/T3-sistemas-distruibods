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

    def can_execute(self) -> bool:
        return self.state in {TransactionState.ABIERTA, 
        TransactionState.EN_PREPARACION}

    def is_final(self) -> bool:
        return self.state in {TransactionState.CONFIRMADA, 
        TransactionState.ABORTADA, TransactionState.INVALIDA}
