import dash_core_components as dcc
import dash_html_components as html


layout = html.Div([
    html.Div('Marketing'),
    html.Div([
        'Enter a number:',
        dcc.Input(id='marketing-x', value='0', type='text'),
    ]),
    html.Div([
        'Result:',
        html.Span(id='marketing-twice'),
    ])
])
