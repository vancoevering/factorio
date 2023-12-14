from recipe import Recipe
from pathlib import Path
import json

DEF_DATA_PATH = Path(__file__).parent / "data"


def main():
    recipes_file = DEF_DATA_PATH / "factorio-recipes.json"
    with recipes_file.open("r") as f:
        recipes_data = json.load(f)
        recipes = {r.name: r for r in [Recipe.from_dict(d) for d in recipes_data]}
    print(recipes)
    print(recipes["atomic-bomb"])
    print(recipes["uranium-processing"])
    print(recipes["uranium-processing"].net())
    print(recipes["steel-plate"])
    print(recipes["kovarex-enrichment-process"])
    print(recipes["kovarex-enrichment-process"].net())


if __name__ == "__main__":
    main()
