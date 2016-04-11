
"""
This module contains API endpoints related to user registration and profiles.

The flask_restful API classes call a helper method to allow the API endpoints
to be used internally in the server without a network call.
"""

import flask
import flask_restful
import peewee
import re
import sys
import werkzeug.security

import data
import tools

import pickle

from flask import session

# Fields that can be edited by the user
USER_EDIT_FIELDS = frozenset([
                   'firstname',
                   'lastname',
                   'education',
                   'email',
                   'employment',
                   'position',
                   'id',
                   'availability',
                   ])

class CreateUser(flask_restful.Resource):
    """
    This endpoint requires seven parameters.
    username - the 5-20 character username
    password - the 8+ character password
    firstname - the 1-255 character firstname
    lastname - the 1-255 character lastname
    email - the 5-255 character email address that matches the regex \w+@\w+\.\w+
    position - the 1-255 position of the person
    is_interviewer - 1 is the user is an interviewer, 0 if the user is an applicant
    """
    def post(self):
        return handle_create_user(flask.request.form)

class Login(flask_restful.Resource):
    """
    This endpoint requires two parameters
    username - the 5-20 character username
    password - the 8+ character password
    """
    def post(self):
        return handle_login(flask.request.form)

class Logout(flask_restful.Resource):
    """
    This endpoint logs out user
    """
    def post(self):
        return handle_logout(flask.request.form)

class GetProfile(flask_restful.Resource):
    """
    Gets the current logged in user
    """
    def get(self):
        return handle_get_profile()

class GetUser(flask_restful.Resource):
    """
    This endpoint requires one parameter
    id - the database ID of the user
    """
    def get(self):
        return handle_get_user(flask.request.args)

class EditUser(flask_restful.Resource):
    """
    This endpoint modifies a user
    id - the database ID of the user
    """
    def put(self):
        return handle_edit_user(flask.request.form)

class UpdateAvailability(flask_restful.Resource):
    """
    This endpoint receive and update time availability set by interviewers from the schedule page
    """
    def get(self):
        return handle_get_availability()

    def put(self):
        return handle_update_availability(flask.request.form)

def handle_get_availability(user_id=None):
    """ Helper method to handle the get_availability API call. """
    response = {}
    try:
        if user_id is None:
            if not 'id' in session:
                raise Exception('No id given')
            else:
                user_id = session['id']

        user = get_user_data_object_from_id(user_id)
        if (user.availability is None):
            response['status'] = 'success'
            response['availability'] = []
        else:
            data = pickle.loads(str(user.availability))

            response['status'] = 'success'
            response['availability'] = tools.unget_ranges(pickle.loads(str(user.availability)))

    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

def handle_update_availability(put_data):
    """ Helper method to handle the update_availability API call. """
    response = {}
    try:
        if not 'id' in session:
            raise Exception('No id given')
        if 'availability' not in put_data:
            raise Exception('No availability provided.')


        if len(put_data['availability']) < 1:
            avail = []
        else:
            avail = tools.get_ranges([int(x) for x in put_data['availability'].split(';')])
        return handle_edit_user({'availability': pickle.dumps(avail)})

    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
        return response

def handle_create_user(post_data):
    """ Helper method to handle the create_user API call. """
    response = {}
    try:
        username = get_username(post_data)
        validate_user_doesnt_exist(username)
        password_hash = get_password_hash(post_data)
        firstname = get_firstname(post_data)
        lastname = get_lastname(post_data)
        email = get_email(post_data)
        education = get_education(post_data)
        employment = get_employment(post_data)
        position = get_position(post_data)
        is_interviewer = get_is_interviewer(post_data)
        data.InterviewboxUser.create(username=username, password=password_hash, firstname=firstname,
                                        lastname=lastname, email=email, total_ratings=0, num_ratings=0,
                                        is_interviewer=is_interviewer, education=education, employment=employment,
                                        position=position)
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

def handle_login(post_data):
    """ Helper method to handle the login API call. """
    response = {}
    try:
        username = get_username(post_data)
        password = get_password(post_data)
        user = get_user_data_object(username)
        validate_credentials(user.password, password)
        session['id'] = user.id
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

def handle_logout(post_data):
    """ Helper method to handle the logout API call. """
    del session['id']
    return {'status' : 'success'}

def handle_get_profile():
    """ Helper method to handle the get_profile API call. """
    response = {}
    if 'id' in session:
        try:
            user_id = session['id']
            user = get_user_data_object_from_id(user_id)
            user_data = {}
            user_data['username'] = user.username
            user_data['firstname'] = user.firstname
            user_data['lastname'] = user.lastname
            user_data['email'] = user.email
            if user.num_ratings == 0:
                user_data['rating'] = 0
            else:
                user_data['rating'] = float(user.total_ratings) / user.num_ratings
            user_data['is_interviewer'] = user.is_interviewer
            user_data['resume'] = user.resume
            user_data['education'] = user.education
            user_data['employment'] = user.employment
            user_data['position'] = user.position
            response['user'] = user_data
            response['status'] = 'success'
            return response
        except Exception as e:
            response['message'] = e.message

    response['status'] = 'failure'
    response['message'] = 'Not currently logged in.'
    return response

def handle_get_user(get_data):
    """ Helper method to handle the get_user API call. """
    response = {}
    try:
        user_id = get_id(get_data)
        user = get_user_data_object_from_id(user_id)
        user_data = {}
        user_data['username'] = user.username
        user_data['firstname'] = user.firstname
        user_data['lastname'] = user.lastname
        user_data['email'] = user.email
        if user.num_ratings == 0:
            user_data['rating'] = 0
        else:
            user_data['rating'] = float(user.total_ratings) / user.num_ratings
        user_data['is_interviewer'] = user.is_interviewer
        user_data['resume'] = user.resume
        user_data['education'] = user.education
        user_data['employment'] = user.employment
        user_data['position'] = user.position
        response['user'] = user_data
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

def handle_edit_user(put_data):
    """
    Helper method to handle the edit_user API call.

    This method looks at the JSON object as a dictionary of key -> new value.
    It then uses reflection to inspect the module and find the accompanying helper
    method to parse the new value from the JSON while validating the new value.

    This allows the edit call to more easily dynamically build the Peewee query
    to update the user entry without adding repetitive if statements while ensuring correctness.
    """
    response = {}
    try:
        if 'id' in session:
            user_id = session['id']
        else:
            user_id = get_id(put_data)
        if not set(put_data.keys()).issubset(USER_EDIT_FIELDS):
            raise Exception('Invalid field to edit in request')
        this_module = sys.modules[__name__]
        query_term = {}
        for field in put_data:
            if field == 'id':
                continue
            get_func = getattr(this_module, 'get_{}'.format(field), None)
            if get_func is None:
                raise Exception('Internal server error - no get function for {}'.format(field))
            value = get_func(put_data)
            query_term[field] = value
        data.InterviewboxUser.update(**query_term).where(data.InterviewboxUser.id == user_id).execute()
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

@tools.escape_html
def get_username(post_data):
    """ Helper method to get the username from a JSON dictionary. """
    if 'username' not in post_data:
        raise Exception('Missing required field: username')
    username = post_data['username']
    if len(username) < 5 or len(username) > 20:
        raise Exception('Username must be between 5 and 20 characters')
    return username

@tools.escape_html
def get_id(post_data):
    """ Helper method to get the user_id from a JSON dictionary. """
    if 'id' not in post_data:
        raise Exception('Missing required field: id')
    try:
        return int(post_data['id'])
    except ValueError:
        raise Exception('Invalid id specified')

def validate_user_doesnt_exist(username):
    """ Helper method to validate that a username doesn't already exist in the database. """
    try:
        existing_user = data.InterviewboxUser.get(username = username)
        raise Exception('User already exists')
    except peewee.DoesNotExist:
        # user does not exist, which is what we want
        return

def get_password(post_data):
    """ Helper method to get the password from a JSON dictionary. """
    if 'password' not in post_data:
        raise Exception('Missing required field: password')
    password = post_data['password']
    if len(password) < 8:
        raise Exception('Password must be 8 or more characters')
    return password

def get_availability(post_data):
    """ Helper method to get the availability from a JSON dictionary. """
    if 'availability' not in post_data:
        raise Exception('Missing required field: availability')
    availability = post_data['availability']
    return availability


def get_password_hash(post_data):
    """ Helper method to get the password from a JSON dictionary return its hash. """
    if 'password' not in post_data:
        raise Exception('Missing required field: password')
    password = post_data['password']
    if len(password) < 8:
        raise Exception('Password must be 8 or more characters')
    return werkzeug.security.generate_password_hash(password)

@tools.escape_html
def get_firstname(post_data):
    """ Helper method to get the firstname from a JSON dictionary. """
    if 'firstname' not in post_data:
        raise Exception('Missing required field: firstname')
    firstname = post_data['firstname']
    if len(firstname) < 1 or len(firstname) > 255:
        raise Exception('Firstname must be between 1 and 255 characters')
    return firstname

@tools.escape_html
def get_lastname(post_data):
    """ Helper method to get the lastname from a JSON dictionary. """
    if 'lastname' not in post_data:
        raise Exception('Missing required field: lastname')
    lastname = post_data['lastname']
    if len(lastname) < 1 or len(lastname) > 255:
        raise Exception('Lastname must be between 1 and 255 characters')
    return lastname

@tools.escape_html
def get_email(post_data):
    """ Helper method to get the email from a JSON dictionary. """
    if 'email' not in post_data:
        return 'unspecified@interviewbox.com'
    email = post_data['email']

    if len(email) < 1:
        return 'unspecified@interviewbox.com'
    if len(email) > 255:
        raise Exception('Email must be between 1 and 255 characters')
    if re.match("\w+@\w+\.\w+", email) is None:
        raise Exception('Invalid email address')
    return email

@tools.escape_html
def get_education(post_data):
    """ Helper method to get the education from a JSON dictionary. """
    if 'education' not in post_data:
        return 'Unspecified'

    education = post_data['education']
    if len(education) < 1:
        return 'Unspecified'
    if len(education) > 255:
        raise Exception('Education must be between 1 and 255 characters')
    return education

@tools.escape_html
def get_employment(post_data):
    """ Helper method to get the employment from a JSON dictionary. """
    if 'employment' not in post_data:
        return 'Unspecified'

    employment = post_data['employment']
    if len(employment) < 1:
        return 'Unspecified'
    if len(employment) > 255:
        raise Exception('Employment must be between 1 and 255 characters')
    return employment

@tools.escape_html
def get_position(post_data):
    """ Helper method to get the position from a JSON dictionary. """
    if 'position' not in post_data:
        return 'Unspecified'

    position = post_data['position']
    if len(position) < 1:
        return 'Unspecified'
    if len(position) > 255:
        raise Exception('Position must be between 1 and 255 characters')
    return position

def validate_email_doesnt_exist(email):
    """ Helper method to validate that an email doesn't already exist in the database. """
    try:
        existing_user = data.InterviewboxUser.get(email = email)
        raise Exception('Email already exists')
    except peewee.DoesNotExist:
        # email does not exist, which is what we want
        return

def get_user_data_object(username):
    """ Helper method to get the user object based on the username. """
    try:
        user = data.InterviewboxUser.get(username = username)
    except peewee.DoesNotExist:
        raise Exception('No such user')
    return user

def get_user_data_object_from_id(user_id):
    """ Helper method to get the user object based on the user_id. """
    try:
        user = data.InterviewboxUser.get(data.InterviewboxUser.id == user_id)
    except peewee.DoesNotExist:
        raise Exception('No such user')
    return user

def get_is_interviewer(post_data):
    """ Helper method to get the is_interview field from a JSON dictionary. """
    if 'is_interviewer' not in post_data:
        raise Exception('Missing required field: is_interviewer')
    is_interviewer = post_data['is_interviewer']
    if is_interviewer != '0' and is_interviewer != '1':
        raise Exception('is_interviewer must be 0 or 1 ' + is_interviewer)
    return int(is_interviewer)

def validate_credentials(stored_pw, provided_pw):
    """ Validate a user's password using werkzeug's built in salt-and-hash functionality. """
    if not werkzeug.security.check_password_hash(stored_pw, provided_pw):
        raise Exception('Invalid password')

