# -*- coding: utf-8 -*-
import bokeh.plotting as plotting
from . import utils
import gazelib.preprocessing as gpre

# For printing environments
import yaml

# Custom HTML templates are required by custom HTML such as tables.
# The following setup is needed for custom HTML with bokeh.
# See http://bokeh.pydata.org/en/0.10.0/docs/user_guide/embed.html
# See http://bokeh.pydata.org/en/latest/docs/reference/embed.html
# For FileSystemLoader, see https://gist.github.com/wrunk/1317933
from bokeh.resources import CDN
from bokeh.embed import file_html
from jinja2 import Environment, FileSystemLoader
import os
this_dir = os.path.dirname(os.path.abspath(__file__))
jinja2loader = FileSystemLoader(os.path.join(this_dir, 'templates'))
jinja2env = Environment(loader=jinja2loader)
overview_template = jinja2env.get_template('overview.html')


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


def render_overview(common, output_html_filepath, title='Overview',
                    emphasize_gaps=False):
    '''
    Create HTML-based visualization from all streams and events.
    Does not understand stream or event semantics like gaze paths for example.

    Can be slow if streams contain large number of gaps.

    Parameters:
        common: A CommonV1 object
        output_html_filepath: a filepath as string
        title: HTML page title as string
        emphasize_gaps: if False, do not show red gaps. Makes it quicker.
    '''

    # Collect figures together
    figs = []

    def to_ms(micros):
        return int(round(micros / 1000))

    def pick_color(d):
        '''
        We visually discriminate original and derived data.

        Parameters:
          d: event or stream object.

        Return color string
        '''
        if 'derived' in d:
            return 'blue'
        return 'black'

    #########
    # Environment constants
    #########

    # Build dict
    env_names = common.list_environment_names()
    envs = {name: common.get_environment(name) for name in env_names}
    # Make human readable
    env_html = '<pre>' + yaml.dump(envs, default_flow_style=False) + '</pre>'

    #########
    # Streams
    #########

    stream_names = sorted(common.list_stream_names())
    for stream_name in stream_names:
        stream = common.get_stream(stream_name)
        x = list(map(to_ms, common.get_timeline(stream['timeline'])))
        y = stream['values']
        color = pick_color(stream)

        fig = plotting.figure(title=stream_name, x_axis_label='time (ms)',
                              plot_width=1000, plot_height=300,
                              toolbar_location=None)

        if emphasize_gaps:
            # Emphasize gaps with red. Slow if data very gapped.
            # Get valid substreams
            sl = utils.get_valid_sublists_2d(x, y)

            for xs, ys in sl:
                fig.line(xs, ys, line_color=color)

            # Emphasize gaps with red line.
            # Loop pairwise, fill gaps.
            # TODO Optimize. Currently very slow.
            for i in range(len(sl) - 1):
                xs0, ys0 = sl[i]
                xs1, ys1 = sl[i + 1]
                # Extrapolate from last known value
                x0 = xs0[-1]
                x1 = xs1[0]
                y = ys0[-1]
                fig.line(x=[x0, x1], y=[y, y], line_width=1, line_color='red')
        else:
            # Fill gaps and draw single line.
            # This should be much faster.
            yy = gpre.fill_gaps(y)
            fig.line(x=x, y=yy, line_width=1, line_color=color)

        figs.append(fig)

    ########
    # Events
    ########

    # Create a row for each event. X is time.
    evs = common.list_events()

    # Visualize in start time, then duration order.
    # Recent topmost, hence minus. If start time same, longest topmost.
    def order_key(ev):
        t0 = -ev['range'][0]
        dur = ev['range'][1] + t0
        return (t0, dur)

    evs = sorted(evs, key=order_key)

    # Plot height: it is dependent on number of events.
    # With one event, we want it still be visible, thus the constant.
    plot_height = (100 + 50 * len(evs))
    fig = plotting.figure(title='Events', y_range=(-1, len(evs)),
                          plot_width=1000,
                          plot_height=plot_height,
                          x_axis_label='time (ms)',
                          toolbar_location=None)

    # Hide event indices and draw custom text instead.
    fig.yaxis.visible = None

    def get_text_position(x0, x1, minx, maxx):
        '''Change text position based on event's horizontal position so that
        the rightmost text do not go over the right edge.'''
        # Event mean, normalized to range
        c = (x0 + x1) / 2 - minx
        # Max range
        r = maxx - minx

        if c < 2 * r / 3:
            return (x0, 'left')
        # Center align was not good because text formed
        # visually annoying justification.
        # if c < 2 * r / 3:
        #     return ((x0 + x1) / 2, 'center')
        return (x1, 'right')

    # Limit for horizontal coordinates. Helps to position text.
    evs_minx = to_ms(evs[-1]['range'][0])
    evs_maxx = to_ms(evs[0]['range'][1])

    for i, ev in enumerate(evs):
        t0 = to_ms(ev['range'][0])
        t1 = to_ms(ev['range'][1])

        color = pick_color(ev)

        x, align = get_text_position(t0, t1, evs_minx, evs_maxx)
        fig.text(text=[', '.join(ev['tags'])], y=[i + 0.1], x=[x],
                 text_align=align, text_color=color)

        fig.line(x=[t0, t1], y=[i, i], line_width=6, line_color=color)
        # Mark where events start and end.
        fig.line(x=[t0, t0], y=[i - 0.1, i + 0.1],
                 line_width=2, line_color=color)
        fig.line(x=[t1, t1], y=[i - 0.1, i + 0.1],
                 line_width=2, line_color=color)

    figs.append(fig)

    # Render HTML
    html = file_html(figs, CDN, title=title,
                     template=overview_template,
                     template_variables={'environment': env_html})
    # Save as html file.
    with open(output_html_filepath, 'w') as f:
        f.write(html)
