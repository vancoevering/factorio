import json
from pathlib import Path

from recipe import ProcessFactory, Recipe

DEF_DATA_PATH = Path(__file__).parent / "data"


def main():
    recipes_file = DEF_DATA_PATH / "factorio-recipes.json"
    with recipes_file.open("r") as f:
        recipes_data = json.load(f)
        recipes = {r.name: r for r in [Recipe.from_dict(d) for d in recipes_data]}

    processor = ProcessFactory([r.net() for r in recipes.values()])
    petroleum = processor.get_process("petroleum-gas")
    for r in petroleum.recipes:
        print("petro from:", r.recipe.name, r, "\n")
    print("-" * 25)
    uranium_235 = processor.get_process("uranium-235")
    for r in uranium_235.recipes:
        print("235 from:", r.recipe.name, r, "\n")
    print(uranium_235.to_printable_str())


if __name__ == "__main__":
    main()
