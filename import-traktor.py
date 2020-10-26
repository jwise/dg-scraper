import sqlite3
from bs4 import BeautifulSoup
import sys

eventnames = [ "Vertigo", "Collapse", "Dark Sunday" ]

def migrate_v1(db):
    db.executescript('''
CREATE TABLE IF NOT EXISTS events
  (id INTEGER PRIMARY KEY NOT NULL,
   title TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dates
  (id INTEGER PRIMARY KEY NOT NULL,
   date TEXT NOT NULL,
   event INTEGER NOT NULL REFERENCES events(id) ON UPDATE CASCADE
   );
CREATE TABLE IF NOT EXISTS artists
  (id INTEGER PRIMARY KEY NOT NULL,
   artist TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS songs
  (id INTEGER PRIMARY KEY NOT NULL,
   artist INTEGER NOT NULL REFERENCES artists(id) ON UPDATE CASCADE,
   title TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS plays
  (id INTEGER PRIMARY KEY NOT NULL,
   date INTEGER NOT NULL REFERENCES dates(id) ON UPDATE CASCADE,
   playorder INTEGER NOT NULL,
   song INTEGER NOT NULL REFERENCES songs(id) ON UPDATE CASCADE);
PRAGMA user_version = 1;
''')
    c = db.cursor()
    for event in eventnames:
        c.execute('INSERT INTO events (title) VALUES (?);', (event, ))
    db.commit()

def migrate(db):
    current_version = db.cursor().execute('PRAGMA user_version').fetchone()[0]
    if current_version < 1: # null to 0 or 0 to 1 migration
        print("Migrating to version 1...")
        migrate_v1(db)

def file_to_tracklist(path):
    with open(path, 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, features = "html.parser")
    ents = [[td.get_text() for td in x.find_all("td")] for x in soup.find("table").find_all("tr")[1:]]
    # 2 is title
    # 3 is artist
    # 27 is play length
    return [ent[2:4] for ent in ents if int(ent[27][0:2]) > 0]

if len(sys.argv) < 5 or sys.argv[3] not in eventnames:
    print(f"Usage: {sys.argv[0]} DBFILE yyyy-mm-dd CLUBNAME TRAKTORFILE.html")
    print("")
    print(f"CLUBNAME can be: {eventnames}")
    sys.exit(1)

db = sqlite3.connect(sys.argv[1])
migrate(db)

c = db.cursor()

# Find the club.
c.execute('SELECT id FROM events WHERE title=?;', (sys.argv[3], ))
(eventid, ) = c.fetchone()

# Find a date entry for it -- and if one exists, bail.
c.execute('SELECT id FROM dates WHERE date=?;', (sys.argv[2], ))
if c.fetchone() is not None:
    print(f"date {sys.argv[2]} already exists in the database?")
    sys.exit(2)
c.execute('INSERT INTO dates (date, event) VALUES (?, ?);', (sys.argv[2], eventid, ))
c.execute('SELECT id FROM dates WHERE date=?;', (sys.argv[2], ))
(dateid, ) = c.fetchone()

tracks = file_to_tracklist(sys.argv[4])
for (i, val) in enumerate(tracks):
    # Look up an artist.
    c.execute('SELECT id FROM artists WHERE artist=?;', (val[1], ))
    ar = c.fetchone()
    if ar is None:
        c.execute('INSERT INTO artists (artist) VALUES (?);', (val[1], ))
        c.execute('SELECT id FROM artists WHERE artist=?;', (val[1], ))
        ar = c.fetchone()
    (ar, ) = ar
    
    c.execute('SELECT id FROM songs WHERE title=? AND artist=?;', (val[0], ar, ))
    so = c.fetchone()
    if so is None:
        c.execute('INSERT INTO songs (artist, title) VALUES (?, ?);', (ar, val[0], ))
        c.execute('SELECT id FROM songs WHERE title=? AND artist=?;', (val[0], ar, ))
        so = c.fetchone()
    (so, ) = so
    
    c.execute('INSERT INTO plays (date, playorder, song) VALUES (?, ?, ?);', (dateid, i + 1, so))

db.commit()
