"""Atomic, versioned JSON saves; no executable pickle data."""
import json
import os
from pathlib import Path
from dataclasses import asdict
from .models import state_from_dict

VERSION = 1


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


class Storage:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.save_path = self.directory / 'save.json'
        self.graves_path = self.directory / 'graveyard.json'

    def save(self, state, rng):
        if state.player.dead:
            self.record_death(state)
            return
        write_json(self.save_path, {'version': VERSION, 'state': asdict(state), 'random': rng.getstate()})

    def load(self):
        with self.save_path.open(encoding='utf-8') as handle:
            raw = json.load(handle)
        if raw.get('version') != VERSION:
            raise ValueError('This save uses an unsupported version.')
        state = state_from_dict(raw['state'])
        if state.player.dead or any(g['id'] == state.id for g in self.graves()):
            raise ValueError('This adventurer is dead and cannot be loaded.')
        def tuples(value):
            return tuple(tuples(x) for x in value) if isinstance(value, list) else value
        return state, tuples(raw['random'])

    def graves(self):
        if not self.graves_path.exists():
            return []
        with self.graves_path.open(encoding='utf-8') as handle:
            raw = json.load(handle)
        if not isinstance(raw, list):
            raise ValueError('The Graveyard file is not a list of records.')
        return raw

    def record_death(self, state):
        p = state.player
        records = self.graves()
        if not any(g['id'] == state.id for g in records):
            records.append({'id': state.id, 'name': p.name, 'fortune': p.fortune,
                            'depth': p.deepest, 'days': state.day, 'cause': p.cause})
            write_json(self.graves_path, records)
        # Persist the tombstone before invalidating the save, including after a crash.
        if self.save_path.exists():
            with self.save_path.open(encoding='utf-8') as handle:
                saved = json.load(handle)
            if saved.get('state', {}).get('id') == state.id:
                self.save_path.unlink()

    def leaderboard(self, state=None):
        records = [dict(g, dead=True) for g in self.graves()]
        if state and not state.player.dead:
            p = state.player
            records.append({'id': state.id, 'name': p.name, 'fortune': p.fortune,
                            'depth': p.deepest, 'days': state.day, 'cause': 'Still living', 'dead': False})
        return sorted(records, key=lambda g: (-g['fortune'], -g['depth'], g['name']))
