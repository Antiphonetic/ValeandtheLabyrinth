VALE & THE LABYRINTH

v0.01 Design Document

---

CORE CONCEPT

The player is an adventurer who has come to the ramshackle town of Vale to seek a fortune in the mysterious Labyrinth beneath the mountain.

The basic gameplay loop is:

Vale → Prepare → Enter Labyrinth → Explore → Fight / Discover / Loot → Decide Whether to Continue → Escape → Vale

The central tension should be:

"Do I go one room farther?"

The player enters the Labyrinth to acquire wealth, but light, HP, equipment, consumables, and other resources are limited. Returning safely with treasure is more important than killing everything encountered.

Combat is deliberately simple. Much of the game comes from exploration, resource management, preparation, risk assessment, and deciding when to retreat.

---

NEW GAME

When the player begins a new game:

- Generate a random medieval European name.
- Generate Might independently from 2–5.
- Generate Cunning independently from 2–5.
- Generate Magic independently from 2–5.
- Give the character one random Tier 1 weapon.
- Give the character three Torches.
- Give the character one random Tier 1 item/loot.
- No point-buy, rerolls, minimum total, or balancing between stats.

Possible names include:

Oswald
Siegfried
Edward
Edmund
Godfrey
Geoffrey
Roland
Hugh
William
Robert
Conrad
Dietrich
Otto
Alaric
Anselm
Baldwin
Bertram
Ulrich
Roderick
Theobald

Opening text:

NEW GAME

You are <random name>, come to Vale to seek your fortune in the Labyrinth beneath its mountain.

You have:

- <random Tier 1 weapon>
- 3 Torches
- <random Tier 1 item>

The entry to the Labyrinth stands before you, a chill breeze like breath touching your cheeks.

--Enter the Labyrinth--
--Go to Vale--

---

CHARACTER ATTRIBUTES

There are three primary attributes.

Might

Might governs:

- Maximum HP
- Weapon damage
- Physical interactions
- Alcohol tolerance
- Resistance to certain physical effects such as venom

Weapon damage bonus:

Might ÷ 2, rounded up

Might 2 = +1 damage
Might 3 = +2 damage
Might 4 = +2 damage
Might 5 = +3 damage

Cunning

Cunning governs:

- Chance to hit
- Merchant prices
- World interactions
- Searching
- Traps
- Locks
- Fleeing
- Potential self-identification mechanics

Merchant price effects are hidden from the player.

Higher Cunning means:

- Lower buying prices
- Higher selling prices

Magic

Magic governs:

- Spells
- Scrolls
- Potions
- Other supernatural interactions

Potion effectiveness may scale with Magic.

Magic does not necessarily imply a mana system.

---

LEVELING AND EXPERIENCE

XP comes from three sources:

Treasure

Treasure successfully extracted from the Labyrinth grants XP based on its silver value.

Tentative rule:

1 sp of extracted treasure = 1 XP

Treasure only grants this XP once.

Items brought into the Labyrinth from Vale do not generate XP by being returned.

The player does not need to sell treasure to gain its XP. The accomplishment is successfully extracting it.

Exploration

Exploration grants XP.

Tentative values:

- New room explored: 2 XP
- Reaching new depths gives larger bonuses.

Exact depth bonuses TBD.

Monsters

Combat XP is deliberately low so that killing monsters does not become the primary advancement strategy.

Threat XP:

Weak: 2 XP
Medium: 4 XP
Tough: 5 XP
Powerful: 7 XP
Impossible: 12 XP

Threat classifications are hidden.

The game should not encourage clearing every room merely for XP.

---

SILVER, FORTUNE, AND XP

These are separate values.

Silver

The player's currently spendable money.

Fortune

The total value of treasure successfully extracted from the Labyrinth over the character's lifetime.

Spending silver does not decrease Fortune.

Fortune determines Graveyard/high-score ranking.

Monster parts and ordinary spoils do not necessarily count as Fortune. Fortune is primarily treasure recovered from the Labyrinth.

XP

Character advancement resource earned from treasure, exploration, and monsters.

---

VALE

Main description:

VALE

This ramshackle town of tents and slapdash buildings has sprung up overnight, ready to service adventurers who attempt the Labyrinth.

Where would you like to go?

--Tavern--
--Merchant--
--Shrine--
--Inn--
--Graveyard--
--Labyrinth--

The Vale screen should display the current in-game day/time.

Example:

Day 12 — Evening

Vale is intentionally small in v0.01. New locations should only be added later when gameplay demands something that cannot comfortably fit within these locations.

---

TIME

The game tracks in-game time.

Merchant inventory refreshes every seven in-game days.

Time can eventually govern:

- Merchant inventories
- Tavern rumors
- Events
- Buff duration
- Quests
- Missing adventurers
- Other world changes

Sleeping can therefore be used to force merchant inventory resets, but doing so costs money at the Inn.

---

THE MERCHANT

Description:

MERCHANT

The greasy man's eyes dart back and forth as he shows you his wares. He would cheat you if he wasn't afraid you'd kill him.

--Buy--
--Sell--
--Leave--

Merchant Prices

Prices are affected by Cunning.

This mechanic is hidden.

Higher Cunning:

- Reduces purchase prices.
- Increases sale prices.

Some random price variation may exist as well.

Merchant Inventory

Inventory is limited.

Buying the merchant's only copy of an item removes it from stock.

Inventory refreshes every seven in-game days.

Some basic goods may be reliably available, while other equipment is randomly generated.

---

THE INN

Description:

INN

The biggest building in Vale. It beats sleeping in the Labyrinth—barely.

The innkeep looks at you with narrowed eyes.

"Want somefin'?"

--Rent a Room 10 sp--
--Buy a Meal 3 sp--
--Leave--

Rent a Room — 10 sp

Provides a safe full rest.

Advances time approximately eight hours.

Exact full-rest recovery rules TBD.

Buy a Meal — 3 sp

Grants:

Well Fed

+3% maximum HP
+3% XP gained

Duration:

24 in-game hours

The effect is time-based rather than lasting until the next rest.

---

RESTING IN THE LABYRINTH

Resting in the Labyrinth costs no silver but carries risk.

When attempting to rest:

- Roll for a random encounter.
- If no encounter occurs, the rest succeeds.
- If an encounter occurs, the rest is interrupted.
- The player does not receive the rest benefits.
- Combat begins with the player Groggy.

Groggy

While Groggy:

- Player hit chance is reduced.
- Enemy hit chance against the player is increased.

Current intended values:

Player: -20 percentage points to hit
Enemies: +20 percentage points to hit

Groggy lasts for the entire encounter that interrupted the rest.

---

THE SHRINE

Description:

SHRINE

A fancier tent than the rest—the cheap canvas is dyed—badly—red. A priest of Pyrios stands inside.

--Healing 2 sp--
--Blessing 5 sp--
--Cure Afflictions 5 sp--
--Identification 5 sp--
--Leave--

Healing — 2 sp

Tentatively restores 25% of maximum HP per treatment.

Exact healing amount can be adjusted during playtesting.

Blessing — 5 sp

For v0.01:

Blessing of Pyrios

+10% chance to hit
+10% damage

Duration:

24 in-game hours

Eventually there should be approximately 3–5 random blessings.

Cure Afflictions — 5 sp

Removes persistent afflictions that ordinary rest does not remove.

Examples may eventually include:

- Poison
- Disease
- Curses
- Other persistent conditions

Identification — 5 sp

Identifies one unidentified magical item.

Shrine identification is reliable.

Players may equip unidentified magical items without identifying them first.

This can reveal beneficial effects through use—or expose the player to cursed items.

Cunning may eventually provide a free but fallible method of self-identification.

---

THE TAVERN

Description:

TAVERN

Rough lumber walls, canvas roof and a battered table separating the patrons from the kegs. Cups are wood too, careful not to get a splinter.

--Buy a Drink 2 sp--
--Talk with Adventurers--
--Leave--

Buy a Drink — 2 sp

Every drink causes the barkeep to tell the player one true fact about the game.

The barkeep acts as an in-world tutorial/help system.

Examples:

"Priest can tell you what those funny-looking things do. Five silver. Or you can put 'em on and find out yourself."

"Don't sleep down there unless you've got to. Things find you, and you don't wake quick."

"Merchant's a cheat. Some folk get better prices out of him than others."

Every drink also carries a chance of making the player Tipsy.

The chance increases with each drink.

Higher Might reduces the chance.

Exact Tipsy mechanics TBD.

The player may continue buying drinks and receiving true information as long as desired.

Talk with Adventurers

Available for useful information once per in-game day.

Adventurers provide colorful rumors.

Their information may be:

- True
- False
- Exaggerated
- Outdated
- Misunderstood
- Complete nonsense

Example:

"My cousin says there's a woman six levels down been there a hundred years. Beautiful as midsummer, she is. Gives you a magic sword if you kiss her."

The game should not explicitly distinguish reliable barkeep information from unreliable adventurer rumors. Their different voices should teach the player the distinction.

---

THE GRAVEYARD

The Graveyard is the game's high-score system.

Every dead character remains recorded.

Suggested information:

- Name
- Total Fortune
- Deepest Depth
- Days Survived
- Cause of Death

Characters are ranked primarily by total Fortune successfully extracted from the Labyrinth.

The current living character also appears on the leaderboard, allowing the player to see themselves climbing past previous dead characters.

Example:

THE GRAVEYARD

Rough wooden markers crowd the hillside outside Vale. Some bear names. Others do not.

1. Siegfried † — 1,842 sp — Depth 6
2. Oswald † — 1,203 sp — Depth 5
3. Edward — 917 sp — Depth 4
4. Godfrey † — 406 sp — Depth 3

---

THE LABYRINTH

Every entry begins with:

THE LABYRINTH

The light of the outside world fades behind you as the gloom and damp press in.

You see...

The remainder is procedurally generated.

Labyrinth Generation

The Labyrinth is random each time the player enters it from Vale.

Once inside, the generated layout remains persistent for that expedition.

Leaving the Labyrinth and later returning causes it to regenerate.

This means adventurer rumors about geography may have been true at one point but no longer correspond to the current Labyrinth.

---

NAVIGATION

Navigation works similarly to Vale.

There is no grid-based movement interface and no automap.

Each room functions conceptually as a card.

Each room card includes:

- Room description
- Number of exits
- Direction/type of exits
- Visible interactive features
- Potential monsters
- Potential treasure
- Potential traps
- Potential puzzles
- Potential hidden features
- Flavor

Geometry does not need to be perfectly coherent.

Possible exits include:

- Northern Hall
- Southern Door
- Eastern Passage
- Curtain of Shadows
- Spiral Stair
- Narrow Crack
- Flooded Tunnel
- Iron Gate
- Hole in Floor
- Shaft
- Etc.

Mechanically, exits connect room nodes.

Entering an unexplored exit generates/draws a new room.

Backtracking through an existing connection returns to the previously generated room.

Rooms remain persistent until the player leaves the Labyrinth.

Empty Rooms

Many rooms should contain nothing important.

This is intentional.

Exploration consumes light and time. The player should not learn that every room necessarily contains a monster, treasure, puzzle, or reward.

Flavor objects may sometimes be meaningless.

Example:

An iron spike driven into a wall may simply be an old iron spike.

Searching it may waste time.

In another room, a similar iron spike might indicate a hidden cache.

---

ROOM GENERATION

Room generation can occur in layers.

Conceptually:

Room Template → Contents → Feature → Hidden Feature

Example:

Flooded Cellar
Contents: None
Feature: Iron Spike
Hidden: None

Another generation of the same basic template:

Flooded Cellar
Contents: 3 Giant Rats
Feature: Corpse
Hidden: Purse beneath corpse

This allows a relatively small set of physical room templates to generate many different experiences.

---

LIGHT

Light is a major dungeon resource.

The HUD should always display:

- Number of spare Torches
- Current light condition

Torches burn for:

1 in-game hour

Light condition should be descriptive rather than displaying exact remaining percentages.

Possible stages:

Bright → Steady → Dim → Guttering → Darkness

The engine may internally track exact remaining burn time.

The player does not receive the exact number.

Lighting a new torch during combat consumes the player's action.

Darkness should be severely dangerous and affect:

- Hit chance
- Perception
- Traps
- Exits
- Loot detection
- Enemy detection
- Potential special encounters

Exact Darkness penalties TBD.

---

COMBAT

Combat is deliberately extremely simple in v0.01.

Player always acts first.

The player receives one action.

Then every surviving enemy receives one action.

Then the player acts again.

Example with three rats:

Player → Rat A → Rat B → Rat C → Player

Being outnumbered is therefore dangerous.

Player combat options:

--Attack--
--Use Item--
--Cast--
--Flee--

Attack

Select target if multiple enemies exist.

Roll hit chance.

On success, roll weapon damage.

Apply Might damage bonus.

Target rolls armor if applicable.

Apply remaining damage.

Use Item

Consumes the player's entire turn.

Examples:

- Drink potion
- Apply venom
- Light torch
- Use another consumable

Enemies then act normally.

Cast

Allows spellcasting.

A character who knows no spells may simply receive:

"You know no spells."

Flee

Fleeing is not automatic.

Exact formula TBD.

Cunning should influence success.

Failure consumes the player's turn and enemies act normally.

Successful fleeing returns the player through the exit by which they entered.

Enemies do not automatically heal/reset when the player flees.

The current Labyrinth remains persistent until the expedition ends.

---

ARMOR

Armor does not make the player harder to hit.

Armor reduces incoming damage.

When hit:

1. Enemy rolls damage.
2. Armor rolls damage reduction.
3. Armor reduction is subtracted from damage.
4. Damage cannot fall below 0.

Might does not add to armor rolls.

Example:

Enemy deals 5 damage.

Padded Jack rolls 3.

Player takes 2 damage.

Tier 1 Armor

Padded Jack
Armor: 1d4

Worn Padded Jack
Armor: 1d4

Ragged Padded Jack
Armor: 1d4-1, minimum 0

Rags
Armor: 0

Condition affects value even when it does not yet affect mechanical performance.

Future Durability System

Not included in v0.01.

Eventually armor should degrade according to damage successfully absorbed, rather than number of hits received.

Tentative durability:

Approximately 10–15 absorbed damage per condition step.

Possible baseline:

12 absorbed damage per step.

Padded Jack
→ Worn Padded Jack
→ Ragged Padded Jack
→ Rags

Durability numbers should be hidden from the player.

The player sees condition states rather than:

"Durability 7/12"

---

WEAPONS AND EQUIPMENT

Dagger

Damage: 1d4

Special:

On a maximum damage roll, add ½ Cunning, rounded down, to the damage.

Example:

Cunning 2–3 = +1
Cunning 4–5 = +2

Might bonus is also applied normally.

Spear

Damage: 1d4+1

Special:

+10 percentage points to hit

Mace

Damage: 1d4

Special:

Reduce opposing armor rolls by 1, minimum 0.

Example:

Skeleton rolls 5 armor.

Mace reduces this to 4.

Arming Sword

Damage: 1d6

Special:

Overkill damage carries into the next enemy.

Example:

Enemy has 2 HP.

Arming Sword deals 6 damage.

Enemy dies.

4 damage carries to the next enemy.

Battle-axe

Damage:

1d6+1

No special ability.

Zweihander

Damage:

2d6+1

Special:

Overkill damage carries into the next enemy.

Requires both hands.

Shield

Special:

May be sacrificed to negate one incoming hit entirely.

The shield is destroyed/removed when used this way.

Torch

Provides light for:

1 hour

Can function as dungeon equipment and potentially interact with fire-sensitive mechanics.

---

UNIDENTIFIED ITEMS

Magical items may be unidentified.

Players may:

- Pay the Shrine 5 sp to identify one.
- Potentially identify one themselves through future mechanics.
- Equip/use the item without identifying it.

Equipping an unidentified item is allowed even if the item is cursed.

---

MONSTER DESIGN

Most monster statistics are hidden.

The player generally sees:

- Monster name
- Tagline
- Current HP, unless the monster specifically conceals HP

The player does NOT normally see:

- Hit chance
- Damage
- Armor
- Threat
- XP
- Special mechanics

Players learn these through experience.

Every monster type has its own hit chance.

---

MONSTERS

Giant Rat

Wait, these really exist?

HP: 5/5

Hidden:

Hit Chance: 50%
Armor: None
Damage: 1d4-1, minimum 1
Threat: Weak
XP: 2

Loot:

Rat Pelt — 2 sp

---

Cave Bat

Don't let it get in your hair

HP: 3/3

Hidden:

Hit Chance: TBD
Armor: None
Damage: 1d4
Evasion: Attackers suffer -15 percentage points to hit
Threat: Weak
XP: 2

Loot:

Bat Wings — 2 sp

---

Goblin

Like if a ferret and a lizard crossbred. Gross.

HP: 5/5

Hidden:

Hit Chance: 50%
Armor: 1d2
Damage: 1d4+1
Threat: Weak
XP: 2

Behavior:

When reduced to 50% HP or lower, the Goblin attempts to flee on its turn.

Fleeing should not necessarily automatically succeed.

Loot:

Dagger
plus
Random carried-drop roll

The dagger has a random condition where applicable.

---

Skeleton

Is that...Geoffrey?

HP: 1/1

Hidden:

Hit Chance: 50%
Armor: 2d4
Damage: 1d6
Threat: Weak
XP: 2

Loot:

- Random Tier 1 weapon, random condition
- Random Tier 1 armor, random condition
- Random carried-drop roll

The Skeleton's identity is extreme fragility protected by strong armor/equipment.

---

Zombie

Oh, no, that's Geoffrey

HP: 7/7

Hidden:

Hit Chance: 50%
Armor: None
Damage: 1d4
Threat: Weak
XP: 2

Special:

Headshot

If the player's weapon damage die rolls its natural maximum, the Zombie is instantly killed.

Only the damage die matters.

Might bonuses, total damage, critical bonuses, etc. do not determine Headshot.

Examples:

1d4 weapon → natural 4 triggers Headshot
1d6 weapon → natural 6 triggers Headshot

Loot:

Random carried-drop roll

---

Giant Spider

Venom drips from its fangs

HP: 8/8

Hidden:

Hit Chance: 50%
Armor: None
Damage: 1d4
Threat: Medium
XP: 4

Special:

Venom

Whenever the Spider deals at least 1 actual HP damage to the player:

Poison chance = 100% ÷ player's Might

Might 2 = 50%
Might 3 = 33.3%
Might 4 = 25%
Might 5 = 20%

If armor reduces damage to 0, poison cannot occur.

Web

Deals 0 damage.

Uses the Spider's attack roll.

On a successful Web attack, the player is Bound and loses their next turn.

Usable once per fight.

Exact Spider AI for deciding when to use Web TBD.

Loot:

The player may harvest Spider Venom if carrying an Empty Bottle.

Spider Venom

Apply to a weapon.

The next successful attack gains:

- +1d2 damage
- Chance to Poison

Exact poison chance against monsters TBD.

Harvesting consumes an Empty Bottle and produces Spider Venom.

Using the venom returns an Empty Bottle.

---

Ooze

HP: ?/?

The player does not know the Ooze's current or maximum HP.

Hidden:

HP: 2d6, rolled when spawned
Hit Chance: 40%
Armor: None
Damage: 1d4
Threat: Medium
XP: 4

Special:

Acidic

When armor durability is eventually implemented, damage absorbed from an Ooze counts twice toward armor degradation.

This property has no mechanical effect in v0.01 because durability is not yet implemented.

The Ooze's HP remains displayed as ?/? throughout combat.

---

Cave Bear

Tagline TBD

HP: 10/10

Hidden:

Hit Chance: 50%
Armor: None
Damage: 1d4+1
Special: None
Threat: Medium
XP: 4

Loot:

Likely Bear Pelt.

Exact value TBD.

---

Ogre

His breath reeks of rotting flesh

HP: 18/18

Hidden:

Hit Chance: 60%
Armor: None
Damage: 1d6+1
Special: None
Threat: Tough
XP: 5

Loot:

Improved random carried-drop roll.

The Ogre's design is intentionally straightforward. It is dangerous because it has a large HP pool, high accuracy, and high damage rather than because of special abilities.
Troll
Scaly, green, huge, and leaking pus from its canker sores.
HP: 12/12
Hidden:
Hit Chance: 50%
Armor: None
Damage: 1d6
Threat: Tough
XP: 5
Special:
Regeneration
Regains 1d2 HP per turn unless it has been dealt Fire or Acid damage.
Fire or Acid suppresses regeneration.
Turn to Stone
Exposure to actual daylight immediately turns the Troll to stone and kills it.
Torchlight does not count.
Fire suppresses regeneration but does not petrify the Troll.
A Troll killed through daylight petrification:
Drops no loot.
This allows the player to potentially lure a Troll to daylight for a safer kill while sacrificing its treasure.
Loot:
Improved random carried-drop roll if killed normally.
MONSTER DISTRIBUTION
Current v0.01 bestiary:
Weak — 2 XP
Giant Rat
Cave Bat
Goblin
Skeleton
Zombie
Medium — 4 XP
Giant Spider
Ooze
Cave Bear
Tough — 5 XP
Ogre
Troll
Powerful — 7 XP
None yet.
Impossible — 12 XP
None yet.
Total:
10 monsters
Distribution:
5 Weak / 3 Medium / 2 Tough
This is sufficient for the initial prototype.
MONSTER LOOT
Monster loot should generally make physical sense rather than use a universal generic loot table.
There are three conceptual kinds of monster loot:
Equipped Loot
Items the creature was visibly using.
Examples:
Goblin dagger
Skeleton weapon
Skeleton armor
Carried Loot
Random possessions found on the creature.
Goblin, Skeleton, Zombie, Ogre, Troll, etc. may receive carried-loot rolls.
Possible results include:
Nothing
Silver
Tier 1 item
Treasure
Tentative basic random-drop table:
1–50: Nothing
51–75: Silver
76–95: Tier 1 item
96–100: Tier 1 treasure
Tentative silver amount:
1d6 sp
Exact table TBD during item/economy design.
Harvested Loot
Requires interaction with the corpse.
Examples:
Rat Pelt
Bat Wings
Spider Venom
SPIDER VENOM AND BOTTLES
Empty Bottles are reusable containers.
If the player has an Empty Bottle after killing a Giant Spider:
--Harvest Venom--
--Leave--
Harvesting changes:
Empty Bottle → Spider Venom
Using Spider Venom changes:
Spider Venom → Empty Bottle
This establishes containers as reusable resources rather than disposable abstractions.

DESIGN PRINCIPLES ESTABLISHED SO FAR
1. The dungeon is the primary game.
Vale exists to prepare for, recover from, and profit from expeditions.
2. Going farther should always be a decision.
The core tension is not simply winning fights. It is deciding whether another room is worth the resources and danger.
3. Combat is simple.
Player gets one action.
Enemies each get one action.
Complexity should primarily come from monsters, equipment, circumstances, and preparation rather than large player combat menus.
4. Fighting is not the primary advancement system.
Treasure and exploration should matter more than monster XP.
Avoiding a pointless fight should often be smart.
5. Items expand options.
Rope should actually solve rope problems.
Empty bottles should allow harvesting liquids.
Torches should actually provide finite light.
Equipment should not merely be collections of abstract stat bonuses.
6. Information is imperfect.
The barkeep tells the truth.
Adventurers may not.
Monster mechanics are hidden.
Merchant price formulas are hidden.
Durability will eventually be hidden.
Players learn the game by playing it.
7. Inconvenience is allowed.
The design should not automatically remove friction.
Limited light, finite merchant stock, risky dungeon rest, identification, equipment condition, resource management, and uncertain information are features.
8. Manipulating systems should be possible, but costly.
The player may sleep for seven days to refresh merchant inventory.
Doing so costs seven nights at the Inn.
The game does not need to forbid behavior simply because it can be exploited. Costs and consequences should make the choice meaningful.
9. The Labyrinth does not care whether the player is prepared.
If the player encounters a shaft without rope, that is their problem.
If their torch dies during combat, lighting another consumes their turn.
If they equip an unidentified cursed item, they chose to take that risk.
10. Death becomes history.
Dead adventurers remain in the Graveyard.
The player's failures become part of the continuing game's record.
CURRENTLY UNRESOLVED BEFORE CODING
The major remaining v0.01 design work is:
Tier 1 Items
Need approximately 8–10 initial tools/consumables.
Known possibilities already include:
Rope
Healing Potion
Empty Bottle
Torch
Possibly Oil
Possibly Chalk
Possibly Antidote
Treasure
Need a basic treasure table with silver values.
Examples discussed:
Silver Candlestick
Brass Reliquary
Ivory Comb
Pewter Goblet
Carved Bone Dice
Silver Brooch
Small Icon
Jeweled Hairpin
Fine Drinking Horn
Bolt of Silk
Character Math
Still need exact formulas for:
Starting HP / Might → HP
Cunning → base player hit chance
Flee chance
Level thresholds
Level-up rewards
Status Effects
Need exact mechanics for:
Poisoned
Tipsy
Darkness
Other initial afflictions as required
Groggy and Well Fed are already substantially defined.
Rooms
Need approximately 15–20 initial room templates.
Need tables for:
Contents
Exits
Features
Hidden features
Traps
Treasure
Monster encounters
Empty rooms
Many rooms should intentionally be empty.
Economy
Need:
Tier 1 item prices
Weapon prices
Armor prices
Treasure values
Monster-part values beyond Rat/Bat
Merchant inventory generation
Loot Tables
Need final carried-loot probabilities and values.
Saving
The game should preserve:
Current character
Vale/time state
Current expedition layout while inside
Graveyard/high scores
Possibly broader persistent data
NEXT DEVELOPMENT ORDER
Finish Tier 1 armor/items.
Create Tier 1 consumables/tools.
Create treasure table.
Finalize character math.
Define status effects needed for v0.01.
Create approximately 15–20 room templates.
Create room-content/encounter generation.
Build playable v0.01.
Play it.
Discover what sucks.
Change it.


VALE & THE LABYRINTH

v0.01 Design Addendum

This addendum supersedes conflicting tentative values in the earlier design document.

---

ARMOR — FINAL v0.01 TABLE

Armor reduces incoming damage rather than affecting chance to hit.

When physical damage is received:

1. Attacker rolls damage.
2. Defender rolls armor.
3. Armor result is subtracted from damage.
4. Minimum final damage is 0.

Might does not add to armor.

Tier 1

Padded Jack

Armor: 1d4

Mail Hauberk

Armor: 1d6

Brigandine Cuirass

Armor: 1d6+1

Tier 2

Plate and Mail

Armor: 1d8+2

Plate and Mail is not part of the normal Tier 1 equipment pool.

Condition

Equipment may generate in varying conditions.

Current intended progression:

Normal
→ Worn
→ Ragged
→ Ruined/Rags

Worn equipment has the same mechanical performance as normal equipment but lower value and less remaining durability.

Ragged armor receives −1 to its armor roll, minimum 0.

Future durability should be based on total damage absorbed.

Tentative future degradation threshold:

Approximately 12 damage absorbed per condition step.

Durability degradation itself does not need to function in v0.01.

---

WEAPONS — FINAL v0.01 TABLE

All player weapon attacks add:

Might ÷ 2, rounded up

to damage.

Dagger

Damage: 1d4

On a maximum natural damage roll, add:

½ Cunning, rounded down

to damage.

Spear

Damage: 1d4+1

+10 percentage points chance to hit

Mace

Damage: 1d4

Reduce opposing armor rolls by 1, minimum 0.

Arming Sword

Damage: 1d6

Overkill damage carries into the next enemy.

Example:

Enemy has 2 HP.

Attack deals 6 damage.

Enemy dies and 4 damage carries to the next enemy.

Battle-axe

Damage: 1d6+1

No special property.

Zweihander

Damage: 2d6+1

Overkill damage carries into the next enemy.

Requires both hands.

Shield

Requires one hand.

May be sacrificed to completely negate one incoming hit.

The Shield is destroyed/removed when used this way.

Torch

Requires one free hand while providing light.

Sheds light for 1 in-game hour.

---

TIER 1 UTILITY ITEMS

Healing Potion

Recover:

1d4 + Magic HP

Torch

Sheds light for:

1 hour

Requires a free hand while in use.

Lighting a Torch during combat consumes the player's action.

Rope

Allows additional navigation options where appropriate.

Examples:

- Descending shafts
- Accessing otherwise unreachable exits
- Potentially escaping certain environmental hazards

Rope should function contextually rather than provide a generic numerical bonus.

Oil

Consumed when used.

Makes a monster:

Flammable

Oil itself deals no damage.

A subsequent source of fire may ignite the target.

This can interact with creatures such as Trolls.

Scroll

Contains one single-use spell.

Anyone may use a Scroll regardless of Magic.

There is no minimum Magic score and no generic casting check merely to activate a Scroll.

Magic may affect the effectiveness of individual spells where appropriate.

Pick

Used to pick locks.

Chance of success:

(12 × Cunning) − Lock Difficulty

If the attempt fails by 10 percentage points or more, the Pick breaks.

Antidote

When consumed:

Chance to cure Poison = 12 × Magic%

Examples:

Magic 2 = 24%
Magic 3 = 36%
Magic 4 = 48%
Magic 5 = 60%

The Antidote is consumed whether or not it succeeds.

Empty Bottle

Reusable container.

Currently used primarily for harvesting Giant Spider Venom.

After harvesting:

Empty Bottle → Spider Venom

After using Spider Venom:

Spider Venom → Empty Bottle

---

TREASURE TABLE

Treasure recovered from the Labyrinth contributes its value to:

- XP
- Fortune
- Sale value

Monster parts/spoils do not necessarily count as treasure for XP/Fortune.

Tier 1 Treasure

Treasure| Value
Brass Candlestick| 1 sp
Tin Cup| 1 sp
Copper Platter| 3 sp
Brass Sculpture| 5 sp
Uncut Gemstone| 6 sp
Silver Candelabra| 12 sp
Silver Goblet| 15 sp
Golden Idol| 35 sp

Normal Treasure Generation

Treasure| Chance
Brass Candlestick| 25%
Tin Cup| 25%
Copper Platter| 15%
Brass Sculpture| 10%
Uncut Gemstone| 10%
Silver Candelabra| 7%
Silver Goblet| 5%
Golden Idol| 3%

Treasure found behind Secret Doors uses an improved rarity distribution weighted toward more valuable treasure.

Exact improved distribution may be implemented/tuned during development.

---

CHARACTER MATH — FINAL v0.01

Starting attributes are independently rolled from:

2–5

for:

- Might
- Cunning
- Magic

There is no minimum total and no reroll protection.

Maximum HP

At character creation:

Max HP = 5 × Might

Examples:

Might 2 = 10 HP
Might 3 = 15 HP
Might 4 = 20 HP
Might 5 = 25 HP

Damage Bonus

All ordinary weapon damage receives:

Might ÷ 2, rounded up

Examples:

Might 2 = +1
Might 3 = +2
Might 4 = +2
Might 5 = +3

Base Hit Chance

(10 × Cunning) + 10%

Examples:

Cunning 2 = 30%
Cunning 3 = 40%
Cunning 4 = 50%
Cunning 5 = 60%

Other effects modify this chance in percentage points unless otherwise specified.

Flee Chance

12 × Cunning%

Examples:

Cunning 2 = 24%
Cunning 3 = 36%
Cunning 4 = 48%
Cunning 5 = 60%

Failure consumes the player's turn.

Level Advancement

Cumulative XP thresholds:

Level 2: 100 XP
Level 3: 300 XP
Level 4: 600 XP
Level 5: 1,000 XP
Level 6: 1,500 XP

This pattern may continue beyond Level 6 if required.

Level-Up Reward

On each level-up, choose one:

- Gain permanent Max HP equal to current Might.
- Increase Might by 1.
- Increase Cunning by 1.
- Increase Magic by 1.

Attributes may exceed 5 through advancement.

5 is the character-generation maximum, not an absolute attribute cap.

---

INVENTORY AND EQUIPMENT

v0.01 uses a simplified Diablo 1-style paper-doll equipment system.

Relevant equipment slots include at minimum:

- Head
- Body
- Main Hand
- Off Hand

Head may remain unused until appropriate equipment is added.

Two-handed weapons occupy both Main Hand and Off Hand.

A lit Torch occupies one hand.

A Shield occupies one hand.

Examples:

Valid:

Arming Sword + Shield
Arming Sword + Torch
Spear + Torch
Zweihander

Invalid:

Zweihander + Torch
Zweihander + Shield

Inventory

The player may carry:

15 unequipped items

No weight system, inventory-grid system, or detailed encumbrance system is required for v0.01.

Each carried object occupies one inventory slot.

This means low-value treasure may become undesirable when inventory space becomes scarce.

---

POISON

Poison causes:

−10 percentage points chance to hit

and

−10% damage

Poison duration:

12 − Might hours

The poisoned character loses:

1 HP per in-game hour

for the duration.

Starting-stat examples:

Might 2 → 10 hours
Might 3 → 9 hours
Might 4 → 8 hours
Might 5 → 7 hours

Poison may be removed early by:

- Successful Antidote
- Shrine Cure Afflictions
- Other future effects

---

DARKNESS

When the player has no functioning light source:

−20 percentage points chance to hit

Darkness also makes dungeon exploration more dangerous.

While exploring in Darkness:

- Increase the chance of generating monsters.
- Introduce an additional chance to roll twice on the monster table.
- Other perception/navigation penalties may be added later.

Exact Darkness encounter-generation percentages are a tuning value and may be established during implementation/playtesting.

---

ROOM GENERATION

A newly generated room first selects a physical room template.

Then its gameplay contents are generated separately.

The room template describes the place.

The content generator determines what is actually happening there.

A mechanically Empty room may still contain substantial descriptive dressing.

---

ROOM CONTENT TABLE

For ordinary rooms:

d100| Result
01–40| Empty
41–65| Monster
66–77| Treasure
78–85| Feature
86–90| Trap
91–95| Special
96–100| Roll Twice

Roll Twice

Roll twice again on the same table.

If Roll Twice is rolled again while resolving Roll Twice, reroll that result.

Duplicates are allowed.

Possible combinations therefore include:

Monster + Treasure
Monster + Monster
Treasure + Treasure
Monster + Trap
Feature + Treasure
Special + Monster
Empty + Monster
Empty + Empty
etc.

Roll Twice does not guarantee a more valuable or dangerous room.

---

HIDDEN FEATURES

Hidden features are generated separately from ordinary room contents.

Tentative chance:

10% per room

Possible hidden features include:

- Secret Door
- Hidden treasure/cache
- Other future discoveries

Searching may reveal these based on Cunning or other circumstances.

---

EXITS

Each room generates:

1d4 exits

For v0.01, strict dungeon geography does not need to be simulated.

The player has access to:

--Return to Vale--

while exploring the Labyrinth.

This is an intentional v0.01 simplification.

More demanding navigation/backtracking rules may replace it later.

---

ROOM TEMPLATES

1. Sunken Crypt

«Water, black and still, floods this room to your ankles. <A sarcophagus on a dais dominates the far wall. OR Bones fill grave niches in the walls. OR A statue worn featureless stands eight feet tall in the center of the room, towering over a small casket.>»

Select one dressing variant.

---

2. Shadowed Hall

«The darkness presses in <against your torchlight>. You feel a faint unease.»

"Against your torchlight" appears only when the player currently has torchlight.

---

3. Decrepit Vault

«The stone here is spalling almost to gravel. <Cracks run down the walls. OR Sunlight filters through a crack in the ceiling.>»

If the sunlight variant is generated, the room contains actual daylight.

This interacts naturally with creatures vulnerable to daylight.

For example:

A Troll entering this variant turns to stone and dies without dropping loot.

---

4. Petrified Courtyard

«Rows of stone planters are filled with stone <ferns OR flowers in full bloom>. In the center, <a stone ash tree OR a fountain where water seems to have turned to stone mid-flow> dominates the space.»

The two variations are independent, allowing four combinations.

The Courtyard does not inherently contain daylight.

---

5. Winding Tunnel

«This tunnel was clearly dug by something. Rough walls of mud and stone bend and bend. It is not tall enough to stand straight up inside.»

The low ceiling may become mechanically significant in later versions.

---

6. Damp Chamber

«Water trickles down the walls and <puddles on the floor OR flows down a shaft in the floor>. The air stinks of stale mildew.»

The shaft variant may sometimes provide an interaction/navigation opportunity.

Rope may allow safe descent where appropriate.

Not every shaft must lead anywhere useful.

---

7. Natural Cavern

Size and lighting description are linked.

Huge

«The masonry gives way to a huge natural cavern. Your torchlight cannot illuminate the whole space.»

Sizeable

«The masonry gives way to a sizeable natural cavern. Your torchlight barely illuminates the whole space.»

Small

«The masonry gives way to a small natural cavern. Your torchlight easily illuminates the whole space.»

If the player has no light, omit the torchlight sentence.

---

8. Terraced Gallery

«A balustrade winds around the edge of this room <above OR below> your vantage point. The ceiling arches away to shadow.»

---

9. Pillared Hall

«A long, wide hall with dozens of broad pillars stretches on for what seems an endless space.»

---

10. Flooded Chamber

«This room is flooded. In the brackish depths, you can just make out <something glimmering OR a shadowy doorway OR some dim shape fluttering>.»

The water is substantially deeper than the ankle-deep water of the Sunken Crypt.

The suggested objects need not always resolve into the same thing.

---

11. Ancient Armory

«The walls are lined in rusted iron blades, the floors strewn with crumbling leather and mail. Rotten chests along the far wall catch your eye.»

The descriptive weapons/armor do not automatically constitute usable loot.

Most may simply be ruined.

---

12. Mosaic Baths

«The ruins of an ancient public bath stretch before you, the water now <dried up OR clouded with dust and grime>.»

---

13. Desecrated Temple

«Still-sticky blood and wet bone litter the floor and altar of this room, arrayed in profane glyphs. The statuette of <Pyrios OR Llamela OR Lyrissia> has its face turned away.»

The blood and bone appear recent.

No explanation is automatically provided for the turned statuette.

---

MONSTER GENERATION

For v0.01:

One Monster result = one monster.

The desired long-term threat distribution is:

Weak: 60%
Medium: 30%
Tough: 5%
Powerful: 3%
Impossible: 2%

Because v0.01 contains no Powerful or Impossible monsters, redistribute those percentages for the prototype:

Threat| v0.01 Chance
Weak| 63%
Medium| 32%
Tough| 5%

Then randomly select a monster from that category.

Weak

- Giant Rat
- Cave Bat
- Goblin
- Skeleton
- Zombie

Medium

- Giant Spider
- Ooze
- Cave Bear

Tough

- Ogre
- Troll

When Powerful and Impossible monsters are introduced, restore the intended:

60 / 30 / 5 / 3 / 2

distribution.

---

SECRET ROOMS

Rooms entered through Secret Doors use a different content table.

Result| Normal| Secret Room
Empty| 40%| 20%
Monster| 25%| 20%
Treasure| 12%| 30%
Feature| 8%| 10%
Trap| 5%| 5%
Special| 5%| 5%
Roll Twice| 5%| 10%

Secret-room treasure should also use a better rarity distribution than ordinary treasure.

Secret rooms therefore:

- Generate treasure more often.
- Generate multiple contents more often.
- Produce higher-value treasure more often.

They may still be completely empty.

---

FEATURES

Features are visible interactive elements.

Interaction is optional.

Features should generally include a chance that interacting produces nothing useful.

This prevents players from learning that every described object necessarily represents a reward.

Corpse

«A corpse lies sprawled on the floor.»

Options:

--Search Corpse--
--Leave It--

Possible results include:

- Nothing
- Loot
- Zombie
- Trap

Exact percentages may be tuned during implementation.

Locked Chest

«A battered ironbound chest rests against the wall.»

Options:

--Pick Lock--
--Leave It--

Uses Pick mechanics.

On successful opening:

Tentative:

70% Treasure
20% Tier 1 item
10% Nothing

These percentages may be tuned.

Deep Shaft

«A black shaft descends beyond the reach of your torchlight.»

If Rope is available:

--Secure Rope and Descend--
--Leave It--

Without Rope, the descent is unavailable.

Using the shaft creates an additional navigation option.

Locked Door

A locked exit.

May be opened using a Pick.

Uses:

(12 × Cunning) − Lock Difficulty

Failure by 10 or more breaks the Pick.

The reward for opening the door is access, not necessarily treasure.

Lifelike Statue

A disturbingly realistic statue.

Possible interaction outcomes:

Tentative:

50% Nothing
20% Treasure
15% Bless
10% Curse
5% Monster

Exact percentages may be tuned.

Iron Spike

An ordinary-looking iron spike protruding from the masonry.

Possible outcomes:

Tentative:

70% Nothing
15% Hidden treasure/cache
10% Trap
5% Secret Door

The high Nothing chance is intentional.

An Iron Spike should not become synonymous with "secret lever."

Fresco

«A faded fresco covers much of one wall.»

Options:

--Examine Fresco--
--Leave It--

Possible outcomes include:

- Lore only
- Nothing mechanically
- Clue/reveal
- Hidden treasure
- Bless
- Curse

Tentative distribution:

60% Lore/no mechanical effect
15% clue/reveal
10% hidden treasure
10% Bless
5% Curse

Lore itself is considered a valid reward even when it has no mechanical effect.

---

SECRET DOOR

Secret Doors are normally hidden rather than presented as ordinary visible Features.

Searching may reveal one.

Once discovered, a Secret Door becomes an additional exit for the duration of that expedition.

The room beyond uses the Secret Room generation table.

---

TRAPS

Traps are not automatically announced.

The player receives a chance to detect them.

Tentative detection formula:

Trap Detection = (12 × Cunning) − Trap Difficulty

If detected, the player may avoid/disarm the trap as appropriate.

Spike Trap

Tentative Difficulty: 10

Damage:

1d6 physical

Armor applies.

Pitfall

Tentative Difficulty: 15

Damage:

1d6+1 physical

Armor applies.

May also affect navigation/position.

Rope may provide additional options for dealing with the pit or escaping it.

Poisoned Arrow

Tentative Difficulty: 20

Damage:

1d4 physical

Armor applies.

If at least 1 HP penetrates armor, the arrow may inflict Poison.

Tentatively use the same poison-resistance formula as Giant Spider venom:

Poison chance = 100 ÷ Might%

---

SPECIAL RESULTS

Specials are rare events/anomalies that do not fit ordinary Feature, Monster, Treasure, or Trap generation.

They should feel unusual, unexplained, or unsettling.

Human Baby

«A human baby lies wailing upon a heap of towels.»

Options:

--Pick Up the Baby--
--Leave--

Exact consequences intentionally unresolved.

The game should not automatically tell the player whether the baby is what it appears to be.

Tavern Sign

«The sign to the tavern hangs on the wall here.»

No required mechanical effect in v0.01.

It is simply inexplicably present inside the Labyrinth.

Opalescent Fountain

«A colorful fountain stands here, spraying opalescent light instead of water.»

Options:

--Touch the Light--
--Leave It--

Tentative effect table:

40% Nothing
20% Heal
15% Bless
15% Curse
10% Reserved/strange effect

For v0.01, the reserved result may simply resolve as Nothing until additional effects are implemented.

Heal

Restore 25% maximum HP.

Bless

Same effect as the Shrine's v0.01 Blessing:

+10 percentage points hit chance
+10% damage

Duration:

24 hours

Curse

Inverse of Blessing:

−10 percentage points hit chance
−10% damage

Duration:

24 hours

Wounded Animal

Generate one:

- Wounded Giant Rat
- Wounded Cave Bat
- Wounded Cave Bear

The creature is not automatically hostile.

Tentative outcomes/interactions may include:

- Nothing unusual
- Creature becomes hostile
- Harvest appropriate monster material
- Attempt to help it
- Strange/unusual result

No animal-companion system is required for v0.01.

Pale Book

«A pale leather book with a tatty cover and yellow pages lies here.»

Options:

--Read--
--Take--
--Leave--

Tentative Read outcomes:

40% Nothing
20% random Scroll/spell-like effect
15% Bless
15% Curse
10% XP

Taking the book occupies an inventory slot.

Its exact nature is not explained.

---

CONTENT-GENERATION PRINCIPLE

The dungeon should not behave as though every noun exists for the player's benefit.

A corpse may contain nothing.

A locked chest may be empty.

An iron spike may just be an iron spike.

A fresco may merely depict something.

A secret room may be empty.

A suspicious statue may do nothing.

A glimmer beneath the water may be worthless.

This uncertainty is intentional.

The player should make decisions about whether curiosity is worth:

- Time
- Torchlight
- Risk
- Inventory space
- Consumables
- HP

The Labyrinth is a place to explore, not a sequence of guaranteed rewards.

---

v0.01 IMPLEMENTATION PRIORITY

The design is now sufficiently complete to begin implementation.

Do not delay the prototype in order to design systems that are not required for the initial gameplay loop.

Implementation should prioritize:

1. New character generation
2. Vale
3. Inventory/equipment
4. Merchant/Inn/Shrine/Tavern/Graveyard
5. Time and Torch tracking
6. Labyrinth room generation
7. Room contents
8. Combat
9. Loot and treasure extraction
10. XP and leveling
11. Poison/Darkness/Bless/Curse
12. Death and Graveyard persistence
13. Save/load

Where this document marks something tentative, choose the simplest reasonable implementation and keep the value easy to change.

The purpose of v0.01 is to discover what works through play.

Do not expand scope merely because additional systems would be interesting.
