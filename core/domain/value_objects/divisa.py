class Divisa:
    __slots__ = ("_codigo",)

    def __init__(self, codigo: str):
        if not codigo or len(codigo) != 3:
            raise ValueError("Código de divisa inválido")

        self._codigo = codigo.upper()

    @property
    def codigo(self) -> str:
        return self._codigo

    def __eq__(self, other):
        return isinstance(other, Divisa) and self._codigo == other._codigo

    def __hash__(self):
        return hash(self._codigo)

    def __repr__(self):
        return f"Divisa('{self._codigo}')"
