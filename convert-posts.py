import os
import shutil
import requests
import json
from dateutil import parser
from contextlib import closing

graphUrl = "https://graph.facebook.com/v2.3/"
accessToken = "CAACEdEose0cBABawvXX4eQyV353ZAL9hvTicGVrjNBAdioBZBhMZCt5lXUcE7mfvm1xoStCoDuByc42E8m8NU3H3dcMqFGHmZBTdELa0vJRQXeua4KEg7XrYojyT9BjmZBhKQWiBZA3PimuzMgCEWZABBc1I55cGERz1suAW7EMCZALWRuVTXLT66VZByPZB7Far1mG1kFu5eZBbuc883C7gKaI"
pageId = "451303254914427"

r = requests.get(graphUrl + pageId + "/feed?access_token=" + accessToken)

data = json.loads(r.text)
del r

posts = data["data"]
nextPageUrl = data["paging"]["next"]

def convertPosts(posts, next):
  postCount = 0
  for post in posts:
    postCount += 1
    print('converting post #%d' % postCount)
    postDate = parser.parse(post["created_time"])
    ymd = str(postDate.year) + "-" + str(postDate.month) + "-" + str(postDate.day)
    fileName = '_posts/' + ymd + "-" + post["id"] + "-human-message-goes-here.md"
    f = open(fileName, 'w')
    if 'picture' in post and 'message' in post:
      fileContents = '''---
tags: [\'\']
layout: post
title: ''' + post["id"] + ''' human message goes here
category: \'\'
---
human message goes here
''' + post["message"] + '''
![''' + post["id"] + '''](/uploads/''' + ymd + '''-''' + post["id"] + '''-human-message-goes-here.jpg)
'''

    elif 'picture' in post:
      fileContents = '''---
tags: [\'\']
layout: post
title: ''' + post["id"] + ''' human message goes here
category: \'\'
---
human message goes here
![''' + post["id"] + '''](/uploads/''' + ymd + '''-''' + post["id"] + '''-human-message-goes-here.jpg)
'''

    elif 'message' in post:
      fileContents = '''---
tags: [\'\']
layout: post
title: ''' + post["id"] + ''' human message goes here
category: \'\'
---
''' + post["message"] + '''
human message goes here
'''

    else:
      f.close()
      os.remove(fileName)
      break

    f.write(fileContents)
    f.close()

    if 'picture' in post and 'object_id' in post:
      with closing(requests.get(graphUrl + post["object_id"] + "/picture?access_token=" + accessToken + "&type=normal", stream=True)) as imageResponse:
        with open('uploads/'+ymd+'-'+post["id"]+'-human-message-goes-here.jpg', 'wb') as out_file:
          shutil.copyfileobj(imageResponse.raw, out_file)
        del imageResponse

  del posts

  if next:
    nextRequest = requests.get(next)
    nextData = json.loads(nextRequest.text)
    del nextRequest
    if 'data' in nextData and 'paging' in nextData:
      if 'next' in nextData['paging']:
        nextPosts = nextData["data"]
        nextPageUrl = nextData["paging"]["next"]
        convertPosts(nextPosts, nextPageUrl)

convertPosts(posts, nextPageUrl)
