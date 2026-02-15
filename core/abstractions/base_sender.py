from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseSender(ABC, Generic[T]):
    """
    Contrato abstracto para componentes responsables de enviar
    mensajes de tipo T a un sistema externo.
    """

    @abstractmethod
    def send(self, message: T) -> None:
        """
        Envía el mensaje al destino configurado.
        """
        pass
