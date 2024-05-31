from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray
import plotly.graph_objects as go
import matplotlib.figure

from src.structures.rectangular_cuboid import RectangularCuboid


class Visualiser:
    def visualise_cuboid_bases(self,
                               cuboids: List[RectangularCuboid],
                               names_items_with_overlap: List[str]) -> go.Figure:
        """Displays a 2d representation (x-z/length-width plane) of a list of RectangularCuboid instances.

        Args:
            names_items_with_overlap (list[str]): The names of items with overlaps.
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.

        Returns:
            (matplotlib.figure.Figure): The result figure showing the cuboid lower bases with red borders for overlaps.
        """
        fig = self._create_empty_arena_figure()
        for cuboid in cuboids:
            r, g, b = self._get_cuboid_colour_components(cuboid)
            x_path, y_path = self._get_cuboid_x_and_y_contour_paths(cuboid)
            name = cuboid.name
            line_colour, line_width = self._get_contour_colour_and_width(name, names_items_with_overlap)
            fig = self._add_item_trace_onto_arena_figure(fig, x_path, y_path, line_colour, line_width, name, r, g, b)
            fig = self._add_legend_to_arena_figure(fig)
        return fig

    @staticmethod
    def _create_empty_arena_figure() -> go.Figure:
        # Configure the figure environment and add an arena rectangle
        fig = go.Figure()
        fig.update_xaxes(range=[-1, 41], showgrid=False, zeroline=False, visible=True, )
        fig.update_yaxes(range=[-1, 41], showgrid=False, zeroline=False, visible=True, )

        # Add an Arena border
        fig.add_shape(type="rect",
                      x0=0, y0=0, x1=40, y1=40,
                      line=dict(color=f"rgba({100}, {100}, {100}, {1})", width=1.5, dash=None),
                      fillcolor=f"rgba({255}, {224}, {130}, {0.1})"
                      )

        # Make the axes equal to mimic square arena in AAI
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
        return fig

    @staticmethod
    def _add_legend_to_arena_figure(fig: go.Figure) -> go.Figure:
        fig.update_layout(
            legend=dict(x=15,
                        y=1,
                        traceorder='normal',
                        font=dict(family='Helvetica', size=20, color='Black'),
                        bgcolor='rgba(231,235,235,0.5)',
                        bordercolor='black',
                        borderwidth=1,
                        orientation='v',
                        xanchor='left',
                        yanchor='top',
                        )
        )
        return fig

    @staticmethod
    def _get_cuboid_colour_components(cuboid: RectangularCuboid) -> Tuple[int, int, int]:
        # Note: all AAI items should be coloured upon generating the item cuboid list; this else branch is simply
        # in place for non-AAI custom cuboids that may lack a colour attribute
        if cuboid.colour is not None:
            r, g, b = cuboid.colour["r"], cuboid.colour["g"], cuboid.colour["b"]
        else:
            r, g, b = 0, 0, 0
        return r, g, b

    @staticmethod
    def _get_cuboid_x_and_y_contour_paths(cuboid) -> Tuple[NDArray, NDArray]:
        # Concatenate because need to provide first element back to contour path for shape contour to be complete
        # See first example of https://plotly.com/python/shapes/
        x_path = np.concatenate(
            (cuboid.lower_base_vertices[:, 0], np.reshape(cuboid.lower_base_vertices[0, 0], newshape=(1,))))
        y_path = np.concatenate(
            (cuboid.lower_base_vertices[:, 1], np.reshape(cuboid.lower_base_vertices[0, 1], newshape=(1,))))
        return x_path, y_path

    @staticmethod
    def _get_contour_colour_and_width(name: str, names_items_with_overlap: List[str]) -> Tuple[str, float]:
        if name in names_items_with_overlap:
            # Make overlapping item's border red and make its width thicker
            line_colour = f"rgba({256}, {0}, {0}, {1})"
            line_width = 1.5
        else:
            # Keep non-overlapping item's border black and standard thickness
            line_colour = f"rgba({0}, {0}, {0}, {1})"
            line_width = 1
        return line_colour, line_width

    @staticmethod
    def _add_item_trace_onto_arena_figure(fig: go.Figure,
                                          x_path: NDArray,
                                          y_path: NDArray,
                                          line_colour: str,
                                          line_width: float,
                                          name: str,
                                          fill_colour_red: float,
                                          fill_colour_green: float,
                                          fill_colour_blue: float) -> go.Figure:
        fig.add_trace(go.Scatter(x=x_path,
                                 y=y_path,
                                 fill="toself",
                                 line=dict(color=line_colour, width=line_width, ),
                                 fillcolor=f"rgba({fill_colour_red}, {fill_colour_green}, {fill_colour_blue}, {0.35})",
                                 name=name,
                                 marker=dict(opacity=0),
                                 showlegend=True,
                                 mode="lines",
                                 ),
                      )
        return fig

# TODO: could change type(names_items_with_overlap) to set, for consistency with checker.
#  check that this does not break anything.

# TODO: could transform this class into a module. Does not matter too much as very small, what is best will depend on
#  the direction this file may take in the future if it is developed further.

# TODO: could have a user-friendly way of editing the style of the figure (a style guide for the arena figure, for e.g.)
