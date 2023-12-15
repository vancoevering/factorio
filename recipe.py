from dataclasses import dataclass, asdict, fields
from sdecimal import SDecimal

DEF_AMOUNT = 1
DEF_CATALYST = 0
DEF_PROBABILITY = 1


@dataclass
class ItemCount:
    name: str
    type: str
    amount: SDecimal = DEF_AMOUNT

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["name"], d["type"], SDecimal.sanitize(d.get("amount", DEF_AMOUNT)))


@dataclass
class Ingredient(ItemCount):
    catalyst_amount: SDecimal = DEF_CATALYST

    @classmethod
    def from_dict(cls, d: dict):
        _super = super().from_dict(d)
        return cls(
            _super.name,
            _super.type,
            _super.amount,
            SDecimal.sanitize(d.get("catalyst_amount", DEF_CATALYST)),
        )

    def net(self):
        net_amount = self.amount - self.catalyst_amount
        self_dict = asdict(self)
        self_dict["amount"] = SDecimal(net_amount)
        return ItemCount.from_dict(self_dict)


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
        return ItemCount.from_dict(super_dict)


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
        return NetRecipe(**self_dict)

    def net_ingredients(self):
        return self._get_net_items(self.ingredients)

    def net_products(self):
        return self._get_net_items(self.products)

    @staticmethod
    def _get_net_items(items: list[Ingredient]):
        return [net_i for net_i in [i.net() for i in items] if net_i.amount > 0]


@dataclass
class NetRecipe(BaseRecipe):
    def normalize_to_item(self, item: ItemCount):
        return self.normalize_to(item.amount)

    def normalize_to_energy(self):
        return self.normalize_to(self.energy)

    def normalize_to(self, val: SDecimal):
        self_dict = asdict(self)
        self_dict["ingredients"] = [
            self._normalize_item_count_to(i, val) for i in self.ingredients
        ]
        self_dict["products"] = [
            self._normalize_item_count_to(p, val) for p in self.products
        ]
        self_dict["energy"] = SDecimal(self.energy / val)
        return self.__class__(**self_dict)

    @staticmethod
    def _normalize_item_count_to(item: ItemCount, val: SDecimal):
        item_dict = asdict(item)
        item_dict["amount"] = SDecimal(item.amount / val)
        return ItemCount.from_dict(item_dict)

    def parallelize(self, operations: SDecimal):
        raise NotImplementedError
