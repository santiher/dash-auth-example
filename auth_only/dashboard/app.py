import logging

from dash import Dash

from dashboard.layout import get_layout


def main():
    app.run_server(debug=True)


logging.basicConfig(level=logging.INFO)
app = Dash(__name__)
server = app.server  # the Flask app for gunicorn
app.title = 'Example dashboard'
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.layout = get_layout()
imported_callbacks = False  # Hack for easier example
if not imported_callbacks:
    import dashboard.callbacks  # noqa
    imported_callbacks = True


if __name__ == '__main__':
    main()
