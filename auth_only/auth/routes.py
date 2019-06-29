import os

from functools import wraps
from os.path import join as join_path

from dash import Dash
from flask import make_response, render_template_string, redirect


excluded_resources_endpoints = (
    '/login', '/logout', '/auth')


def add_routes(app, authorizer):
    """Adds authentication endpoints to a flask app.
    Decorates other endpoints to grant access.

    The endpoints are:

    * /login
        * Method: GET
    * /logout
        * Method: GET
        * Erases cookies
    * /auth
        * Method: GET
        * Validates cookies if present or header authentication
        * Header:
            'Authorization: DASHBOARD-AUTH username=([^/]*)/password=([^/]*)'
        * Sets cookies on login
        * Rejects unauthorized users

    Parameters
    ----------
    app: flask.Flask or dash.Dash
        The flask or dash application
    excluded_resources_endpoints: tuple(str)
        Tuple with endpoints where access must not be checked.
    """
    def login():
        ok, _ = authorizer.validate()
        if ok:
            return make_response(redirect('/'), 307)
        return render_template_string(login_template)

    def logout():
        _, response = authorizer.clean_cookie()
        return response

    def auth():
        _, response = authorizer.validate()
        return response

    def authorize_endpoint(function):
        @wraps(function)
        def authorized_function(*args, **kwargs):
            ok, response = authorizer.validate()
            if ok:
                return function(*args, **kwargs)
            return response
        return authorized_function

    if isinstance(app, Dash):
        app = app.server
    login_template = load_template('login.html')
    app.add_url_rule('/auth', '/auth', auth)
    app.add_url_rule('/login', '/login', login)
    app.add_url_rule('/logout', '/logout', logout)
    for endpoint, function in app.view_functions.items():
        if endpoint not in excluded_resources_endpoints:
            app.view_functions[endpoint] = authorize_endpoint(function)


def load_template(filename):
    """Loads the login html template."""
    pyfile_path = os.path.dirname(os.path.abspath(__file__))
    path = join_path(pyfile_path, 'templates', filename)
    with open(path, 'r') as f:
        return f.read().strip()
