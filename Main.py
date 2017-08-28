#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 14:50
# @File    : Start.py
"""
应用启动类
"""


from __future__ import unicode_literals
from flask import Flask,render_template,flash,url_for,redirect,Blueprint
from flask_bootstrap import Bootstrap
from flask_pagedown import PageDown
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_login import LoginManager,login_user,UserMixin,logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from flask_mail import Mail, Message

#解决flash的一个bug
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)



login_manger = LoginManager()
login_manger.session_protection = 'strong'
login_manger.login_view = 'blog.login'
db = SQLAlchemy()
mail=Mail()


@login_manger.user_loader
def load_user(user_id):
    from Model import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    # 各项插件的配置
    app.config['SECRET_KEY'] = 'kkk'
    app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:1996112lin@localhost/flask1'#配置数据库

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['FLASKY_FOLLOWERS_PER_PAGE'] = 5
    app.config['FLASKY_POSTS_PER_PAGE'] = 5
    app.config['FLASKY_COMMENTS_PER_PAGE'] = 5

    app.config['UPLOAD_FOLDER'] = 'E:/Python工作空间/Flasky0.1/static/avatar/'
    app.config['MAIL_DEBUG'] = True  # 开启debug，便于调试看信息
    app.config['MAIL_SUPPRESS_SEND'] = False  # 发送邮件，为True则不发送
    app.config['MAIL_SERVER'] = 'smtp.qq.com'  # 邮箱服务器
    app.config['MAIL_PORT'] = 465  # 端口
    app.config['MAIL_USE_SSL'] = True  # 重要，qq邮箱需要使用SSL
    app.config['MAIL_USE_TLS'] = False  # 不需要使用TLS
    app.config['MAIL_USERNAME'] = 'xxxxxxxxxxxx@qq.com'  # 填邮箱
    app.config['MAIL_PASSWORD'] = 'xxxxxxxxxxxx'  # 填授权码
    app.config['MAIL_DEFAULT_SENDER'] = 'xxxxxxxxxxxxqq.com'  # 填邮箱，默认发送者
    app.config['FLASKY_MAIL_SUBJECT_PREFIX']='[blog]'
    app.config['FLASKY_MAIL_SENDER']='xxxxxxxxxxxx@qq.com'


    db.init_app(app)
    page_down = PageDown()
    page_down.init_app(app)
    bootstrap = Bootstrap(app)
    moment = Moment(app)
    mail.init_app(app)

    login_manger.init_app(app)

    from auth_Views import auth
    app.register_blueprint(auth, url_prefix='/auth')
    from blog_Views import blog
    app.register_blueprint(blog, url_prefix='/blog')
    return app


if __name__ == '__main__':
    app=create_app()
    app.run(port=6155, debug=True)