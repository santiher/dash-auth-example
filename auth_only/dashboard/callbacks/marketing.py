from dash.dependencies import Input, Output

from dashboard.app import app


@app.callback(
    Output(component_id='marketing-twice', component_property='children'),
    [Input('marketing-x', 'value')],
)
def twice_x(x):
    """Callback to fill the marketing example value."""
    return float(x) * 2
