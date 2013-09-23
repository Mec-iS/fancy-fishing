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
 
 
# python c:\google_appengine\appcfg.py --email=tunedconsulting@gmail.com update --no_cookies moloco-blog
import os 
from google.appengine.ext.webapp import template
import webapp2

from home  import *
from edit import *
from rss import *



app = webapp2.WSGIApplication([
        ('/', HomeController),
        ('/edit', EditController),
        ('/rss.xml', RssController),
        ('/meta/([\w-]+)', MetaController),
        ('/page/([\w-]+)', PageController),
        ('/tag/([\w-]+)', TagController),
        ('/category/([\w-]+)', CategoryController)
    ], debug=True)