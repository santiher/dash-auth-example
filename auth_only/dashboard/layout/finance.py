import dash_core_components as dcc
import dash_html_components as html


layout = html.Div([
    html.Div('Finance'),
    html.Div([
        'Enter a number:',
        dcc.Input(id='finance-x', value='0', type='text'),
    ]),
    html.Div([
        'Result:',
        html.Span(id='finance-triple'),
    ])
])
