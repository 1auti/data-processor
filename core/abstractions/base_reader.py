from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseReader(ABC, Generic[T]):
    """
    Contrato abstracto para componentes que obtienen datos desde
    una fuente externa y los convierten en un tipo T.

    T representa el tipo ya interpretado que será utilizado
    por la capa de aplicación.
    """

    @abstractmethod
    def read(self) -> T:
        """
        Obtiene datos desde la fuente configurada y devuelve
        una instancia del tipo T.
        """
        pass
