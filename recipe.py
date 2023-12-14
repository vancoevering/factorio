from dataclasses import dataclass, asdict, field
from sdecimal import SDecimal

DEF_AMOUNT = 1
DEF_CATALYST = 0
DEF_PROBABILITY = 1


@dataclass
class ItemCount:
    name: str
    type: str
    amount: SDecimal = DEF_AMOUNT


@dataclass
class Ingredient(ItemCount):
    catalyst_amount: SDecimal = DEF_CATALYST

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d["name"],
            d["type"],
            SDecimal.sanitize(d.get("amount", DEF_AMOUNT)),
            SDecimal.sanitize(d.get("catalyst_amount", DEF_CATALYST)),
        )

    def net(self):
        net_amount = self.amount - self.catalyst_amount
        self_dict = asdict(self)
        self_dict["amount"] = SDecimal(net_amount)
        self_dict["catalyst_amount"] = SDecimal(0)
        return ItemCount(**self_dict)


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

    def net(self):
        super_net = super().net()
        super_dict = asdict(super_net)
        # The 'Law of Large Numbers' suggests this should be true at Factorio scales
        # https://en.wikipedia.org/wiki/Law_of_large_numbers
        super_dict["amount"] = super_net.amount * self.probability
        super_dict["probability"] = SDecimal(1)
        return self.__class__(**super_dict)


@dataclass
class BaseRecipe:
    name: str
    category: str
    ingredients: list[ItemCount]
    products: list[ItemCount]
    energy: SDecimal


@dataclass
class Recipe(BaseRecipe):
    ingredients: list[Ingredient]
    products: list[Product]

    @classmethod
    def from_dict(cls, d: dict):
        return Recipe(
            d["name"],
            d["category"],
            [Ingredient.from_dict(i) for i in d["ingredients"]],
            [Product.from_dict(p) for p in d["products"]],
            SDecimal.sanitize(d["energy"]),
        )

    def net(self):
        self_dict = asdict(self)
        self_dict["ingredients"] = self.net_ingredients()
        self_dict["products"] = self.net_products()
        return self.__class__(**self_dict)

    def net_ingredients(self):
        return self._get_net_items(self.ingredients)

    def net_products(self):
        return self._get_net_items(self.products)

    @staticmethod
    def _get_net_items(items: list[Ingredient]):
        return [net_i for net_i in [i.net() for i in items] if net_i.amount > 0]


@dataclass
class NetRecipe(BaseRecipe):
    @classmethod
    def from_recipe(recipe: Recipe):
        net_recipe = recipe.net()
        pass
