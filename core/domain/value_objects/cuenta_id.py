from uuid import UUID


class CuentaId:
    __slots__ = ("_value",)

    def __init__(self, value: UUID):
        if not isinstance(value, UUID):
            raise TypeError("El ID debe ser unico")

        self._value = value

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other):
        if not isinstance(other, CuentaId):
            return NotImplemented
        return self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        return f"CuentaId({self._value})"
