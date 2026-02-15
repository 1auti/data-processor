from typing import Generic, TypeVar, Callable
from abc import ABC,abstractmethod

T = TypeVar("T")

class BaseConsumer(ABC, Generic[T]):

    """
    Contrato abstracto para componentes que escuchan una fuente externa de eventos y delegan el procesamiento
    de cada mensaje recibido a un handler externo

    El consumer es responsable unicamente del transporte y la recepcion de mensajes, NO contien logica de negocio
    """

    @abstractmethod
    def start(self, handler: Callable[[T], None]) -> None:
        """
        Inicia el ciclo de consumo y ejecuta el handler por cada mensaje consumido
        """
        pass
