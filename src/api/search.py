
""" This module contains API endpoints related to searching for interviews. """

import flask
import flask_restful
import peewee
from datetime import datetime
from flask import session

import data
import user
import interview

# Fields that are available as search fields and their corresponding ORM field
USER_SEARCH_FIELDS = {
                      'username'   : data.InterviewboxUser.username,
                      'email'      : data.InterviewboxUser.email,
                      'firstname'  : data.InterviewboxUser.firstname,
                      'lastname'   : data.InterviewboxUser.lastname,
                      'education'  : data.InterviewboxUser.education,
                      'employment' : data.InterviewboxUser.employment,
                      'position' : data.InterviewboxUser.position
                     }

class SearchUser(flask_restful.Resource):
    """
    This endpoint takes optional parameters to search by and returns a list
    of matching usernames.  It then filters the result by availability.
    """
    def post(self):
        post_data = flask.request.form
        print post_data
        response = {}
        try:
            if not 'id' in session:
                raise Exception('No id given')
            else:
                current_user_id = session['id']

            date = post_data['date']
            start_time = post_data['start_time']
            end_time = post_data['end_time']
            start_datetime = datetime.strptime(date + ' ' + start_time, '%Y-%m-%d %H:%M')
            end_datetime = datetime.strptime(date + ' ' + end_time, '%Y-%m-%d %H:%M')
            start_availability = interview.datetime_to_weekly_availability(start_datetime)
            # make sure there's at least an hour long block
            end_availability = interview.datetime_to_weekly_availability(end_datetime) - 2

            my_upcoming_inteviews = interview.handle_get_upcoming_interviews({'id' : current_user_id})['interviews']

            user_list = set()
            user_list.update(get_users_matching_fields(post_data))
            response['results'] = []
            for user_id in user_list:
                user_profile = user.handle_get_user({'id' : user_id})
                interviewer_upcoming_inteviews = interview.handle_get_upcoming_interviews({'id' : user_id})['interviews']
                if user_profile['status'] == 'success':
                    user_profile['user']['available_start_timestamps'] = []
                    user_profile['user']['available_start_timestamps_display'] = []
                    avails = user.handle_get_availability(user_id)['availability']
                    for avail in avails:
                        avail_timestamp = interview.weekly_availability_to_timestamp(avail, start_datetime)
                        no_overlapping = True
                        # check interviewer's availability
                        for existing_interview in interviewer_upcoming_inteviews:
                            if ((avail_timestamp >= existing_interview['date'] and avail_timestamp < existing_interview['date'] + 3600) or
                                (existing_interview['date'] >= avail_timestamp and existing_interview['date'] < avail_timestamp + 3600)):
                                no_overlapping = False
                                break

                        # check my availability
                        if no_overlapping:
                            for existing_interview in my_upcoming_inteviews:
                                if ((avail_timestamp > existing_interview['date'] and avail_timestamp < existing_interview['date'] + 3600) or
                                    (existing_interview['date'] > avail_timestamp and existing_interview['date'] < avail_timestamp + 3600)):
                                    no_overlapping = False
                                    break


                        avail_time_display = interview.weekly_availability_to_datetime(avail, start_datetime).strftime('%m/%d/%Y %H:%M')
                        if no_overlapping and avail >= start_availability and avail <= end_availability and ((avail+1) in avails):
                            user_profile['user']['available_start_timestamps'].append(avail_timestamp)
                            user_profile['user']['available_start_timestamps_display'].append(avail_time_display)
                    if len(user_profile['user']['available_start_timestamps']) > 0:
                        response['results'].append(user_profile['user'])
                else:
                    raise Exception(user_profile['message'])
            response['status'] = 'success'
        except Exception as e:
            response['status'] = 'failure'
            response['message'] = e.message
        return response

def get_users_matching_fields(post_data):
    """
    Helper method to get a list of users matching on non-time related fields.
    Dynamically build the Peewee query based on the fields present in the request.
    """
    excluded_match_list = set(['date', 'start_time', 'end_time'])
    matching_users = set()
    if len(post_data.keys()) == 0:
        return matching_users
    if not set(post_data.keys()).difference(excluded_match_list).issubset(set(USER_SEARCH_FIELDS.keys())):
        raise Exception('Unknown field in request')
    query_term = True
    for field in post_data:
        if field not in excluded_match_list and post_data[field] != '':
            query_term = query_term & (USER_SEARCH_FIELDS[field] == post_data[field])
    for entry in data.InterviewboxUser.select().where(query_term):
        matching_users.add(entry.id)
    return matching_users

