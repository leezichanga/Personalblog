from flask import render_template,request,redirect,url_for,abort,flash
from . import main
from flask_login import login_required,current_user
from ..models import User,Blog,Comment,Subscribe
from .forms import UpdateProfile,BlogForm,CommentForm,SubscribeForm
from .. import db,photos
from ..email import mail_message

@main.route('/')
def index():
    '''
        View root page function that returns the index page and its data
    '''
    poems = Blog.query.all()
    comments = Comment.query.all()
    title = 'My Blog | My Blog'

    return render_template('index.html',comments=comments,poems=poems,title=title)

@main.route('/user/<uname>')
def profile(uname):
    user=User.query.filter_by(username=uname).first()

    if user is None:
        abort(404)

    title = "My Blog"

    return render_template("profile/profile.html",title=title,user=user)

@main.route('/user/<uname>/update',methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username=uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()
    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname=user.username))
    return render_template('profile/update.html',form=form)

@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'image' in request.files:
        filename = images.save(request.files['image'])
        path = f'images/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/blog/new',methods=['GET','POST'])
@login_required
def new_blog():
    form = BlogForm()
    subscriber= Subscribe.query.all()
    if form.validate_on_submit():
        title=form.title.data
        body=form.body.data
        new_blog=Blog(title=title,body=body,user=current_user)
        new_blog.save_blog()
        for sub in subscriber:
            mail_message("New Blog Alert","email/update",sub.email,sub=sub)
        return redirect(url_for('main.index'))

    title = 'My Blog'
    return render_template('new_blog.html',title=title,blog_form=form)

@main.route('/blog/<int:id>')
def view_blog(id):
    form=BlogForm()
    user=User.query.filter_by(id=id).first()
    blog= Blog.query.filter_by(id=id).first()

    comments = Comment.get_comments(id)


    title = 'My Blog'
    return render_template('blog.html',comments=comments,title=title,blog=blog,blog_form=form,user=user)


@main.route('/about')
def about():
    title = 'My Blog'
    return render_template('about.html',title=title)

@main.route('/comment/new/<int:id>',methods=['GET','POST'])
def new_comment(id):
    blog=Blog.query.filter_by(id=id).first()

    if blog is None:
        abort(404)
    form = CommentForm()

    if form.validate_on_submit():
        name = form.name.data
        comment_body = form.comment_body.data
        new_comment = Comment(comment_body=comment_body,name=name,blog=blog)
        new_comment.save_comment()
        return redirect(url_for('main.view_blog',id=blog.id))

    title='Comment'
    return render_template('new_comment.html',title=title,comment_form=form)

@main.route('/subscribe',methods=["GET","POST"])
def subscribe():
    form=SubscribeForm()

    if form.validate_on_submit():
        subscriber = Subscribe(name=form.name.data,email=form.email.data)
        db.session.add(subscriber)
        db.session.commit()

        mail_message("Welcome to my blog","email/subscribe_user",subscriber.email,subscriber=subscriber)
        flash('A confirmation by email has been sent to you by email')
        return redirect(url_for('main.index'))
        title = 'Subscribe'
    return render_template('subscribe.html',subscribe_form=form)
