from dash.dependencies import Input, Output

from dashboard.app import app
from dashboard.layout.finance import layout as finance_layout
from dashboard.layout.marketing import layout as marketing_layout


@app.callback(
    [Output('_section', 'children'),
     Output('_nav-bar-finance', 'className'),
     Output('_nav-bar-marketing', 'className'),
     ],
    [Input('_url', 'pathname')]
)
def display_page(pathname):
    active, inactive = 'nav-link nav-active', 'nav-link'
    if pathname == '/finance':
        return finance_layout, active, inactive
    elif pathname == '/marketing':
        return marketing_layout, inactive, active
    return '', inactive, inactive
