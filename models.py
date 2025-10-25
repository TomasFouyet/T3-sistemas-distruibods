from __future__ import annotations
import dataclasses
import enum

DELETE_SENTINEL = "__DELETE__"

class TransactionState(str, enum.Enum):
    ABIERTA = "ABIERTA"
    EN_PREPARACION = "EN_PREPARACION"
    CONFIRMADA = "CONFIRMADA"
    ABORTADA = "ABORTADA"
    INVALIDA = "INVALIDA"

@dataclasses.dataclass
class AcceptedRecord:
    transaction_id: str
    read_set: set[str]
    write_set: set[str]
