import operator
from dataclasses import asdict, dataclass

import dacite

from sdecimal import SDecimal

DEF_AMOUNT = 1
DEF_CATALYST = 0
DEF_PROBABILITY = 1


@dataclass
class ItemCountBase:
    name: str
    type: str
    amount: SDecimal = DEF_AMOUNT

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["name"], d["type"], SDecimal.sanitize(d.get("amount", DEF_AMOUNT)))


@dataclass
class ItemCount(ItemCountBase):
    def __truediv__(self, divisor: SDecimal):
        self_dict = asdict(self)
        self_dict["amount"] = self.amount / divisor
        return ItemCount.from_dict(self_dict)

    def __mul__(self, multiplier: SDecimal):
        self_dict = asdict(self)
        self_dict["amount"] = self.amount * multiplier
        return ItemCount.from_dict(self_dict)


@dataclass
class Ingredient(ItemCountBase):
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
    def normalize_to_ingredient(self, index: int):
        return self.normalize_to_item(self.ingredients[index])

    def normalize_to_product(self, index: int):
        return self.normalize_to_item(self.products[index])

    def normalize_to_item(self, item: ItemCount):
        return self.normalize_to(item.amount)

    def normalize_to_energy(self):
        return self.normalize_to(self.energy)

    def normalize_to(self, val: SDecimal):
        return self / val

    def parallelize(self, crafters: SDecimal):
        """Return a recipe where multiple crafters work in parallel."""
        # ingredients and products should be multiplied by number of crafters
        self_times_crafters = self * crafters
        parallel_dict = asdict(self_times_crafters)
        # ... but the time it takes should stay the same
        parallel_dict["energy"] = self.energy

        # we change the name to indicate this is a truly new recipe
        parallel_dict["name"] = self.name + f"-w/{crafters}-crafters"
        return self.from_dict(parallel_dict)

    def target_product_per_energy(self, product_index: int, target_count: SDecimal):
        # blue_science.normalize_to_product(0)
        # .parallelize(SDecimal(12))
        # .normalize_to_energy()
        energy_per_product = self.normalize_to_product(product_index).energy
        parallels = energy_per_product * target_count
        return self.parallelize(parallels).normalize_to_energy()

    @classmethod
    def from_dict(cls, d: dict):
        return dacite.from_dict(data_class=cls, data=d)

    def _apply_binary_operator(self, op, input: SDecimal):
        self_dict = asdict(self)
        self_dict["ingredients"] = [op(i, input) for i in self.ingredients]
        self_dict["products"] = [op(p, input) for p in self.products]
        self_dict["energy"] = op(self.energy, input)
        return self.__class__(**self_dict)

    def __truediv__(self, divisor: SDecimal):
        return self._apply_binary_operator(operator.truediv, divisor)

    def __mul__(self, multiplier: SDecimal):
        return self._apply_binary_operator(operator.mul, multiplier)


@dataclass
class ProcessNodeChild:
    recipe: NetRecipe
    processes: list["ProcessNode"]

    def to_printable_str(self, _depth: int=0):
        s = f"{'.'*_depth}{self.recipe.__class__.__name__}({self.recipe.name})"
        for p in self.processes:
            s = f"{s}\n{p.to_printable_str(_depth+1)}"
        return s


@dataclass
class ProcessNode:
    product: str
    recipes: list[ProcessNodeChild]

    def to_printable_str(self, _depth: int=0):
        s = f"{'.'*_depth}{self.__class__.__name__}({self.product})"
        for r in self.recipes:
            # s = s + f"\n{'.'*_depth}"
            s = f"{s}\n{r.to_printable_str(_depth+1)}"
        return s


class ProcessFactory:
    def __init__(self, recipes: list[NetRecipe]) -> None:
        self.recipes = recipes
        self.products: dict[str, list[NetRecipe]] = {}
        for r in self.recipes:
            for p in r.products:
                if p.name not in self.products:
                    self.products[p.name] = []
                self.products[p.name].append(r)

        self.processes: dict[str, ProcessNode] = {}

    def get_process(self, product: str):
        # Check cache to shortcut if possible
        if product in self.processes:
            return self.processes[product]

        # Create the process
        recipes = self.products.get(product, [])
        process = ProcessNode(
            product, [self.get_process_for_recipe(r) for r in recipes]
        )

        # Cache and return the process
        self.processes[product] = process
        return process

    def get_process_for_recipe(self, recipe: NetRecipe):
        return ProcessNodeChild(
            recipe, [self.get_process(ing.name) for ing in recipe.ingredients]
        )
