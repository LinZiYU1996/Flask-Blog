#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/23 22:46
# @File    : decorators.py
from functools import wraps

from flask import flash, redirect, url_for
from flask.ext.login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('blog.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function


