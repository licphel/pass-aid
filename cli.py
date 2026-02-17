import argparse
import sys
import core
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="pass-aid",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', '-v', action='store_true', help="Display version info")
    parser.add_argument('--db', '-d', type=str, help="Set database path")
    
    subparsers = parser.add_subparsers(dest='command', help='Ready commands')
    
    # insert
    insert_parser = subparsers.add_parser('add', aliases=['a'], help="Add or update a user")
    insert_parser.add_argument('--site', '-s', required=True, help="Site name (only accept letters and underscore)")
    insert_parser.add_argument('--username', '-u', required=True, help="Your username")
    insert_parser.add_argument('--password', '-p', required=True, help="Your password")
    
    # fuzzy search
    search_parser = subparsers.add_parser('fuzzy', aliases=['f'], help="Search a site fuzzily")
    search_parser.add_argument('--keyword', '-k', required=True, help="Site keyword")
    
    # list
    list_parser = subparsers.add_parser('list', aliases=['l'], help="List all registered sites")
    list_parser.add_argument('--expand', '-e', action='store_true', help="List out users in sites, not merely user counts")
   
    # delete
    delete_parser = subparsers.add_parser('delete', aliases=['d'], help="Delete a site")
    delete_parser.add_argument('--site', '-s', required=True, help="The site name to delete")
    delete_parser.add_argument('--username', '-u', help="Target user. If not specified, delete the whole site")
    
    # clear
    subparsers.add_parser('clear', aliases=['c'], help="(Dangerous) Clear all data in the database")

    # info
    subparsers.add_parser('info', aliases=['i'], help="Display database info")
    
    return parser.parse_args()

def handle_add(args):
    core.insert_suk(args.site, args.username, args.password)

def handle_search(args):
    results = core.match_suk(args.keyword)
    
    if not results:
        core.warnw(f"no result relative to '{args.keyword}'")
        return
    
    current_site = None
    for table, key, value in results:
        if table != current_site:
            current_site = table
            core.acptw(f"\n[{table}]")
        core.acptw(f"  username: {key}")
        core.acptw(f"  password: {value}")
        core.acptw()

def handle_list(args):
    try:
        conn = core.sqlite3.connect(str(core.DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            conn.close()
            core.warnw("empty data")
            return
        
        core.acptw(f"{len(tables)} sites found\n")
        
        for table in tables:
            site = table[0]
            
            if args.expand:
                cursor.execute(f"SELECT key, value FROM {site}")
                users = cursor.fetchall()
                core.acptw(f"  {site} ({len(users)} users)")
                for key, value in users:
                    core.acptw(f"    username: {key}")
                    core.acptw(f"    password: {value}")
                    core.acptw()
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {site}")
                count = cursor.fetchone()[0]
                core.acptw(f"  {site} ({count} users)")
        
        conn.close()
            
    except Exception as e:
        core.errw(f"fail to list sites: {e}")

def handle_delete(args):
    try:
        conn = core.sqlite3.connect(str(core.DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (args.site,))
        if not cursor.fetchone():
            conn.close()
            core.acptw(f"delete operation failed: no site named '{args.site}'")
            return
        
        if args.username:
            cursor.execute(f"DELETE FROM {args.site} WHERE key=?", (args.username,))
            if cursor.rowcount > 0:
                core.acptw(f"delete operation succeeds: '{args.username}' in site '{args.site}'")
            else:
                core.warnw(f"delete operation failed: no '{args.username}' in site '{args.site}'")
        else:
            cursor.execute(f"DROP TABLE {args.site}")
            core.acptw(f"whole site '{args.site}' removed")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        core.errw(f"error at deleting: {e}")

def handle_clear(args):
    core.clear()

def handle_info(args):
    core.printinfo()

def main():
    args = parse_args()
    
    if args.version:
        core.printver()
        return
    
    if hasattr(args, 'db') and args.db:
        core.set_path(Path(args.db))
    
    if not args.command:
        core.errw("null command. please use passaid -h (or --help) for help")
        sys.exit(1)

    try:
        if args.command in ['add', 'a']:
            handle_add(args)
        elif args.command in ['fuzzy', 'f']:
            handle_search(args)
        elif args.command in ['list', 'l']:
            handle_list(args)
        elif args.command in ['delete', 'd']:
            handle_delete(args)
        elif args.command in ['clear', 'c']:
            handle_clear(args)
        elif args.command in ['info', 'i']:
            handle_info(args)
        else:
            core.errw(f"unknown command: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        core.errw("\noperation cancelled")
        sys.exit(1)
    except Exception as e:
        core.errw(f"error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()