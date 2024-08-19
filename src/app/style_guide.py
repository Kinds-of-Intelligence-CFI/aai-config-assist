from typing import Dict


class AppStyleGuide:
    """The AppStyleGuide defines the styles (font, colours, sizes, ...) of each section of the application's UI."""

    def __init__(self) -> None:
        # Font
        self.font_size = "17px"
        self.font_family = "Helvetica"

        # Margins around interactive components
        self.margin_between_components = 12
        self.margin_at_bottom_of_components = self.margin_between_components * 3
        self.margin_left = 3
        self.margin_right = 3

        # Misc
        self.component_height = 21
        self.border_radius = 3
        self.tooltip_placement = "top"
        self.width_percentage_left_hand_section = "60%"
        self.display_type = "inline-block"
        self.background_colour = "rgba(231,235,235,0.5)"

    def left_hand_section_style(self) -> Dict:
        return {
            "display": self.display_type,
            "width": self.width_percentage_left_hand_section,
            "verticalAlign": "middle",
        }

    def right_hand_section_style(self) -> Dict:
        # Ensures that left and right hand side sections make up 100% of the total width
        left_width = int(self.width_percentage_left_hand_section.strip("%"))
        right_width = 100 - left_width
        return {
            "display": self.display_type,
            "width": f"{right_width}%",
            "verticalAlign": "bottom",
        }

    @staticmethod
    def aai_figure_style() -> Dict:
        return {"height": "100vh"}

    def heading_style(self) -> Dict:
        return {
            "fontFamily": self.font_family,
            "font-weight": "normal",
            "marginLeft": f"{self.margin_left / 3}%",
        }

    def normal_text_style(self) -> Dict:
        return {
            "fontFamily": self.font_family,
            "font-size": self.font_size,
            "font-weight": "normal",
            "marginLeft": f"{self.margin_left / 3}%",
            "marginBottom": self.margin_between_components * 2,
        }

    def dropdown_style(self) -> Dict:
        return {
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "marginLeft": f"{self.margin_left - 1.5}%",
            "marginRight": f"{self.margin_right}%",
        }

    def size_input_style(self) -> Dict:
        return {
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "marginBottom": self.margin_between_components,
            "marginTop": self.margin_between_components,
        }

    def length_input_style(self) -> Dict:
        return {
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "marginBottom": self.margin_between_components,
            "marginTop": self.margin_between_components,
            "marginLeft": f"{self.margin_left}%",
        }

    def width_input_style(self) -> Dict:
        return self.size_input_style()

    def height_input_style(self) -> Dict:
        return self.size_input_style()

    def button_style(self) -> Dict:
        return {
            "height": self.component_height,
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "marginBottom": self.margin_between_components * 2,
            "marginTop": self.margin_between_components,
            "marginLeft": f"{self.margin_left}%",
            "marginRight": f"{self.margin_right}%",
            "cursor": "pointer",
        }

    def slider_tooltip_style(self) -> Dict:
        return {
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
        }

    def new_config_path_input_style(self) -> Dict:
        return {
            "width": "80%",
            "height": self.component_height,
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "marginBottom": self.margin_between_components,
            "marginLeft": f"{self.margin_left}%",
            "marginRight": f"{self.margin_right}%",
            "border-style": "solid",
            "border-width": 0.5,
            "border-radius": self.border_radius,
        }

    def new_config_generation_button_style(self) -> Dict:
        return {
            "height": self.component_height,
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "marginBottom": self.margin_at_bottom_of_components,
            "marginTop": self.margin_between_components,
            "marginLeft": f"{self.margin_left}%",
            "marginRight": f"{self.margin_right}%",
            "cursor": "pointer",
        }
