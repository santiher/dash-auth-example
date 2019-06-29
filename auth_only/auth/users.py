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
            return {'username': username,
                    'extra_info': None,
                    'allowed_resources': []}
        return False

    def validate_resource_access(self, payload, request):
        """Receives a payload from a user's cookie and a request and allows or
        denies access."""
        return True


users = {'mica': {'username': 'mica', 'password': '1234'},
         'mike': {'username': 'mike', 'password': '123456'}}
user_access = UserAccess()
