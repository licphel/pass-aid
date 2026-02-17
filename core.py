import sqlite3
from pathlib import Path
import os
import re
import sys
from difflib import SequenceMatcher

EXT_PATH = Path(".pass-aid/object.db")
HOME_PATH = Path.home() / EXT_PATH
DB_PATH = HOME_PATH

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def errw(*args, **kwargs):
    print(f"{RED}{' '.join(map(str, args))}{RESET}", **kwargs, file=sys.stderr)

def acptw(*args, **kwargs):
    print(f"{GREEN}{' '.join(map(str, args))}{RESET}", **kwargs, file=sys.stdout)

def warnw(*args, **kwargs):
    print(f"{YELLOW}{' '.join(map(str, args))}{RESET}", **kwargs, file=sys.stderr)

def set_to_home_path():
    set_path(HOME_PATH)

def set_path(path):
    global DB_PATH
    DB_PATH = path / EXT_PATH

def match_suk(search_term):
    results = []
    
    try:
        db_dir = DB_PATH.parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        table_scores = []
        for table in tables:
            table_name = table[0]
            score = SequenceMatcher(None, search_term.lower(), table_name.lower()).ratio()
            if score > 0:
                table_scores.append((table_name, score))
        
        table_scores.sort(key=lambda x: x[1], reverse=True)
        
        for table_name, score in table_scores:
            acptw(f"site matched: {table_name}.")
            
            cursor.execute(f"SELECT key, value FROM {table_name} LIMIT 100")
            rows = cursor.fetchall()
            
            for key, value in rows:
                results.append((table_name, key, value))
        
        conn.close()
        
    except Exception as ex:
        errw(f"operation cancelled, error at searching: {ex}")
        return []
    
    return results

def insert_suk(site, key, value):
    if not bool(re.fullmatch(r'[a-zA-Z_]+', site)):
        errw(f"operation cancelled, error at inserting: only [a-zA-Z_] acceptable for '--site/-s', however got '{site}'.")
        return

    db_dir = DB_PATH.parent
        
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
    
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {site} (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
    
        cursor.execute(
            f"INSERT OR REPLACE INTO {site} (key, value) VALUES (?, ?)",
            (key, value)
        )
    
        conn.commit()
        conn.close()
        acptw(f"write operation succeeds: in '{site}', username = {key}, password = {value}.")
    except Exception as ex:
        errw(f"operation cancelled, error at inserting: {ex}")

def clear():
    if DB_PATH.exists():
        os.remove(DB_PATH)
        acptw("clear operation succeeds.")

def printinfo():
    acptw("database at: ", DB_PATH)

def printver():
    acptw("pass-aid 1.0")