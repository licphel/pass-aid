# Pass-aid

A command-line password manager for personal offline use.

## Quick start

### Clone the repository

```bash
git clone https://github.com/licphel/pass-aid.git
cd pass-aid
pip install -e .
```

### Launch

```bash
python cli.py [command]
```

Or packed with pyinstaller and add to env variables:

```bash
pip install pyinstaller
pyinstaller --onefile --name passaid cli.py
# (After setting env variables)
passaid ...
```

## Tutorial

### Basic

```bash
passaid -h, --help      # Display help messages
passaid -v, --version   # Display version
passaid -d PATH, --db PATH  # Specify database location
```

### Command list

| Command | Abbreviation | Function |
|------|------|------|
| `add` | `a` | Add/update password |
| `fuzzy` | `f` | Fuzzy search |
| `list` | `l` | List all |
| `delete` | `d` | Delete sites/user |
| `clear` | `c` | Clear all data |
| `info` | `i` | Display database info |

### Examples

```bash
# Add a user
passaid add --site google --username user@gmail.com --password 123456

# Add a user (shortened)
passaid a -s github -u myname -p 123456

# Update a user
passaid a -s google -u user@gmail.com -p New_123456
```

```bash
# Fuzzy search sites about 'msg'
passaid fuzzy --keyword msg

# Fuzzy search (shortened)
passaid f -k msg

# A possible output
site matched: google.
site matched: microsoft.

[microsoft]
  username: user@outlook.com
  password: 123456

[google]
  username: user@gmail.com
  password: 123456

  username: user@outlook.com
  password: 123456
```

```bash
# List all sites
passaid list

# List all sites and all users in them
passaid list --expand
# or simply
passaid list -e
```

```bash
# Delete a specified user
passaid delete --site github --username olduser

# Delete a site and all users in it
passaid delete --site github

# or simply
passaid d -s github -u olduser
```

```bash
# (Dangerous) Clear all data in current database
passaid clear
```

## Data storage

By default the database is at:
- **Windows**: `C:/Users/[username]/.pass-aid/object.db`
- **Linux/macOS**: `/home/[username]/.pass-aid/object.db`

You can also specify another path. The database will be automatically created once used.
```bash
passaid -d "D:/mydb.db" add ...
```
