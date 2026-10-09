# Vale & The Labyrinth

**v0.01a is playable.** A Python terminal roguelike about exploring the Labyrinth beneath Vale, managing scarce light and supplies, and surviving long enough to bring treasure home.

## Install and run on Windows

1. Install **Python 3.10 or newer** from https://www.python.org/downloads/windows/. Include the Python launcher during installation; selecting **Add Python to PATH** is also helpful.
2. Download this repository with Git or GitHub's **Code → Download ZIP**, and extract the ZIP if needed.
3. Open PowerShell or Windows Terminal in the folder containing `play.py`.
4. Run:

   ```powershell
   py -3 play.py
   ```

No packages, virtual environment, account, or internet connection are needed to play. If `py` is unavailable but Python is on PATH, use `python play.py`.

For reproducible new-game randomness:

```powershell
py -3 play.py --seed 12345
```

Continue restores the saved random-generator state, so it does not replace it with the command-line seed. The same seed reproduces events when you make the same choices and take the same actions.

On Linux/macOS, use `python3 play.py`. Alternatively, run `python3 -m vale` (Windows: `py -3 -m vale`) from the repository folder.

## Playing

Enter the number beside a menu option and press Enter. Begin with **New Game**, use **Inventory / Equipment** on the opening screen to prepare, or choose **Go to Vale**.

- **Inventory / Equipment → Use Item → Torch** lights a torch. You need a free hand. A Zweihander occupies both hands; unequip it to carry light. Each spare torch takes its own inventory slot.
- Town actions keep you at the current location until you choose **Leave**. Inventory returns to its calling screen.
- Vale has the Tavern, Merchant, Shrine, Inn, Graveyard, and Labyrinth. Your starting silver is zero; sell an unwanted starting item or recover loot to earn money.
- A torch burns for an in-game hour. Ordinary travel takes five minutes (roughly 8–12 movements per torch with light interaction); searching takes ten minutes. Prose wraps at word boundaries; use `--text-width 72` to change the default width of 76. The HUD shows descriptive light stages, spare torches, HP, time, silver, Fortune, and statuses.
- Explore numbered exits, investigate prominent room objects and optional features, search for hidden caches/passages, collect loot, and harvest useful remains. Backtracking preserves the rooms and enemies already generated. There is no automap.
- In combat, choose **Attack**, **Use Item**, **Cast**, or **Flee**. Every surviving enemy acts after your action. A lit torch can be used as a fire attack. Scrolls are used through **Use Item**; characters start with no learned spells.
- A shield can be sacrificed when an incoming hit lands. Failed flight costs your action; successful flight takes you through the entrance you used. Monster damage persists.
- **Return to Vale** is available outside combat. Recovering dungeon treasure awards Fortune and XP once, immediately on extraction. Sell objects at the Merchant for spendable silver. Loose Silver caches go directly into your purse and award Fortune/XP only when safely extracted. Fortune never decreases when you spend money.
- Level-ups offer your choice of HP, Might, Cunning, or Magic. Inn rest recovers HP; the Shrine treats wounds and afflictions. Dungeon rest is free but can be interrupted.
- Death is permanent. The Graveyard ranks dead adventurers and the current living character by extracted Fortune.

Empty means no independently generated content; its descriptive objects can still be investigated, often yielding nothing. Sometimes looking costs more than it yields. Retreating is part of the game.

## Saves and Graveyard

The game autosaves after actions and offers **Save and Quit**, including during combat. Ctrl+C or end-of-input also saves an active game. **Continue** resumes your character, clock, merchant stock, statuses, current expedition, and random sequence.

Data lives in `.vale/save.json` and `.vale/graveyard.json` beside the source by default. Files are JSON and writes use atomic replacement. Death records a marker and invalidates that character's save; a recorded dead character cannot be continued. The program does not prevent someone from deliberately editing local data.

There is one active save per data directory. Starting another character asks before replacing a living save. Previous graves remain. For a separate playtest:

```powershell
py -3 play.py --seed 12345 --data-dir .vale-playtest
```

Save format version 1 is intended for this prototype; migration to future versions is not yet implemented.

## Implemented

- Independent random attributes and starting equipment; equipment slots and a 15-object unequipped inventory.
- All six Vale destinations, limited weekly merchant stock, Cunning pricing, rumors, drinks, meals, healing, blessings, identification, safe rest, and Graveyard ranking.
- All 13 specified room templates and their description variants; normal/secret content tables, persistent exit connections, depth advancement, hidden features, and better secret-room treasure.
- All seven features, three traps, five special encounters, eight utility items, eight treasures, six weapons, shields, and the final armor table. Tier 2 Plate and Mail is defined but excluded from ordinary Tier 1 generation.
- All ten monsters, equipment/corpse loot, venom harvesting, webbing, goblin flight, armor rolls, zombie headshots, sword overkill, troll regeneration, fire/acid suppression, and daylight petrification.
- Finite hand-held light, dangerous darkness, time-based poison/blessings/curses/meals/Tipsy, encounter-long Groggy, XP, chosen advancement, extraction accounting, saves, and permanent death.

`DESIGN.MD` describes the baseline; the v0.01a playtest patch changes ordinary content weights to 30/27/17/10/5/5/6, Skeleton armor to 1d4, and ordinary treasure results to 15% loose Silver (1d6+2) / 85% the unchanged treasure table. The final addendum overrides earlier tentative text. Prototype choices and remaining limitations are documented in [ASSUMPTIONS.md](ASSUMPTIONS.md).

## Tests and code

Run the standard-library test suite:

```powershell
py -3 -m unittest discover -s tests -v
```

Linux/macOS: `python3 -m unittest discover -s tests -v`.

Tests cover character creation, combat, equipment, inventory, generation probabilities, XP, extraction/Fortune, status timing, merchant refresh, room persistence, saves, death, and a real terminal expedition through all Vale destinations.

- `vale/data.py`: content, statistics, prices, and tuning constants.
- `vale/models.py`: character, items, rooms, and state.
- `vale/dungeon.py`: procedural generation and dice.
- `vale/engine.py`: gameplay rules, independent of terminal input.
- `vale/storage.py`: save and Graveyard persistence.
- `vale/cli.py`: terminal menus.

Further playtesting should check the revised exploration pacing, early economy, and contextual interactions. Windows launch instructions are provided; automated validation was performed on Python 3.12 on Linux, not on a Windows host.
