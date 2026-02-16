from dataclasses import dataclass


@dataclass
class TransferemciaDTO:
    transferencia_id: int
    cuenta_origen: str
    cuenta_destino: str
    monto:str
    divisa: str
    origen:str








