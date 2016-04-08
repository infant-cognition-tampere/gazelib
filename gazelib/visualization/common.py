# -*- coding: utf-8 -*-
import bokeh.plotting as plotting
from . import utils


def render_path(common, output_html_filepath, title='Path'):
    '''
    Create a HTML-based visualization of the gaze path.
    '''
    lxs = common.get_stream_values('gazelib/gaze/left_eye_x_relative')
    lys = common.get_stream_values('gazelib/gaze/left_eye_y_relative')
    rxs = common.get_stream_values('gazelib/gaze/right_eye_x_relative')
    rys = common.get_stream_values('gazelib/gaze/right_eye_y_relative')

    p = plotting.figure(title=title, x_axis_label='X', y_axis_label='Y',
                        plot_width=640, plot_height=480)

    # Visualize only valid points.
    # We do that by visualizing valid subpaths

    def validator(x):
        return x[0] is not None and x[1] is not None

    lpaths = utils.get_valid_sublists(zip(lxs, lys), validator)
    rpaths = utils.get_valid_sublists(zip(rxs, rys), validator)

    for valid_path in lpaths:
        valid_xs = list(map(lambda x: x[0], valid_path))
        valid_ys = list(map(lambda x: x[1], valid_path))

        p.cross(valid_xs, valid_ys, size=10, line_color='blue')
        p.line(valid_xs, valid_ys, line_width=1, line_color='blue')

    for valid_path in rpaths:
        valid_xs = list(map(lambda x: x[0], valid_path))
        valid_ys = list(map(lambda x: x[1], valid_path))

        p.cross(valid_xs, valid_ys, size=10, line_color='red')
        p.line(valid_xs, valid_ys, line_width=1, line_color='red')
        # Red as Right

    plotting.output_file(output_html_filepath, title)
    plotting.save(p)


def render_path_for_each_event(common, event_tag, output_html_filepath):
    pass


def render_overview(common, output_html_filepath):
    pass
