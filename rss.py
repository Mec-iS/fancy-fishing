 #  Copyright 2012 Geraint Williams, www.verdata.co.uk

 #  Licensed under the Apache License, Version 2.0 (the "License");
 #  you may not use this file except in compliance with the License.
 #  You may obtain a copy of the License at

 #      http://www.apache.org/licenses/LICENSE-2.0

 #  Unless required by applicable law or agreed to in writing, software
 #  distributed under the License is distributed on an "AS IS" BASIS,
 #  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 #  See the License for the specific language governing permissions and
 #  limitations under the License.
 
import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
import datetime
import webapp2

from model import *
from config import *

class RssController(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/xml; charset=utf-8"
        self.response.out.write(GetRSS(self, GetRssList(GetRssData()))) 
        
def GetRSS(self, content):
    
    page_values = {
        'siteurl': SITE_URL,
        'headline': HEADLINE,
        'mission': MISSION,
        'items':content
        }
    path = os.path.join(os.path.dirname(__file__), 'view/rss.xml')
    return template.render(path, page_values)         

def GetRssList(results):
    content=""
    content_values= {}
    contentFound = False
    for result in results:
        if not (result.category_id == 'site-meta'):
            content_values = {
                'itemTitle':  result.title,
                'itemLink':  SITE_URL + '/page/' + result.slug ,
                'itemcontent':  '<h1>' + result.title + '</h1>' + result.content.replace('[more]','') 
                }
            contentFound = True
            path = os.path.join(os.path.dirname(__file__), 'view/_rss-item.xml')
            content += template.render(path, content_values)
    if not contentFound:
        path = os.path.join(os.path.dirname(__file__), 'view/404.html')
        content = template.render(path, {})
    return content

def GetRssData():
    q = Post.all()
    q.order("-created")
    results = q.fetch(50)
    return results