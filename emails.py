#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/22 21:37
# @File    : email.py
"""
邮箱发送
"""


from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from Main import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

