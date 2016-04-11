
import flask
import requests
import os
from jinja2 import TemplateNotFound
from functools import wraps
from flask import session, redirect, url_for, request

pages_blueprint = flask.Blueprint('pages_blueprint', __name__, template_folder='../static')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@pages_blueprint.route('/')
@pages_blueprint.route('/index')
def index():
    return flask.render_template('index.html') 

@pages_blueprint.route('/profile', methods=['post', 'get'])
@login_required
def profile():
    # if request.method == 'POST':
    #     return str(request.form)
    return flask.render_template('profile.html')  

@pages_blueprint.route('/edit_profile')
@login_required
def edit_profile():
    return flask.render_template('edit_profile.html')  

@pages_blueprint.route('/search')
@login_required
def search():
    times = []
    for i in range(24):
        hr = str(i)
        if len(hr) == 1:
            hr = '0' + hr
        times.append(hr +':00')
        times.append(hr +':30')
    return flask.render_template('search.html', times = times)  

@pages_blueprint.route('/search_result')
@login_required
def search_result():
    return flask.render_template('search_result.html')  

@pages_blueprint.route('/schedule')
@login_required
def schedule():
    return flask.render_template('schedule.html')  

@pages_blueprint.route('/contact')
@login_required
def contact():
    return flask.render_template('contact.html')

@pages_blueprint.route('/login')
def login():
    if 'id' in session:
        return redirect('/profile') 
    return flask.render_template('login.html')

@pages_blueprint.route('/register')
def register():
    return flask.render_template('register.html')
