from decimal import Decimal

from core.domain.value_objects.divisa import Divisa

class Dinero:
    def __init__(self, monto:Decimal, divisa: Divisa):
        if monto < Decimal("0"):
            raise ValueError("El monto no puede ser menor a 0")
        if not isinstance(divisa, Divisa):
            raise ValueError("Divisa invalida")
        self._monto = monto
        self._divisa = divisa

    @property
    def monto(self) -> Decimal:
        return self._monto

    @property
    def divisa(self) -> Divisa:
        return self._divisa

    def __eq__(self, other):
        return isinstance(other, Dinero) and self._monto == other._monto and self._divisa == other._divisa

    def __add__(self, other):
        if self.divisa != other.divisa:
            raise ValueError("No se puede sumar Money de distintas divisas")
        return Dinero(self.monto + other.monto, self.divisa)

    def __sub__(self, other):
        if self.divisa != other.divisa:
            raise ValueError("No se puede restar Money de distintas divisas")
        result = self.monto - other.monto
        if result < 0:
            raise ValueError("El resultado no puede ser negativo")
        return Dinero(result, self.divisa)



