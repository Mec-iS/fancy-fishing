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
import cgi

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache

import datetime
import webapp2

from model import *
from config import *



class EditController(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if (not users.is_current_user_admin()):
                self.redirect("/")
                return
        else:
            self.redirect(users.create_login_url(self.request.uri))   
            return
        post = GetPostDataBySlug(self.request.get('slug')) 
        if post:
            content_values={
                'formTitle': 'Edit Post',
                'title': post.title,
                'slug' : post.slug,
                'author': post.author,
                'meta_text' : post.meta_text,
                'content' : post.content,
                'category_id': post.category_id,
                'tag_list': MakeTagList(post.tag_list)
                }
            path = os.path.join(os.path.dirname(__file__), 'view/admin/_edit.html')
            content=template.render(path, content_values)
        else:
            content_values={
                'formTitle': 'New Post',
                'title': 'New post',
                'slug' : 'slug',
                'author': DEFAULT_AUTHOR,
                'meta_text' : '150 character keyword rich description',
                'content' : '<h4>heading</h4><p>text data</p>',
                'category_id': 'site-news',
                'tag_list':'verdata'
                }
            path = os.path.join(os.path.dirname(__file__), 'view/admin/_new.html')
            content=template.render(path, content_values)
        
        page_values = {
            'content': content
            }
        path = os.path.join(os.path.dirname(__file__), 'view/admin/admin.html')
        self.response.out.write(template.render(path, page_values))

    def post(self):
        user = users.get_current_user()
        if user:
            if (not users.is_current_user_admin()):
                self.redirect("/")
                return
        else:
            self.redirect(users.create_login_url(self.request.uri))   
            return
        type=self.request.get('action_type')

        if type=='new':
            slug=self.request.get('new_slug')
            post=GetPostDataBySlug(slug)
            if post:
                postfix=1
                while (post):
                    postfix +=1
                    slug = self.request.get('new_slug') + "-" + str(postfix)
                    post=GetPostDataBySlug(slug) 
            CreatePost(self,slug)        
        
        if type== 'edit':
            slug=self.request.get('slug')
            post=GetPostDataBySlug(slug)
            UpdatePost(self, post)
        
        if type=='delete':
            slug=self.request.get('slug')
            post=GetPostDataBySlug(slug)
            DeletePost(self, post)


        memcache.flush_all()
        self.redirect("/page/" + slug )


def CreatePost(self,slug):
        
    def txn():
        post_index = IncrementPostCount()
        post=Post(
            key_name = slug, 
            parent = post_index )
        post.slug=slug
        post.created=datetime.datetime.now()
        post.updated=datetime.datetime.now()
        post.category_id =self.request.get('category_id')
        post.tag_list=self.request.get('tag_list').split('|')
        post.title=self.request.get('title')
        post.meta_text=self.request.get('meta_text')
        post.content=self.request.get('content')
        post.author=self.request.get('author')
        post.status= STATUS_LIVE
        post.put()
        
    db.run_in_transaction(txn)

    UpdateCategory(self.request.get('category_id'))
    UpdateTags(self.request.get('tag_list').split('|'))   


def UpdatePost(self, post):
    StripCategory(self.request.get('old_category_id'))
    StripTags(self.request.get('old_tag_list').split('|'))
    post.title=self.request.get('title')
    post.meta_text=self.request.get('meta_text')
    post.content=self.request.get('content')
    post.author=self.request.get('author')
    post.updated=datetime.datetime.now()
    post.category_id=self.request.get('category_id')
    post.tag_list=self.request.get('tag_list').split('|')
    post.status= STATUS_LIVE
    post.put()
    UpdateCategory(self.request.get('category_id'))
    UpdateTags(self.request.get('tag_list').split('|'))   

def DeletePost(self, post):
    DecrementPostCount()
    post.delete()
    StripCategory(self.request.get('old_category_id'))
    StripTags(self.request.get('old_tag_list').split('|'))

def CreateTag(data):
    tag=Tag(key_name = data[0])
    tag.tag_id = data[0]
    tag.display = data[1]
    tag.css_class = data[2]
    tag.tag_count = 0
    tag.put()
    return tag

def CreateCategory(data):
    category=Category(key_name=data[0])
    category.category_id =data[0]
    category.display=data[1]
    category.category_count=0
    category.put()   
    return category

def IncrementPostCount():
    post_index=GetPostIndexFromDB()
    post_index.post_count += 1
    post_index.put()
    return post_index
def DecrementPostCount():
    post_index=GetPostIndexFromDB()
    post_index.post_count -=  1
    post_index.put()
    return post_index


def UpdateCategory(category_id ):
    category=db.get(db.Key.from_path('Category', category_id ))
    if category:
        category.category_count += 1
    else:
        category = CreateCategory([category_id , category_id ])
        category.category_count += 1
    category.put()


def UpdateTags(tag_list):
    post_index=GetPostIndex()
    for tag_id in tag_list:
        tag=db.get(db.Key.from_path('Tag', tag_id))
        if tag:
            tag.tag_count += 1
            tag.css_class='tag' + str(int(((float(tag.tag_count) / float(post_index.post_count)) * 10)/2) + 1)
        else:
            tag = CreateTag([tag_id, tag_id,'tag1']) 
            tag.tag_count += 1
        tag.put()


def StripTags(tag_list):
    post_index=GetPostIndex()
    for tag_id in tag_list:
        tag=db.get(db.Key.from_path('Tag', tag_id))
        if tag:
            tag.tag_count -= 1
            tag.cssClass='tag' + str(int(((float(tag.tag_count) / float(post_index.post_count)) * 10)/2) + 1)
            tag.put()
    
def StripCategory(category_id):
    category=db.get(db.Key.from_path('Category', category_id))
    if category:
        category.category_count -= 1
        category.put()

def MakeTagList(tag_list):
    tags=""             
    for tag_id in tag_list:
        tags += tag_id + '|'
    return tags[:-1]   