import os
import shutil
import requests
import json
from dateutil import parser
from contextlib import closing

graphUrl = "https://graph.facebook.com/v2.3/"
accessToken = "CAACEdEose0cBAPlBJs3yyZB5ChWFx4wjEKNIjRISrZAFWQ23pRTEgyViwRyv0Sfc5HOjxtMIfPYZB5APeDtZAivI79OZA29rDOsytG89phO69ICyqNuo8fFb2mCSkDhXshkrcgns4SOFZA743tbRDNoC9AP4IyZCdgjbBDHUnhPmZCwbpR6BmOCApqAGwAuVyqDMECMkGxaZATQI3gAtyJJebnsUdCAoge5MZD"
pageId = "451303254914427"

r = requests.get(graphUrl + pageId + "/feed?access_token=" + accessToken)

data = json.loads(r.text)
del r

posts = data["data"]
nextPageUrl = data["paging"]["next"]

def convertPosts(posts, next):
  for post in posts:
    postDate = parser.parse(post["created_time"])
    ymd = str(postDate.year) + "-" + str(postDate.month) + "-" + str(postDate.day)
    fileName = '_posts/' + ymd + "-" + post["id"] + ".md"
    f = open(fileName, 'w')
    if 'picture' in post and 'message' in post:
      fileContents = '''---
tags: [\'\']
layout: post
title: ''' + post["id"] + '''
category: \'\'
---
''' + post["message"] + '''
![''' + post["id"] + '''](/uploads/''' + ymd + '''-''' + post["id"] + '''.jpg)
'''
 
    elif 'picture' in post:   
      fileContents = '''---
tags: [\'\']
layout: post
title: ''' + post["id"] + '''
category: \'\'
---
![''' + post["id"] + '''](/uploads/''' + ymd + '''-''' + post["id"] + '''.jpg)
'''
 
    elif 'message' in post:
      fileContents = '''---
tags: [\'\']
layout: post
title: ''' + post["id"] + '''
category: \'\'
---
''' + post["message"]


    else:
      f.close()
      os.remove(fileName)
      break

    f.write(fileContents)
    f.close()
    
    if 'picture' in post and 'object_id' in post:
      with closing(requests.get(graphUrl + post["object_id"] + "/picture?access_token=" + accessToken + "&type=normal", stream=True)) as imageResponse: 
        with open('uploads/'+ymd+'-'+post["id"]+'.jpg', 'wb') as out_file:
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