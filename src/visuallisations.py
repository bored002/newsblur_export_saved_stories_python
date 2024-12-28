import plotly.graph_objects as go


def create_plotly_gauge(value, min_value, max_value):
    """
    Creates a gauge chart using Plotly.

    Args:
        value: The value to display on the gauge.
        min_value: The minimum value for the gauge.
        max_value: The maximum value for the gauge.
    """

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Gauge Chart"},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [min_value, max_value], 'color': "lightgray"}
            ]
        }
    ))

    return fig

def generate_html_file(fig, filename="delta_gauge.html"):
    """
    Generates an HTML file from a plotly figure.

    Args:
      fig: The plotly figure object.
      filename: The name of the HTML file to be saved.
    """

    html_string = fig.to_html(full_html=False)
    with open(filename, "w") as f:
        f.write(html_string)
