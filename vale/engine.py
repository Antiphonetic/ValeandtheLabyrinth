"""Game rules. Menus call these actions; rules never read terminal input."""
import random
import uuid
from math import ceil, floor
from . import data as D
from .models import Character, Item, State, Exit, Element
from .dungeon import chance, dice, weighted, tier_item, treasure, spawn, generate, silver_cache


class Game:
    def __init__(self, seed=None, storage=None, state=None, random_state=None):
        self.rng = random.Random(seed)
        self.storage = storage
        self.messages = []
        if state is None:
            might, cunning, magic = (self.rng.randint(*D.START_ATTRIBUTE_RANGE) for _ in range(3))
            p = Character(self.rng.choice(D.NAMES), might, cunning, magic, D.HP_PER_START_MIGHT * might, D.HP_PER_START_MIGHT * might)
            p.equipment['main'] = Item(self.rng.choice(list(D.WEAPONS)))
            p.inventory = [Item('Torch') for _ in range(3)] + [tier_item(self.rng, found=False)]
            self.state = State(p, id=uuid.uuid4().hex)
            self.refresh_stock()
        else:
            self.state = state
            self.rng.setstate(random_state)

    @property
    def p(self):
        return self.state.player

    @property
    def room(self):
        return self.state.rooms.get(self.state.current)

    @property
    def enemies(self):
        return [m for m in self.room.monsters if m.alive] if self.room else []

    @property
    def combat(self):
        return bool(self.enemies)

    @property
    def torch(self):
        return next((i for i in self.p.equipment.values() if i and i.name == 'Torch' and i.burn > 0), None)

    @property
    def darkness(self):
        return self.state.location == 'Labyrinth' and not self.torch and not (self.room and self.room.daylight)

    @property
    def light(self):
        if self.state.location == 'Vale' or self.room and self.room.daylight:
            return 'Daylight' if self.state.location == 'Labyrinth' else 'Vale lanterns'
        torch = self.torch
        if not torch:
            return 'Darkness'
        return 'Bright' if torch.burn > 45 else 'Steady' if torch.burn > 25 else 'Dim' if torch.burn > 10 else 'Guttering'

    def say(self, text):
        self.messages.append(text)

    def save(self):
        if self.storage:
            self.storage.save(self.state, self.rng)

    def die(self, cause):
        if self.p.dead:
            return
        self.p.hp = 0
        self.p.dead = True
        self.p.cause = cause
        self.say(f'{self.p.name} dies. {cause}. Your marker joins the Graveyard.')
        if self.storage:
            self.storage.record_death(self.state)

    def hurt(self, amount, cause):
        self.p.hp -= amount
        if self.p.hp <= 0:
            self.die(cause)

    def advance(self, minutes):
        """Minute ticks keep poison and torch depletion correct across long rests."""
        for _ in range(minutes):
            if self.p.dead:
                break
            self.state.minute += 1
            now = self.state.minute
            for item in list(self.p.all_items()):
                if item.name == 'Torch' and item.burn > 0:
                    item.burn -= 1
                    if item.burn == 0:
                        carried = next((i for i, carried_item in enumerate(self.p.inventory) if carried_item is item), None)
                        if carried is not None:
                            self.p.inventory.pop(carried)
                        else:
                            for slot, equipped in self.p.equipment.items():
                                if equipped is item:
                                    self.p.equipment[slot] = None
                        self.say('Your torch gutters out.')
            if self.p.poison_tick and now >= self.p.poison_tick and now <= self.p.effects.get('Poison', 0):
                self.hurt(1, 'Poison')
                self.p.poison_tick += 60
                self.say('Poison takes 1 HP.')
            self.p.effects = {k: end for k, end in self.p.effects.items() if end > now}
            if 'Poison' not in self.p.effects:
                self.p.poison_tick = 0
            self.p.hp = min(self.p.hp, self.p.max_hp(now))
        self.refresh_stock()

    def poison(self):
        duration = max(0, 12 - self.p.might) * 60
        if duration:
            self.p.effects['Poison'] = self.state.minute + duration
            if not self.p.poison_tick:
                self.p.poison_tick = self.state.minute + 60
            self.say('Venom burns through your blood. You are Poisoned.')

    def effect(self, name):
        self.p.effects[name] = self.state.minute + (D.TIPSY_MINUTES if name == 'Tipsy' else D.BUFF_MINUTES)
        self.say(f'You receive {name}.')

    def modifiers(self):
        active = lambda name: self.p.active(name, self.state.minute)
        magical = sum(1 if i.magic == 'Bless' else -1 if i.magic == 'Curse' else 0 for i in self.p.equipment.values() if i)
        balance = int(active('Bless')) - int(active('Curse')) + magical
        poison = int(active('Poison'))
        hit = D.BLESS_HIT_BONUS * balance - D.POISON_HIT_PENALTY * poison - (D.DARK_HIT_PENALTY if self.darkness else 0) - (D.GROGGY_PENALTY if self.p.groggy else 0) - (D.TIPSY_HIT_PENALTY if active('Tipsy') else 0)
        return hit, max(0, 1 + D.BLESS_DAMAGE_BONUS * balance - D.POISON_DAMAGE_PENALTY * poison)

    def hit_chance(self, monster, weapon_bonus=True):
        weapon = self.p.equipment['main']
        return max(0, min(100, 10 * self.p.cunning + 10 + self.modifiers()[0]
                              + (10 if weapon_bonus and weapon and weapon.name == 'Spear' else 0)
                              - (15 if monster.name == 'Cave Bat' else 0)))

    def armor(self):
        item = self.p.equipment['body']
        if not item or item.condition == 'Ruined':
            return 0
        return max(0, dice(self.rng, D.ARMOR[item.name])[0] - (1 if item.condition == 'Ragged' else 0))

    def require_safe(self):
        if self.p.dead:
            raise ValueError('This adventurer is dead.')
        if self.combat:
            raise ValueError('The monsters will not let you do that. Fight or flee.')

    def require_town(self):
        self.require_safe()
        if self.state.location != 'Vale':
            raise ValueError('You must return to Vale first.')

    def enter(self):
        self.require_town()
        self.state.rooms = {}
        self.state.current = self.state.previous = None
        self.state.location = 'Labyrinth'
        self.state.expedition_silver = 0
        self.say('THE LABYRINTH\nThe light of the outside world fades behind you as the gloom and damp press in.\nYou see...')
        self.advance(D.ACTION_MINUTES['move'])
        if not self.p.dead:
            room = generate(self.rng, 0, 1, darkness=not bool(self.torch))
            self.state.rooms[0] = room
            self.state.current = 0
            self.arrive(new=True)

    def arrive(self, new=False):
        room = self.room
        if new:
            self.p.gain_xp(D.ROOM_XP, self.state.minute)
            if room.depth > self.p.deepest:
                self.p.deepest = room.depth
                self.p.gain_xp(D.DEPTH_BONUS * room.depth, self.state.minute)
                self.say(f'You reach depth {room.depth}.')
        if room.daylight:
            for monster in self.enemies:
                if monster.name == 'Troll':
                    monster.hp = 0
                    monster.petrified = True
                    self.say('The Troll turns to stone in the sunlight.')
        self.resolve_deaths()
        for trap in room.traps:
            if trap.done or trap.detected:
                continue
            difficulty = D.TRAPS[trap.name][0]
            if chance(self.rng, 12 * self.p.cunning - difficulty - (D.DARK_PERCEPTION_PENALTY if self.darkness else 0)):
                trap.detected = True
                self.say(f'You spot a {trap.name}. You can avoid or disarm it.')
            else:
                self.trigger_trap(trap)
            if self.p.dead:
                break
        if not self.combat:
            self.p.groggy = False

    def move(self, index):
        self.require_safe()
        if not self.room:
            raise ValueError('You are not in the Labyrinth.')
        exit = self.room.exits[index]
        old = self.room
        self.advance(D.ACTION_MINUTES['move'])
        if self.p.dead:
            return
        new = exit.target is None
        if new:
            room_id = max(self.state.rooms) + 1
            target = generate(self.rng, room_id, max(1, old.depth + exit.depth_change), exit.secret, self.darkness, old.id)
            self.state.rooms[room_id] = target
            exit.target = room_id
        self.state.previous = old.id
        self.state.current = exit.target
        self.arrive(new)

    def return_to_vale(self):
        self.require_safe()
        if self.state.location != 'Labyrinth':
            raise ValueError('You are already in Vale.')
        self.advance(D.ACTION_MINUTES['move'])
        if self.p.dead:
            return
        value = self.state.expedition_silver
        self.state.expedition_silver = 0
        for item in self.p.all_items():
            if item.name in D.TREASURES and item.found and not item.extracted:
                value += D.TREASURES[item.name]
                item.extracted = True
        self.p.fortune += value
        self.p.gain_xp(value * D.TREASURE_XP_PER_SILVER, self.state.minute)
        self.say(f'You return to Vale. Extracted treasure: {value} sp. Fortune and XP earned; sell items for spendable silver.')
        self.state.location = 'Vale'
        self.state.rooms = {}
        self.state.current = self.state.previous = None
        self.p.groggy = False

    def take(self, index):
        self.require_safe()
        if self.darkness:
            raise ValueError('You cannot make out the loot in the darkness. Find light first.')
        item = self.room.loot[index]
        if item.name == 'Loose Silver':
            self.p.silver += item.silver_amount
            if item.found and not item.extracted:
                self.state.expedition_silver += item.silver_amount
        else:
            self.p.add(item)
        self.room.loot.pop(index)
        self.say(f'You take {item.label}.')
        self.advance(D.ACTION_MINUTES['interact'])

    def drop(self, index):
        self.require_safe()
        item = self.p.inventory.pop(index)
        if self.room:
            self.room.loot.append(item)
        self.say(f'You leave {item.label} behind.')

    def equip(self, index):
        self.require_safe()
        self.p.equip(index)
        self.advance(1)

    def unequip(self, slot):
        self.require_safe()
        self.p.unequip(slot)
        self.advance(1)

    def search(self):
        self.require_safe()
        if not self.room:
            raise ValueError('Search inside the Labyrinth.')
        self.advance(D.ACTION_MINUTES['search'])
        if self.p.dead:
            return
        if self.room.hidden and chance(self.rng, 12 * self.p.cunning - (D.DARK_PERCEPTION_PENALTY if self.darkness else 0)):
            self.reveal()
        else:
            self.say('You find nothing useful.')

    def reveal(self):
        if self.room.hidden == 'Secret Door':
            self.room.exits.append(Exit('Secret Door', secret=True))
            self.say('A hidden door opens in the wall.')
        elif self.room.hidden == 'Cache':
            self.room.loot.append(treasure(self.rng, self.room.secret))
            self.say('You uncover a hidden cache.')
        else:
            self.say('The markings offer a clue, but you find no hidden passage.')
        self.room.hidden = ''

    def trigger_trap(self, trap):
        trap.done = True
        damage = max(0, dice(self.rng, D.TRAPS[trap.name][1])[0] - self.armor())
        self.say(f'{trap.name}! You take {damage} damage.')
        self.hurt(damage, trap.name)
        if trap.name == 'Poisoned Arrow' and damage and not self.p.dead and chance(self.rng, 100 / self.p.might):
            self.poison()

    def disarm(self, index):
        self.require_safe()
        trap = self.room.traps[index]
        if not trap.detected or trap.done:
            raise ValueError('No detected trap remains there.')
        self.advance(D.ACTION_MINUTES['interact'])
        if self.p.dead:
            return
        difficulty = D.TRAPS[trap.name][0]
        rope = trap.name == 'Pitfall' and any(i.name == 'Rope' for i in self.p.all_items())
        if rope or chance(self.rng, 12 * self.p.cunning - difficulty - (D.DARK_PERCEPTION_PENALTY if self.darkness else 0)):
            trap.done = True
            self.say('You make the trap safe.')
        else:
            self.trigger_trap(trap)

    def pick_lock(self, element):
        pick = next((i for i in self.p.inventory if i.name == 'Pick'), None)
        if not pick:
            raise ValueError('You need a Pick.')
        percent = max(0, min(100, 12 * self.p.cunning - element.difficulty))
        roll = self.rng.random() * 100
        if roll < percent:
            self.say('The lock opens.')
            return True
        if roll >= percent + D.LOCK_BREAK_MARGIN:
            self.p.inventory.pop(next(i for i, item in enumerate(self.p.inventory) if item is pick))
            self.say('The Pick breaks in the lock.')
        else:
            self.say('The lock resists.')
        return False

    def interact(self, index, option='interact'):
        self.require_safe()
        element = self.room.elements[index]
        if element.done:
            raise ValueError('You have already investigated this.')
        name = element.name
        if name == 'Deep Shaft' and not any(i.name == 'Rope' for i in self.p.all_items()):
            raise ValueError('You need Rope to descend safely.')
        if name in ('Locked Chest', 'Locked Door') and not any(i.name == 'Pick' for i in self.p.inventory):
            raise ValueError('You need a Pick.')
        if name in ('Human Baby', 'Pale Book') and option == 'take' and len(self.p.inventory) >= D.INVENTORY_LIMIT:
            raise ValueError('Your inventory is full.')
        self.advance(D.ACTION_MINUTES['interact'])
        if self.p.dead:
            return
        if name in ('Locked Chest', 'Locked Door') and not self.pick_lock(element):
            return
        element.done = True
        if name in D.CONTEXT_ACTIONS:
            if name == 'Floor Shaft':
                if element.animal == 'navigable':
                    self.room.elements.append(Element('Deep Shaft'))
                    self.say('The shaft reaches a lower passage. Rope would allow a safe descent.')
                else:
                    self.say('The shaft narrows into a drain. There is no useful way down.')
            elif name in D.CONTEXT_OUTCOMES:
                table = D.CONTEXT_OUTCOMES[name]
                self.outcome(weighted(self.rng, [t[0] for t in table], [t[1] for t in table]))
            else:
                self.say('You examine it closely. Nothing useful is found; the worn stone keeps its secrets.')
        elif name == 'Deep Shaft':
            self.room.exits.append(Exit('Rope down the shaft', depth_change=1))
            self.say('You secure your rope. A descent is now available.')
        elif name == 'Locked Door':
            self.room.exits.append(Exit('Unlocked Door'))
        elif name == 'Human Baby':
            self.p.add(Item('Human Baby', found=True))
            self.say('It falls silent in your arms. You cannot tell what it is watching.')
        elif name == 'Tavern Sign':
            self.say('It is unmistakably the same sign. How did it get here?')
        elif name == 'Pale Book' and option == 'take':
            self.p.add(Item('Pale Book', found=True))
            self.say('You take the pale book.')
        elif name == 'Wounded Animal':
            animal = element.animal
            if option == 'harvest':
                part = {'Giant Rat': 'Rat Pelt', 'Cave Bat': 'Bat Wings', 'Cave Bear': 'Bear Pelt'}[animal]
                self.room.loot.append(Item(part, found=True))
                self.say('You put the creature out of its misery.')
            elif chance(self.rng, D.WOUNDED_HOSTILE_CHANCE):
                monster = spawn(self.rng, animal)
                monster.hp = max(1, monster.hp // 2)
                self.room.monsters.append(monster)
                self.say('It lashes out at you!')
            else:
                self.say('It limps away into the shadows.')
        else:
            table = D.FEATURE_OUTCOMES[name]
            outcome = weighted(self.rng, [t[0] for t in table], [t[1] for t in table])
            self.outcome(outcome)
        if not self.p.dead:
            self.arrive()

    def outcome(self, result):
        if result == 'Silver':
            self.room.loot.append(silver_cache(self.rng))
            self.say('A few loose coins lie within reach.')
        elif result in ('Undead', 'Undead Treasure'):
            self.room.monsters.append(spawn(self.rng, self.rng.choice(['Skeleton', 'Zombie'])))
            self.say('Bones shift in the dark. An undead creature rises!')
            if result == 'Undead Treasure':
                self.outcome('Treasure')
        elif result == 'Treasure':
            self.room.loot.append(treasure(self.rng, self.room.secret))
            self.say('Something of value lies within reach.')
        elif result == 'Item':
            self.room.loot.append(tier_item(self.rng, equipment=chance(self.rng, D.CARRIED_MAGICAL_POOL_CHANCE)))
            self.say('You uncover an object.')
        elif result in ('Zombie', 'Monster'):
            self.room.monsters.append(spawn(self.rng, 'Zombie' if result == 'Zombie' else None))
            self.say('Something stirs!')
        elif result == 'Trap':
            self.trigger_trap(Element(self.rng.choice(list(D.TRAPS))))
        elif result in ('Bless', 'Curse'):
            self.effect(result)
        elif result == 'Heal':
            self.p.heal(ceil(self.p.max_hp(self.state.minute) * D.HEAL_FRACTION), self.state.minute)
            self.say('Warmth soothes your wounds.')
        elif result == 'XP':
            self.p.gain_xp(D.BOOK_XP, self.state.minute)
            self.say('An impossible insight settles in your mind.')
        elif result == 'Scroll':
            self.cast_scroll(self.rng.choice(D.SPELLS), self.enemies[0] if self.enemies else None)
        elif result == 'Secret Door':
            self.room.exits.append(Exit('Secret Door', secret=True))
            self.say('A hidden door opens.')
        elif result == 'Reveal':
            self.reveal()
        elif result == 'Lore':
            self.say('A procession descends beneath a mountain. In the last panel, every face is turned away.')
        else:
            self.say('Nothing happens.' if result == 'Nothing' else 'For a moment your shadow points in the wrong direction.')

    def harvest(self, index):
        self.require_safe()
        name = self.room.harvest[index]
        if name == 'Giant Spider':
            bottle = next((i for i in self.p.inventory if i.name == 'Empty Bottle'), None)
            if not bottle:
                raise ValueError('An Empty Bottle is required to harvest venom.')
            bottle.name = 'Spider Venom'
            bottle.found = True
            self.say('You bottle the Spider Venom.')
        else:
            part = {'Giant Rat': 'Rat Pelt', 'Cave Bat': 'Bat Wings', 'Cave Bear': 'Bear Pelt'}[name]
            self.p.add(Item(part, found=True))
            self.say(f'You harvest {part}.')
        self.room.harvest.pop(index)
        self.advance(D.ACTION_MINUTES['interact'])

    def carried_drop(self, improved=False):
        kind = weighted(self.rng, D.CARRIED_KINDS, D.IMPROVED_CARRIED_WEIGHTS if improved else D.CARRIED_WEIGHTS)
        if kind == 'Silver':
            silver = dice(self.rng, D.CARRIED_SILVER)[0]
            self.p.silver += silver
            self.say(f'You find {silver} sp among the spoils.')
        elif kind == 'Item':
            self.room.loot.append(tier_item(self.rng, equipment=chance(self.rng, D.CARRIED_MAGICAL_POOL_CHANCE)))
        elif kind == 'Treasure':
            self.room.loot.append(treasure(self.rng, self.room.secret))

    def resolve_deaths(self):
        if not self.room:
            return
        for monster in self.room.monsters:
            if monster.hp > 0 or monster.rewarded or monster.fled:
                continue
            monster.rewarded = True
            threat = next(k for k, names in D.THREATS.items() if monster.name in names)
            self.p.gain_xp(D.THREAT_XP[threat], self.state.minute)
            if monster.petrified:
                continue
            self.say(f'{monster.name} dies. {D.THREAT_XP[threat] * (1 + D.MEAL_XP_BONUS if self.p.active("Well Fed", self.state.minute) else 1):g} XP awarded.')
            self.room.loot.extend(monster.gear)
            if monster.name in ('Giant Rat', 'Cave Bat', 'Giant Spider', 'Cave Bear'):
                self.room.harvest.append(monster.name)
            elif monster.name in ('Goblin', 'Skeleton', 'Zombie', 'Ogre', 'Troll'):
                self.carried_drop(monster.name in ('Ogre', 'Troll'))
        if not self.combat:
            self.p.groggy = False
            self.p.bound = False

    def attack_damage(self, monster):
        weapon = self.p.equipment['main']
        name = weapon.name if weapon else 'Fists'
        spec = D.WEAPONS.get(name, D.UNARMED_DAMAGE)
        rolled, maximum = dice(self.rng, spec)
        damage = rolled + ceil(self.p.might / 2)
        if name == 'Dagger' and maximum:
            damage += self.p.cunning // 2
        if weapon and weapon.venom:
            damage += dice(self.rng, D.VENOM_DAMAGE)[0]
            if chance(self.rng, D.VENOM_MONSTER_POISON):
                monster.poisoned = True
            weapon.venom = False
        damage = floor(damage * self.modifiers()[1] + 1e-9)
        armor = dice(self.rng, D.MONSTERS[monster.name][2])[0]
        if name == 'Mace':
            armor = max(0, armor - 1)
        before_armor = damage
        damage = max(0, damage - armor)
        self.say(f'Weapon roll: {rolled}; damage before armor: {before_armor}; armor absorbs {min(armor, before_armor)}; damage dealt: {damage}.')
        if monster.poisoned:
            self.say(f'{monster.name} is Poisoned.')
        headshot = monster.name == 'Zombie' and maximum
        if headshot:
            self.say('Headshot! The Zombie collapses regardless of remaining HP.')
        return max(monster.hp, damage) if headshot else damage

    def attack(self, target=0, shield_decider=None):
        if self.p.dead:
            raise ValueError("This adventurer is dead.")
        if self.skip_bound(shield_decider):
            return
        if not self.combat:
            raise ValueError('There is no enemy to attack.')
        monster = self.enemies[target]
        if chance(self.rng, self.hit_chance(monster)):
            damage = self.attack_damage(monster)
            self.say(f'You hit {monster.name} for {damage}.')
            weapon = self.p.equipment['main']
            cleave = weapon and weapon.name in ('Arming Sword', 'Zweihander')
            overflow = max(0, damage - monster.hp)
            monster.hp -= damage
            # Overkill is already post-armor damage; it carries without a second hit roll.
            if cleave:
                for next_monster in self.enemies:
                    if not overflow:
                        break
                    self.say(f'The swing carries into {next_monster.name} for {overflow}.')
                    remaining = max(0, overflow - next_monster.hp)
                    next_monster.hp -= overflow
                    overflow = remaining
        else:
            self.say(f'You miss {monster.name}.')
        self.finish_turn(shield_decider)

    def finish_turn(self, shield_decider=None):
        self.resolve_deaths()
        self.advance(D.ACTION_MINUTES['combat'])
        if not self.p.dead:
            self.enemy_turn(shield_decider)
        self.resolve_deaths()

    def enemy_turn(self, shield_decider=None):
        for monster in list(self.enemies):
            if self.p.dead:
                break
            if monster.burning or monster.poisoned:
                damage = (dice(self.rng, D.BURN_DAMAGE)[0] if monster.burning else 0) + int(monster.poisoned)
                monster.hp -= damage
                self.say(f'{monster.name} suffers {damage} from its afflictions.')
                if monster.hp <= 0:
                    continue
            if monster.name == 'Troll' and not monster.suppressed:
                monster.hp = min(monster.max_hp, monster.hp + dice(self.rng, (1, 2, 0))[0])
                self.say('The Troll knits its wounds together.')
            if monster.name == 'Goblin' and monster.hp <= monster.max_hp / 2:
                if chance(self.rng, D.GOBLIN_FLEE):
                    monster.fled = True
                    self.say('The Goblin bolts into the dark.')
                else:
                    self.say('The Goblin tries to escape, but stumbles.')
                continue
            hit = D.MONSTERS[monster.name][1] + (D.GROGGY_PENALTY if self.p.groggy else 0)
            if monster.name == 'Giant Spider' and not monster.web_used:
                monster.web_used = True
                if chance(self.rng, hit):
                    self.p.bound = True
                    self.say('Web binds you! You will lose your next action.')
                else:
                    self.say('A web sails past you.')
                continue
            if not chance(self.rng, hit):
                self.say(f'{monster.name} misses you.')
                continue
            damage = max(1, dice(self.rng, D.MONSTERS[monster.name][3])[0])
            shield_slot = next((slot for slot, item in self.p.equipment.items() if item and item.name == 'Shield'), None)
            if shield_slot and shield_decider and shield_decider(monster.name, damage):
                self.p.equipment[shield_slot] = None
                self.say('Your shield splinters, negating the hit entirely.')
                continue
            rolled = damage
            absorbed = min(damage, self.armor())
            damage -= absorbed
            self.say(f'{monster.name} hits you for {damage}. Damage rolled: {rolled}; armor absorbs {absorbed}.')
            self.hurt(damage, f'Killed by {monster.name}')
            if not self.p.dead and monster.name == 'Giant Spider' and damage and chance(self.rng, 100 / self.p.might):
                self.poison()

    def skip_bound(self, shield_decider=None):
        if not self.p.bound or not self.combat:
            return False
        self.p.bound = False
        self.say('You tear free of the web, losing your action.')
        self.finish_turn(shield_decider)
        return True

    def flee(self, shield_decider=None):
        if self.p.dead:
            raise ValueError("This adventurer is dead.")
        if self.skip_bound(shield_decider):
            return
        if not self.combat:
            raise ValueError('There is nothing to flee from.')
        if not chance(self.rng, 12 * self.p.cunning):
            self.say('You fail to escape!')
            self.finish_turn(shield_decider)
            return False
        origin = self.room
        destination = self.state.previous
        pursuers = [m for m in self.enemies if m.name == 'Troll' and chance(self.rng, D.TROLL_PURSUIT_CHANCE)]
        self.advance(D.ACTION_MINUTES['combat'])
        if self.p.dead:
            return False
        if destination is None:
            # The entrance room's incoming exit leads outside.
            self.say('You escape through the entrance.')
            self.state.location = 'Vale'
            value = self.state.expedition_silver + sum(D.TREASURES[i.name] for i in self.p.all_items() if i.name in D.TREASURES and i.found and not i.extracted)
            self.state.expedition_silver = 0
            for item in self.p.all_items():
                if item.name in D.TREASURES and item.found:
                    item.extracted = True
            self.p.fortune += value
            self.p.gain_xp(value * D.TREASURE_XP_PER_SILVER, self.state.minute)
            self.state.rooms = {}
            self.state.current = self.state.previous = None
            self.p.groggy = self.p.bound = False
        else:
            self.state.current = destination
            self.state.previous = origin.id
            self.say('You escape back through the exit you entered.')
            # Slow trolls follow: this makes luring one into existing daylight possible.
            for troll in pursuers:
                origin.monsters.remove(troll)
                self.room.monsters.append(troll)
                self.say('The Troll follows your footsteps.')
            self.p.groggy = self.p.bound = False
            self.arrive()
        return True

    def cast_scroll(self, spell, target=None):
        if spell == 'Mending':
            amount = dice(self.rng, D.SPELL_DAMAGE)[0] + self.p.magic
            self.p.heal(amount, self.state.minute)
            self.say(f'Mending restores up to {amount} HP.')
        elif target:
            damage = dice(self.rng, D.SPELL_DAMAGE)[0] + self.p.magic
            target.hp -= damage
            target.suppressed = True
            if spell == 'Ember' and target.flammable:
                target.burning = True
            self.say(f'{spell} deals {damage} damage to {target.name}.')
        else:
            self.say('The spell dissolves in the empty air.')

    def use(self, index, target=0, shield_decider=None):
        if self.p.dead:
            raise ValueError("This adventurer is dead.")
        if self.skip_bound(shield_decider):
            return
        item = self.p.inventory[index]
        name = item.name
        in_combat = self.combat
        monster = self.enemies[target] if in_combat else None
        if name == 'Torch':
            if self.p.equipment['main'] and self.p.equipment['main'].name == 'Zweihander':
                raise ValueError('A Zweihander occupies both hands. Unequip it before lighting a Torch.')
            slot = 'off'
            off = self.p.equipment['off']
            if off and off.name != 'Torch':
                main = self.p.equipment['main']
                if main and main.name != 'Torch':
                    raise ValueError('Both hands are occupied. Unequip an item before lighting a Torch.')
                slot = 'main'
            self.p.inventory.pop(index)
            item.burn = item.burn or 60
            self.p.equipment[slot] = item
            self.say('You raise a lit torch.')
        elif name == 'Healing Potion':
            self.p.inventory.pop(index)
            amount = dice(self.rng, D.SPELL_DAMAGE)[0] + self.p.magic
            self.p.heal(amount, self.state.minute)
            self.say(f'The potion restores up to {amount} HP.')
        elif name == 'Antidote':
            self.p.inventory.pop(index)
            if chance(self.rng, 12 * self.p.magic):
                self.p.effects.pop('Poison', None)
                self.p.poison_tick = 0
                self.say('The poison subsides.')
            else:
                self.say('The antidote has no effect.')
        elif name == 'Spider Venom':
            if not self.p.equipment['main'] or self.p.equipment['main'].name not in D.WEAPONS:
                raise ValueError('Equip a weapon before applying venom.')
            item.name = 'Empty Bottle'
            self.p.equipment['main'].venom = True
            self.say('You coat your weapon. The empty bottle is yours again.')
        elif name == 'Oil':
            if not monster:
                raise ValueError('Choose a monster to coat with Oil during combat.')
            self.p.inventory.pop(index)
            monster.flammable = True
            self.say(f'{monster.name} is coated in oil.')
        elif name == 'Scroll':
            self.p.inventory.pop(index)
            self.cast_scroll(item.spell, monster)
        elif name == 'Pale Book':
            self.p.inventory.pop(index)
            self.outcome(weighted(self.rng, [x[0] for x in D.FEATURE_OUTCOMES[name]], [x[1] for x in D.FEATURE_OUTCOMES[name]]))
        else:
            raise ValueError('This item is used contextually, equipped, or sold.')
        if in_combat:
            self.finish_turn(shield_decider)
        else:
            self.advance(1)

    def torch_attack(self, target=0, shield_decider=None):
        if self.p.dead:
            raise ValueError("This adventurer is dead.")
        if self.skip_bound(shield_decider):
            return
        if not self.combat or not self.torch:
            raise ValueError('You need a lit torch and a target.')
        monster = self.enemies[target]
        if chance(self.rng, self.hit_chance(monster, weapon_bonus=False)):
            damage = dice(self.rng, D.TORCH_DAMAGE)[0]
            monster.hp -= damage
            monster.suppressed = True
            if monster.flammable:
                monster.burning = True
            self.say(f'Your torch scorches {monster.name} for {damage}.')
        else:
            self.say('The torch misses.')
        self.finish_turn(shield_decider)

    def rest(self):
        self.require_safe()
        if self.state.location != 'Labyrinth':
            raise ValueError('Rent a room at the Inn for a safe rest.')
        if chance(self.rng, D.REST_ENCOUNTER):
            self.advance(self.rng.randint(*D.REST_INTERRUPT_MINUTES))
            if not self.p.dead:
                self.room.monsters.append(spawn(self.rng))
                self.p.groggy = True
                self.say('Something wakes you before you recover. You are Groggy.')
                self.arrive()
        else:
            self.advance(D.ACTION_MINUTES['rest'])
            if not self.p.dead:
                self.p.hp = self.p.max_hp(self.state.minute)
                self.say('You wake rested. Persistent afflictions remain.')

    def refresh_stock(self):
        week = self.state.minute // (7 * 1440)
        if self.state.stock_week == week:
            return
        self.state.stock_week = week
        self.state.stock = [Item('Torch') for _ in range(D.STOCK_TORCHES)]
        self.state.stock += [Item(name, spell=self.rng.choice(D.SPELLS) if name == 'Scroll' else '') for name in D.UTILITY if name != 'Torch']
        self.state.stock += [tier_item(self.rng, found=False, equipment=True) for _ in range(D.STOCK_EQUIPMENT)]

    def price(self, item, buying=True):
        # Buy always exceeds sell; attributes can improve prices without arbitrage.
        multiplier = max(D.BUY_MIN_MULTIPLIER, D.BUY_MULTIPLIER - D.BUY_CUNNING_DISCOUNT * self.p.cunning) if buying else min(D.SELL_MAX_MULTIPLIER, D.SELL_MULTIPLIER + D.SELL_CUNNING_BONUS * self.p.cunning)
        return max(1, ceil(item.value * multiplier)) if buying else (max(1, floor(item.value * multiplier)) if item.value else 0)

    def pay(self, amount):
        if self.p.silver < amount:
            raise ValueError(f'You need {amount} sp.')
        self.p.silver -= amount

    def buy(self, index):
        self.require_town()
        item = self.state.stock[index]
        if len(self.p.inventory) >= D.INVENTORY_LIMIT:
            raise ValueError('Your inventory is full.')
        self.pay(self.price(item))
        self.state.stock.pop(index)
        item.found = False
        self.p.add(item)
        self.say(f'You buy {item.label}.')
        self.advance(D.ACTION_MINUTES['town'])

    def sell(self, index):
        self.require_town()
        item = self.p.inventory.pop(index)
        amount = self.price(item, False)
        self.p.silver += amount
        item.found = False
        self.state.stock.append(item)
        self.say(f'You sell {item.label} for {amount} sp.')
        self.advance(D.ACTION_MINUTES['town'])

    def inn(self, meal=False):
        self.require_town()
        self.pay(D.SERVICE_COSTS['Meal' if meal else 'Room'])
        if meal:
            self.effect('Well Fed')
            self.advance(D.ACTION_MINUTES['town'])
        else:
            self.advance(D.ACTION_MINUTES['rest'])
            if not self.p.dead:
                self.p.hp = self.p.max_hp(self.state.minute)
                self.say('You wake fully rested. Persistent afflictions remain.')

    def shrine(self, service, index=None):
        self.require_town()
        if service == 'Identification':
            if index is None or self.p.inventory[index].identified:
                raise ValueError('Choose an unidentified item in your inventory.')
        self.pay(D.SERVICE_COSTS[service])
        if service == 'Healing':
            self.p.heal(ceil(self.p.max_hp(self.state.minute) * D.HEAL_FRACTION), self.state.minute)
            self.say('The priest tends your wounds.')
        elif service == 'Blessing':
            self.effect('Bless')
        elif service == 'Cure Afflictions':
            self.p.effects.pop('Poison', None)
            self.p.effects.pop('Curse', None)
            self.p.poison_tick = 0
            for item in self.p.all_items():
                if item.magic == 'Curse':
                    item.magic = ''
                    item.identified = True
            self.say('The priest lifts poison and curses.')
        elif service == 'Identification':
            self.p.inventory[index].identified = True
            self.say(f'The priest identifies {self.p.inventory[index].label}.')
        else:
            raise ValueError('Unknown Shrine service.')
        self.advance(D.ACTION_MINUTES['town'])

    def drink(self):
        self.require_town()
        self.pay(D.SERVICE_COSTS['Drink'])
        if self.state.drink_day != self.state.day:
            self.state.drinks = 0
            self.state.drink_day = self.state.day
        self.state.drinks += 1
        self.say('The barkeep says: "' + self.rng.choice(D.FACTS) + '"')
        if chance(self.rng, D.DRINK_CHANCE_PER_DRINK * self.state.drinks - D.DRINK_MIGHT_RESISTANCE * self.p.might):
            self.effect('Tipsy')
        self.advance(D.ACTION_MINUTES['town'])

    def rumor(self):
        self.require_town()
        if self.state.rumor_day == self.state.day:
            self.say('The adventurers have nothing new to tell you today.')
        else:
            self.state.rumor_day = self.state.day
            self.say('An adventurer says: "' + self.rng.choice(D.RUMORS) + '"')
        self.advance(D.ACTION_MINUTES['town'])
