from typing import List

import matplotlib.figure
from dash import dcc, html

from src.app.style_guide import AppStyleGuide

DEFAULT_BUTTON_NUMBER_CLICKS = 0

SPAWN_SECTION_TITLE = "Place new item"
SPAWN_LENGTH_TEXT = "Length (x)"
SPAWN_WIDTH_TEXT = "Width (z)"
SPAWN_HEIGHT_TEXT = "Height (y)"
SPAWN_BUTTON_TEXT = "Spawn new item"

MOVE_ITEM_SECTION_TITLE = "Move item"

MIN_X_SLIDER = 0
MAX_X_SLIDER = 40
STEP_X_SLIDER = 1
DEFAULT_X_SLIDER = 0

MIN_Z_SLIDER = MIN_X_SLIDER
MAX_Z_SLIDER = MAX_X_SLIDER
STEP_Z_SLIDER = STEP_X_SLIDER
DEFAULT_Z_SLIDER = DEFAULT_X_SLIDER

MIN_Y_SLIDER = 0
MAX_Y_SLIDER = 20
STEP_Y_SLIDER = 0.1
DEFAULT_Y_SLIDER = 0

MIN_ROTATION_SLIDER = 0
MAX_ROTATION_SLIDER = 360
STEP_ROTATION_SLIDER = 1
DEFAULT_ROTATION_SLIDER = 0

NEW_CONFIG_SECTION_TITLE = "Generate new config"
NEW_CONFIG_DEFAULT_PATH = "example_configs/new_config.yaml"
NEW_CONFIG_BUTTON_TEXT = "Generate new YAML config"

SLIDER_TOOLTIP_ALWAYS_VISIBLE = True
SLIDER_X_TEMPLATE = "x = {value}"
SLIDER_Y_TEMPLATE = "y = {value}"
SLIDER_Z_TEMPLATE = "z = {value}"
SLIDER_XZ_TEMPLATE = "xz = {value}"

# TODO: decide how to constant management across the whole library (and apply the decision to these constants too)


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
        html.H2(SPAWN_SECTION_TITLE, id='heading-place-new-item', style=style_guide.heading2_style()),

        dcc.Dropdown(aai_item_names, id='item-dropdown', style=style_guide.dropdown_style()),

        dcc.Input(placeholder=SPAWN_LENGTH_TEXT,
                  type='text',
                  value='',
                  id="spawn-x",
                  style=style_guide.length_input_style()),

        dcc.Input(placeholder=SPAWN_WIDTH_TEXT,
                  type='text',
                  value='',
                  id="spawn-z",
                  style=style_guide.width_input_style()),

        dcc.Input(placeholder=SPAWN_HEIGHT_TEXT,
                  type='text',
                  value='',
                  id="spawn-y",
                  style=style_guide.height_input_style()),

        html.Button(SPAWN_BUTTON_TEXT,
                    id='new-item-button',
                    n_clicks=DEFAULT_BUTTON_NUMBER_CLICKS,
                    style=style_guide.button_style(), )
    ])
    return layout


def _set_up_move_item_layout(style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
        html.H2(MOVE_ITEM_SECTION_TITLE, id='heading-move-an-item', style=style_guide.heading2_style()),

        dcc.Slider(id="x-slider",
                   min=MIN_X_SLIDER,
                   max=MAX_X_SLIDER,
                   step=STEP_X_SLIDER,
                   value=DEFAULT_X_SLIDER,
                   marks=None,
                   tooltip={"placement": style_guide.tooltip_placement,
                            "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                            "template": SLIDER_X_TEMPLATE,
                            "style": style_guide.slider_tooltip_style()}),

        dcc.Slider(id="y-slider",
                   min=MIN_Y_SLIDER,
                   max=MAX_Y_SLIDER,
                   step=STEP_Y_SLIDER,
                   value=DEFAULT_Y_SLIDER,
                   marks=None,
                   tooltip={"placement": style_guide.tooltip_placement,
                            "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                            "template": SLIDER_Y_TEMPLATE,
                            "style": style_guide.slider_tooltip_style()}),

        dcc.Slider(id="z-slider",
                   min=MIN_Z_SLIDER,
                   max=MAX_Z_SLIDER,
                   step=STEP_Z_SLIDER,
                   value=DEFAULT_Z_SLIDER,
                   marks=None,
                   tooltip={"placement": style_guide.tooltip_placement,
                            "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                            "template": SLIDER_Z_TEMPLATE,
                            "style": style_guide.slider_tooltip_style()}),

        dcc.Slider(id="xz-rotation-slider",
                   min=MIN_ROTATION_SLIDER,
                   max=MAX_ROTATION_SLIDER,
                   step=STEP_ROTATION_SLIDER,
                   value=DEFAULT_ROTATION_SLIDER,
                   marks=None,
                   tooltip={"placement": style_guide.tooltip_placement,
                            "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                            "template": SLIDER_XZ_TEMPLATE,
                            "style": style_guide.slider_tooltip_style()}, )
    ])
    return layout


def _set_up_generate_config_layout(style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
        html.H2(NEW_CONFIG_SECTION_TITLE,
                id='heading-generate-a-new-configuration-file',
                style=style_guide.heading2_style()),

        dcc.Input(id="new-config-path",
                  style=style_guide.new_config_path_input_style(),
                  type="text",
                  placeholder=NEW_CONFIG_DEFAULT_PATH),

        html.Div(html.Button(NEW_CONFIG_BUTTON_TEXT,
                             id='new-config-path-button',
                             n_clicks=DEFAULT_BUTTON_NUMBER_CLICKS,
                             style=style_guide.new_config_generation_button_style(),
                             ), ),

        html.Div(id='new-config-path-output', style={'whiteSpace': 'pre-line'})
    ])
    return layout
