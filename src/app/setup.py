from typing import List

import matplotlib.figure
from dash import dcc, html

from src.app.style_guide import AppStyleGuide


def set_up_app_layout(fig_init: matplotlib.figure.Figure, aai_item_names: List[str]) -> html.Div:
    style_guide = AppStyleGuide()
    layout = html.Div([
        _set_up_left_hand_section(fig_init, style_guide),
        _set_up_right_hand_section(aai_item_names, style_guide),
        html.Div(id='app_id')
    ], style={'backgroundColor': style_guide.background_colour})
    return layout


def _set_up_left_hand_section(fig_init: matplotlib.figure.Figure, style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
        dcc.Graph(figure=fig_init, id='aai-diagram', style=style_guide.aai_figure_style()),
    ], style=style_guide.left_hand_section_style())
    return layout


def _set_up_right_hand_section(aai_item_names: List[str], style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
        _set_up_new_item_layout(aai_item_names, style_guide),
        _set_up_move_item_layout(style_guide),
        _set_up_generate_config_layout(style_guide)
    ], style=style_guide.right_hand_section_style())
    return layout


def _set_up_new_item_layout(aai_item_names: List[str], style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
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
                  style=style_guide.width_input_style()),

        dcc.Input(placeholder='Height (y)',
                  type='text',
                  value='',
                  id="spawn-y",
                  style=style_guide.height_input_style()),

        html.Button('Spawn new item', id='new-item-button', n_clicks=0, style=style_guide.button_style(), )
    ])
    return layout


def _set_up_move_item_layout(style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
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
                            "style": style_guide.slider_tooltip_style()}, )
    ])
    return layout


def _set_up_generate_config_layout(style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
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

        html.Div(id='new-config-path-output', style={'whiteSpace': 'pre-line'})
    ])
    return layout
