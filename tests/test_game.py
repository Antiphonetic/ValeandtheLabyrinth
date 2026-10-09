import random
import tempfile
import unittest
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from vale import data as D
from vale.dungeon import contents, generate, spawn, treasure, dice, describe, weighted
from vale.engine import Game
from vale.models import Item, Room, Exit, Element
from vale.storage import Storage


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.storage = Storage(self.temp.name)
        self.g = Game(7, self.storage)
        self.p = self.g.p

    def room(self, monsters=(), daylight=False):
        g = self.g
        g.state.location = 'Labyrinth'
        g.state.current = 0
        g.state.previous = None
        g.state.rooms = {0: Room(0, 1, 'Test', 'A chamber.', daylight=daylight,
                                monsters=[spawn(g.rng, name) for name in monsters], exits=[Exit('Northern Hall')])}
        return g.room

    def test_character_generation_and_reproducibility(self):
        for seed in range(100):
            a, b = Game(seed), Game(seed)
            self.assertEqual(asdict(a.p), asdict(b.p))
            for attr in ('might', 'cunning', 'magic'):
                self.assertIn(getattr(a.p, attr), range(2, 6))
            self.assertEqual(a.p.hp, 5 * a.p.might)
            self.assertEqual(a.p.base_hp, a.p.hp)
            self.assertIn(a.p.equipment['main'].name, D.WEAPONS)
            self.assertEqual(len(a.p.inventory), 4)
            self.assertTrue(all(i.name == 'Torch' for i in a.p.inventory[:3]))
        # No minimum total; the full random space includes three low rolls.
        self.assertTrue(any((Game(seed).p.might, Game(seed).p.cunning, Game(seed).p.magic) == (2, 2, 2) for seed in range(1000)))

    def test_inventory_limit_and_swap(self):
        self.p.inventory = [Item('Rope') for _ in range(14)] + [Item('Spear')]
        with self.assertRaises(ValueError):
            self.p.add(Item('Rope'))
        self.p.equip(14)
        self.assertEqual(len(self.p.inventory), 15)
        self.assertEqual(self.p.equipment['main'].name, 'Spear')
        with self.assertRaises(ValueError):
            self.p.unequip('main')
        self.assertEqual(self.p.equipment['main'].name, 'Spear')

    def test_two_handed_restrictions_are_atomic(self):
        self.p.equipment['main'] = Item('Zweihander')
        self.p.inventory = [Item('Torch'), Item('Shield')]
        before = asdict(self.p)
        with self.assertRaises(ValueError):
            self.g.use(0)
        with self.assertRaises(ValueError):
            self.p.equip(1)
        self.assertEqual(before, asdict(self.p))
        self.p.equipment['main'] = Item('Dagger')
        self.p.equip(1)
        self.p.inventory.append(Item('Zweihander'))
        with self.assertRaises(ValueError):
            self.p.equip(1)

    def test_torch_hand_duration_and_description(self):
        self.room()
        self.p.equipment['main'] = Item('Spear')
        self.g.use(0)
        self.assertEqual(self.g.light, 'Bright')
        self.assertIsNotNone(self.p.equipment['off'])
        self.g.advance(14)
        self.assertEqual(self.g.light, 'Steady')
        self.g.advance(20)
        self.assertEqual(self.g.light, 'Dim')
        self.g.advance(15)
        self.assertEqual(self.g.light, 'Guttering')
        self.g.advance(10)
        self.assertEqual(self.g.light, 'Darkness')
        self.assertIsNone(self.p.equipment['off'])

    def test_unequipped_lit_torch_still_burns(self):
        self.room()
        self.p.equipment['main'] = Item('Dagger')
        self.g.use(0)
        self.g.unequip('off')
        self.assertTrue(self.g.darkness)
        self.g.advance(60)
        self.assertFalse(any(i.burn for i in self.p.all_items()))
        self.assertEqual(sum(i.name == 'Torch' for i in self.p.inventory), 2)

    def test_torch_and_shield_can_fill_two_free_hands(self):
        self.room()
        self.p.equipment['main'] = None
        self.p.equipment['off'] = Item('Shield')
        self.p.inventory = [Item('Torch')]
        self.g.use(0)
        self.assertEqual(self.p.equipment['main'].name, 'Torch')
        self.assertEqual(self.p.equipment['off'].name, 'Shield')
        self.assertIsNotNone(self.g.torch)

    def test_venom_stays_on_coated_weapon_when_swapped(self):
        self.p.equipment['main'] = Item('Dagger')
        self.p.inventory = [Item('Spider Venom'), Item('Mace')]
        self.g.use(0)
        self.g.equip(1)
        self.assertFalse(self.p.equipment['main'].venom)
        self.assertTrue(self.p.inventory[-1].venom)

    def test_bound_action_is_enforced_without_terminal(self):
        self.room(['Giant Spider'])
        self.p.bound = True
        with patch.object(self.g, 'enemy_turn') as enemies, patch.object(self.g, 'attack_damage') as attack:
            self.g.attack()
            enemies.assert_called_once()
            attack.assert_not_called()
        self.assertFalse(self.p.bound)

    def test_final_armor_table(self):
        self.assertEqual(D.ARMOR['Mail Hauberk'], (1, 6, 0))
        self.assertEqual(D.ARMOR['Brigandine Cuirass'], (1, 6, 1))
        for condition, expected in [('Normal', 4), ('Worn', 4), ('Ragged', 3), ('Ruined', 0)]:
            self.p.equipment['body'] = Item('Padded Jack', condition)
            with patch('vale.engine.dice', return_value=(4, True)):
                self.assertEqual(self.g.armor(), expected)

    def test_hit_chance_spear_bat_darkness_status(self):
        monster = spawn(self.g.rng, 'Cave Bat')
        self.p.cunning = 4
        self.p.equipment['main'] = Item('Spear')
        self.assertEqual(self.g.hit_chance(monster), 45)
        self.room()
        self.assertEqual(self.g.hit_chance(monster), 25)
        self.g.effect('Bless')
        self.assertEqual(self.g.hit_chance(monster), 35)
        self.g.poison()
        self.assertEqual(self.g.hit_chance(monster), 25)
        self.p.groggy = True
        self.assertEqual(self.g.hit_chance(monster), 5)

    def test_dagger_maximum_adds_cunning_and_might(self):
        self.p.might, self.p.cunning = 5, 5
        self.p.equipment['main'] = Item('Dagger')
        m = spawn(self.g.rng, 'Ogre')
        with patch('vale.engine.dice', side_effect=[(4, True), (0, False)]):
            self.assertEqual(self.g.attack_damage(m), 9)
        with patch('vale.engine.dice', side_effect=[(3, False), (0, False)]):
            self.assertEqual(self.g.attack_damage(m), 6)

    def test_mace_reduces_armor(self):
        self.p.might = 2
        self.p.equipment['main'] = Item('Mace')
        with patch('vale.engine.dice', side_effect=[(4, True), (5, False)]):
            self.assertEqual(self.g.attack_damage(spawn(self.g.rng, 'Skeleton')), 1)

    def test_zombie_headshot_only_natural_maximum(self):
        self.p.might = 2
        self.p.equipment['main'] = Item('Dagger')
        m = spawn(self.g.rng, 'Zombie')
        with patch('vale.engine.dice', side_effect=[(4, True), (0, False)]):
            self.assertGreaterEqual(self.g.attack_damage(m), 7)
        with patch('vale.engine.dice', side_effect=[(3, False), (0, False)]):
            self.assertEqual(self.g.attack_damage(m), 4)

    def test_multi_die_maximum_requires_all_dice_max(self):
        rng = random.Random(4)
        for _ in range(100):
            value, maximum = dice(rng, (2, 6, 1))
            self.assertEqual(maximum, value == 13)

    def test_overkill_carries_and_dead_enemies_do_not_act(self):
        self.room(['Giant Rat', 'Giant Rat', 'Giant Rat'])
        self.p.equipment['main'] = Item('Arming Sword')
        self.g.room.monsters[0].hp = 2
        with patch('vale.engine.chance', return_value=True), patch.object(self.g, 'attack_damage', return_value=8), patch.object(self.g, 'enemy_turn') as enemies:
            self.g.attack()
            enemies.assert_called_once()
        self.assertEqual([m.hp for m in self.g.room.monsters], [-6, -1, 4])
        self.assertEqual(len(self.g.enemies), 1)
        self.assertEqual(self.p.xp, 4)
        self.g.resolve_deaths()
        self.assertEqual(self.p.xp, 4)

    def test_each_surviving_enemy_acts_once(self):
        self.room(['Giant Rat', 'Giant Rat', 'Giant Rat'])
        with patch('vale.engine.chance', return_value=True), patch('vale.engine.dice', return_value=(1, False)):
            hp = self.p.hp
            self.g.enemy_turn()
            self.assertEqual(self.p.hp, hp - 3)

    def test_shield_negates_spider_poison(self):
        self.room(['Giant Spider'])
        self.g.enemies[0].web_used = True
        self.p.equipment['off'] = Item('Shield')
        hp = self.p.hp
        with patch('vale.engine.chance', return_value=True):
            self.g.enemy_turn(lambda *_: True)
        self.assertEqual(self.p.hp, hp)
        self.assertIsNone(self.p.equipment['off'])
        self.assertNotIn('Poison', self.p.effects)

    def test_zero_penetration_prevents_poison(self):
        self.room(['Giant Spider'])
        self.g.enemies[0].web_used = True
        with patch('vale.engine.chance', return_value=True), patch('vale.engine.dice', return_value=(4, True)), patch.object(self.g, 'armor', return_value=10):
            self.g.enemy_turn()
        self.assertNotIn('Poison', self.p.effects)

    def test_web_used_once_and_loses_one_action(self):
        self.room(['Giant Spider'])
        with patch('vale.engine.chance', return_value=True):
            self.g.enemy_turn()
        self.assertTrue(self.p.bound)
        self.assertTrue(self.g.enemies[0].web_used)
        with patch.object(self.g, 'enemy_turn') as enemy:
            self.assertTrue(self.g.skip_bound())
            enemy.assert_called_once()
            self.assertFalse(self.g.skip_bound())

    def test_goblin_flee_attempt_costs_its_turn(self):
        self.room(['Goblin'])
        self.g.enemies[0].hp = 2
        hp = self.p.hp
        with patch('vale.engine.chance', return_value=False):
            self.g.enemy_turn()
        self.assertEqual(hp, self.p.hp)
        with patch('vale.engine.chance', return_value=True):
            self.g.enemy_turn()
        self.assertFalse(self.g.combat)
        self.assertEqual(self.p.xp, 0)

    def test_flee_preserves_enemy_damage_and_room(self):
        self.room(['Giant Rat'])
        self.g.state.rooms[1] = Room(1, 1, 'Test', 'Another room.')
        self.g.state.previous = 1
        rat = self.g.enemies[0]
        rat.hp = 2
        with patch('vale.engine.chance', return_value=True):
            self.assertTrue(self.g.flee())
        self.assertEqual(self.g.state.current, 1)
        self.assertEqual(self.g.state.rooms[0].monsters[0].hp, 2)

    def test_flee_failure_runs_enemy_turn(self):
        self.room(['Giant Rat'])
        with patch('vale.engine.chance', return_value=False), patch.object(self.g, 'enemy_turn') as enemies:
            self.assertFalse(self.g.flee())
            enemies.assert_called_once()

    def test_daylight_troll_death_no_loot(self):
        room = self.room(['Troll'], daylight=True)
        self.g.arrive()
        self.assertFalse(self.g.combat)
        self.assertTrue(room.monsters[0].petrified)
        self.assertEqual(room.loot, [])
        self.assertEqual(self.p.xp, 5)

    def test_lure_troll_into_daylight(self):
        room = self.room(['Troll'])
        self.g.state.rooms[1] = Room(1, 1, 'Decrepit Vault', 'Sunlight.', daylight=True)
        self.g.state.previous = 1
        with patch('vale.engine.chance', return_value=True):
            self.g.flee()
        self.assertEqual(room.monsters, [])
        self.assertTrue(self.g.room.monsters[0].petrified)
        self.assertEqual(self.g.room.loot, [])

    def test_troll_regeneration_and_fire_suppression(self):
        self.room(['Troll'])
        troll = self.g.enemies[0]
        troll.hp = 5
        with patch('vale.engine.chance', return_value=False), patch('vale.engine.dice', return_value=(2, False)):
            self.g.enemy_turn()
            self.assertEqual(troll.hp, 7)
            self.g.cast_scroll('Ember', troll)
            hp = troll.hp
            self.g.enemy_turn()
            self.assertEqual(troll.hp, hp)
            self.assertTrue(troll.suppressed)

    def test_oil_fire_and_no_oil_damage(self):
        self.room(['Troll'])
        troll = self.g.enemies[0]
        self.p.inventory = [Item('Oil'), Item('Scroll', spell='Ember')]
        with patch.object(self.g, 'finish_turn'):
            self.g.use(0)
            self.assertEqual(troll.hp, 12)
            self.assertTrue(troll.flammable)
            self.g.use(0)
            self.assertTrue(troll.burning)
            self.assertTrue(troll.suppressed)

    def test_scroll_no_minimum_magic_or_hit_roll(self):
        self.room(['Ogre'])
        self.p.magic = 1
        self.p.inventory = [Item('Scroll', spell='Acid')]
        with patch('vale.engine.chance', return_value=False), patch.object(self.g, 'enemy_turn'):
            self.g.use(0)
        self.assertLess(self.g.enemies[0].hp, 18)
        self.assertEqual(self.p.inventory, [])

    def test_venom_bottle_reuse_and_next_successful_hit(self):
        self.room()
        self.g.room.harvest = ['Giant Spider']
        self.p.inventory = [Item('Empty Bottle')]
        self.g.harvest(0)
        self.assertEqual(self.p.inventory[0].name, 'Spider Venom')
        self.g.use(0)
        self.assertEqual(self.p.inventory[0].name, 'Empty Bottle')
        self.assertTrue(self.p.equipment['main'].venom)
        self.g.room.monsters.append(spawn(self.g.rng, 'Ogre'))
        with patch('vale.engine.chance', return_value=False), patch.object(self.g, 'enemy_turn'):
            self.g.attack()
        self.assertTrue(self.p.equipment['main'].venom)
        with patch('vale.engine.chance', return_value=True), patch.object(self.g, 'enemy_turn'):
            self.g.attack()
        self.assertFalse(self.p.equipment['main'].venom)

    def test_poison_duration_tick_and_modifiers(self):
        self.p.might = 5
        self.p.base_hp = self.p.hp = 100
        now = self.g.state.minute
        self.g.poison()
        self.assertEqual(self.p.effects['Poison'], now + 420)
        self.assertEqual(self.g.modifiers(), (-10, .9))
        self.g.advance(59)
        self.assertEqual(self.p.hp, 100)
        self.g.advance(1)
        self.assertEqual(self.p.hp, 99)
        self.g.advance(360)
        self.assertEqual(self.p.hp, 93)
        self.assertNotIn('Poison', self.p.effects)

    def test_poison_can_kill_during_rest(self):
        self.p.hp = 1
        self.p.silver = 10
        self.g.poison()
        self.g.inn()
        self.assertTrue(self.p.dead)
        self.assertEqual(self.p.cause, 'Poison')
        self.assertEqual(len(self.storage.graves()), 1)

    def test_rest_does_not_cure_poison(self):
        self.p.might = 2
        self.p.base_hp = self.p.hp = 100
        self.p.silver = 10
        self.g.poison()
        self.g.inn()
        self.assertIn('Poison', self.p.effects)
        self.assertEqual(self.p.hp, 100)

    def test_rest_interrupted_has_no_recovery_and_groggy(self):
        self.room()
        self.p.hp = 1
        with patch('vale.engine.chance', return_value=True):
            self.g.rest()
        self.assertEqual(self.p.hp, 1)
        self.assertTrue(self.p.groggy)
        self.assertTrue(self.g.combat)
        self.g.enemies[0].hp = 0
        self.g.resolve_deaths()
        self.assertFalse(self.p.groggy)

    def test_meal_bless_curse_expire(self):
        self.p.base_hp = 20
        self.p.silver = 20
        self.g.inn(meal=True)
        self.assertEqual(self.p.max_hp(self.g.state.minute), 21)
        self.p.gain_xp(100, self.g.state.minute)
        self.assertEqual(self.p.xp, 103)
        self.g.effect('Bless')
        self.g.effect('Curse')
        self.assertEqual(self.g.modifiers(), (0, 1))
        self.g.advance(1440)
        self.assertEqual(self.p.max_hp(self.g.state.minute), 20)
        self.assertEqual(self.p.effects, {})

    def test_antidote_consumed_on_failure(self):
        self.p.inventory = [Item('Antidote')]
        self.g.poison()
        with patch('vale.engine.chance', return_value=False):
            self.g.use(0)
        self.assertIn('Poison', self.p.effects)
        self.assertEqual(self.p.inventory, [])

    def test_extraction_once_and_no_spoils_or_imported_xp(self):
        self.room(daylight=True)
        self.p.inventory = [Item('Golden Idol', found=True), Item('Silver Goblet'), Item('Rat Pelt', found=True)]
        self.g.return_to_vale()
        self.assertEqual(self.p.fortune, 35)
        self.assertEqual(self.p.xp, 35)
        self.assertEqual(self.p.silver, 0)
        self.room(daylight=True)
        self.g.return_to_vale()
        self.assertEqual(self.p.fortune, 35)
        self.g.sell(0)
        self.assertGreater(self.p.silver, 0)
        self.assertEqual(self.p.fortune, 35)
        self.p.silver += 100  # Buy back at the merchant's higher asking price.
        self.g.buy(len(self.g.state.stock) - 1)
        self.room(daylight=True)
        self.g.return_to_vale()
        self.assertEqual(self.p.fortune, 35)

    def test_flee_from_entry_extracts_treasure(self):
        self.room(['Giant Rat'])
        self.p.inventory = [Item('Golden Idol', found=True)]
        with patch('vale.engine.chance', return_value=True):
            self.g.flee()
        self.assertEqual(self.g.state.location, 'Vale')
        self.assertEqual(self.p.fortune, 35)

    def test_level_thresholds_rewards_and_attribute_cap(self):
        self.p.gain_xp(99, self.g.state.minute)
        self.assertEqual(self.p.level, 1)
        self.p.gain_xp(1401, self.g.state.minute)
        self.assertEqual(self.p.level, 6)
        self.assertEqual(self.p.rewards, 5)
        self.p.might = 5
        hp = self.p.base_hp
        self.p.reward('HP')
        self.assertEqual(self.p.base_hp, hp + 5)
        self.p.reward('might')
        self.assertEqual(self.p.might, 6)
        # Increasing Might does not retrospectively award the separate HP reward.
        self.assertEqual(self.p.base_hp, hp + 5)

    def test_unidentified_cursed_equipment_and_cure(self):
        self.p.inventory = [Item('Mace', magic='Curse', identified=False)]
        self.p.equip(0)
        self.assertIn('Unidentified', self.p.equipment['main'].label)
        self.assertEqual(self.g.modifiers(), (-10, .9))
        self.p.silver = 5
        self.g.shrine('Cure Afflictions')
        self.assertEqual(self.g.modifiers(), (0, 1))

    def test_identification_and_price_cunning(self):
        self.p.inventory = [Item('Mace', magic='Bless', identified=False)]
        self.p.silver = 5
        self.g.shrine('Identification', 0)
        self.assertTrue(self.p.inventory[0].identified)
        item = Item('Brigandine Cuirass')
        self.p.cunning = 2
        low_buy, low_sell = self.g.price(item), self.g.price(item, False)
        self.p.cunning = 5
        self.assertLess(self.g.price(item), low_buy)
        self.assertGreater(self.g.price(item, False), low_sell)

    def test_stock_is_limited_and_refreshes_at_seven_days(self):
        self.p.silver = 100
        before = len(self.g.state.stock)
        self.g.buy(0)
        self.assertEqual(len(self.g.state.stock), before - 1)
        self.g.advance(7 * 1440 - self.g.state.minute - 1)
        self.assertEqual(len(self.g.state.stock), before - 1)
        self.g.advance(1)
        self.assertEqual(len(self.g.state.stock), before)

    def test_rumor_once_per_day(self):
        self.g.rumor()
        self.g.messages.clear()
        self.g.rumor()
        self.assertIn('nothing new', self.g.messages[-1])
        self.g.advance(1440)
        self.g.messages.clear()
        self.g.rumor()
        self.assertIn('An adventurer', self.g.messages[-1])

    def test_pick_break_boundary(self):
        element = Element('Locked Chest', difficulty=20)
        self.p.cunning = 5  # 40% success
        self.p.inventory = [Item('Pick')]
        with patch.object(self.g.rng, 'random', return_value=.49):
            self.assertFalse(self.g.pick_lock(element))
        self.assertEqual(len(self.p.inventory), 1)
        with patch.object(self.g.rng, 'random', return_value=.50):
            self.assertFalse(self.g.pick_lock(element))
        self.assertEqual(self.p.inventory, [])

    def test_rope_shaft_and_secret_door(self):
        self.room(daylight=True)
        self.g.room.elements = [Element('Deep Shaft')]
        self.p.inventory = []
        with self.assertRaises(ValueError):
            self.g.interact(0)
        self.p.inventory = [Item('Rope')]
        self.g.interact(0)
        self.assertEqual(self.g.room.exits[-1].depth_change, 1)
        self.g.room.hidden = 'Secret Door'
        self.g.reveal()
        self.assertTrue(self.g.room.exits[-1].secret)
        with patch('vale.dungeon.contents', return_value=['Empty']), patch('vale.dungeon.chance', return_value=False):
            self.g.move(len(self.g.room.exits) - 1)
        self.assertTrue(self.g.room.secret)

    def test_features_cannot_be_farmed(self):
        self.room(daylight=True)
        self.g.room.elements = [Element('Iron Spike')]
        with patch('vale.engine.weighted', return_value='Treasure'):
            self.g.interact(0)
        self.assertEqual(len(self.g.room.loot), 1)
        with self.assertRaises(ValueError):
            self.g.interact(0)

    def test_trap_detection_and_damage(self):
        self.room(daylight=True)
        self.g.room.traps = [Element('Spike Trap')]
        with patch('vale.engine.chance', return_value=True):
            self.g.arrive()
        trap = self.g.room.traps[0]
        self.assertTrue(trap.detected)
        self.assertFalse(trap.done)
        with patch('vale.engine.chance', return_value=False), patch('vale.engine.dice', return_value=(6, True)), patch.object(self.g, 'armor', return_value=4):
            hp = self.p.hp
            self.g.disarm(0)
            self.assertEqual(self.p.hp, hp - 2)
        self.assertTrue(trap.done)

    def test_return_blocked_by_monsters(self):
        self.room(['Giant Rat'])
        with self.assertRaises(ValueError):
            self.g.return_to_vale()
        with self.assertRaises(ValueError):
            self.g.search()

    def test_death_record_idempotent_ranking_and_permadeath(self):
        self.p.fortune = 42
        self.p.deepest = 3
        self.g.save()
        self.g.die('A test trap')
        self.g.save()
        self.assertFalse(self.storage.save_path.exists())
        graves = self.storage.graves()
        self.assertEqual(len(graves), 1)
        self.assertEqual(graves[0]['fortune'], 42)
        self.assertEqual(graves[0]['cause'], 'A test trap')
        living = Game(1, self.storage)
        living.p.fortune = 100
        self.assertFalse(self.storage.leaderboard(living.state)[0]['dead'])
        # Even restoring a copied save cannot resurrect a recorded dead character.
        self.p.dead = False
        self.storage.save(self.g.state, self.g.rng)
        with self.assertRaises(ValueError):
            self.storage.load()

    def test_save_load_preserves_expedition_and_rng(self):
        self.room(['Ooze', 'Goblin'])
        self.g.room.monsters[0].hp = 2
        self.g.room.loot = [Item('Golden Idol', found=True)]
        self.g.room.hidden = 'Cache'
        self.g.room.elements = [Element('Pale Book')]
        self.p.effects = {'Bless': self.g.state.minute + 1440}
        self.g.save()
        state, rng_state = self.storage.load()
        loaded = Game(storage=self.storage, state=state, random_state=rng_state)
        self.assertEqual(asdict(self.g.state), asdict(loaded.state))
        self.assertEqual(self.g.rng.random(), loaded.rng.random())

    def test_expedition_regeneration_and_backtracking(self):
        with patch('vale.dungeon.contents', return_value=['Empty']), patch('vale.dungeon.chance', return_value=False):
            self.g.enter()
            first = self.g.room
            self.g.move(0)
            second = self.g.room
            xp = self.p.xp
            self.g.move(0)
            self.assertIs(self.g.room, first)
            self.assertEqual(self.p.xp, xp)
            self.g.return_to_vale()
            self.g.enter()
            self.assertIsNot(self.g.room, first)
            self.assertEqual(len(self.g.state.rooms), 1)
            self.assertEqual(second.exits[0].target, 0)

    def test_smoke_expedition_sell_recover_save_load_and_death(self):
        self.p.equipment['main'] = Item('Spear')
        self.g.use(0)
        with patch('vale.dungeon.contents', return_value=['Treasure']), patch('vale.dungeon.chance', return_value=False):
            self.g.enter()
        self.g.take(0)
        self.g.return_to_vale()
        self.assertGreater(self.p.fortune, 0)
        # Supply enough money to visit every paid destination in the fixture.
        self.p.silver += 100
        self.g.sell(len(self.p.inventory) - 1)
        self.g.buy(0)
        self.g.drink()
        self.g.rumor()
        self.g.shrine('Healing')
        self.g.shrine('Blessing')
        self.g.inn(meal=True)
        self.g.inn()
        self.g.save()
        self.assertEqual(self.storage.load()[0].player.fortune, self.p.fortune)
        self.g.die('Smoke test concluded')
        self.assertEqual(self.storage.leaderboard()[0]['cause'], 'Smoke test concluded')


class GenerationTests(unittest.TestCase):
    def test_normal_and_secret_exact_boundaries(self):
        for secret, weights in [(False, D.NORMAL_CONTENT), (True, D.SECRET_CONTENT)]:
            offset = 0
            for kind, weight in zip(D.CONTENT_KINDS[:-1], weights[:-1]):
                for roll in (offset + 1, offset + weight):
                    with patch.object(random.Random, 'randint', return_value=roll):
                        self.assertEqual(contents(random.Random(), secret), [kind])
                offset += weight

    def test_roll_twice_rerolls_nested_twice_and_allows_duplicates(self):
        rng = random.Random()
        with patch.object(rng, 'randint', side_effect=[100, 100, 1, 100, 1]):
            self.assertEqual(contents(rng), ['Empty', 'Empty'])

    def test_distribution_matches_tables(self):
        rng = random.Random(188)
        for secret, weights in [(False, D.NORMAL_CONTENT), (True, D.SECRET_CONTENT)]:
            # Test first rolls to distinguish Roll Twice from its resolved contents.
            counts = Counter(weighted(rng, D.CONTENT_KINDS, weights) for _ in range(30000))
            for name, percent in zip(D.CONTENT_KINDS, weights):
                self.assertAlmostEqual(counts[name] / 300, percent, delta=1.0)
        monsters = Counter()
        for _ in range(30000):
            name = spawn(rng).name
            monsters[next(k for k, names in D.THREATS.items() if name in names)] += 1
        for name, percent in zip(D.THREATS, D.THREAT_WEIGHTS):
            self.assertAlmostEqual(monsters[name] / 300, percent, delta=1.0)
        loot = Counter(treasure(rng).name for _ in range(30000))
        for name, percent in zip(D.TREASURES, D.TREASURE_WEIGHTS):
            self.assertAlmostEqual(loot[name] / 300, percent, delta=1.0)

    def test_rooms_templates_hidden_exits_and_darkness(self):
        lit_rng, dark_rng = random.Random(25), random.Random(25)
        normal = [generate(lit_rng, i, 1) for i in range(5000)]
        dark = [generate(dark_rng, i, 1, darkness=True) for i in range(5000)]
        self.assertEqual(len({r.template for r in normal}), 13)
        self.assertTrue(all(1 <= len(r.exits) <= 4 for r in normal))
        self.assertAlmostEqual(sum(bool(r.hidden) for r in normal) / 50, 10, delta=2)
        self.assertGreater(sum(len(r.monsters) for r in dark), sum(len(r.monsters) for r in normal))
        for room in normal:
            if room.daylight:
                self.assertEqual(room.template, 'Decrepit Vault')
        cavern = next(r for r in normal if r.template == 'Natural Cavern')
        self.assertNotIn('torchlight', describe(cavern, False))
        self.assertIn('torchlight', describe(cavern, True))


if __name__ == '__main__':
    unittest.main()
