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
                        plot_width=640, plot_height=480,
                        x_range=(-0.2, 1.2), y_range=(-0.2, 1.2))

    # Render screen rectangle
    p.quad(left=[0.0], right=[1.0], top=[0.0], bottom=[1.0],
           line_width=1, line_color='black', fill_alpha=0)

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

    # Display start points.
    lfirst = lpaths[0][0]
    rfirst = rpaths[0][0]
    # Width and height in x_axis and y_axis units.
    p.oval(x=lfirst[0], y=lfirst[1], width=0.17, height=0.2,
           line_color='blue', fill_alpha=0)
    p.oval(x=rfirst[0], y=rfirst[1], width=0.17, height=0.2,
           line_color='red', fill_alpha=0)

    plotting.output_file(output_html_filepath, title)
    plotting.save(p)


def render_path_for_each_event(common, event_tag, output_html_filepath):
    pass


def render_overview(common, output_html_filepath, title='Overview'):
    '''
    Create HTML-based visualization from all streams and events.
    Does not understand stream or event semantics like gaze paths for example.
    '''

    # Collect figures together
    figs = []

    def to_ms(micros):
        return int(round(micros / 1000))

    # Streams
    for stream_name in common.get_stream_names():
        tl_name = common.get_stream_timeline_name(stream_name)
        x = list(map(to_ms, common.get_timeline(tl_name)))
        y = common.get_stream_values(stream_name)

        # Get valid substreams
        sl = utils.get_valid_sublists_2d(x, y)

        fig = plotting.figure(title=stream_name, x_axis_label='time (ms)',
                              plot_width=1000, plot_height=300,
                              toolbar_location=None)

        for xs, ys in sl:
            fig.line(xs, ys, line_color='black')

        figs.append(fig)

    # Events

    # Lay out multiple figures
    p = plotting.vplot(*figs)
    # Save
    plotting.output_file(output_html_filepath, title)
    plotting.save(p)
