from random import random
from datetime import datetime
from bokeh.layouts import layout, Spacer
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc

# RUN bokeh serve --show bokeh_dashboard.py

# create a plot and style its properties
rri_plot = figure(x_axis_label="Time",
                  x_axis_type="datetime",
                  y_axis_label="RRI",
                  toolbar_location=None)


diag_plot = figure(toolbar_location=None,
                   x_axis_label="Previous RRI",
                   y_axis_label="Current RRI")


def gen_final_data():
    # Timespec argument errored out for me. Maybe need to update Python?
    new_t = datetime.now()  # .isoformat()#timespec='milliseconds')
    new_RRI = 600 + 600 * random()
    return (new_t, new_RRI)


initial_data = [gen_final_data() for i in range(1)]
start_x, start_y = list(zip(*initial_data))


source = ColumnDataSource(data=dict(x=start_x, y=start_y))
source_mask = ColumnDataSource(data=dict(prev=[], cur=[], alphas=[]))

rri_plot.line(x='x', y='y', source=source)
diag_plot.line(x=(0, 1200), y=(0, 1200),
               line_color='grey', line_dash='dotted')
diag_plot.circle(x='prev', y='cur', alpha='alphas', source=source_mask,
                 size=15)

doc = curdoc()
# i = 0

# def gen_input_data():


def calc_alphas(column):
    interval = 1 / len(column)
    alphas = [interval * i for i in range(1, 1 + len(column))]
    return alphas


def update():
    new_x, new_y = gen_final_data()
    source.stream(dict(x=[new_x], y=[new_y]), rollover=10000)
    if len(source_mask.data['prev']) == 0:
        source_mask.stream(dict(prev=[new_y], cur=[new_y], alphas=[1]))
    else:
        prev = source_mask.data['cur'][-1]
        source_mask.stream(
            dict(prev=[prev], cur=[new_y], alphas=[1]), rollover=10)
    source_mask.data['alphas'] = calc_alphas(source_mask.data['cur'])


doc.add_periodic_callback(update, 1000)

curdoc().add_root(layout([[rri_plot], [Spacer(), diag_plot]],
                         sizing_mode='stretch_both'))
