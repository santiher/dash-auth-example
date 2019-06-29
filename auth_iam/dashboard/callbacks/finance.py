from dash.dependencies import Input, Output

from dashboard.app import app


@app.callback(
    Output(component_id='finance-triple', component_property='children'),
    [Input('finance-x', 'value')],
)
def triple_x(x):
    """Callback to fill the finance example value."""
    return float(x) * 3
