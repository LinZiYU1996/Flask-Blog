#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/23 18:09
# @File    : Forms.py

from __future__ import unicode_literals
from wtforms import StringField,SubmitField,PasswordField,TextAreaField,FileField
from wtforms.validators import  Required,Length
from flask_wtf import FlaskForm
from flask_pagedown.fields import  PageDownField
from Model import User
from wtforms import ValidationError

#登录表单
class Login_Form(FlaskForm):
    email=StringField('email',validators=[Required()])
    pwd=PasswordField('pwd',validators=[Required()])
    submit=SubmitField('Login in')


#注册表单
class Register_Form(FlaskForm):
    email=StringField('email',validators=[Required()])


    name=StringField('name',validators=[Required()])
    pwd=PasswordField('pwd',validators=[Required()
                                        ,Length(3,10)])
    submit=SubmitField('register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册。')

    def validate_name(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用。')

class EditProfile_Form(FlaskForm):
    real_name=StringField('真实姓名',validators=[Length(0,64)])
    location=StringField('所在地',validators=[Length(0,64)])
    about_me=TextAreaField('形容你自己')
    avatar=FileField('头像')
    submit=SubmitField('Submit')

class PostForm(FlaskForm):
    body=PageDownField('What is you mind',validators=[Required()])
    submit=SubmitField('Submit')


class CommentForm(FlaskForm):
    body=StringField('评论',validators=[Required()])
    submit=SubmitField('提交')
