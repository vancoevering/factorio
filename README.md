# Factorio

Scripts for making factory recipe calculations.

## game-scraper

Lua script that generates JSON files from local recipes (including installed mods).

### Usage

1. Copy the contents of the [Lua script](game-scraper.lua) to the clipboard.
2. Start Factorio and open a new world. (Be sure that you have enabled any mods you're using.)

**NOTE**: It is strongly recommended that
you DO NOT use an existing world. Running the script on an existing save WILL disable achievements. The script necessarily unlocks all research on this save so that each recipe can be scraped.

3. Open the console (usually using the `~` key).
4. Type `/c` followed by the `SPACEBAR` key, then paste the script from your clipboard and hit `ENTER`.
5. The game will show a console message warning of achievements being disabled if you continue. Open the console again and use the `UP` arrow key followed by `ENTER` to run the command.

**DONE!** The JSON files will appear in the `C:\Users\<UserName>\AppData\Roaming\Factorio\script-output\` folder.

Example outputs can be found [here](data/).
