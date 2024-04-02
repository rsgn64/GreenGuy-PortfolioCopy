from flask import render_template, url_for, Flask, flash, request, redirect
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.models import User, BlogPost, get_json_data, create_blog_post, delete_blog_post
from app.forms import AddBlogPostForm, LoginForm, DelBlogPostForm

@app.route('/')
def index():
    #Route to blog portion for now
    return redirect(url_for('blog'))

@app.route('/cv')
def cv():
    cv_data, use_gist_img = get_json_data(app.config['CV_JSON_GIST_URL'])
    #Grab desired parts so we don't need to pass the full dict
    basics = cv_data['basics']
    skills = cv_data['skills']
    experience = cv_data['work']
    educ = cv_data['education']
    certs = cv_data['certificates']
    projects = cv_data['projects']
    pubs = cv_data['publications']
    #Covert JSON Schema date formats within Experience, Education, Publications, and Certificates from 2020-04 to Apr 2020
    conv_dict = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sept', '10':'Oct', '11':'Nov', '12':'Dec'}
    for item in experience:
        item['startDate'] = conv_dict[item['startDate'][5:7]] + ' ' + item['startDate'][0:4]
        item['endDate'] = conv_dict[item['endDate'][5:7]] + ' ' + item['endDate'][0:4]
    for item in educ:
        item['startDate'] = conv_dict[item['startDate'][5:7]] + ' ' + item['startDate'][0:4]
        item['endDate'] = conv_dict[item['endDate'][5:7]] + ' ' + item['endDate'][0:4]
    for item in certs:
        item['date'] = conv_dict[item['date'][5:7]] + ' ' + item['date'][0:4]
    for item in pubs:
        item['releaseDate'] = conv_dict[item['releaseDate'][5:7]] + ' ' + item['releaseDate'][0:4]
    return render_template('CV.html', title='CV', basics=basics, skills=skills, experience=experience, educ=educ, certs=certs, projects=projects, pubs=pubs, use_gist_img=use_gist_img)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    #Add a descending/ascending filter option
    descending = request.args.get('desc', 1, type=int)
    if descending:
        query = sa.select(BlogPost).order_by(BlogPost.date.desc())
    else: query = sa.select(BlogPost).order_by(BlogPost.date)
    #paginate posts and create urls to next/prev
    posts = db.paginate(query, page=page, per_page=app.config['BLOG_POST_PER_PAGE'], error_out=False)
    next_url = url_for('blog', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('blog', page=posts.prev_num) if posts.has_prev else None
    return render_template('blog.html', title='GreenGuy', posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/blog/<post_name>')
def blog_post(post_name):
    post = db.session.scalar(sa.select(BlogPost).where(BlogPost.post_name == post_name))
    post_title = post.post_title
    date = post.date
    return render_template('blog_post.html', blog_post=post_name, title=post_title, date=date)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #Login for 1 account only. Intended for me to easily add new posts
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == app.config['ADMIN_USERNAME'] and form.password.data == app.config['ADMIN_PASSWORD']:
            login_user(user=User())
            return redirect(url_for('add_post'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_post', methods=['GET', 'POST'])
@login_required #Require login in to add posts
def add_post():
    form = AddBlogPostForm()
    if form.validate_on_submit():
        #Read the uploaded .zip as bytes:
        file_data = form.post_zip_file.data.read()
        #Run the add_blog_post function which extracts and modifies the Quarto output to fit this web app:
        post_title, description = create_blog_post(file_data, form.post_name.data)
        #Add post metadata to database:
        new_post = BlogPost(post_name=form.post_name.data, post_title=post_title, description=description)
        db.session.add(new_post)
        db.session.commit()
        #Redirect to new post:
        return redirect(url_for('blog_post', post_name=form.post_name.data))

    return render_template('add_blog_post.html', form=form)

@app.route('/delete_post', methods=['GET', 'POST'])
@login_required
def delete_post():
    form = DelBlogPostForm()
    if form.validate_on_submit():
        to_del = form.post_name.data
        delete_blog_post(to_del)
        BlogPost.query.filter(BlogPost.post_name == to_del).delete()
        db.session.commit()
        flash(f'{to_del} has been deleted.')
    return render_template('del_blog_post.html', form=form)