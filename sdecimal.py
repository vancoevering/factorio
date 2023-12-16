from decimal import Decimal
from operator import truediv

DEF_QUANTIZE_EXP = "1.0000"


class SDecimal(Decimal):
    @classmethod
    def sanitize(cls, val, prec: int = None):
        if prec:
            prec = "1." + ("0" * prec)
        return cls(Decimal(val).quantize(Decimal(prec or DEF_QUANTIZE_EXP)).normalize())

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"('{str(self)}')"

    def __str__(self) -> str:
        return "{:,f}".format(self)

    def __truediv__(self, __value):
        return self.__class__(super().__truediv__(__value))

    def __mul__(self, __value):
        return self.__class__(super().__mul__(__value))
