import re

from datetime import datetime, timedelta

import jwt

from flask import abort, make_response, redirect, request
from werkzeug.exceptions import BadRequest

from dashboard.auth.users import user_access


class Authorizer:

    auth_info_regex = re.compile(
        r'DASHBOARD-AUTH username=([^/]*)/password=([^/]*)')

    def __init__(self, secret='change_me', cookie_max_age=None,
                 token_duration=timedelta(days=7), cookie_name='dashboard_jwt',
                 algorithm='HS256'):
        """Validates json web tokens and users.

        Parameters
        ----------
        secret: str
            Secret key to encode json web tokens
        cookie_max_age: int or None
            None: the cookie remains in the browser until it is closed.
            int: duration in seconds
        token_duration: datetime.timedelta
            Duration of the validity of the json web token.
        cookie_name: str
            Name used to store the cookie.
        algorithms: str
            Algorithm name to encode / decode the tokens.
        """
        self.secret = secret
        self.cookie_max_age = cookie_max_age
        self.token_duration = token_duration
        self.cookie_name = cookie_name
        self.algorithm = algorithm

    def validate(self):
        """Validates if the flask request is authenticated.
        Checks json web token cookie payload, sets the cookie, verifies user
        and password, redirects the user, all as required.
        """
        payload = self.read_cookie(request)
        if isinstance(payload, dict):
            return self.validate_cookie(payload)
        elif payload is not None:
            return payload
        return self.validate_login()

    def default_resource(self, default='/'):
        """Returns the default allowed resource for the user if authenticated.
        """
        payload = self.read_cookie(request)
        if isinstance(payload, dict):
            allowed_resources = [
                x for x in payload['allowed_resources'] if x != '_all_']
            if allowed_resources:
                return f'/{allowed_resources[0]}'
            return default
        return ''

    def read_cookie(self, request):
        """Reads an encoded cookie and returns the payload.

        Parameters
        ----------
        request: flask.request

        Returns
        -------
        dict
            The cookie payload
        """
        cookie = request.cookies.get(self.cookie_name)
        if cookie:
            try:
                return jwt.decode(cookie, self.secret,
                                  algorithms=self.algorithm)
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return self.clean_cookie()

    def allowed_resources(self):
        """Reads an encoded cookie and returns the allowed_resources.

        Parameters
        ----------
        request: flask.request

        Returns
        -------
        [str]
            The cookie payload's allowed_resources
        """
        if request:
            cookie = request.cookies.get(self.cookie_name)
            if cookie:
                try:
                    payload = jwt.decode(
                        cookie, self.secret, algorithms=self.algorithm)
                    return payload.get('allowed_resources', [])
                except (jwt.DecodeError, jwt.ExpiredSignatureError):
                    pass
        return []

    def validate_cookie(self, payload):
        """Validates if the json web token in the cookies is ok."""
        return self.validate_resource_access(payload)

    def validate_login(self):
        """Validates if the login is correct."""
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header is None:
                return False, self.redirect_response()
            credentials = self.auth_info_regex.match(auth_header)
            if credentials is None:
                return False, self.redirect_response()
            username, password = credentials.groups()
            user_data = user_access.validate_user(username, password)
            if user_data:
                payload, expires = self.generate_payload(user_data)
                return self.set_cookie(payload, expires)
            return False, abort(401)
        except (BadRequest, KeyError):
            return False, abort(400)

    def validate_resource_access(self, payload):
        """Validates that the user has access to the requested resource."""
        if user_access.validate_resource_access(payload, request):
            return True, make_response('/', 200)
        return False, make_response(redirect('/'), 307)

    def generate_payload(self, user_data):
        """Generates the json web token payload.

        Parameters
        ----------
        user_data: dict
            Dictionary with the user's data.
        """
        expires = datetime.now() + self.token_duration
        payload = {'user': user_data.get('username'),
                   'exp': expires,
                   'allowed_resources': user_data.get('allowed_resources')}
        payload = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return payload, expires

    def set_cookie(self, payload, expires):
        """Sets the cookie with the json web token payload."""
        res = make_response('/', 200)
        res.set_cookie(
            self.cookie_name,
            value=payload,
            max_age=self.cookie_max_age,
            expires=expires)
        return True, res

    def clean_cookie(self):
        res = self.redirect_response()
        res.set_cookie(self.cookie_name, value='', expires=0)
        return False, res

    @staticmethod
    def redirect_response():
        return make_response(redirect('/login'), 302)
