"""Layered procedural generation, independent of the terminal interface."""
from . import data as D
from .models import Item, Monster, Room, Exit, Element


def dice(rng, spec):
    count, sides, modifier = spec
    rolls = [rng.randint(1, sides) for _ in range(count)]
    return max(0, sum(rolls) + modifier), bool(rolls) and all(r == sides for r in rolls)


def chance(rng, percent):
    return rng.random() * 100 < max(0, min(100, percent))


def weighted(rng, values, weights):
    roll = rng.randint(1, sum(weights))
    for value, weight in zip(values, weights):
        roll -= weight
        if roll <= 0:
            return value
    raise AssertionError('Invalid probability table')


def tier_item(rng, found=True, equipment=False):
    pool = list(D.WEAPONS) + D.TIER1_ARMOR + ['Shield']
    if not equipment:
        pool += D.UTILITY
    name = rng.choice(pool)
    condition = rng.choice(['Normal', 'Normal', 'Worn', 'Ragged']) if name in D.WEAPONS or name in D.ARMOR else 'Normal'
    magic = rng.choice(['Bless', 'Curse']) if equipment and chance(rng, D.MAGICAL_EQUIPMENT_CHANCE) else ''
    return Item(name, condition, magic, not bool(magic), rng.choice(D.SPELLS) if name == 'Scroll' else '', found)


def treasure(rng, secret=False):
    return Item(weighted(rng, list(D.TREASURES), D.SECRET_TREASURE_WEIGHTS if secret else D.TREASURE_WEIGHTS), found=True)


def spawn(rng, name=None):
    if name is None:
        threat = weighted(rng, list(D.THREATS), D.THREAT_WEIGHTS)
        name = rng.choice(D.THREATS[threat])
    hp = D.MONSTERS[name][0]
    if isinstance(hp, tuple):
        hp = dice(rng, hp)[0]
    monster = Monster(name, hp, hp)
    if name == 'Goblin':
        monster.gear = [Item('Dagger', rng.choice(['Normal', 'Worn', 'Ragged']), found=True)]
    if name == 'Skeleton':
        monster.gear = [Item(rng.choice(list(D.WEAPONS)), rng.choice(['Normal', 'Worn', 'Ragged']), found=True),
                        Item(rng.choice(D.TIER1_ARMOR), rng.choice(['Normal', 'Worn', 'Ragged']), found=True)]
    return monster


def contents(rng, secret=False):
    weights = D.SECRET_CONTENT if secret else D.NORMAL_CONTENT
    result = weighted(rng, D.CONTENT_KINDS, weights)
    if result != 'Twice':
        return [result]
    results = []
    for _ in range(2):
        again = 'Twice'
        while again == 'Twice':
            again = weighted(rng, D.CONTENT_KINDS, weights)
        results.append(again)
    return results


def template(rng):
    """Keep light-sensitive prose as placeholders, resolved at display time."""
    index = rng.randrange(13)
    daylight = False
    shaft = False
    if index == 0:
        name = 'Sunken Crypt'
        text = 'Water, black and still, floods this room to your ankles. ' + rng.choice([
            'A sarcophagus on a dais dominates the far wall.', 'Bones fill grave niches in the walls.',
            'A statue worn featureless stands eight feet tall in the center of the room, towering over a small casket.'])
    elif index == 1:
        name, text = 'Shadowed Hall', 'The darkness presses in{torch_pressure}. You feel a faint unease.'
    elif index == 2:
        name = 'Decrepit Vault'
        daylight = chance(rng, 50)
        text = 'The stone here is spalling almost to gravel. ' + ('Sunlight filters through a crack in the ceiling.' if daylight else 'Cracks run down the walls.')
    elif index == 3:
        name = 'Petrified Courtyard'
        text = 'Rows of stone planters are filled with stone ' + rng.choice(['ferns', 'flowers in full bloom']) + '. In the center, ' + rng.choice(['a stone ash tree', 'a fountain where water seems to have turned to stone mid-flow']) + ' dominates the space.'
    elif index == 4:
        name, text = 'Winding Tunnel', 'This tunnel was clearly dug by something. Rough walls of mud and stone bend and bend. It is not tall enough to stand straight up inside.'
    elif index == 5:
        name = 'Damp Chamber'
        shaft = chance(rng, 50)
        text = 'Water trickles down the walls and ' + ('flows down a shaft in the floor' if shaft else 'puddles on the floor') + '. The air stinks of stale mildew.'
    elif index == 6:
        name = 'Natural Cavern'
        size = rng.choice(['huge', 'sizeable', 'small'])
        verb = {'huge': 'cannot', 'sizeable': 'barely', 'small': 'easily'}[size]
        text = f'The masonry gives way to a {size} natural cavern.' + '{torch_cavern:' + verb + '}'
    elif index == 7:
        name = 'Terraced Gallery'
        text = 'A balustrade winds around the edge of this room ' + rng.choice(['above', 'below']) + ' your vantage point. The ceiling arches away to shadow.'
    elif index == 8:
        name, text = 'Pillared Hall', 'A long, wide hall with dozens of broad pillars stretches on for what seems an endless space.'
    elif index == 9:
        name = 'Flooded Chamber'
        text = 'This room is flooded. In the brackish depths, you can just make out ' + rng.choice(['something glimmering', 'a shadowy doorway', 'some dim shape fluttering']) + '.'
    elif index == 10:
        name, text = 'Ancient Armory', 'The walls are lined in rusted iron blades, the floors strewn with crumbling leather and mail. Rotten chests along the far wall catch your eye.'
    elif index == 11:
        name = 'Mosaic Baths'
        text = 'The ruins of an ancient public bath stretch before you, the water now ' + rng.choice(['dried up', 'clouded with dust and grime']) + '.'
    else:
        name = 'Desecrated Temple'
        text = 'Still-sticky blood and wet bone litter the floor and altar of this room, arrayed in profane glyphs. The statuette of ' + rng.choice(['Pyrios', 'Llamela', 'Lyrissia']) + ' has its face turned away.'
    return name, text, daylight, shaft


def describe(room, torch):
    text = room.description.replace('{torch_pressure}', ' against your torchlight' if torch else '')
    for word in ('cannot', 'barely', 'easily'):
        text = text.replace('{torch_cavern:' + word + '}', (' Your torchlight cannot illuminate the whole space.' if word == 'cannot' else f' Your torchlight {word} illuminates the whole space.') if torch else '')
    return text


def generate(rng, room_id, depth, secret=False, darkness=False, parent=None):
    name, text, daylight, shaft = template(rng)
    room = Room(room_id, depth, name, text, daylight, secret)
    count = rng.randint(1, 4)
    # An incoming connection is one of the room's 1d4 ordinary exits.
    if parent is not None:
        room.exits.append(Exit('Back through the entrance', parent))
    for _ in range(count - len(room.exits)):
        exit_name = rng.choice(D.EXITS)
        room.exits.append(Exit(exit_name, depth_change=1 if exit_name in ('Spiral Stair', 'Hole in Floor') else 0))
    for content in contents(rng, secret):
        if content == 'Monster':
            room.monsters.append(spawn(rng))
        elif content == 'Treasure':
            room.loot.append(treasure(rng, secret))
        elif content == 'Feature':
            room.elements.append(Element(rng.choice(list(D.FEATURES)), difficulty=rng.choice(D.LOCK_DIFFICULTIES)))
        elif content == 'Trap':
            room.traps.append(Element(rng.choice(list(D.TRAPS))))
        elif content == 'Special':
            special = rng.choice(list(D.SPECIALS))
            animal = rng.choice(['Giant Rat', 'Cave Bat', 'Cave Bear']) if special == 'Wounded Animal' else ''
            room.elements.append(Element(special, animal=animal))
    if shaft and chance(rng, D.SHAFT_NAVIGATION_CHANCE):
        room.elements.append(Element('Deep Shaft'))
    if chance(rng, D.HIDDEN_CHANCE):
        room.hidden = rng.choice(['Secret Door', 'Cache'])
    if darkness and not daylight:
        if chance(rng, D.DARK_EXTRA_MONSTER):
            room.monsters.append(spawn(rng))
        if chance(rng, D.DARK_DOUBLE_MONSTER):
            room.monsters.extend([spawn(rng), spawn(rng)])
    return room
