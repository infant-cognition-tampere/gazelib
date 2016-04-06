# -*- coding: utf-8 -*-
import bokeh.plotting as plotting
from . import utils


def render_path(common, output_html_filepath, title='Path'):
    xs = common.get_stream_values('gazelib/gaze/left_eye_x_relative')
    ys = common.get_stream_values('gazelib/gaze/left_eye_y_relative')

    p = plotting.figure(title=title, x_axis_label='X', y_axis_label='Y',
                        plot_width=400, plot_height=300)

    # Visualize only valid points.
    # We do that by visualizing valid subpaths

    def validator(x):
        return x[0] is not None and x[1] is not None

    paths = utils.get_valid_sublists(zip(xs, ys), validator)

    for valid_path in paths:
        valid_xs = list(map(lambda x: x[0], valid_path))
        valid_ys = list(map(lambda x: x[1], valid_path))

        p.cross(valid_xs, valid_ys, size=10)
        p.line(valid_xs, valid_ys, line_width=1)

    plotting.output_file(output_html_filepath, title)
    plotting.save(p)


def render_path_for_each_event(common, event_tag, output_html_filepath):
    pass


def render_overview(common, output_html_filepath):
    pass
