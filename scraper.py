import requests
from bs4 import BeautifulSoup
import re

def url_to_tracklist(url):
  r = requests.get(url)
  text = r.text
  text = text.replace('</br>','<br />')
  soup = BeautifulSoup(text)
  
  playlist = soup.find(id="playlist")
  
  isrequest = False
  haslounge = False
  artist = None
  title = None
  plays = []
  
  for frag in playlist.contents:
    if frag == '\n':
      continue
    
    if frag == '\nPrevious: ':
      break
    
    if type(frag) == type(playlist): # i.e., it is a tag
      if frag.name == "span":
        if frag['class'][0] == 'date':
          pass
        elif frag['class'][0] == 'request':
          isrequest = True
        elif frag['class'][0] == 'room':
          if frag.get_text() == "Lounge":
            haslounge = True
            break
        elif frag['class'][0] == 'dj':
          pass
        else:
          raise ValueError("unknown span class %s<%s>" % (frag['class'], frag.get_text(), ))
      elif frag.name == "em":
        artist = frag.get_text()
      elif frag.name == "br":
        if artist is not None:
          plays.append({"artist": artist, "title": title, "req": isrequest})
        artist = None
        title = None
        isrequest = False
      else:
        raise ValueError("unknown tag %s" % (str(frag)))
    
    else: # it is a play, I hope
      title = re.sub("^ - ", "", frag)
  
  return plays

def get_tracklists():
  r = requests.get("http://www.deathguild.com/playdates/")
  soup = BeautifulSoup(r.text)
  
  return \
    { re.match(r'/playlist/(.*)', a['href']).group(1):
        "http://www.deathguild.com/" + a['href']
      for a in soup.find(id="playlist").find_all("a")
    }
