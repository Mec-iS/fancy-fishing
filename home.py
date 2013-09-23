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

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import memcache

import os
import datetime
import webapp2
from random import choice

from model import *
from config import *


class PageController(webapp2.RequestHandler):
    def get(self, page_id):
        self.response.out.write(GetPage(self, GetPost(GetPostDataBySlug(page_id)),page_id))  

class TagController(webapp2.RequestHandler):
    def get(self, tag_id):
        self.response.out.write(GetPage(self, GetTagList((ParsePageNumber(self.request.get("page"))),tag_id),None,tag_id))      

class CategoryController(webapp2.RequestHandler):
    def get(self, category_id):
        self.response.out.write(GetPage(self, GetCategoryList((ParsePageNumber(self.request.get("page"))),category_id),None, category_id))      

class HomeController(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(GetPage(self, GetPostList(ParsePageNumber(self.request.get("page")))))    

class MetaController(webapp2.RequestHandler):
    def get(self, meta_id):
        self.response.out.write(GetPage(self, GetMataContent(meta_id)))      

def GetMataContent(metaId):
    content_values = {}
    path = os.path.join(os.path.dirname(__file__), 'view/meta/_' + metaId + '.html')
    content = template.render(path, content_values)
    return content

def GetCategoryList(page_number, category_id ):
    count=GetCategoryById(category_id )
    if count:
        return GetListContent(GetPostDataByCategory(category_id , page_number),page_number, '/category/'+ category_id , count.category_count)

def GetTagList(page_number, tag_id):
    count=GetTagById(tag_id)
    if count:
        return GetListContent(GetPostDataByTag(tag_id, page_number), page_number, '/tag/' + tag_id, count.tag_count)

def GetPostList(page_number):
    post_index = GetPostIndex()   
    return GetListContent(GetPostData(page_number), page_number, '/',post_index.post_count)

def ParsePageNumber(page):
    page_number=1
    if page.isdigit() and len(page) <= 3:
        page_number=int(page)
    return page_number

def GetListContent(results, page_number, path, max_count):

    navigation_style, back_link, forward_link = '', '', ''
   
    if page_number * POSTS_PER_PAGE < max_count: 
        back_link = '<a class="btn btn-mini" href="' + SITE_URL + path + '?page=' + str(page_number + 1) + '">&laquo;&nbsp;Post precedenti</a>'
    if page_number > 2:
        forward_link = '<a class="btn btn-mini" href="' + SITE_URL + path + '?page=' + str(page_number -1) + '">Post recenti&nbsp;&raquo;</a>'
    if page_number == 2:
        forward_link = '<a class="btn btn-mini" href="' + SITE_URL + path + '">Post recenti&nbsp;&raquo;</a>'
    if page_number == 1:
        forward_link = ''
    
    if back_link == '' and forward_link =='':
        navigation_style = 'display:none'

    content_values = {
        'navigation_style': navigation_style,
        'back_link':  back_link,
        'forward_link':  forward_link
        }
    path = os.path.join(os.path.dirname(__file__), 'view/_navigation.html')
    navigation = template.render(path, content_values)
    content = navigation
    content_values= {}
    contentFound = False
    for result in results:
        more=result.content.find('[continua]')
        moreLink=''
        if more != -1:
            moreLink='<a href="' + SITE_URL + '/page/' + result.slug + '"><em>[leggi]</em></a>'
        category=GetCategoryById(result.category_id )
        content_values = {
            'title':  '<a href="' + SITE_URL + '/page/' + result.slug + '">' + result.title + '</a>',
            'contentText':  result.content.split('[continua]')[0] + moreLink,
            'author':  result.author,
            'created':result.created,
            'category': '<a href="' + SITE_URL + '/category/' + category.category_id + '">' + category.display + '</a>'   ,
            'tag_list':  ParseTagList(result.tag_list)
            }
        contentFound = True
        path = os.path.join(os.path.dirname(__file__), 'view/_list.html')
        content += template.render(path, content_values)
    content += navigation
    if not contentFound:
        path = os.path.join(os.path.dirname(__file__), 'view/404.html')
        content = template.render(path, {})
    return content

def GetPost(post):
    content=""
    back_link , forward_link = "", ""
    content_values= {}
    contentFound = False
    if post:
        category=GetCategoryById(post.category_id)
        
        disqus_values = {
        'disqus_shortname': DISQUS_SHORTNAME ,
        'slug':  post.slug,
        'pageURL':  SITE_URL + '/page/' + post.slug ,
        'title': post.title
        }
        path = os.path.join(os.path.dirname(__file__), 'view/_disqus.html')
        disqus = template.render(path, disqus_values)
        
        content_values = {
            'slug':  post.slug,
            'title': post.title,
            'content':  post.content.replace('[more]',''),
            'author':  post.author,
            'created':  str(post.created)[0:10],
            'disqus' : disqus,
            'category': '<a href="' + SITE_URL + '/category/' + category.category_id + '">' + category.display + '</a>',
            'tag_list':  ParseTagList(post.tag_list)
            }
        contentFound = True
        path = os.path.join(os.path.dirname(__file__), 'view/_post.html')
        content += template.render(path, content_values)
  
    if not contentFound:
        path = os.path.join(os.path.dirname(__file__), 'view/404.html')
        content = template.render(path, {})
    return content

def GetPage(self, content, pageId = None, title=None):
    author , logStatus = GetLoginLinks(self.request.uri,pageId)
    pageTitle=HEADLINE
    meta_text=MISSION
    disqus_sidebar = ''
    if title is not None:
        pageTitle = title.replace('-',' ') + ' - verdata'
    if pageId is not None:
        post=GetPostDataBySlug(pageId)
        if post: 
            pageTitle=post.title
            meta_text=post.meta_text
    
    content_values = {}
    path = os.path.join(os.path.dirname(__file__), 'view/_disqus-sidebar.html')
    #disqus_sidebar = template.render(path, content_values)
    
    isotope = getIsotopeContent()
    el_styling = getElementsStyle()
    
    page_values = {
        'siteurl': SITE_URL,
        'headline': HEADLINE,
        'mission': MISSION,
        'disqus_sidebar': disqus_sidebar,
        'pageTitle':pageTitle,
        'pageDescription':meta_text,
        'content': content,
        'isotope': isotope,
        'elements_css': el_styling,
        'catList': getCatList()[0],
        'categories': getCatList()[1],
        'tagCloud': getTagCloud()[0],
        'fulltags': getTagCloud()[1],
        'footerText': FOOTER_TEXT,
        'author': author,
        'logStatus': logStatus
        }
    path = os.path.join(os.path.dirname(__file__), 'view/home.html')
    return template.render(path, page_values)

def getElementsStyle():
    el_styling = memcache.get("elements-colors")
    if el_styling is None:
        t = Tag.all()
        elements = t.run()
        el_styling = '<style>'
        for e in elements:
            el_styling += '.element.'+e.display+'{'+choice(COLORS)+'} ' 
        el_styling += '</style>'
        memcache.set("elements-colors", el_styling)
    
    return el_styling

       
def getIsotopeContent():
    isotope = memcache.get("get-isotope-html")
    if isotope is None:
       isotope = ''
       q = Post.all()
       results = q.run()
       for result in results:
           isotope += '<div class="element '+ " ".join(result.tag_list) +' '+ result.category_id +'" data-symbol="'+ result.author[0:2] +'" data-category="'+ result.category_id +'" data-href="' + SITE_URL + '/page/' + result.slug + '"><p class="number">80</p><h3 class="symbol">'+ result.author[0:2] +'</h3><h2 class="name">'+result.title+'</h2><p class="weight">'+str(result.created)[0:10]+'</p></div>'
       memcache.set("get-isotope-html", isotope)
    
    #print isotope
    return isotope



def getCatList():
    catList = memcache.get("get-cat-list") 
    categories = memcache.get("get-categories")
    if catList is None or categories is None:
        categories = ''
        q = Category.all()
        q.order("category_id")
        results = q.run()
        catList = '<ul class="category-list">'
        catList += '<li class="category-list-title">argomenti:</li>'
        for result in results:
            categories += '<li><a href="#filter" data-option-value=".'+ result.category_id +'">' + result.display.replace('-',' ') + '</a></li>'
            catList += '<li class="category-menu"><a href="' + SITE_URL + '/category/' + result.category_id + '">' + result.display.replace('-',' ') + '</a><span class="category-count">&nbsp;(' + str(result.category_count) + ')</span></li>'
        catList += '</ul>'    
        memcache.set("get-cat-list", catList)
        memcache.set("get-categories", categories)
    
    #print categories
    catList = [catList, categories]
    return catList
    

def getTagCloud():
    tagCloud = memcache.get("get-tag-cloud")
    fulltags = memcache.get("get-fulltags")
    if tagCloud is None or fulltags is None:
        fulltags = ''
        q = Tag.all()
        q.order("tag_id")
        results = q.run()
        tagCloud = '<ul class="category-list">'
        tagCloud += '<li class="category-list-title">tags:</li></ul>'
        tagCloud += '<div class="tag-cloud">'
        for result in results:
            fulltags += '<li><a href="#filter" data-option-value=".' + result.tag_id + '">' + result.display + '</a></li>'
            tagCloud += '<span class="' + result.css_class + '"><a href="' + SITE_URL + '/tag/' + result.tag_id + '">' + result.display + '</a> </span>'
        tagCloud += '</div>'    
        memcache.set("get-tag-cloud", tagCloud)
        memcache.set("get-fulltags", fulltags)
    tagCloud = [tagCloud, fulltags]
    return tagCloud

def ParseTagList(tag_list):
    tags=""             
    for tag_id in tag_list:
        tag=GetTagById(tag_id)
        tags += '<a href="' + SITE_URL + '/tag/' + tag_id + '">' + tag.display + '</a> | '
    return tags[:-2]

def GetLoginLinks(callbackURI, pageId):
    user = users.get_current_user()
    logStatus = ' <a href="' + users.create_login_url(callbackURI) + '">log on</a>'
    userName = "Benvenuto"
    if user:
        logStatus = ' <a href="' + users.create_logout_url(callbackURI) + '">log off</a>'
        userName = user.nickname() + " "
    if (users.is_current_user_admin()):
        if pageId == None:   
            logStatus = ' <a href="' + SITE_URL + '/edit?slug=new">posta</a> |' + logStatus
        else:
            logStatus = ' <a href="' + SITE_URL + '/edit?slug=new">posta</a> | <a href="' + SITE_URL + '/edit?slug=' + pageId + '">modifica</a> |'  + logStatus
    return userName , logStatus

