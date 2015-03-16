import db,json
import sys

print >> sys.stderr, 'building object...'
a = db.open('dg-new.db')
obj = db.toobj(a)

print >> sys.stderr, 'mangling object...'

# Precompute some data.
artist_fwd = {}
song_fwd = {}
for k in obj['artists']:
  k['playcount'] = 0
  artist_fwd[k['id']] = k
for k in obj['songs']:
  k['plays'] = []
  song_fwd[k['id']] = k
for set in obj['sets']:
  for play in set['plays']:
    song_fwd[play['songid']]['plays'].append(set['id'])
    artist_fwd[song_fwd[play['songid']]['artistid']]['playcount'] += 1

# Then, compress the object by mangling keys.
zobj = {
  'version': 2,
  'artists': [ { '_i': v['id'], '_a': v['artist'], '_p': v['playcount'] } for v in obj['artists'] ],
  'songs': [ { '_i': v['id'], '_a': v['artistid'], '_t': v['title'], '_p': v['plays'] } for v in obj['songs'] ],
  'sets': [ { '_i': v['id'],
              '_d': v['date'],
              '_p': [ [ v2['songid'], v2['request'] ] for v2 in v['plays'] ] 
            } for v in obj['sets'] ]
}

print >> sys.stderr, 'dumping json...'
print json.dumps(zobj)