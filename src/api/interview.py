
""" This module contains the API endponits related to creating and scheduling interviews. """

import datetime
import flask
import flask_restful
import peewee
import time

from flask import session

import data
import tools
import search

class CreateInterview(flask_restful.Resource):
    """
    Create a new interview
    id - the first person in the interview
    target_id - the second person in the interview
    timestamp - the number of seconds since the unix epoch that the interview will take place
    """
    def post(self):
        return handle_create_interview(create_interview_wrapper(flask.request.form))

def create_interview_wrapper(post_data):
    """
    Create a new interview wrapper to convert post data to format above
    target_username - the interviewer's username
    timestamp - the unix timestamp of the interview start time
    """
    updated_post_data = {
        'id': None,
        'target_id': None,
        'time': None
    }
    if not 'id' in session:
        return post_data
    else:
        updated_post_data['id'] = session['id']

    updated_post_data['target_id'] = list(search.get_users_matching_fields({'username': post_data['target_username']}))[0]
    updated_post_data['timestamp'] = post_data['timestamp']
    return updated_post_data


class GetUpcomingInterviews(flask_restful.Resource):
    """
    Get upcoming interviews for a user
    id - the user to look for
    """
    def get(self):
        # return handle_get_upcoming_interviews(flask.request.args)
        return handle_get_upcoming_interviews({'id': session['id']})

class GetPastInterviews(flask_restful.Resource):
    """
    This endpoint retrieves all the past interviews for a user.  It requires one parameter.
    id - the database ID of the user.
    """
    def get(self):
        # return handle_get_past_interviews(flask.request.args)
        return handle_get_past_interviews({'id': session['id']})

class AddFeedbackToInterview(flask_restful.Resource):
    """
    Add feedback to an interview.
    id - the database ID of the interview
    feedback - a list of feedback strings to add to the interview
    """
    def post(self):
        return handle_add_feedback_to_interview(flask.request.form)

def handle_create_interview(post_data):
    """
    Create a new interview.
    id - the database ID of the scheduling user
    target_id - the person with whom the interview will be scheduled
    timestamp - the time at which the interview will take place

    Note both users must be available at the provided timestamp.
    """
    print post_data
    response = {}
    try:
        user_id = get_id(post_data)
        get_user_data_object_from_id(user_id)
        target_id = get_target_id(post_data)
        get_user_data_object_from_id(target_id)
        timestamp = get_timestamp(post_data)
        validate_user_is_available(user_id, timestamp)
        validate_user_is_available(target_id, timestamp)
        data.Interview.create(user1=user_id, user2=target_id, time=timestamp)
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

def handle_get_upcoming_interviews(get_data):
    """
    Fetch all upcoming interviews for a given user from the database
    id - the user ID for whom the interviews need to be fetched
    """
    response = {}
    try:
        user_id = get_id(get_data)
        get_user_data_object_from_id(user_id)
        interviews = []
        print 'the current user is', user_id
        for interview in data.Interview.select().where(((data.Interview.user1 == user_id) | (data.Interview.user2 == user_id)) &
                                                       (data.Interview.time > datetime.datetime.now())):
            interview_response = {}
            interview_response['date'] = time.mktime(interview.time.timetuple())
            interview_response['id'] = interview.id
            if int(interview.user1.id) == int(user_id):
                interview_response['person'] = interview.user2.id
                interview_response['person_firstname'] = interview.user2.firstname
            else:
                interview_response['person'] = interview.user1.id
                interview_response['person_firstname'] = interview.user1.firstname
            interviews.append(interview_response)
        response['interviews'] = interviews
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

def handle_get_past_interviews(get_data):
    """
    Fetch all past interviews for a given user from the database
    id - the user ID for whom the interviews need to be fetched
    """
    response = {}
    try:
        user_id = get_id(get_data)
        interviews = []
        for interview in data.Interview.select().where(((data.Interview.user1 == user_id) | (data.Interview.user2 == user_id)) &
                                                       (data.Interview.time < datetime.datetime.now())):
            interview_response = {}
            interview_response['date'] = time.mktime(interview.time.timetuple())
            interview_response['id'] = interview.id
            if int(interview.user1.id) == int(user_id):
                interview_response['person'] = interview.user2.id
                interview_response['person_firstname'] = interview.user2.firstname
            else:
                interview_response['person'] = interview.user1.id
                interview_response['person_firstname'] = interview.user1.firstname
            interview_response['feedback'] = []
            for feedback in data.InterviewFeedback.select().where(data.InterviewFeedback.interview_id == interview.id):
                interview_response['feedback'].append(feedback.feedback)
            interviews.append(interview_response)
        response['interviews'] = interviews
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

def handle_add_feedback_to_interview(post_data):
    """
    Add feedback to an interview.
    interview_id - the database interview ID that the feedback will be added to
    fedback - the string to store as feedback
    """
    response = {}
    try:
        interview_id = get_id(post_data)
        get_interview_data_object_from_id(interview_id)
        feedback = get_feedback(post_data)
        data.InterviewFeedback.create(interview_id=interview_id, feedback=feedback)
        response['status'] = 'success'
    except Exception as e:
        response['status'] = 'failure'
        response['message'] = e.message
    return response

@tools.escape_html
def get_id(post_data):
    """ Helper method to get the user_id from a JSON dictionary """
    if 'id' not in post_data:
        raise Exception('Missing required field: id')
    try:
        return int(post_data['id'])
    except ValueError:
        raise Exception('Invalid id specified')

@tools.escape_html
def get_target_id(post_data):
    """ Helper method to get the target_id from a JSON dictionary """
    if 'target_id' not in post_data:
        raise Exception('Missing required field: target_id')
    try:
        return int(post_data['target_id'])
    except ValueError:
        raise Exception('Invalid target_id specified')

def get_user_data_object_from_id(user_id):
    """ Helper method to get the user object from the database for a given user id """
    try: user = data.InterviewboxUser.get(data.InterviewboxUser.id == user_id)
    except peewee.DoesNotExist:
        raise Exception('No such user')
    return user

def get_interview_data_object_from_id(interview_id):
    """ Helper method to get the interview object from the database for a given interview id """
    try:
        interview = data.Interview.get(data.Interview.id == interview_id)
    except peewee.DoesNotExist:
        raise Exception('No such interview')
    return interview

@tools.escape_html
def get_feedback(post_data):
    """ Helper method to get the feedback from a JSON dictionary """
    if 'feedback' not in post_data:
        raise Exception('Missing requried field: feedback')
    feedback = post_data['feedback']
    if len(feedback) < 1 or len(feedback) > 255:
        raise Exception('Feedback must be between 1 and 255 characters')
    return feedback

def get_timestamp(post_data):
    """ Helper method to get the timestamp from a JSON dictionary """
    if 'timestamp' not in post_data:
        raise Exception('Missing required field: timestamp')
    try:
        timestamp = datetime.datetime.fromtimestamp(int(post_data['timestamp']))
    except ValueError:
        raise Exception('Invalid timestamp')
    if datetime.datetime.now() > timestamp:
        raise Exception('Date must be in the future')
    return timestamp

def validate_user_is_available(target_id, timestamp):
    """ Verify that a user is available at the provided timestamp """
    pass

def datetime_to_weekly_availability(datetime_obj):
    """ Convert a python time object to a numeric representation of the timeslot """
    return (datetime_obj.isoweekday()-1) * 48 + int(datetime_obj.strftime('%H')) * 2 + int(datetime_obj.strftime('%M'))/30

def weekly_availability_to_datetime(weekly_avail, base_datetime_obj):
    """ Convert a numeric representation of the timeslot to a timestamp """
    hr = str(weekly_avail%48/2)
    if len(hr) == 1:
        hr = '0' + hr
    mm = weekly_avail%48%2
    if mm == 0:
        mm = '00'
    else:
        mm = '30'
    construct_string = (base_datetime_obj.strftime('%Y-%m-%d') + ' ' + hr + ':' + mm)
    return datetime.datetime.strptime(construct_string, '%Y-%m-%d %H:%M')

def weekly_availability_to_timestamp(weekly_avail, base_datetime_obj):
    """ Convert a numeric representation of the timeslot to a python time object """
    return time.mktime(weekly_availability_to_datetime(weekly_avail, base_datetime_obj).timetuple())

def timestamp_to_weekly_availability(timestamp):
    """ Convert a timestamp object to a numeric representation of the timeslot """
    return datetime_to_weekly_availability(datetime.datetime.fromtimestamp(timestamp))

