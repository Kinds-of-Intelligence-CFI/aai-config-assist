from typing import List

import matplotlib.figure
from dash import dcc, html

from src.app.style_guide import AppStyleGuide

DEFAULT_BUTTON_NUMBER_CLICKS = 0

CONFIG_PARAMS_SECTION_TITLE = "Set configuration parameters"
PASS_MARK_TEXT = "Pass mark (1)"
TIME_LIMIT_TEXT = "Time limit (1)"
CONFIG_PARAMS_BUTTON_TEXT = "Set parameters"

SPAWN_SECTION_TITLE = "Place new item"
LENGTH_INPUT_TEXT = "Length (x)"
WIDTH_INPUT_TEXT = "Width (z)"
HEIGHT_INPUT_TEXT = "Height (y)"
SPAWN_BUTTON_TEXT = "Spawn new item"

CURRENT_ITEMS_SECTION_TITLE = "Modify existing item"
CURRENT_ITEM_TEXT = "Currently selected item: "

MIN_X_SLIDER = 0
MAX_X_SLIDER = 40
STEP_X_SLIDER = 0.1
DEFAULT_X_SLIDER = 0

MIN_Z_SLIDER = MIN_X_SLIDER
MAX_Z_SLIDER = MAX_X_SLIDER
STEP_Z_SLIDER = STEP_X_SLIDER
DEFAULT_Z_SLIDER = DEFAULT_X_SLIDER

MIN_Y_SLIDER = 0
MAX_Y_SLIDER = 20
STEP_Y_SLIDER = STEP_X_SLIDER
DEFAULT_Y_SLIDER = 0

MIN_ROTATION_SLIDER = 0
MAX_ROTATION_SLIDER = 360
STEP_ROTATION_SLIDER = 1
DEFAULT_ROTATION_SLIDER = 0

NEW_CONFIG_SECTION_TITLE = "Generate new configuration"
NEW_CONFIG_DEFAULT_PATH = "example_configs/new_config.yaml"
NEW_CONFIG_BUTTON_TEXT = "Generate new YAML config"

SLIDER_TOOLTIP_ALWAYS_VISIBLE = True
SLIDER_X_TEMPLATE = "x = {value}"
SLIDER_Y_TEMPLATE = "y = {value}"
SLIDER_Z_TEMPLATE = "z = {value}"
SLIDER_XZ_TEMPLATE = "xz = {value}"

REMOVE_ITEM_BUTTON_TEXT = "Remove current item"
RESIZE_ITEM_BUTTON_TEXT = "Resize current item"


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
        _set_up_config_params_layout(style_guide),
        _set_up_new_item_layout(aai_item_names, style_guide),
        _set_up_move_item_layout(style_guide),
        _set_up_generate_config_layout(style_guide)
    ], style=style_guide.right_hand_section_style())
    return layout


def _set_up_config_params_layout(style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
        html.H2(CONFIG_PARAMS_SECTION_TITLE, id='heading-set-config-params', style=style_guide.heading_style()),

        dcc.Input(placeholder=PASS_MARK_TEXT,
                  type='text',
                  value='',
                  id="pass-mark",
                  style=style_guide.length_input_style()),

        dcc.Input(placeholder=TIME_LIMIT_TEXT,
                  type='text',
                  value='',
                  id="time-limit",
                  style=style_guide.width_input_style()),

        html.Button(CONFIG_PARAMS_BUTTON_TEXT,
                    id='config-params-button',
                    n_clicks=DEFAULT_BUTTON_NUMBER_CLICKS,
                    style=style_guide.button_style())
    ])
    return layout


def _set_up_new_item_layout(aai_item_names: List[str], style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
        html.H2(SPAWN_SECTION_TITLE, id='heading-place-new-item', style=style_guide.heading_style()),

        dcc.Dropdown(aai_item_names, id='item-dropdown', style=style_guide.dropdown_style()),

        dcc.Input(placeholder=LENGTH_INPUT_TEXT,
                  type='text',
                  value='',
                  id="spawn-x",
                  style=style_guide.length_input_style()),

        dcc.Input(placeholder=WIDTH_INPUT_TEXT,
                  type='text',
                  value='',
                  id="spawn-z",
                  style=style_guide.width_input_style()),

        dcc.Input(placeholder=HEIGHT_INPUT_TEXT,
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
        html.H2(CURRENT_ITEMS_SECTION_TITLE, id='heading-move-an-item', style=style_guide.heading_style()),
        _set_up_current_item_board_layout(style_guide),
        _set_up_x_slider_layout(style_guide),
        _set_up_y_slider_layout(style_guide),
        _set_up_z_slider_layout(style_guide),
        _set_up_xz_slider_layout(style_guide),
        _set_up_remove_current_item_button_layout(style_guide),
        _set_up_resize_current_item_section_layout(style_guide),
    ])
    return layout


def _set_up_current_item_board_layout(style_guide: AppStyleGuide) -> html.Div:
    return html.Div([
        html.Plaintext(id='output-current-item', children='No item selected', style=style_guide.normal_text_style()),
    ])


def _set_up_remove_current_item_button_layout(style_guide: AppStyleGuide) -> html.Div:
    return html.Div([html.Button(REMOVE_ITEM_BUTTON_TEXT,
                                 id='remove-item-button',
                                 n_clicks=DEFAULT_BUTTON_NUMBER_CLICKS,
                                 style=style_guide.button_style()), ])


def _set_up_x_slider_layout(style_guide: AppStyleGuide) -> html.Div:
    return html.Div([dcc.Slider(id="x-slider",
                                min=MIN_X_SLIDER,
                                max=MAX_X_SLIDER,
                                step=STEP_X_SLIDER,
                                value=DEFAULT_X_SLIDER,
                                marks=None,
                                tooltip={"placement": style_guide.tooltip_placement,
                                         "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                                         "template": SLIDER_X_TEMPLATE,
                                         "style": style_guide.slider_tooltip_style()})
                     ])


def _set_up_y_slider_layout(style_guide: AppStyleGuide) -> html.Div:
    return html.Div([dcc.Slider(id="y-slider",
                                min=MIN_Y_SLIDER,
                                max=MAX_Y_SLIDER,
                                step=STEP_Y_SLIDER,
                                value=DEFAULT_Y_SLIDER,
                                marks=None,
                                tooltip={"placement": style_guide.tooltip_placement,
                                         "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                                         "template": SLIDER_Y_TEMPLATE,
                                         "style": style_guide.slider_tooltip_style()}),
                     ])


def _set_up_z_slider_layout(style_guide: AppStyleGuide) -> html.Div:
    return html.Div([dcc.Slider(id="z-slider",
                                min=MIN_Z_SLIDER,
                                max=MAX_Z_SLIDER,
                                step=STEP_Z_SLIDER,
                                value=DEFAULT_Z_SLIDER,
                                marks=None,
                                tooltip={"placement": style_guide.tooltip_placement,
                                         "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                                         "template": SLIDER_Z_TEMPLATE,
                                         "style": style_guide.slider_tooltip_style()}),

                     ])


def _set_up_xz_slider_layout(style_guide: AppStyleGuide) -> html.Div:
    return html.Div([dcc.Slider(id="xz-rotation-slider",
                                min=MIN_ROTATION_SLIDER,
                                max=MAX_ROTATION_SLIDER,
                                step=STEP_ROTATION_SLIDER,
                                value=DEFAULT_ROTATION_SLIDER,
                                marks=None,
                                tooltip={"placement": style_guide.tooltip_placement,
                                         "always_visible": SLIDER_TOOLTIP_ALWAYS_VISIBLE,
                                         "template": SLIDER_XZ_TEMPLATE,
                                         "style": style_guide.slider_tooltip_style()}),

                     ])


def _set_up_resize_current_item_section_layout(style_guide: AppStyleGuide) -> html.Div:
    return html.Div([
        dcc.Input(placeholder=LENGTH_INPUT_TEXT,
                  type='text',
                  value='',
                  id="resize-x",
                  style=style_guide.length_input_style()),

        dcc.Input(placeholder=WIDTH_INPUT_TEXT,
                  type='text',
                  value='',
                  id="resize-z",
                  style=style_guide.width_input_style()),

        dcc.Input(placeholder=HEIGHT_INPUT_TEXT,
                  type='text',
                  value='',
                  id="resize-y",
                  style=style_guide.height_input_style()),

        html.Button(RESIZE_ITEM_BUTTON_TEXT,
                    id='resize-item-button',
                    n_clicks=DEFAULT_BUTTON_NUMBER_CLICKS,
                    style=style_guide.button_style(), )

    ])


def _set_up_generate_config_layout(style_guide: AppStyleGuide) -> html.Div:
    layout = html.Div([
        html.H2(NEW_CONFIG_SECTION_TITLE,
                id='heading-generate-a-new-configuration-file',
                style=style_guide.heading_style()),

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

# TODO: consider whether to make a function for setting up the slider layouts
#  (to prepare for slider implementation changing)

# TODO: consider whether this setup module should not be a class whereby the style_guide is an attribute to avoid
#  passing it around very frequently. Even though, of course, this setup object wouldn't have a meaningful lifecycle
#  with an evolving state, so could remain with a module, up for discussion.

# TODO: in general, decide whether to split all layouts into single component functions or whether to combine certain
#  components into single function layouts. Decide on a rule for how you are designing the setup code, in general.

# TODO: consider somehow combining both the spawn sizing and resizing sections because they are very similar,
#  could combine them somehow (either in the code: combine their implementations to avoid duplication) or even in the
#  UI, have only one sizing section for example and depending on which button is pressed something new is done.

# TODO: consider also having Dash 'tabs' for the various modalities:
#  New item spawning
#  Current item manipulation
#  Dumping to YAML

# TODO: decide how to constant management across the whole library (and apply the decision to these constants too)
