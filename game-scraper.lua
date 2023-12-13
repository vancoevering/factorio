game.player.force.research_all_technologies()

local recipes = {}
for _, recipe in pairs(game.player.force.recipes) do
    if recipe.enabled then
        local entry = {}
        entry["name"] = recipe.name
        entry["category"] = recipe.category
        entry["ingredients"] = recipe.ingredients
        entry["products"] = recipe.products
        entry["energy"] = recipe.energy
        recipes[#recipes + 1] = entry
    end
end
game.write_file("factorio-recipes.json", game.table_to_json(recipes) .. "\n", false)

local crafters = {}
for _, proto in pairs(game.entity_prototypes) do
    if proto.crafting_categories ~= nil and proto.name ~= nil then
        local entry = {}
        entry["name"] = proto.name
        entry["crafting_speed"] = proto.crafting_speed
        entry["crafting_categories"] = proto.crafting_categories
        crafters[#crafters + 1] = entry
    end
end
game.write_file("factorio-crafters.json", game.table_to_json(crafters) .. "\n", false)
