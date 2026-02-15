from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseValidator(ABC, Generic[T]):
    """
    Contrato para validadores de reglas de negocio
    sobre entidades del tipo T.
    """

    @abstractmethod
    def validate(self, entity: T) -> None:
        """
        Lanza excepción si la entidad no es válida.
        """
        pass
