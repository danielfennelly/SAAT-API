from random import random
from datetime import datetime
from bokeh.layouts import layout, Spacer
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from db import user_walker

# RUN bokeh serve --show bokeh_dashboard.py

# create a plot and style its properties
rri_plot = figure(x_axis_label="Time",
                  x_axis_type="datetime",
                  y_axis_label="RRI",
                  toolbar_location=None,
                  y_range=(0,1200))


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


stream = user_walker()

start_x, start_y = zip(*next(stream))


source = ColumnDataSource(data=dict(x=list(start_x), y=list(start_y)))
source_mask = ColumnDataSource(data=dict(
    prev=start_y[-11:-1], cur=start_y[-10:], alphas=calc_alphas(start_y[-10:])))

rri_plot.line(x='x', y='y', source=source)
diag_plot.line(x=(0, 1200), y=(0, 1200),
               line_color='grey', line_dash='dotted')
diag_plot.circle(x='prev', y='cur', alpha='alphas', source=source_mask,
                 size=15)

doc = curdoc()
# i = 0

# def gen_input_data():


def update():
    new_x, new_y = zip(*next(stream))
    source.stream(dict(x=list(new_x), y=list(new_y)), rollover=10000)
    if len(source_mask.data['prev']) == 0:
      source_mask.stream(dict(prev=[new_y], cur=[new_y], alphas=[1]))
    else:
      num_new = len(new_y)
      prev = source_mask.data['cur'][-num_new - 1:-1]
      source_mask.stream(
          dict(prev=prev, cur=list(new_y), alphas=[1] * num_new), rollover=10)
    source_mask.data['alphas'] = calc_alphas(source_mask.data['cur'])


doc.add_periodic_callback(update, 1000)

curdoc().add_root(layout([[rri_plot], [Spacer(), diag_plot]],
                         sizing_mode='stretch_both'))
