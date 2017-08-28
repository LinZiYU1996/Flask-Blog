#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/23 18:09
# @File    : Views.py
from __future__ import unicode_literals
from  flask import render_template,Blueprint,redirect,url_for,flash,request,current_app
from Main import login_manger
from Forms import Login_Form,Register_Form,PostForm
from Model import  User,Post,Permission
from flask_login import LoginManager,login_user,UserMixin,logout_user,login_required,current_user
from emails import send_email

from decorators import check_confirmed
blog=Blueprint('blog',__name__)  #蓝图

@blog.route('/register', methods=['GET', 'POST'])
def register():
    #注册
    from  Main import db
    form = Register_Form()
    if form.validate_on_submit():
        user = User(email=form.Email.data,
                    name=form.name.data,
                    password=form.pwd.data)
        db.session.add(user)
        db.session.commit()  #这里不能等数据库自动保存，因为用户在验证时需要登录
        token = user.generate_confirmation_token()  #生成HASH码
        send_email(user.email, 'Confirm Your Account',
                    'confirm', user=user, token=token)#发送验证信息
        flash('邮件已经发送！')
        return redirect(url_for('blog.login'))#重定向到登录页面
    return render_template('register.html', form=form)


@blog.route('/login',methods=['GET','POST'])

def login():
        form=Login_Form()

        if form.validate_on_submit():
            user=User.query.filter_by(email=form.email.data).first()
            if user is not  None and user.verify_password(form.pwd.data):
                login_user(user)
                flash('登录成功')

                return redirect(request.args.get('next') or url_for('blog.index'))
            else:
                flash('用户或密码错误')
                return render_template('login.html',form=form)
        return render_template('login.html',form=form)
#用户登出
@blog.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出登录')
    return redirect(url_for('blog.index'))


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



@blog.before_app_request
def before_request():
    # if current_user.is_authenticated() \
    #         and not current_user.confirmed \
    #         and request.endpoint[:5] != 'blog.' \
    #         and request.endpoint != 'static':
    #     # return redirect(url_for('blog.inde'))



    if current_user.is_authenticated:
        flash('aaa')
        if not current_user.confirmed :
            return render_template('unconfirmed.html')



@blog.route('/unconfirmed')
@login_required
def unconfirmed():
    # if current_user.is_anonymous or current_user.confirmed:
    #     return redirect(url_for('blog.index'))
    return render_template('unconfirmed.html')

@blog.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        #如果你已经激活过了
        return redirect(url_for('blog.index'))
    if current_user.confirm(token):
        #去激活并且激活成功了
        flash('账户激活成功！')
    else:
        flash('你是盗号的还是迟到鬼?')
    return redirect(url_for('blog.index'))



@blog.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'confirm', user=current_user, token=token)
    flash('新的确认电子邮件已经通过邮件发送给您。')
    return redirect(url_for('blog.index'))













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