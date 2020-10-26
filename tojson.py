from __future__ import print_function
import db,json
import sys

print('building object...', file=sys.stderr)
a = db.open('mg.db')
obj = db.toobj(a)

print('mangling object...', file=sys.stderr)

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
              '_p': [ [ v2['songid'], v2['request'] ] for v2 in v['plays'] ],
              '_c': v['club'] 
            } for v in obj['sets'] ]
}

print('dumping json...', file=sys.stderr)
print(json.dumps(zobj))