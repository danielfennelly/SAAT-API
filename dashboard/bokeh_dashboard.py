from random import random
from datetime import datetime
from bokeh.layouts import layout, Spacer
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from db import user_walker_date_interval
from collections import defaultdict

# RUN bokeh serve --show bokeh_dashboard.py

# create a plot and style its properties
rri_plot = figure(x_axis_label="Time",
                  x_axis_type="datetime",
                  y_axis_label="RRI",
                  toolbar_location=None,
                  y_range=(0, 1200))


diag_plot = figure(toolbar_location=None,
                   x_axis_label="Previous RRI",
                   y_axis_label="Current RRI")


def gen_final_data():
    # Timespec argument errored out for me. Maybe need to update Python?
    new_t = datetime.now()  # .isoformat()#timespec='milliseconds')
    new_RRI = 600 + 600 * random()
    return (new_t, new_RRI)


def calc_alphas(column):
    interval = 1 / len(column)
    alphas = [interval * i for i in range(1, 1 + len(column))]
    return alphas

user_colors = {
    'watson': "LimeGreen",
}


stream = user_walker_date_interval()

start_x = defaultdict(list)
start_y = defaultdict(list)

for time, rri, user in next(stream):
    start_x[user].append(time)
    start_y[user].append(rri)

user_sources = {}
user_source_masks = {}
for user in start_x.keys():
    user_sources[user] = ColumnDataSource(data=dict(x=start_x[user],
                                                    y=start_y[user]))
    user_source_masks[user] = ColumnDataSource(data=dict(prev=start_y[user][-11:-1],
                                                         cur=start_y[
                                                             user][-10:],
                                                         alphas=calc_alphas(start_y[user][-10:])))
    rri_plot.line(x='x', y='y', source=user_sources[user],
                  color=user_colors[user],
                  legend=user)
    diag_plot.circle(x='prev', y='cur', alpha='alphas',
                     source=user_source_masks[user],
                     color=user_colors[user],
                     size=15)

diag_plot.line(x=(0, 1200), y=(0, 1200),
               line_color='grey', line_dash='dotted')
doc = curdoc()


def update():
    new_x = defaultdict(list)
    new_y = defaultdict(list)
    for time, rri, user in next(stream):
        new_x[user].append(time)
        new_y[user].append(rri)
    for user in new_x.keys():
        user_sources[user].stream(
            dict(x=new_x[user], y=new_y[user]), rollover=1000)
        num_new = len(new_y[user])
        prev = user_source_masks[user].data['cur'][-num_new - 1:-1]
        user_source_masks[user].stream(
            dict(prev=prev, cur=new_y[user], alphas=[1] * num_new), rollover=10)
    user_source_masks[user].data['alphas'] = calc_alphas(
        user_source_masks[user].data['cur'])


doc.add_periodic_callback(update, 1000)

curdoc().add_root(layout([[rri_plot], [Spacer(), diag_plot]],
                         sizing_mode='stretch_both'))
