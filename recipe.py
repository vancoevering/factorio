from dataclasses import dataclass
from sdecimal import SDecimal

DEF_AMOUNT = 1
DEF_CATALYST = 0
DEF_PROBABILITY = 1


@dataclass
class Ingredient:
    name: str
    type: str
    amount: SDecimal = DEF_AMOUNT
    catalyst_amount: SDecimal = DEF_CATALYST

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d["name"],
            d["type"],
            SDecimal.sanitize(d.get("amount", DEF_AMOUNT)),
            SDecimal.sanitize(d.get("catalyst_amount", DEF_CATALYST)),
        )


@dataclass
class Product(Ingredient):
    probability: SDecimal = DEF_PROBABILITY

    @classmethod
    def from_dict(cls, d: dict):
        _super = super().from_dict(d)
        return cls(
            _super.name,
            _super.type,
            _super.amount,
            _super.catalyst_amount,
            SDecimal.sanitize(d.get("probability", DEF_PROBABILITY)),
        )


@dataclass
class Recipe:
    name: str
    category: str
    ingredients: list[Ingredient]
    products: list[Product]
    energy: SDecimal

    @classmethod
    def from_dict(cls, d: dict):
        return Recipe(
            d["name"],
            d["category"],
            [Ingredient.from_dict(i) for i in d["ingredients"]],
            [Product.from_dict(p) for p in d["products"]],
            SDecimal.sanitize(d["energy"]),
        )
