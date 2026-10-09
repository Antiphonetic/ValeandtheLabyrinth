"""End-to-end terminal checks using the real launcher and saved JSON files."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TerminalTests(unittest.TestCase):
    def run_game(self, directory, commands):
        return subprocess.run(
            [sys.executable, str(ROOT / 'play.py'), '--seed', '1', '--data-dir', directory],
            input='\n'.join(map(str, commands)) + '\n', capture_output=True,
            text=True, encoding='utf-8', timeout=15, cwd=ROOT,
        )

    def test_terminal_expedition_and_all_vale_destinations(self):
        with tempfile.TemporaryDirectory() as directory:
            commands = [
                1, 2,            # New game; go to Vale.
                7, 3, 1, 5,      # Inventory; use first Torch; back.
                6, 5, 1, 2,      # Enter; collect Tin Cup; return.
                2, 2, 4, 3,      # Merchant; sell the Tin Cup; leave.
                1, 2, 3,         # Tavern; talk to adventurers; leave.
                3, 5,            # Shrine; leave (no treatment purchased).
                4, 3,            # Inn; leave (no room purchased).
                5, 1,            # Graveyard includes living adventurer; leave.
                8, 2, 8, 4,      # Save/quit; continue; save/quit; main quit.
            ]
            result = self.run_game(directory, commands)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertNotIn('Cannot complete', result.stdout)
            for expected in ('You take Tin Cup', 'You return to Vale', 'You sell Tin Cup',
                             'TAVERN', 'MERCHANT', 'SHRINE', 'INN', 'THE GRAVEYARD',
                             'Game saved.'):
                self.assertIn(expected, result.stdout)
            raw = json.loads((Path(directory) / 'save.json').read_text(encoding='utf-8'))
            self.assertEqual(raw['state']['location'], 'Vale')
            self.assertEqual(raw['state']['player']['fortune'], 1)
            self.assertGreater(raw['state']['player']['silver'], 0)
            self.assertFalse(raw['state']['player']['dead'])

    def test_main_menu_graveyard_without_character(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_game(directory, [3, 4])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('THE GRAVEYARD', result.stdout)
            self.assertNotIn('Traceback', result.stderr)

    def test_invalid_input_and_eof_save(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_game(directory, ['wrong', 0, 99, 1, 2])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Enter a number', result.stdout)
            self.assertIn('Game saved.', result.stdout)
            self.assertTrue((Path(directory) / 'save.json').exists())


if __name__ == '__main__':
    unittest.main()
