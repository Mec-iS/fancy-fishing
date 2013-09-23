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

from google.appengine.ext import db
from google.appengine.api import memcache

from paged_query import PagedQuery

from config import *

STATUS_DRAFT=1
STATUS_LIVE=2
STATUS_RETIRED=3

class Post(db.Model):
    slug = db.StringProperty()
    title = db.StringProperty()
    meta_text = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty()
    updated = db.DateTimeProperty()
    author = db.StringProperty()
    category_id = db.StringProperty()
    tag_list=db.StringListProperty()
    status=db.IntegerProperty()

class Tag(db.Model):
    tag_id = db.StringProperty()
    display = db.StringProperty()
    css_class = db.StringProperty()
    tag_count = db.IntegerProperty()

class Category(db.Model):
    category_id = db.StringProperty()
    display = db.StringProperty()
    category_count = db.IntegerProperty()

class PostIndex(db.Model):
    post_count = db.IntegerProperty(required=True, default=0)
 

def GetPostIndex():
    post_index=memcache.get("post-index")
    if post_index is None:
        post_index=db.get(db.Key.from_path('PostIndex', 'verdatacms'))
        if post_index is None:
            post_index=PostIndex(key_name='verdatacms')
            post_index.post_count=0
            post_index.put()
    memcache.set("post-index",post_index)
    return post_index

def GetPostIndexFromDB():
    post_index=db.get(db.Key.from_path('PostIndex', 'verdatacms'))
    if post_index is None:
        post_index=PostIndex(key_name='verdatacms')
        post_index.post_count=0
        post_index.put()
    return post_index

def GetPostDataBySlug(slug):
    post = memcache.get("postSlug:" + slug) 
    if post is None:
        post = db.get(db.Key.from_path('PostIndex','verdatacms','Post', slug))       
        memcache.set("postSlug:" + slug, post) 
    return post

def GetPostData(page_number):
    records = memcache.get("post-list:" + str(page_number)) 
    if records is None:
        paged_query = PagedQuery(Post.all(), POSTS_PER_PAGE)
        paged_query.order('-created')

        if page_number == 0:
            results = paged_query.fetch_page()
        else :
            results = paged_query.fetch_page(page_number)        
        records=[]
        for result in results:
            records.append(result)
        memcache.set("post-list:" + str(page_number), records)
    return records

def GetPostDataByTag(tag_id, page_number):
    records = memcache.get("post-tag:" + str(page_number) + ':' + tag_id) 
    if records is None:
        paged_query = PagedQuery(Post.all().filter("tag_list =",tag_id), POSTS_PER_PAGE)
        paged_query.order('-created')
        if page_number == 0:
            results = paged_query.fetch_page()
        else :
            results = paged_query.fetch_page(page_number)        
        records=[]
        for result in results:
            records.append(result)
        memcache.set("post-tag:" + str(page_number) + ':' + tag_id, records)
    return records 
  
def GetPostDataByCategory(cat_id, page_number):
    records = memcache.get("post-category:" + str(page_number) + ':' + cat_id) 
    if records is None:
        paged_query = PagedQuery(Post.all().filter("category_id =",cat_id), POSTS_PER_PAGE)
        paged_query.order('-created')
        if page_number == 0:
            results = paged_query.fetch_page()
        else :
            results = paged_query.fetch_page(page_number)        
        records=[]
        for result in results:
            records.append(result)
        memcache.set("post-category:" + str(page_number) + ':' + cat_id, records)
    return records 

def GetCategoryById(category_id ):
    category = memcache.get("category:" + category_id ) 
    if category is None:
        category = db.get(db.Key.from_path('Category', category_id ))
        memcache.set("category:" + category_id , category) 
    return category

def GetTagById(tag_id):
    tag = memcache.get("tag:" + tag_id) 
    if tag is None:
        tag = db.get(db.Key.from_path('Tag', tag_id))
        memcache.set("tag:" + tag_id,tag) 
    return tag


