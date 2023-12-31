import json
from pathlib import Path

from recipe import Recipe, ProcessFactory
from sdecimal import SDecimal

DEF_DATA_PATH = Path(__file__).parent / "data"


def main():
    recipes_file = DEF_DATA_PATH / "factorio-recipes.json"
    with recipes_file.open("r") as f:
        recipes_data = json.load(f)
        recipes = {r.name: r for r in [Recipe.from_dict(d) for d in recipes_data]}
    # print(recipes["iron-gear-wheel"].net().normalize_to_energy())
    # uranium_processing = recipes["uranium-processing"].net()
    # print(uranium_processing)
    # print(uranium_processing.normalize_to_energy())
    # print(uranium_processing.normalize_to_item(uranium_processing.ingredients[0]))
    # advanced_circuit = recipes["military-science-pack"].net()
    # print(advanced_circuit)
    # print(advanced_circuit.normalize_to_energy())
    # print(advanced_circuit.normalize_to_item(advanced_circuit.products[0]))
    # kovarex = recipes["kovarex-enrichment-process"].net()
    # print(kovarex)
    # print(kovarex.normalize_to_energy())
    # print(kovarex.normalize_to_product(0))
    # print(kovarex.normalize_to_ingredient(0))
    # print(kovarex.normalize_to_energy().parallelize(SDecimal(15)))
    # blue_science = recipes["chemical-science-pack"].net()
    # print(blue_science)
    # print(blue_science.normalize_to_product(0))
    # print(
    #     blue_science.normalize_to_product(0)
    #     .parallelize(SDecimal(12))
    #     .normalize_to_energy()
    # )
    # print(blue_science.target_product_per_energy(0, SDecimal(1)))
    # print(
    #     recipes["electronic-circuit"].net().target_product_per_energy(0, SDecimal(15))
    # )
    processor = ProcessFactory([r.net() for r in recipes.values()])
    petroleum = processor.get_process("petroleum-gas")
    for r in petroleum.recipes:
        print("petro from:", r.recipe.name, r, "\n")
    print("-" * 25)
    uranium_235 = processor.get_process("uranium-235")
    for r in uranium_235.recipes:
        print("235 from:", r.recipe.name, r, "\n")


if __name__ == "__main__":
    main()
