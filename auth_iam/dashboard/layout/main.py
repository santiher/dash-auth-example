import dash_core_components as dcc
import dash_html_components as html
import flask

from dashboard.layout.finance import layout as finance
from dashboard.layout.marketing import layout as marketing


def get_layout(get_allowed_resources):
    """Returns the main layout.

    Parameters
    ----------
    get_allowed_resources: callable
        A callable that returns the current request's allowed resources
    """
    def serve_layout():
        # For a user only return the current page
        if flask.has_request_context():
            allowed_resources = get_allowed_resources()
            return get_user_layout(allowed_resources, False)
        # For dash at building time return everthing for components and
        # callbacks validation
        return full_layout
    return serve_layout


def get_user_layout(allowed_resources, full):
    """Builds the layout for a user.

    Parameters
    ----------
    allowed_resources: [str]
        A list of sections to display.
    full: Boolean
        If true all the sections will be displayed.
    """
    user_layout = html.Div([
        dcc.Location(id='_url', refresh=False),
        get_navbar(allowed_resources, full),
        html.Div(id='_section', className='content'),
    ])
    return user_layout


def get_navbar(allowed_resources, full):
    """Returns the navigation bar.

    Parameters
    ----------
    allowed_resources: [str]
        A list of sections to display.
    full: Boolean
        If true all the sections will be displayed.
    """
    if full or '_all_' in allowed_resources:
        allowed_resources = list(sections)
    items = []
    for i, section_name in enumerate(allowed_resources):
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
full_layout = html.Div([get_user_layout([], True), *sections.values()])
