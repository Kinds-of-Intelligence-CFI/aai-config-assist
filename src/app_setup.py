from src.app_style_guide import AppStyleGuide
from dash import dcc, html


def set_up_app_layout(fig_init, aai_item_names):
    style_guide = AppStyleGuide()

    layout = html.Div([
        html.Div([
            dcc.Graph(figure=fig_init, id='aai-diagram', style=style_guide.aai_figure_style()),
        ], style=style_guide.left_hand_section_style()),

        html.Div([
            html.H2("Place new item", id='heading-place-new-item', style=style_guide.heading2_style()),

            dcc.Dropdown(aai_item_names, id='item-dropdown', style=style_guide.dropdown_style()),

            dcc.Input(placeholder='Length (x)',
                      type='text',
                      value='',
                      id="spawn-x",
                      style=style_guide.length_input_style()),

            dcc.Input(placeholder='Width (z)',
                      type='text',
                      value='',
                      id="spawn-z",
                      style=style_guide.width_input_style()
                      ),

            dcc.Input(placeholder='Height (y)',
                      type='text',
                      value='',
                      id="spawn-y",
                      style=style_guide.height_input_style()
                      ),

            html.Button('Spawn new item',
                        id='new-item-button',
                        n_clicks=0,
                        style=style_guide.button_style(),
                        ),

            html.H2("Move item", id='heading-move-an-item', style=style_guide.heading2_style()),

            dcc.Slider(id="x-slider", min=0, max=40, step=1, value=0, marks=None,
                       tooltip={"placement": style_guide.tooltip_placement,
                                "always_visible": True,
                                "template": "x = {value}",
                                "style": style_guide.slider_tooltip_style()}),

            dcc.Slider(id="y-slider", min=0, max=20, step=0.1, value=0, marks=None,
                       tooltip={"placement": style_guide.tooltip_placement,
                                "always_visible": True,
                                "template": "y = {value}",
                                "style": style_guide.slider_tooltip_style()}),

            dcc.Slider(id="z-slider", min=0, max=40, step=1, value=0, marks=None,
                       tooltip={"placement": style_guide.tooltip_placement,
                                "always_visible": True,
                                "template": "z = {value}",
                                "style": style_guide.slider_tooltip_style()}),

            dcc.Slider(id="xz-rotation-slider", min=0, max=360, step=1, value=0, marks=None,
                       tooltip={"placement": style_guide.tooltip_placement,
                                "always_visible": True,
                                "template": "xz = {value} deg",
                                "style": style_guide.slider_tooltip_style()}, ),

            html.H2("Generate new config",
                    id='heading-generate-a-new-configuration-file',
                    style=style_guide.heading2_style()),

            dcc.Input(id="new-config-path",
                      style=style_guide.new_config_path_input_style(),
                      type="text",
                      placeholder="example_configs/new_config.yaml"),

            html.Div(html.Button('Generate new YAML config',
                                 id='new-config-path-button',
                                 n_clicks=0,
                                 style=style_guide.new_config_generation_button_style(),
                                 ), ),

            html.Div(id='new-config-path-output', style={'whiteSpace': 'pre-line'}),

        ], style=style_guide.right_hand_section_style()),

        html.Div(id='app_id')

    ], style={'backgroundColor': style_guide.background_colour})

    return layout
