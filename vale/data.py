"""Content and tuning values. Dice are (count, sides, modifier)."""
NAMES = 'Oswald Siegfried Edward Edmund Godfrey Geoffrey Roland Hugh William Robert Conrad Dietrich Otto Alaric Anselm Baldwin Bertram Ulrich Roderick Theobald'.split()
INVENTORY_LIMIT = 15
ACTION_MINUTES = {'move': 5, 'search': 10, 'interact': 5, 'combat': 1, 'rest': 480, 'town': 5}
REST_ENCOUNTER = 35
DARK_EXTRA_MONSTER = 25
DARK_DOUBLE_MONSTER = 15
HIDDEN_CHANCE = 10
DEPTH_BONUS = 5
BAT_HIT = 50
GOBLIN_FLEE = 50
VENOM_MONSTER_POISON = 50
PRICES = {
    'Dagger': 8, 'Spear': 12, 'Mace': 10, 'Arming Sword': 20,
    'Battle-axe': 22, 'Zweihander': 40, 'Shield': 12,
    'Padded Jack': 15, 'Mail Hauberk': 30, 'Brigandine Cuirass': 45,
    'Plate and Mail': 100, 'Rags': 1, 'Healing Potion': 8, 'Torch': 2,
    'Rope': 8, 'Oil': 4, 'Scroll': 10, 'Pick': 5, 'Antidote': 6,
    'Empty Bottle': 2, 'Spider Venom': 6, 'Rat Pelt': 2, 'Bat Wings': 2,
    'Bear Pelt': 8, 'Pale Book': 3, 'Human Baby': 0,
}
WEAPONS = {
    'Dagger': (1, 4, 0), 'Spear': (1, 4, 1), 'Mace': (1, 4, 0),
    'Arming Sword': (1, 6, 0), 'Battle-axe': (1, 6, 1), 'Zweihander': (2, 6, 1),
}
ARMOR = {'Padded Jack': (1, 4, 0), 'Mail Hauberk': (1, 6, 0),
         'Brigandine Cuirass': (1, 6, 1), 'Plate and Mail': (1, 8, 2), 'Rags': (0, 0, 0)}
TIER1_ARMOR = ['Padded Jack', 'Mail Hauberk', 'Brigandine Cuirass']
UTILITY = ['Healing Potion', 'Torch', 'Rope', 'Oil', 'Scroll', 'Pick', 'Antidote', 'Empty Bottle']
TREASURES = {'Brass Candlestick': 1, 'Tin Cup': 1, 'Copper Platter': 3,
             'Brass Sculpture': 5, 'Uncut Gemstone': 6, 'Silver Candelabra': 12,
             'Silver Goblet': 15, 'Golden Idol': 35}
TREASURE_WEIGHTS = [25, 25, 15, 10, 10, 7, 5, 3]
SECRET_TREASURE_WEIGHTS = [10, 10, 15, 15, 15, 15, 12, 8]
CONTENT_KINDS = ['Empty', 'Monster', 'Treasure', 'Feature', 'Trap', 'Special', 'Twice']
NORMAL_CONTENT = [30, 27, 17, 10, 5, 5, 6]
LOOSE_SILVER_CHANCE = 15
LOOSE_SILVER_DICE = (1, 6, 2)
SECRET_CONTENT = [20, 20, 30, 10, 5, 5, 10]
THREATS = {'Weak': ['Giant Rat', 'Cave Bat', 'Goblin', 'Skeleton', 'Zombie'],
           'Medium': ['Giant Spider', 'Ooze', 'Cave Bear'], 'Tough': ['Ogre', 'Troll']}
THREAT_WEIGHTS = [63, 32, 5]
THREAT_XP = {'Weak': 2, 'Medium': 4, 'Tough': 5}
# name: HP (or dice), hit chance, armor dice, damage dice, tagline
MONSTERS = {
    'Giant Rat': (5, 50, (0, 0, 0), (1, 4, -1), 'Wait, these really exist?'),
    'Cave Bat': (3, BAT_HIT, (0, 0, 0), (1, 4, 0), "Don't let it get in your hair"),
    'Goblin': (5, 50, (1, 2, 0), (1, 4, 1), 'Like if a ferret and a lizard crossbred. Gross.'),
    'Skeleton': (1, 50, (1, 4, 0), (1, 6, 0), 'Is that...Geoffrey?'),
    'Zombie': (7, 50, (0, 0, 0), (1, 4, 0), "Oh, no, that's Geoffrey"),
    'Giant Spider': (8, 50, (0, 0, 0), (1, 4, 0), 'Venom drips from its fangs'),
    'Ooze': ((2, 6, 0), 40, (0, 0, 0), (1, 4, 0), ''),
    'Cave Bear': (10, 50, (0, 0, 0), (1, 4, 1), 'Its claws scrape the stone.'),
    'Ogre': (18, 60, (0, 0, 0), (1, 6, 1), 'His breath reeks of rotting flesh'),
    'Troll': (12, 50, (0, 0, 0), (1, 6, 0), 'Scaly, green, huge, and leaking pus from its canker sores.'),
}
EXITS = ['Northern Hall', 'Southern Door', 'Eastern Passage', 'Curtain of Shadows',
         'Spiral Stair', 'Narrow Crack', 'Flooded Tunnel', 'Iron Gate', 'Hole in Floor']
FEATURES = {
    'Corpse': 'A corpse lies sprawled on the floor.',
    'Locked Chest': 'A battered ironbound chest rests against the wall.',
    'Deep Shaft': 'A black shaft descends beyond the reach of your torchlight.',
    'Locked Door': 'A locked iron door blocks a passage.',
    'Lifelike Statue': 'A disturbingly realistic statue stands here.',
    'Iron Spike': 'An ordinary-looking iron spike protrudes from the masonry.',
    'Fresco': 'A faded fresco covers much of one wall.',
}
FEATURE_OUTCOMES = {
    'Corpse': [('Nothing', 50), ('Item', 15), ('Silver', 10), ('Zombie', 15), ('Trap', 10)],
    'Locked Chest': [('Treasure', 70), ('Item', 20), ('Nothing', 10)],
    'Lifelike Statue': [('Nothing', 50), ('Treasure', 20), ('Bless', 15), ('Curse', 10), ('Monster', 5)],
    'Iron Spike': [('Nothing', 70), ('Treasure', 15), ('Trap', 10), ('Secret Door', 5)],
    'Fresco': [('Lore', 60), ('Reveal', 15), ('Treasure', 10), ('Bless', 10), ('Curse', 5)],
    'Opalescent Fountain': [('Nothing', 40), ('Heal', 20), ('Bless', 15), ('Curse', 15), ('Strange', 10)],
    'Pale Book': [('Nothing', 40), ('Scroll', 20), ('Bless', 15), ('Curse', 15), ('XP', 10)],
}
SPECIALS = {
    'Human Baby': 'A human baby lies wailing upon a heap of towels.',
    'Tavern Sign': 'The sign to the tavern hangs on the wall here.',
    'Opalescent Fountain': 'A colorful fountain stands here, spraying opalescent light instead of water.',
    'Wounded Animal': 'A wounded creature shivers on the stone.',
    'Pale Book': 'A pale leather book with a tatty cover and yellow pages lies here.',
}
TRAPS = {'Spike Trap': (10, (1, 6, 0)), 'Pitfall': (15, (1, 6, 1)), 'Poisoned Arrow': (20, (1, 4, 0))}
SPELLS = ['Ember', 'Mending', 'Acid']
SPELL_DESCRIPTIONS = {'Ember': 'Fire: 1d4 + Magic damage.', 'Mending': 'Recover 1d4 + Magic HP.', 'Acid': 'Acid: 1d4 + Magic damage.'}
TOWN = {
    'Vale': 'This ramshackle town of tents and slapdash buildings has sprung up overnight, ready to service adventurers who attempt the Labyrinth.',
    'Merchant': "The greasy man's eyes dart back and forth as he shows you his wares. He would cheat you if he wasn't afraid you'd kill him.",
    'Inn': 'The biggest building in Vale. It beats sleeping in the Labyrinth—barely.\nThe innkeep looks at you with narrowed eyes.\n"Want somefin\'?"',
    'Shrine': 'A fancier tent than the rest—the cheap canvas is dyed—badly—red. A priest of Pyrios stands inside.',
    'Tavern': 'Rough lumber walls, canvas roof and a battered table separating the patrons from the kegs. Cups are wood too, careful not to get a splinter.',
    'Graveyard': 'Rough wooden markers crowd the hillside outside Vale. Some bear names. Others do not.',
}
FACTS = [
    "Priest can tell you what those funny-looking things do. Five silver. Or you can put 'em on and find out yourself.",
    "Don't sleep down there unless you've got to. Things find you, and you don't wake quick.",
    "Merchant's a cheat. Some folk get better prices out of him than others.",
    "Torches last an hour. Big swords need both hands. Can't hold a torch with one of those.",
    "Bring the treasure home and you've earned your fortune. Selling it just puts silver in your purse.",
    "A shield can save your life once, if you're willing to leave it in pieces.",
    "Trolls turn to stone in daylight. Torchlight won't do it. Fire stops them mending, though.",
    "Rope for shafts, picks for locks, empty bottles for spider venom. Pack with care.",
    "Poison lingers after a rest. The priest can cure it, or you can try an antidote.",
    "A spear helps you hit. A mace helps against armor. A sword can cut through a crowd.",
    "Not every corpse has a purse. Not every chest has treasure. Looking still burns light.",
]
RUMORS = [
    "My cousin says there's a woman six levels down been there a hundred years. Beautiful as midsummer, she is. Gives you a magic sword if you kiss her.",
    "Northern passage led me straight to gold yesterday. Reckon it'll still be there?",
    "Saw a baby down there. Didn't sound like any baby I've heard.",
    "All the statues move when you turn your back. That's why I walk backwards.",
    "Geoffrey went in last week. Think I saw him again. Didn't look well.",
]

# Prototype decisions and shared balance values; see ASSUMPTIONS.md.
START_ATTRIBUTE_RANGE = (2, 5)
HP_PER_START_MIGHT = 5
XP_THRESHOLD_FACTOR = 50
ROOM_XP = 2
TREASURE_XP_PER_SILVER = 1
BUFF_MINUTES = 1440
TIPSY_MINUTES = 120
TIPSY_HIT_PENALTY = 10
DRINK_CHANCE_PER_DRINK = 15
DRINK_MIGHT_RESISTANCE = 5
DARK_HIT_PENALTY = 20
DARK_PERCEPTION_PENALTY = 20
GROGGY_PENALTY = 20
POISON_HIT_PENALTY = 10
POISON_DAMAGE_PENALTY = .1
BLESS_HIT_BONUS = 10
BLESS_DAMAGE_BONUS = .1
HEAL_FRACTION = .25
MEAL_HP_BONUS = .03
MEAL_XP_BONUS = .03
LOCK_BREAK_MARGIN = 10
LOCK_DIFFICULTIES = [10, 20, 30]
REST_INTERRUPT_MINUTES = (10, 120)
SPELL_DAMAGE = (1, 4, 0)
TORCH_DAMAGE = (1, 2, 0)
UNARMED_DAMAGE = (1, 2, 0)
VENOM_DAMAGE = (1, 2, 0)
BURN_DAMAGE = (1, 4, 0)
MAGICAL_EQUIPMENT_CHANCE = 10
CARRIED_MAGICAL_POOL_CHANCE = 20
CARRIED_KINDS = ['Nothing', 'Silver', 'Item', 'Treasure']
CARRIED_WEIGHTS = [50, 25, 20, 5]
IMPROVED_CARRIED_WEIGHTS = [30, 25, 20, 25]
CARRIED_SILVER = (1, 6, 0)
BOOK_XP = 10
WOUNDED_HOSTILE_CHANCE = 30
SHAFT_NAVIGATION_CHANCE = 35
STOCK_TORCHES = 8
STOCK_EQUIPMENT = 6
BUY_MULTIPLIER = 1.6
BUY_CUNNING_DISCOUNT = .06
BUY_MIN_MULTIPLIER = 1.05
SELL_MULTIPLIER = .4
SELL_CUNNING_BONUS = .04
SELL_MAX_MULTIPLIER = .95
SERVICE_COSTS = {'Room': 10, 'Meal': 3, 'Drink': 2, 'Healing': 2,
                 'Blessing': 5, 'Cure Afflictions': 5, 'Identification': 5}

TROLL_PURSUIT_CHANCE = 50


CONTEXT_ACTIONS = {
    'Sarcophagus': 'Open Sarcophagus', 'Grave Niches': 'Search Grave Niches',
    'Casket': 'Open Casket', 'Crypt Statue': 'Examine Statue',
    'Rotten Chests': 'Open Rotten Chests', 'Ruined Equipment': 'Examine Ruined Equipment',
    'Stone Plants': 'Examine Stone Plants', 'Stone Tree': 'Examine Stone Tree',
    'Petrified Fountain': 'Examine Petrified Fountain', 'Floor Shaft': 'Inspect Shaft',
    'Underwater Glimmer': 'Investigate Underwater Glimmer',
    'Underwater Doorway': 'Inspect Underwater Doorway',
    'Fluttering Shape': 'Investigate Fluttering Shape',
    'Altar': 'Examine Altar', 'Glyphs': 'Examine Glyphs', 'Statuette': 'Examine Statuette',
    'Vault Cracks': 'Examine Cracks', 'Balustrade': 'Examine Balustrade',
    'Pillars': 'Examine Pillars', 'Baths': 'Examine Baths',
}
CONTEXT_OUTCOMES = {
    'Sarcophagus': [('Nothing', 45), ('Treasure', 20), ('Undead', 20), ('Undead Treasure', 10), ('Strange', 5)],
    'Grave Niches': [('Nothing', 60), ('Silver', 15), ('Undead', 20), ('Item', 5)],
    'Casket': [('Nothing', 60), ('Treasure', 20), ('Undead', 15), ('Strange', 5)],
    'Rotten Chests': [('Nothing', 65), ('Item', 15), ('Silver', 15), ('Trap', 5)],
    'Underwater Glimmer': [('Nothing', 60), ('Treasure', 20), ('Silver', 10), ('Trap', 10)],
    'Underwater Doorway': [('Nothing', 75), ('Secret Door', 15), ('Trap', 10)],
    'Fluttering Shape': [('Nothing', 70), ('Monster', 20), ('Strange', 10)],
}
