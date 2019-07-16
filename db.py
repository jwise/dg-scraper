import sqlite3
import scraper

def open(name):
  return sqlite3.connect(name)

def createtables_v0(db):
  db.executescript('''
CREATE TABLE IF NOT EXISTS dates
  (id INTEGER PRIMARY KEY NOT NULL,
   date TEXT NOT NULL,
   url TEXT NOT NULL,
   imported BIT);
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
   song INTEGER NOT NULL REFERENCES songs(id) ON UPDATE CASCADE,
   request BIT NOT NULL);
''')
  db.commit()

def migrate(db):
  current_version = db.cursor().execute('PRAGMA user_version').fetchone()[0]
  if current_version < 1: # null to 0 or 0 to 1 migration
    print "Migrating to version 1..."
    createtables_v0(db)
    db.executescript('''
ALTER TABLE dates ADD COLUMN lounge BIT;
UPDATE dates SET lounge=0;
PRAGMA user_version = 1;
''')
    db.commit()

def updurls(db):
  urls = scraper.get_tracklists()
  c = db.cursor()
  
  for date in urls:
    c.execute('SELECT * FROM dates WHERE date=?;', (date,))
    if c.fetchone() is None:
      print "Inserting %s" % date
      c.execute('INSERT INTO dates (date, url, imported, lounge) VALUES (?, ?, 0, 0);', (date, urls[date], ))
  db.commit()

def getone(db):
  c = db.cursor()
  
  c.execute('SELECT id, date, url, lounge FROM dates WHERE imported=0;')
  next = c.fetchone()
  if next is None:
    return False
  
  (id, date, url, lounge) = next
  if lounge:
    print "Skipping lounge from %s" % date
  print "Importing %s" % date
  
  try:
    trs = scraper.url_to_tracklist(url)
    for (i, val) in enumerate(trs):
      c.execute('SELECT id FROM artists WHERE artist=?;', (val['artist'], ))
      ar = c.fetchone()
      if ar is None:
        c.execute('INSERT INTO artists (artist) VALUES (?);', (val['artist'], ))
        c.execute('SELECT id FROM artists WHERE artist=?;', (val['artist'], ))
        ar = c.fetchone()
      (ar, ) = ar
      
      c.execute('SELECT id FROM songs WHERE title=? AND artist=?;', (val['title'], ar, ))
      so = c.fetchone()
      if so is None:
        c.execute('INSERT INTO songs (artist, title) VALUES (?, ?);', (ar, val['title'], ))
        c.execute('SELECT id FROM songs WHERE title=? AND artist=?;', (val['title'], ar, ))
        so = c.fetchone()
      (so, ) = so
      
      c.execute('INSERT INTO plays (date, playorder, song, request) VALUES (?, ?, ?, ?);', (id, i + 1, so, 1 if val['req'] else 0, ))
  
    c.execute('UPDATE dates SET imported=1 WHERE id=?;', (id, ))
    db.commit()
  except Exception as e:
    print "*** exception", e
    db.rollback()
    return False
  
  return True

def update(name):
  d = open(name)
  createtables(d)
  updurls(d)
  while getone(d):
    pass

def toobj(db):
  c = db.cursor()
  
  c.execute('SELECT id, artist FROM artists;')
  r = c.fetchall()
  artists = [ { 'id': v[0], 'artist': v[1] } for v in r ]

  c.execute('SELECT id, artist, title FROM songs;')
  r = c.fetchall()
  songs = [ { 'id': v[0], 'artistid': v[1], 'title': v[2] } for v in r ]
  
  def getd(da):
    c.execute('SELECT playorder, song, request FROM plays WHERE date=? ORDER BY playorder;', (da, ))
    r = c.fetchall()
    return [ { 'songid': v[1], 'request': v[2] == 1 } for v in r ]
  
  c.execute('SELECT id, date FROM dates;')
  r = c.fetchall()
  sets = [ { 'id': v[0], 'date': v[1], 'plays': getd(v[0]) } for v in r ]
  
  return { 'artists': artists, 'songs': songs, 'sets': sets }
