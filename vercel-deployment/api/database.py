"""
SQLite Database for AOTR Run Statistics

Stores run history, drops, and special rewards for analytics and chart generation.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Use /tmp for SQLite in serverless environment
DB_PATH = '/tmp/aotr_stats.db'


def get_connection():
    """Get database connection and ensure tables exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn):
    """Create tables if they don't exist."""
    cursor = conn.cursor()

    # Runs table - stores each run's basic info
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user TEXT,
            level INTEGER,
            gold INTEGER,
            gems INTEGER,
            time_taken TEXT,
            time_seconds INTEGER,
            damage_dealt INTEGER,
            titan_kills INTEGER,
            critical_hits INTEGER,
            rewards_gold INTEGER,
            rewards_xp INTEGER,
            rewards_gems INTEGER
        )
    ''')

    # Drops table - stores each drop from a run
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            drop_type TEXT NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    ''')

    # Special rewards table - stores special rewards from a run
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS special_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            reward_name TEXT NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    ''')

    # Stats message table - stores the Discord message ID for editing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats_message (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            message_id TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    conn.commit()


def parse_aotr_payload(payload: Dict) -> Optional[Dict]:
    """
    Parse AOTR Discord webhook payload into structured data.

    Returns:
        Dict with parsed data, or None if parsing fails
    """
    try:
        if 'embeds' not in payload or not payload['embeds']:
            return None

        embed = payload['embeds'][0]
        fields = embed.get('fields', [])

        # Create a map of field names to values
        field_map = {}
        for field in fields:
            name = field.get('name', '').strip(':').strip()
            value = field.get('value', '')
            # Remove backticks and code blocks for parsing
            value = value.replace('```', '').replace('`', '').strip()
            field_map[name] = value

        # Parse User field
        user = field_map.get('User', 'Unknown')

        # Parse Totals field (Level, Gold, Gems)
        totals = field_map.get('Totals', '')
        level = None
        gold = None
        gems = None
        for line in totals.split('\n'):
            line = line.strip()
            if line.startswith('Level:'):
                level = int(line.split(':')[1].strip().replace(',', ''))
            elif line.startswith('Gold:'):
                gold = int(line.split(':')[1].strip().replace(',', ''))
            elif line.startswith('Gems:'):
                gems = int(line.split(':')[1].strip().replace(',', ''))

        # Parse Stats field (Time, Damage, Kills, Crits)
        stats = field_map.get('Stats', '')
        time_taken = None
        time_seconds = None
        damage_dealt = None
        titan_kills = None
        critical_hits = None
        for line in stats.split('\n'):
            line = line.strip()
            if 'Time Taken' in line:
                time_taken = line.split()[0]  # e.g., "01:47"
                # Convert to seconds
                parts = time_taken.split(':')
                time_seconds = int(parts[0]) * 60 + int(parts[1])
            elif 'Damage Dealt' in line:
                damage_dealt = int(line.split()[0].replace(',', ''))
            elif 'Titan Kills' in line:
                titan_kills = int(line.split()[0].replace(',', ''))
            elif 'Critical Hits' in line:
                critical_hits = int(line.split()[0].replace(',', ''))

        # Parse Rewards field (Gold, XP, Gems)
        rewards = field_map.get('Rewards', '')
        rewards_gold = None
        rewards_xp = None
        rewards_gems = None
        for line in rewards.split('\n'):
            line = line.strip()
            if line.endswith('Gold'):
                rewards_gold = int(line.split()[0].replace(',', ''))
            elif line.endswith('XP'):
                rewards_xp = int(line.split()[0].replace(',', ''))
            elif line.endswith('Gems'):
                rewards_gems = int(line.split()[0].replace(',', ''))

        # Parse Drops field
        drops_text = field_map.get('Drops', '')
        drops = []
        for line in drops_text.split('\n'):
            line = line.strip()
            if not line or line == 'None':
                continue
            # Determine rarity based on keywords
            line_lower = line.lower()
            if 'mythic' in line_lower:
                drops.append('mythic')
            elif 'legendary' in line_lower:
                drops.append('legendary')
            elif 'epic' in line_lower:
                drops.append('epic')
            elif 'rare' in line_lower:
                drops.append('rare')
            elif 'common' in line_lower:
                drops.append('common')
            # Ignore BP XP as per user request

        # Parse Special Rewards field
        special_text = field_map.get('Special Rewards', '')
        special_rewards = []
        for line in special_text.split('\n'):
            line = line.strip()
            if line and line != 'None':
                special_rewards.append(line)

        return {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'level': level,
            'gold': gold,
            'gems': gems,
            'time_taken': time_taken,
            'time_seconds': time_seconds,
            'damage_dealt': damage_dealt,
            'titan_kills': titan_kills,
            'critical_hits': critical_hits,
            'rewards_gold': rewards_gold,
            'rewards_xp': rewards_xp,
            'rewards_gems': rewards_gems,
            'drops': drops,
            'special_rewards': special_rewards
        }

    except Exception as e:
        print(f'Error parsing AOTR payload: {e}')
        import traceback
        print(traceback.format_exc())
        return None


def save_run(conn, run_data: Dict) -> int:
    """
    Save a run to the database.

    Returns:
        run_id of the inserted run
    """
    cursor = conn.cursor()

    # Insert run
    cursor.execute('''
        INSERT INTO runs (
            timestamp, user, level, gold, gems,
            time_taken, time_seconds, damage_dealt, titan_kills, critical_hits,
            rewards_gold, rewards_xp, rewards_gems
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        run_data['timestamp'],
        run_data['user'],
        run_data['level'],
        run_data['gold'],
        run_data['gems'],
        run_data['time_taken'],
        run_data['time_seconds'],
        run_data['damage_dealt'],
        run_data['titan_kills'],
        run_data['critical_hits'],
        run_data['rewards_gold'],
        run_data['rewards_xp'],
        run_data['rewards_gems']
    ))

    run_id = cursor.lastrowid

    # Insert drops
    for drop_type in run_data['drops']:
        cursor.execute('''
            INSERT INTO drops (run_id, drop_type)
            VALUES (?, ?)
        ''', (run_id, drop_type))

    # Insert special rewards
    for reward in run_data['special_rewards']:
        cursor.execute('''
            INSERT INTO special_rewards (run_id, reward_name)
            VALUES (?, ?)
        ''', (run_id, reward))

    conn.commit()
    return run_id


def get_drops_summary() -> Dict[str, int]:
    """Get all-time count of each drop type."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT drop_type, COUNT(*) as count
        FROM drops
        GROUP BY drop_type
    ''')

    result = {row['drop_type']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return result


def get_special_rewards_summary() -> Dict[str, int]:
    """Get all-time count of each special reward."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT reward_name, COUNT(*) as count
        FROM special_rewards
        GROUP BY reward_name
    ''')

    result = {row['reward_name']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return result


def get_last_n_runs(n: int = 50) -> List[Dict]:
    """Get the last N runs for time-series charts."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM runs
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (n,))

    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dicts and reverse to get chronological order
    result = [dict(row) for row in rows]
    result.reverse()
    return result


def get_stats_message_id() -> Optional[str]:
    """Get the stored stats message ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT message_id FROM stats_message WHERE id = 1')
    row = cursor.fetchone()
    conn.close()

    return row['message_id'] if row else None


def set_stats_message_id(message_id: str):
    """Store the stats message ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO stats_message (id, message_id, updated_at)
        VALUES (1, ?, ?)
    ''', (message_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def has_special_rewards(run_data: Dict) -> bool:
    """Check if a run has special rewards."""
    return bool(run_data.get('special_rewards'))
