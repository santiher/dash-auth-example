import dash_core_components as dcc
import dash_html_components as html
import flask

from dashboard.layout.finance import layout as finance
from dashboard.layout.marketing import layout as marketing


def get_layout():
    """Returns the main layout. """
    def serve_layout():
        # For a user only return the current page
        if flask.has_request_context():
            return user_layout
        # For dash at building time return everthing for components and
        # callbacks validation
        return full_layout
    return serve_layout


def get_navbar():
    """Returns the navigation bar."""
    items = []
    for i, section_name in enumerate(sections):
        list_item = html.Li(
           html.A(
               section_name.capitalize(),
               href=f'/{section_name}',
               id=f'_nav-bar-{section_name}',
               ),
        )
        items.append(list_item)
    # Add a logout button to send the user somewhere
    items.append(html.Li(html.A('Logout', href=f'/logout')))
    navbar = html.Ul(items)
    return navbar


sections = {'finance': finance, 'marketing': marketing}
user_layout = html.Div([
    dcc.Location(id='_url', refresh=False),
    get_navbar(),
    html.Div(id='_section', className='content'),
])
full_layout = html.Div([user_layout, *sections.values()])
