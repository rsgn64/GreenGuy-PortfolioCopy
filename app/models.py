from app import app, db, login
from flask_login import UserMixin
from datetime import datetime, date
import sqlalchemy as sa
import sqlalchemy.orm as so
import requests
import json
import zipfile
import os
import io
import shutil
from bs4 import BeautifulSoup, Doctype

#flask-login requires User class with an id.
#UserMixin adds all the other needed stuff like .is_authenticated, etc
#Since I just need one account, an id = 1 works.
class User(UserMixin):
    id = 1

class BlogPost(db.Model):
    #Use SQLite3 DB to store blog post meta-data.
    #To-Do: Add a second DB with tags once I create enough posts to need searching.
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    post_name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    post_title: so.Mapped[str] = so.mapped_column(sa.String(128))
    date: so.Mapped[datetime] = so.mapped_column(default=lambda: date.today())
    description: so.Mapped[str] = so.mapped_column(sa.String(256))

@login.user_loader
def load_user(id):
    return User()

def get_json_data(gist_url):
    #Attempt to grab the data from online Raw Gist
    try:
        response = requests.get(gist_url)
        data = json.loads(response.text)
        return (data, True)
    #Resort to using Static file if error using Gist Url
    except:
        print('Unable to read JSON from GIST, using Static version instead.')
        with open(app.config['STATIC_CV_JSON_LOC'], 'r') as file:
            data = json.load(file)
        file.close()
        return (data, False)
    
def create_blog_post(zip_file, post_name):
    #First extract the uploaded .zip, modify the html, and then extract/store in static/templates
    #Returns (post_title, description)
    post_title = ''
    description = ''
    zip_in_memory = io.BytesIO(zip_file)
    with zipfile.ZipFile(zip_in_memory, 'r') as zf:
        for item in zf.infolist():
            if item.is_dir(): continue
            f_name, file_ext = os.path.splitext(item.filename)
            if file_ext.lower() == '.html':
                soup = BeautifulSoup(zf.read(item).decode('UTF-8'), 'html.parser')
                #Remove top !DOCTYPE, which is usually always line #1, but catch if it's not and iterate contents to find it:
                if isinstance(soup.contents[0], Doctype):
                    soup.contents[0].extract()
                else:
                    for item in soup.contents:
                        if isinstance(item, Doctype):
                            item.extract()
                #Remove all <meta>:
                for item in soup.find_all('meta'):
                    item.decompose()
                #Extract title and description text:
                post_title = soup.title.get_text()
                description = soup.find(class_='abstract').contents[2].get_text().strip() #abstract div has a title div, then the actual abstract.
                #Remove <html> and <head> wrappers:
                soup.html.unwrap()
                soup.head.unwrap()
                #Remove the <title> and the <header>:
                soup.title.decompose()
                soup.header.decompose()
                #Modify the <script> and <link> 'src' items from filename_files/libs/ into jinja static location
                for src in soup.find_all('script',{"src":True}):
                    src['src'] = src['src'].replace(f_name + "_files/libs/", "{{url_for('static', filename='quarto_inc/')}}")
                for href in soup.find_all('link',{"href":True}):
                    href['href'] = href['href'].replace(f_name + "_files/libs/", "{{url_for('static', filename='quarto_inc/')}}")
                #Modify the <img> 'src' items from filename_files/ into jinja static post_name locations
                    #Note: if f_name has a space in it, Quarto changes it to %20
                for img in soup.find_all('img',{"src":True}):
                    img['src'] = "{{url_for('static', filename='blog_post_media/" + post_name + "/" + img['src'].rsplit('/', 1)[1] + "')}}"
                #Save the output to post_name.html:
                with open(os.path.join(app.config['BLOG_HTML_LOC'], post_name + '.html'), "w", encoding='utf-8') as f:
                    f.write(str(soup))
            else:
                #Quarto's 'extract-media' option places all media into a named folder, but still has some sub-folder structure to it.
                #Flatten that structure and 
                item.filename = item.filename.rsplit('/', 1)[1]
                zf.extract(item, path=os.path.join(app.config['BLOG_FILES_LOC'], post_name))
    return (post_title, description)

def delete_blog_post(post_name):
    os.remove(os.path.join(app.config['BLOG_HTML_LOC'], post_name + '.html'))
    shutil.rmtree(os.path.join(app.config['BLOG_FILES_LOC'], post_name))