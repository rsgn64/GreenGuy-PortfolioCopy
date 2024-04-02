import os
basedir = os.path.abspath(os.path.dirname(__file__))

#Config info (Not to be used in production)
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'insert-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    CV_JSON_GIST_URL = "https://gist.githubusercontent.com/rsgn64/47c0a6ef15ba65847295a7626e6dbeed/raw/"
    STATIC_CV_JSON_LOC = os.path.join(basedir, 'app', 'static', 'resume.json')
    BLOG_HTML_LOC = os.path.join(basedir, 'app', 'templates', 'blog_posts')
    BLOG_FILES_LOC = os.path.join(basedir, 'app', 'static', 'blog_post_media')
    BLOG_QUARTO_INC_LOC =  os.path.join(basedir, 'app', 'static', 'quarto_inc')
    BLOG_POST_PER_PAGE = 10
    ADMIN_USERNAME = 'Admin'
    ADMIN_PASSWORD = 'Admin'