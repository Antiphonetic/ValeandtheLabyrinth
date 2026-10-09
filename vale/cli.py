"""Numbered terminal menus. No third-party dependencies."""
import argparse
import json
from pathlib import Path
from . import data as D
from .dungeon import describe
from .engine import Game
from .storage import Storage


def choose(title, options):
    print('\n' + title)
    for i, text in enumerate(options, 1):
        print(f'  {i}. {text}')
    while True:
        answer = input('> ').strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        print(f'Enter a number from 1 to {len(options)}.')


def pick_item(title, items, labels=None):
    if not items:
        print('Nothing available.')
        return None
    choice = choose(title, labels or [i.label for i in items] + ['Cancel'])
    return None if choice == len(items) else choice


class Terminal:
    def __init__(self, game):
        self.game = game

    def messages(self):
        for message in self.game.messages:
            print(message)
        self.game.messages.clear()

    def hud(self):
        g, p = self.game, self.game.p
        spare = sum(i.name == 'Torch' and i.burn == 0 for i in p.inventory)
        effects = [name for name in p.effects if p.active(name, g.state.minute)]
        effects += ['Groggy'] if p.groggy else []
        effects += ['Bound'] if p.bound else []
        print(f'\n{p.name} | HP {p.hp}/{p.max_hp(g.state.minute)} | Level {p.level} | XP {p.xp:.2f}')
        print(f'Might {p.might} | Cunning {p.cunning} | Magic {p.magic} | Silver {p.silver} sp | Fortune {p.fortune} sp')
        print(f'{g.state.clock} | Spare Torches {spare} | Light: {g.light} | Inventory {len(p.inventory)}/15')
        if effects:
            print('Effects: ' + ', '.join(effects))

    def shield(self, enemy, damage):
        return choose(f'{enemy} is about to hit you. Sacrifice your Shield to negate the hit?', ['Keep Shield', 'Sacrifice Shield']) == 1

    def target(self):
        enemies = self.game.enemies
        if len(enemies) == 1:
            return 0
        return choose('Choose target', [f'{m.name} — HP {m.display_hp}' for m in enemies])

    def use_item(self):
        g = self.game
        usable = [(i, item) for i, item in enumerate(g.p.inventory) if item.name in ('Torch', 'Healing Potion', 'Antidote', 'Spider Venom', 'Oil', 'Scroll', 'Pale Book')]
        if not usable:
            print('You have no usable items.')
            return
        choice = choose('Use Item', [item.label for _, item in usable] + ['Cancel'])
        if choice == len(usable):
            return
        index, item = usable[choice]
        target = self.target() if g.combat and item.name in ('Oil', 'Scroll') and item.spell != 'Mending' else 0
        g.use(index, target, self.shield)

    def inventory(self):
        g = self.game
        while True:
            print('\nEQUIPMENT')
            for slot, item in g.p.equipment.items():
                label = item.label if item else ('Occupied by Zweihander' if slot == 'off' and g.p.equipment['main'] and g.p.equipment['main'].name == 'Zweihander' else 'Empty')
                print(f'  {slot}: {label}')
            print('INVENTORY')
            for i, item in enumerate(g.p.inventory, 1):
                print(f'  {i}. {item.label}')
            if g.combat:
                print('Equipment changes and dropping items are unavailable during combat.')
                return
            option = choose('Inventory', ['Equip', 'Unequip', 'Use Item', 'Drop Item', 'Back'])
            try:
                if option == 0:
                    index = pick_item('Equip which item?', g.p.inventory)
                    if index is not None:
                        g.equip(index)
                elif option == 1:
                    slots = [s for s, item in g.p.equipment.items() if item]
                    if not slots:
                        print('Nothing equipped.')
                    else:
                        slot = choose('Unequip', slots + ['Cancel'])
                        if slot < len(slots):
                            g.unequip(slots[slot])
                elif option == 2:
                    self.use_item()
                elif option == 3:
                    index = pick_item('Drop which item? Items dropped in Vale are lost.', g.p.inventory)
                    if index is not None:
                        g.drop(index)
                else:
                    return
            except ValueError as error:
                print(error)
            self.messages()
            g.save()
            if g.p.dead:
                return

    def graveyard(self):
        print('\nTHE GRAVEYARD\n' + D.TOWN['Graveyard'])
        for rank, grave in enumerate(self.game.storage.leaderboard(self.game.state), 1):
            mark = ' †' if grave['dead'] else ''
            print(f"{rank}. {grave['name']}{mark} — {grave['fortune']} sp — Depth {grave['depth']} — {grave['days']} days — {grave['cause']}")

    def merchant(self):
        g = self.game
        print('\nMERCHANT\n' + D.TOWN['Merchant'])
        action = choose('Merchant', ['Buy', 'Sell', 'Leave'])
        if action == 0:
            stock = g.state.stock
            labels = [f'{item.label} — {g.price(item)} sp' for item in stock] + ['Cancel']
            index = pick_item('Buy', stock, labels)
            if index is not None:
                g.buy(index)
        elif action == 1:
            items = g.p.inventory
            labels = [f'{item.label} — {g.price(item, False)} sp' for item in items] + ['Cancel']
            index = pick_item('Sell (unequip equipment first)', items, labels)
            if index is not None:
                g.sell(index)

    def shrine(self):
        g = self.game
        print('\nSHRINE\n' + D.TOWN['Shrine'])
        services = ['Healing', 'Blessing', 'Cure Afflictions', 'Identification']
        choice = choose('Shrine', ['Healing 2 sp', 'Blessing 5 sp', 'Cure Afflictions 5 sp', 'Identification 5 sp', 'Leave'])
        if choice == 4:
            return
        index = None
        if choice == 3:
            unknown = [(i, item) for i, item in enumerate(g.p.inventory) if not item.identified]
            if not unknown:
                print('No unidentified carried items. Unequip an item first if necessary.')
                return
            chosen = choose('Identify', [item.label for _, item in unknown] + ['Cancel'])
            if chosen == len(unknown):
                return
            index = unknown[chosen][0]
        g.shrine(services[choice], index)

    def town(self):
        g = self.game
        print('\nVALE\n' + D.TOWN['Vale'])
        options = ['Tavern', 'Merchant', 'Shrine', 'Inn', 'Graveyard', 'Labyrinth', 'Inventory / Equipment', 'Save and Quit']
        action = choose('Where would you like to go?', options)
        if action == 0:
            print('\nTAVERN\n' + D.TOWN['Tavern'])
            choice = choose('Tavern', ['Buy a Drink 2 sp', 'Talk with Adventurers', 'Leave'])
            if choice == 0:
                g.drink()
            elif choice == 1:
                g.rumor()
        elif action == 1:
            self.merchant()
        elif action == 2:
            self.shrine()
        elif action == 3:
            print('\nINN\n' + D.TOWN['Inn'])
            choice = choose('Inn', ['Rent a Room 10 sp', 'Buy a Meal 3 sp', 'Leave'])
            if choice < 2:
                g.inn(meal=choice == 1)
        elif action == 4:
            self.graveyard()
        elif action == 5:
            g.enter()
        elif action == 6:
            self.inventory()
        else:
            return False
        return True

    def combat_menu(self):
        g = self.game
        if g.skip_bound(self.shield):
            return
        for m in g.enemies:
            print(f'\n{m.name} — {D.MONSTERS[m.name][4]}\nHP {m.display_hp}')
        choice = choose('COMBAT', ['Attack', 'Use Item', 'Cast', 'Flee', 'Inventory (view)', 'Save and Quit'])
        if choice == 0:
            if g.torch:
                method = choose('Attack with', ['Weapon / Fists', 'Lit Torch', 'Cancel'])
                if method == 2:
                    return
                if method == 1:
                    g.torch_attack(self.target(), self.shield)
                    return
            g.attack(self.target(), self.shield)
        elif choice == 1:
            self.use_item()
        elif choice == 2:
            print('You know no spells. Scrolls can be used through Use Item.')
        elif choice == 3:
            g.flee(self.shield)
        elif choice == 4:
            self.inventory()
        else:
            return False
        return True

    def feature(self):
        g = self.game
        elements = [(i, e) for i, e in enumerate(g.room.elements) if not e.done]
        if not elements:
            print('There is nothing left to investigate here.')
            return
        choice = choose('Investigate', [e.name + (f' ({e.animal})' if e.animal else '') for _, e in elements] + ['Cancel'])
        if choice == len(elements):
            return
        index, element = elements[choice]
        print(D.FEATURES.get(element.name, D.SPECIALS.get(element.name)))
        if element.name == 'Pale Book':
            options = ['Read', 'Take', 'Leave']
            choice = choose('Pale Book', options)
            if choice < 2:
                g.interact(index, 'take' if choice == 1 else 'read')
        elif element.name == 'Wounded Animal':
            choice = choose('Wounded Animal', ['Attempt to help', 'Harvest material', 'Leave'])
            if choice < 2:
                g.interact(index, 'harvest' if choice == 1 else 'help')
        else:
            verbs = {'Corpse': 'Search Corpse', 'Locked Chest': 'Pick Lock', 'Deep Shaft': 'Secure Rope and Descend', 'Locked Door': 'Pick Lock', 'Lifelike Statue': 'Touch Statue', 'Iron Spike': 'Examine Spike', 'Fresco': 'Examine Fresco', 'Human Baby': 'Pick Up the Baby', 'Opalescent Fountain': 'Touch the Light', 'Tavern Sign': 'Examine Sign'}
            if choose(element.name, [verbs[element.name], 'Leave It']) == 0:
                g.interact(index, 'take' if element.name == 'Human Baby' else 'interact')

    def dungeon(self):
        g = self.game
        room = g.room
        print(f'\n{room.template.upper()} — Depth {room.depth}')
        print(describe(room, bool(g.torch)))
        if g.combat:
            return self.combat_menu()
        for element in room.elements:
            if not element.done:
                print(D.FEATURES.get(element.name, D.SPECIALS.get(element.name)))
        for trap in room.traps:
            if trap.detected and not trap.done:
                print(f'Detected: {trap.name} (you can avoid it simply by leaving).')
        if g.darkness:
            print('Shapes and passages are hard to distinguish. You cannot see loose loot.')
        elif room.loot:
            print('Within reach: ' + ', '.join(item.label for item in room.loot))
        choices = ['Travel through an Exit', 'Return to Vale', 'Search', 'Investigate Feature / Special', 'Collect Loot', 'Harvest Remains', 'Disarm Detected Trap', 'Rest', 'Inventory / Equipment', 'Use Item', 'Save and Quit']
        choice = choose('LABYRINTH', choices)
        if choice == 0:
            exit = choose('Exits', [e.name for e in room.exits] + ['Cancel'])
            if exit < len(room.exits):
                g.move(exit)
        elif choice == 1:
            g.return_to_vale()
        elif choice == 2:
            g.search()
        elif choice == 3:
            self.feature()
        elif choice == 4:
            if g.darkness:
                print('You cannot see loot in the darkness.')
            else:
                index = pick_item('Collect Loot', room.loot)
                if index is not None:
                    g.take(index)
        elif choice == 5:
            if not room.harvest:
                print('No useful remains.')
            else:
                index = choose('Harvest Remains', room.harvest + ['Cancel'])
                if index < len(room.harvest):
                    g.harvest(index)
        elif choice == 6:
            traps = [(i, t) for i, t in enumerate(room.traps) if t.detected and not t.done]
            if not traps:
                print('No detected traps.')
            else:
                index = choose('Disarm', [t.name for _, t in traps] + ['Cancel'])
                if index < len(traps):
                    g.disarm(traps[index][0])
        elif choice == 7:
            if choose('Risk an eight-hour rest here?', ['Rest', 'Cancel']) == 0:
                g.rest()
        elif choice == 8:
            self.inventory()
        elif choice == 9:
            self.use_item()
        else:
            return False
        return True

    def play(self, opening=False):
        g = self.game
        if opening:
            print(f'\nNEW GAME\nYou are {g.p.name}, come to Vale to seek your fortune in the Labyrinth beneath its mountain.')
            print('You have:\n- ' + g.p.equipment['main'].label + '\n- 3 Torches\n- ' + g.p.inventory[-1].label)
            print('The entry to the Labyrinth stands before you, a chill breeze like breath touching your cheeks.')
            print('Use Inventory to prepare your equipment and light a Torch before entering.')
            if choose('Begin', ['Enter the Labyrinth', 'Go to Vale']) == 0:
                g.enter()
        try:
            while not g.p.dead:
                self.messages()
                g.save()
                self.hud()
                if g.p.rewards:
                    choice = choose('LEVEL UP — choose one reward', ['Gain permanent Max HP equal to current Might', 'Increase Might by 1', 'Increase Cunning by 1', 'Increase Magic by 1'])
                    g.p.reward(['HP', 'might', 'cunning', 'magic'][choice])
                    continue
                try:
                    proceed = self.town() if g.state.location == 'Vale' else self.dungeon()
                    if proceed is False:
                        g.save()
                        print('Game saved. Your expedition will be here when you return.')
                        return
                except ValueError as error:
                    print(error)
            self.messages()
            self.graveyard()
        except (EOFError, KeyboardInterrupt):
            g.save()
            print('\nGame saved. Farewell.')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Vale & The Labyrinth v0.01')
    parser.add_argument('--seed', type=int, help='Reproducible random seed for a new character')
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent.parent / '.vale', help='Directory for save.json and graveyard.json')
    args = parser.parse_args(argv)
    storage = Storage(args.data_dir)
    print('VALE & THE LABYRINTH — v0.01')
    while True:
        try:
            option = choose('Main Menu', ['New Game', 'Continue', 'Graveyard', 'Quit'])
            if option == 3:
                return
            if option == 0:
                if storage.save_path.exists() and choose('A living character is saved. Replace that save?', ['Keep existing character', 'Replace save']) == 0:
                    continue
                game = Game(args.seed, storage)
                game.save()
                Terminal(game).play(opening=True)
            elif option == 1:
                if not storage.save_path.exists():
                    print('There is no living adventurer to continue.')
                    continue
                state, random_state = storage.load()
                Terminal(Game(storage=storage, state=state, random_state=random_state)).play()
            else:
                print('\nTHE GRAVEYARD\n' + D.TOWN['Graveyard'])
                state = storage.load()[0] if storage.save_path.exists() else None
                for i, grave in enumerate(storage.leaderboard(state), 1):
                    print(f"{i}. {grave['name']}{' †' if grave['dead'] else ''} — {grave['fortune']} sp — Depth {grave['depth']} — {grave['days']} days — {grave['cause']}")
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            print(f'Cannot complete that operation: {error}. Your existing data files have been preserved.')
        except (EOFError, KeyboardInterrupt):
            print('\nFarewell.')
            return
