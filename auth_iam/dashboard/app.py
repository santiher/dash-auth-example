import logging

from dashboard.auth import add_authentication_routes, Authorizer, DashIam
from dashboard.layout import get_layout


def main():
    app.run_server(debug=True)


logging.basicConfig(level=logging.INFO)
authorizer = Authorizer(secret='change_me_for_token_encryption')
app = DashIam(authorizer, __name__)
server = app.server  # the Flask app for gunicorn
app.title = 'Example dashboard'
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.layout = get_layout(authorizer.allowed_resources)
imported_callbacks = False  # Hack for easier example
if not imported_callbacks:
    import dashboard.callbacks  # noqa
    imported_callbacks = True
    add_authentication_routes(app, authorizer)


if __name__ == '__main__':
    main()
