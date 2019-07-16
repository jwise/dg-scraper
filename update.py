import db

a = db.open('dg-new.db')
db.migrate(a)
db.updurls(a)
while db.getone(a):
  pass
