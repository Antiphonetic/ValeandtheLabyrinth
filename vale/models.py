"""Plain serializable game state and character/equipment invariants."""
from dataclasses import dataclass, field
from math import ceil
from . import data as D


@dataclass
class Item:
    name: str
    condition: str = 'Normal'
    magic: str = ''
    identified: bool = True
    spell: str = ''
    found: bool = False
    extracted: bool = False
    burn: int = 0
    venom: bool = False
    silver_amount: int = 0

    @property
    def label(self):
        if self.name == 'Loose Silver':
            return f'Loose Silver ({self.silver_amount} sp)'
        prefix = '' if self.condition == 'Normal' else self.condition + ' '
        magic = ('Blessed ' if self.magic == 'Bless' else 'Cursed ') if self.identified and self.magic else ('Unidentified ' if self.magic else '')
        suffix = f' ({self.spell})' if self.name == 'Scroll' else ''
        return magic + prefix + self.name + suffix

    @property
    def value(self):
        if self.name == 'Loose Silver':
            return self.silver_amount
        value = D.TREASURES.get(self.name, D.PRICES.get(self.name, 0))
        factor = {'Normal': 1, 'Worn': .75, 'Ragged': .5, 'Ruined': .1}[self.condition]
        return max(0, int(value * factor))

    @property
    def slot(self):
        if self.name in D.WEAPONS:
            return 'main'
        if self.name in D.ARMOR:
            return 'body'
        if self.name == 'Shield' or self.name == 'Torch' and self.burn > 0:
            return 'off'
        return None


@dataclass
class Character:
    name: str
    might: int
    cunning: int
    magic: int
    base_hp: int
    hp: int
    inventory: list[Item] = field(default_factory=list)
    equipment: dict[str, Item | None] = field(default_factory=lambda: dict(head=None, body=None, main=None, off=None))
    silver: int = 0
    fortune: int = 0
    xp: float = 0
    level: int = 1
    rewards: int = 0
    deepest: int = 0
    effects: dict[str, int] = field(default_factory=dict)
    poison_tick: int = 0
    bound: bool = False
    groggy: bool = False
    dead: bool = False
    cause: str = ''
    spells: list[str] = field(default_factory=list)

    def all_items(self):
        return self.inventory + [i for i in self.equipment.values() if i]

    def active(self, effect, minute):
        return self.effects.get(effect, 0) > minute

    def max_hp(self, minute):
        return ceil(self.base_hp * ((1 + D.MEAL_HP_BONUS) if self.active('Well Fed', minute) else 1))

    def heal(self, amount, minute):
        self.hp = min(self.max_hp(minute), self.hp + amount)

    def add(self, item):
        if len(self.inventory) >= D.INVENTORY_LIMIT:
            raise ValueError('Your inventory is full (15 unequipped objects).')
        self.inventory.append(item)

    def equip(self, index):
        item = self.inventory[index]
        slot = item.slot
        if slot is None:
            raise ValueError('That item cannot be equipped. Use a Torch to light it.')
        if item.name == 'Zweihander' and self.equipment['off']:
            raise ValueError('A Zweihander requires both hands. Unequip your off hand first.')
        if slot == 'off' and self.equipment['main'] and self.equipment['main'].name == 'Zweihander':
            raise ValueError('Both hands are occupied by your Zweihander.')
        if slot == 'off' and self.equipment['off'] and not self.equipment['main']:
            slot = 'main'
        old = self.equipment[slot]
        self.inventory.pop(index)
        if old:
            self.inventory.append(old)
        self.equipment[slot] = item

    def unequip(self, slot):
        item = self.equipment[slot]
        if not item:
            raise ValueError('That slot is empty.')
        self.add(item)
        self.equipment[slot] = None

    def gain_xp(self, amount, minute):
        self.xp += amount * ((1 + D.MEAL_XP_BONUS) if self.active('Well Fed', minute) else 1)
        while self.xp >= D.XP_THRESHOLD_FACTOR * self.level * (self.level + 1):
            self.level += 1
            self.rewards += 1

    def reward(self, choice):
        if not self.rewards:
            raise ValueError('No level-up reward is waiting.')
        if choice == 'HP':
            self.base_hp += self.might
            self.hp += self.might
        elif choice in ('might', 'cunning', 'magic'):
            setattr(self, choice, getattr(self, choice) + 1)
        else:
            raise ValueError('Choose HP, might, cunning, or magic.')
        self.rewards -= 1


@dataclass
class Monster:
    name: str
    hp: int
    max_hp: int
    web_used: bool = False
    suppressed: bool = False
    flammable: bool = False
    burning: bool = False
    poisoned: bool = False
    rewarded: bool = False
    fled: bool = False
    gear: list[Item] = field(default_factory=list)
    petrified: bool = False

    @property
    def alive(self):
        return self.hp > 0 and not self.fled

    @property
    def display_hp(self):
        return '?/?' if self.name == 'Ooze' else f'{max(0, self.hp)}/{self.max_hp}'


@dataclass
class Exit:
    name: str
    target: int | None = None
    depth_change: int = 0
    secret: bool = False


@dataclass
class Element:
    name: str
    done: bool = False
    detected: bool = False
    difficulty: int = 20
    animal: str = ''


@dataclass
class Room:
    id: int
    depth: int
    template: str
    description: str
    daylight: bool = False
    secret: bool = False
    exits: list[Exit] = field(default_factory=list)
    monsters: list[Monster] = field(default_factory=list)
    loot: list[Item] = field(default_factory=list)
    elements: list[Element] = field(default_factory=list)
    traps: list[Element] = field(default_factory=list)
    hidden: str = ''
    harvest: list[str] = field(default_factory=list)


@dataclass
class State:
    player: Character
    minute: int = 8 * 60
    location: str = 'Vale'
    rooms: dict[int, Room] = field(default_factory=dict)
    current: int | None = None
    previous: int | None = None
    stock: list[Item] = field(default_factory=list)
    stock_week: int = -1
    rumor_day: int = -1
    drinks: int = 0
    drink_day: int = -1
    id: str = ''
    expedition_silver: int = 0
    town_screen: str = 'Vale'

    @property
    def day(self):
        return self.minute // 1440 + 1

    @property
    def clock(self):
        hour = self.minute // 60 % 24
        period = 'Morning' if 6 <= hour < 12 else 'Afternoon' if 12 <= hour < 18 else 'Evening' if 18 <= hour < 22 else 'Night'
        return f'Day {self.day} — {period}'


def state_from_dict(raw):
    p = dict(raw['player'])
    p['inventory'] = [Item(**i) for i in p['inventory']]
    p['equipment'] = {k: Item(**v) if v else None for k, v in p['equipment'].items()}
    rooms = {}
    for key, value in raw['rooms'].items():
        r = dict(value)
        r['exits'] = [Exit(**x) for x in r['exits']]
        r['loot'] = [Item(**x) for x in r['loot']]
        r['elements'] = [Element(**x) for x in r['elements']]
        r['traps'] = [Element(**x) for x in r['traps']]
        r['monsters'] = [Monster(**dict(m, gear=[Item(**i) for i in m['gear']])) for m in r['monsters']]
        rooms[int(key)] = Room(**r)
    return State(**dict(raw, player=Character(**p), rooms=rooms, stock=[Item(**i) for i in raw['stock']]))
