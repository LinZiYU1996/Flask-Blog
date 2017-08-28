#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/24 21:36
# @File    : Views.py
from __future__ import unicode_literals
from  flask import render_template,Blueprint,redirect,url_for,flash,request,current_app
from Main import login_manger
from Forms import Login_Form,Register_Form,PostForm,EditProfile_Form,CommentForm
from Model import  User,Post,Permission
from flask_login import LoginManager,login_user,UserMixin,logout_user,login_required,current_user
from emails import send_email

"""
主页路由
"""



blog = Blueprint('blog', __name__)

@blog.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@blog.route('/index',methods=['GET','POST'])
def index():
    from Main import db
    form=PostForm()

    if form.validate_on_submit():
        if current_user.is_authenticated:
            post=Post(body=form.body.data,author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('.index'))
        else:
            flash('请先登录')
            return redirect(url_for('.index'))
    query = Post.query
    page = request.args.get('page', 1, type=int)
    posts=Post.query.order_by(Post.timestamp.desc()).all()      #分页处理
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=6,
        error_out=False)
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination)


@blog.route('/user/<name>')
def user(name):
    user=User.query.filter_by(name=name).first()
    page=request.args.get('page',1,type=int)
    pagination=user.posts.order_by(Post.timestamp.desc()).paginate(
       page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )

    posts=pagination.items

    return render_template('user.html',user=user,posts=posts,
                           pagination=pagination)


@blog.route('/followers/<name>')
def followers(name):
    user=User.query.filter_by(name=name).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))

    page=request.args.get('page',1,type=int)

    pagination=user.followers.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows=[{'user':item.follower,'timestamp':item.timestamp}
             for item in pagination.items]
    return render_template('followers.html',user=user,
                           title='Followers of',
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows
                           )




@blog.route('/followed-by/<name>')
def followed_by(name):
    user=User.query.filter_by(name=name).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followed.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False
    )

    follows=[{'user':item.followed,'timestamp':item.timestamp}
             for item in pagination.items]

    return render_template(
        'followers.html', user=user, title="Followed by",
        endpoint='.followed_by', pagination=pagination,
        follows=follows
    )



@blog.route('/follow/<name>')
def follow(name):
    user=User.query.filter_by(name=name).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注过此用户')
        return redirect(url_for('.user',name=name))

    current_user.follow(user)
    flash('你关注了用户%s' %name)
    return redirect(url_for('.user',name=name))




@blog.route('/unfollow/<name>')
def unfollow(name):
    user=User.query.filter_by(name=name).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你并未关注此用户')
        return redirect(url_for('.user',name=name))

    current_user.unfollow(user)
    flash('不再关注%s'% name)
    return redirect(url_for('.user',name=name))


@blog.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    from Model import db,Comment
    post=Post.query.get_or_404(id)
    form=CommentForm()
    if form.validate_on_submit():
        comment=Comment(body=form.body.data,
                        post=post,
                        author=current_user._get_current_object()

                        )

        db.session.add(comment)
        db.session.commit()
        flash('你的评论已发布')
        return redirect(url_for('.post',id=post.id,page=-1))


    page=request.args.get('page',1,type=int)
    if page==-1:
        page=(post.comments.count()-1)// \
                current_app.config['FLASKY_COMMENTS_PER_PAGE']+1
    pagination=post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )

    comments=pagination.items
    return render_template('post.html',posts=[post],form=form,

                           comments=comments,pagination=pagination)



@blog.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    from Model import db  #解决session问题
    form=EditProfile_Form()
    if form.validate_on_submit():
        current_user.real_name=form.real_name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data

        avatar=request.files['avatar']


        fname=avatar.filename
        UPLOAD_FOLDER=current_app.config['UPLOAD_FOLDER']
        ALLOW_EXT=['png','jpg','jpeg','gif']
        flag='.'in fname and fname.rsplit('.',1)[1] in ALLOW_EXT
        if fname is None:
            if not flag:
                flash('error')
                return redirect(url_for('.user',name=current_user.name))
        avatar.save('{}{}_{}'.format(UPLOAD_FOLDER, current_user.name, fname))
        current_user.real_avatar = '/static/avatar/{}_{}'.format(current_user.name, fname)
        db.session.add(current_user)






        db.session.commit()
        flash('个人信息已保存')
        return redirect(url_for('blog.user',name=current_user.name))
    form.real_name=current_user.real_name
    form.location=current_user.location
    form.about_me=current_user.about_me
    return render_template('edit_profile.html',form=form)

