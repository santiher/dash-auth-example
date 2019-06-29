class UserAccess:

    def validate_user(self, username, password):
        """Validates that the username and password match.

        Parameters
        ----------
        username: str
        password: str

        Returns
        -------
        dict
            Dictionary with the user's data, particularly user name and allowed
            resources.
        """
        user_data = users.get(username)
        if user_data and password == user_data.get('password'):
            return {
                'username': username,
                'extra_info': None,
                'allowed_resources': user_data.get('allowed_resources', [])}
        return False

    def validate_resource_access(self, payload, request):
        """Validates that the request is for granted resources annotated in the
        payload.
        original_uri will be something like /marketing

        Parameters
        ----------
        payload: dict
            A dictionary with the user payload.
            Should contain a list of valid resources under the *resources*
            keyword.
        request: flask.request
            The flask request to validate.
        """
        original_uri = request.path.lstrip('/')
        if not original_uri or original_uri.startswith('_'):
            return True
        requested_resource = original_uri.rsplit('/', 1)[0]
        return (requested_resource in payload.get('allowed_resources', []) or
                '_all_' in payload.get('allowed_resources', []))


users = {
    'mica': {
        'username': 'mica',
        'password': '1234',
        'allowed_resources': ['_all_']
        },
    'mike': {
        'username': 'mike',
        'password': '123456',
        'allowed_resources': ['marketing']
        }
    }
user_access = UserAccess()
