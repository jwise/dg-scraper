# dg-scraper

## Quick start

Either [download a database](http://nyus.joshuawise.com/dg-new.db)
(preferred, to reduce the load on Ed's machine), or create yourself a
database:

```python
>>> import db
>>> a = db.open('dg-database.db')
>>> db.createtables(a)
>>> db.updurls(a)
[...]
>>> while db.getone(a):
>>> while db.getone(a):
...  pass
...
[...]
```

If you name your database `dg-new.db`, then you can automate the update
process with `update.py` and `tojson.py` (the latter should be redirected to
create a `db.json` file for dgjs2).

## Some questions you can ask

Here are some questions you can ask the database:

```sql
-- What's overplayed?
SELECT count(*) AS plays,artists.artist,songs.title
  FROM plays
  JOIN songs ON plays.song=songs.id
  JOIN artists ON songs.artist=artists.id
  GROUP BY song
  ORDER BY plays DESC
  LIMIT 20;

-- What got played last night?
SELECT id,date FROM dates ORDER BY date DESC limit 1;
SELECT playorder,artists.artist,songs.title
  FROM plays
  JOIN songs ON plays.song=songs.id
  JOIN artists ON songs.artist=artists.id
  WHERE date=86
  ORDER BY playorder;

-- How overplayed was last night's stuff?
SELECT p1.playorder,artists.artist,songs.title,count(*)
  FROM plays p1
  JOIN songs ON p1.song=songs.id
  JOIN artists ON songs.artist=artists.id
  JOIN plays p2 ON p1.song=p2.song
  WHERE p1.date=86
  GROUP BY p1.song,p1.playorder
  ORDER BY p1.playorder;

-- What's been played 16 times?
SELECT count(*) AS plays,artists.artist,songs.title
  FROM plays
  JOIN songs ON plays.song=songs.id
  JOIN artists ON songs.artist=artists.id
  GROUP BY song
  HAVING plays=16;

-- What's Hello?
SELECT songs.id,artists.artist,title
  FROM songs
  JOIN artists ON songs.artist=artists.id
  WHERE title='Hello';

-- What gets played after Hello?
SELECT artists.artist,songs.title
  FROM plays p1
  JOIN songs ON p2.song=songs.id
  JOIN artists ON songs.artist=artists.id
  JOIN plays p2 ON p2.playorder=p1.playorder+1
  WHERE p1.song=1636
    AND p2.date=p1.date;

-- Who gets played after Hello?
SELECT COUNT(*) as plays, artists.artist
  FROM plays p1
  JOIN songs ON p2.song=songs.id
  JOIN artists ON songs.artist=artists.id
  JOIN plays p2 ON p2.playorder=p1.playorder+1
  WHERE p1.song=1636
    AND p2.date=p1.date
  GROUP BY artists.artist
  ORDER BY plays;

-- What gets played after Annie Would I Lie To You?
SELECT COUNT(*) as plays, artists.artist, songs.title
  FROM plays p1
  JOIN songs ON p2.song=songs.id
  JOIN artists ON songs.artist=artists.id
  JOIN plays p2 ON p2.playorder=p1.playorder+1
  WHERE p1.song=422
    AND p2.date=p1.date
  GROUP BY p2.song
  ORDER BY plays;

-- When does Annie Would I Lie To You get played?
SELECT COUNT(*) as plays, p1.playorder / 5 * 5 as grelt
  FROM plays p1
  WHERE p1.song=422
  GROUP BY grelt
  ORDER BY grelt;
```
