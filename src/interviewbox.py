#!/usr/bin/env python2

import flask
import flask_restful

import api as interviewbox_api
import web as interviewbox_web

app = flask.Flask(__name__)
api = flask_restful.Api(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def register_flask_blueprints():
    """
    This function registers all the UI URLs for the website.
    """
    app.register_blueprint(interviewbox_web.pages_blueprint)

def register_api_endpoints():
    """
    This function registers all the flask-restful endpoints for the API.
    The convention is that all API endpoints will have the 'api_' prefix in the URL.
    """
    api.add_resource(interviewbox_api.Login, '/api_login')
    api.add_resource(interviewbox_api.CreateUser, '/api_create_user')
    api.add_resource(interviewbox_api.GetUser, '/api_get_user')
    api.add_resource(interviewbox_api.GetProfile, '/api_get_profile')
    api.add_resource(interviewbox_api.SearchUser, '/api_search')
    api.add_resource(interviewbox_api.UpdateAvailability, '/api_availability')
    api.add_resource(interviewbox_api.Logout, '/api_logout')
    api.add_resource(interviewbox_api.EditUser, '/api_edit_user')
    api.add_resource(interviewbox_api.CreateInterview, '/api_create_interview')
    api.add_resource(interviewbox_api.GetUpcomingInterviews, '/api_upcoming_interviews')
    api.add_resource(interviewbox_api.GetPastInterviews, '/api_past_interviews')
    api.add_resource(interviewbox_api.AddFeedbackToInterview, '/api_add_interview_feedback')

def main():
    """
    This is the main entry point of the flask application.
    It registers the API and UI endpoints and starts the web server.
    """
    register_flask_blueprints()
    register_api_endpoints()
    app.run(debug=True)

if __name__ == '__main__':
    main()

