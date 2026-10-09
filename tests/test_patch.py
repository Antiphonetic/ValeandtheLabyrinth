"""v0.01a regressions: pacing, template objects, cash and frontend navigation."""
import contextlib
import io
import random
import tempfile
import unittest
from dataclasses import asdict
from unittest.mock import patch

from vale import data as D
from vale.cli import Terminal, wrap_prose
from vale.dungeon import contextual_elements, generate, ordinary_treasure, spawn, template
from vale.engine import Game
from vale.models import Element, Exit, Item, Room, state_from_dict
from vale.storage import Storage


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.g = Game(1, Storage(self.temp.name))
        self.g.p.equipment['main'] = Item('Spear')

    def room(self, elements=()):
        g = self.g
        g.state.location = 'Labyrinth'
        g.state.current = 0
        g.state.rooms = {0: Room(0, 1, 'Test', 'A room.', daylight=True,
                                elements=list(elements), exits=[Exit('Exit', 0)])}
        return g.room

    def test_exact_patch_tables_and_skeleton(self):
        self.assertEqual(D.NORMAL_CONTENT, [30, 27, 17, 10, 5, 5, 6])
        self.assertEqual(sum(D.NORMAL_CONTENT), 100)
        self.assertEqual(D.SECRET_CONTENT, [20, 20, 30, 10, 5, 5, 10])
        self.assertEqual(D.MONSTERS['Skeleton'][2], (1, 4, 0))
        monster = spawn(self.g.rng, 'Skeleton')
        self.assertEqual(monster.hp, 1)
        self.assertEqual(len(monster.gear), 2)
        self.assertEqual(list(D.TREASURES.values()), [1, 1, 3, 5, 6, 12, 15, 35])
        self.assertEqual(D.TREASURE_WEIGHTS, [25, 25, 15, 10, 10, 7, 5, 3])

    def test_silver_chance_boundaries_and_amount(self):
        rng = random.Random(1)
        with patch.object(rng, 'random', return_value=.14999), patch.object(rng, 'randint', return_value=1):
            item = ordinary_treasure(rng)
            self.assertEqual((item.name, item.value), ('Loose Silver', 3))
        with patch.object(rng, 'random', return_value=.15), patch('vale.dungeon.treasure') as normal:
            ordinary_treasure(rng)
            normal.assert_called_once_with(rng, False)
        with patch('vale.dungeon.chance') as chance, patch('vale.dungeon.treasure') as normal:
            ordinary_treasure(rng, secret=True)
            chance.assert_not_called()
            normal.assert_called_once_with(rng, True)
        rng = random.Random(89)
        items = [ordinary_treasure(rng) for _ in range(20000)]
        cash = [i for i in items if i.name == 'Loose Silver']
        self.assertAlmostEqual(len(cash) / 200, 15, delta=1)
        self.assertEqual({i.value for i in cash}, set(range(3, 9)))

    def test_generate_treasure_uses_cash_pool(self):
        with patch('vale.dungeon.contents', return_value=['Treasure']), patch('vale.dungeon.chance', return_value=True):
            room = generate(self.g.rng, 0, 1)
        self.assertEqual(room.loot[0].name, 'Loose Silver')

    def test_cash_no_slot_and_extraction_once_including_flee(self):
        for flee in (False, True):
            with self.subTest(flee=flee):
                self.g = Game(1)
                room = self.room()
                self.g.p.inventory = [Item('Rope') for _ in range(15)]
                room.loot = [Item('Loose Silver', found=True, silver_amount=8)]
                self.g.take(0)
                self.assertEqual(self.g.p.silver, 8)
                self.assertEqual(self.g.p.fortune, 0)
                self.assertEqual(len(self.g.p.inventory), 15)
                if flee:
                    room.monsters = [spawn(self.g.rng, 'Giant Rat')]
                    with patch('vale.engine.chance', return_value=True):
                        self.g.flee()
                else:
                    self.g.return_to_vale()
                self.assertEqual(self.g.p.fortune, 8)
                self.assertEqual(self.g.p.xp, 8)
                self.assertEqual(self.g.state.expedition_silver, 0)
                self.room()
                self.g.return_to_vale()
                self.assertEqual(self.g.p.fortune, 8)

    def test_torch_supports_eleven_moves_after_lighting(self):
        room = self.room()
        room.daylight = False
        self.g.use(0)
        start = self.g.state.minute
        for _ in range(11):
            self.g.move(0)
        self.assertEqual(self.g.state.minute - start, 55)
        self.assertIsNotNone(self.g.torch)
        self.g.move(0)
        self.assertIsNone(self.g.torch)
        self.assertEqual(D.ACTION_MINUTES['search'], 10)
        self.assertEqual(D.ACTION_MINUTES['combat'], 1)

    def test_every_template_variant_interaction_and_empty(self):
        seen = set()
        rng = random.Random(52)
        for _ in range(1000):
            name, text, _, shaft = template(rng)
            elements = contextual_elements(name, text, shaft)
            seen.update(e.name for e in elements)
            if name == 'Sunken Crypt':
                self.assertEqual([e.name for e in elements], ['Sarcophagus'] if 'sarcophagus' in text else
                                 ['Grave Niches'] if 'niches' in text else ['Crypt Statue', 'Casket'])
            if name == 'Petrified Courtyard':
                self.assertEqual(len(elements), 2)
            if name == 'Damp Chamber':
                self.assertEqual(bool(elements), shaft)
        self.assertEqual(seen, set(D.CONTEXT_ACTIONS))
        with patch('vale.dungeon.template', return_value=('Sunken Crypt', 'A sarcophagus.', False, False)), \
             patch('vale.dungeon.contents', return_value=['Empty']), patch('vale.dungeon.chance', return_value=False):
            room = generate(rng, 0, 1)
        self.assertFalse(room.monsters or room.loot or room.traps or room.hidden)
        self.assertEqual([e.name for e in room.elements], ['Sarcophagus'])

    def test_all_context_nothing_results_are_safe_and_once(self):
        for name in D.CONTEXT_ACTIONS:
            with self.subTest(name=name):
                self.room([Element(name)])
                with patch('vale.engine.weighted', return_value='Nothing'):
                    self.g.interact(0)
                self.assertTrue(self.g.room.elements[0].done)
                self.assertFalse(self.g.room.monsters or self.g.room.loot)
                with self.assertRaises(ValueError):
                    self.g.interact(0)

    def test_sarcophagus_undead_with_treasure(self):
        self.room([Element('Sarcophagus')])
        with patch('vale.engine.weighted', return_value='Undead Treasure'):
            self.g.interact(0)
        self.assertIn(self.g.enemies[0].name, ('Skeleton', 'Zombie'))
        self.assertEqual(len(self.g.room.loot), 1)
        self.assertIn(self.g.room.loot[0].name, D.TREASURES)
        self.assertEqual(D.CONTEXT_OUTCOMES['Sarcophagus'], [
            ('Nothing', 45), ('Treasure', 20), ('Undead', 20), ('Undead Treasure', 10), ('Strange', 5)])

    def test_inspect_then_rope_only_for_navigable_shaft(self):
        self.room([Element('Floor Shaft', animal='navigable')])
        self.g.interact(0)
        self.assertEqual(self.g.room.elements[1].name, 'Deep Shaft')
        with self.assertRaises(ValueError):
            self.g.interact(1)
        self.g.p.inventory.append(Item('Rope'))
        self.g.interact(1)
        self.assertEqual(self.g.room.exits[-1].name, 'Rope down the shaft')
        self.room([Element('Floor Shaft')])
        self.g.interact(0)
        self.assertEqual(len(self.g.room.elements), 1)

    def test_word_boundaries_and_no_hyphen_split(self):
        text = 'ordinary words stay whole while extraordinarily-long-words stay whole too'
        output = wrap_prose(text, 20)
        self.assertEqual(output.split(), text.split())
        self.assertIn('extraordinarily-long-words', output.splitlines())
        self.assertTrue(all(len(line) <= 20 or len(line.split()) == 1 for line in output.splitlines()))
        self.assertEqual(wrap_prose('first\n\nsecond', 20), 'first\n\nsecond')

    def test_location_action_and_inventory_callers(self):
        # Menu dispatch is mocked, but actual rule actions, nested menus and saves run.
        g = self.g
        g.p.silver = 100
        cases = [('Tavern', [0, 1, 3, 4, 2]), ('Merchant', [0, 0, 3, 4, 2]),
                 ('Shrine', [0, 5, 4, 4]), ('Inn', [1, 0, 3, 4, 2]),
                 ('Graveyard', [1, 4, 0])]
        for name, answers in cases:
            with self.subTest(name=name), contextlib.redirect_stdout(io.StringIO()):
                def select(title, options):
                    self.assertEqual(g.state.location, 'Vale')
                    self.assertEqual(g.state.town_screen, name)
                    return next(sequence)
                sequence = iter(answers)
                with patch('vale.cli.choose', side_effect=select):
                    Terminal(g).location(name)
                self.assertEqual(g.state.town_screen, 'Vale')
        self.room()
        current = g.state.current
        with contextlib.redirect_stdout(io.StringIO()), patch('vale.cli.choose', return_value=4):
            Terminal(g).inventory()
        self.assertEqual(g.state.location, 'Labyrinth')
        self.assertEqual(g.state.current, current)

    def test_merchant_sale_stays_and_can_buy_again(self):
        g = self.g
        g.p.inventory = [Item('Silver Goblet')]
        g.p.silver = 100
        sequence = iter([1, 0, 0, 0, 2])
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch('vale.cli.choose', side_effect=lambda *args: next(sequence)):
            Terminal(g).location('Merchant')
        self.assertIn('You sell Silver Goblet', output.getvalue())
        self.assertTrue(any(i.name == 'Torch' for i in g.p.inventory))

    def test_opening_inventory_and_return(self):
        g = self.g
        calls = []
        sequence = iter([2, 4, 1, 7])
        def select(title, options):
            calls.append((title, options))
            return next(sequence)
        with contextlib.redirect_stdout(io.StringIO()), patch('vale.cli.choose', side_effect=select):
            Terminal(g).play(opening=True)
        self.assertEqual(calls[0][1][2], 'Inventory / Equipment')
        self.assertEqual([title for title, _ in calls].count('Begin'), 2)
        self.assertEqual(g.state.location, 'Vale')

    def test_save_cash_context_location_and_old_save_defaults(self):
        room = self.room([Element('Sarcophagus', done=True), Element('Floor Shaft', animal='navigable')])
        room.loot = [Item('Loose Silver', found=True, silver_amount=4)]
        self.g.state.expedition_silver = 8
        with tempfile.TemporaryDirectory() as directory:
            storage = Storage(directory)
            storage.save(self.g.state, self.g.rng)
            loaded, rng = storage.load()
            self.assertEqual(asdict(loaded), asdict(self.g.state))
        self.g.return_to_vale()
        self.g.state.town_screen = 'Merchant'
        raw = asdict(self.g.state)
        raw.pop('town_screen')
        raw.pop('expedition_silver')
        for i in raw['player']['inventory']:
            i.pop('silver_amount')
        for i in raw['player']['equipment'].values():
            if i:
                i.pop('silver_amount')
        old = state_from_dict(raw)
        self.assertEqual(old.town_screen, 'Vale')
        self.assertEqual(old.expedition_silver, 0)

    def test_smoke_prepare_explore_interact_combat_loot_return_recover(self):
        g = self.g
        g.p.inventory.append(Item('Padded Jack'))
        g.equip(len(g.p.inventory) - 1)
        g.use(0)
        with patch('vale.dungeon.template', return_value=('Sunken Crypt', 'A sarcophagus.', False, False)), \
             patch('vale.dungeon.contents', return_value=['Treasure']), patch('vale.dungeon.chance', return_value=False):
            g.enter()
        with patch('vale.engine.weighted', return_value='Undead'):
            g.interact(0)
        for _ in range(30):
            if not g.combat or g.p.dead:
                break
            g.attack()
        self.assertFalse(g.p.dead)
        self.assertFalse(g.combat)
        results = '\n'.join(g.messages)
        for expected in ('Weapon roll:', 'armor absorbs', 'XP awarded.', 'dies.'):
            self.assertIn(expected, results)
        while g.room.loot:
            g.take(0)
        g.return_to_vale()
        self.assertGreater(g.p.fortune, 0)
        # Deterministic service coverage; don't make starting characters wealthy.
        g.p.silver += 100
        for index in range(len(g.p.inventory) - 1, -1, -1):
            if g.p.inventory[index].name in D.TREASURES:
                g.sell(index)
        g.buy(0)
        g.shrine('Healing')
        g.inn()
        g.save()
        self.assertEqual(g.storage.load()[0].player.hp, g.p.max_hp(g.state.minute))

    def test_last_action_survives_menu_redraw(self):
        term = Terminal(self.g)
        self.g.say('A round happened.')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            term.screen('Room')
            term.screen('Inventory')
        self.assertEqual(output.getvalue().count('A round happened.'), 2)
        self.g.say('New result.')
        with contextlib.redirect_stdout(io.StringIO()):
            term.screen('Room')
        self.assertEqual(term.recent, ['New result.'])


if __name__ == '__main__':
    unittest.main()
