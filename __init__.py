#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

# Author: Jean-Denis Girard <jd.girard@sysnux.pf>

'''
CanvasGauge
=====

The :class:`CanvasGauge` widget is a widget for displaying gauge, using pure
canvas drawing (no image).

'''

__all__ = ('CanvasGauge',)

__title__ = 'garden.canvasjauge'
__version__ = '0.1'
__author__ = 'jd.girard@sysnux.pf'


from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Point, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.label import Label
from kivy.lang import Builder

from math import pi, cos, sin
#from time import time


def ellipse(u, v, a, b, angle):
    ''' Cartesian coordinates of a point on an ellipse given angle

    (u, v): center of ellipse
    (a, b): values of ellipse at axes intersection
    angle: in degrees, 
    Returns (x, y) coordinates
    '''

    angle *= pi / 180
    return u + a * cos(angle), v + b * sin(angle)

Builder.load_string('''\
<CanvasGauge>:
    bgcolor: (.5, .5, .5, .5)
    canvas.before:
        Color:
            rgba: self.bgcolor
        Ellipse:
            pos: self.pos
            size: self.size
''')

class CanvasGauge(Widget):

    begin = NumericProperty(210)
    end = NumericProperty(-30)
    mini = NumericProperty(0)
    maxi = NumericProperty(100)
    values = ListProperty((0, ))
    labels = ListProperty()
    graduations = ListProperty()
    needles_props = ListProperty()
    bgcolor = ListProperty((1, 1, 1, .1))
    alarms = ListProperty()
#        ( 
#        # mini, maxi, rgba
#        (-1000000, 10, (0, 0, 1, .5)),
#        (11, 60, (0, 1, 1, .5)),
#        (61, 90, (1, 1, 0, .5)),
#        (91, 10000000, (1, 0, 0, 1)),
#        ))

    def __init__(self, **kwargs):
        super(CanvasGauge, self).__init__(**kwargs)
        # /!\ Component properties are not available in __init__
        self._ready = False
        self._previous_values = []
        self._needles = []
        self._labels = []
        self._needles_props = []
        self._alarm_value = None
        self.bind(pos = self.update_canvas,
                  size = self.update_canvas,
                  values = self.update_values)
        self.bind(values = self.set_bgcolor)

    def update_canvas(self, *args):

        for i, value in enumerate(self.values):
            self._previous_values.append(None)
            if self.needles_props:
                props = self.needles_props[i]
                color = Color(* props.get('color') or \
                                ((i%3)*.5, ((i+1)%3)*.5, ((i+2)%3*.5)))
                length = props.get('length') or 1.0
                width = props.get('width') or 1.0
            else:
                color = Color((i%3)*.5, ((i+1)%3)*.5, ((i+2)%3*.5))
                length = 1.0
                width = 2.0
            self._needles_props.append({'color':  color,
                                      'width': width,
                                      'length': length})
            self._needles.append(None)

        self.canvas.clear()
        x0, y0 = self.pos
        with self.canvas:

            e_width = self.width / 2
            e_height = self.height / 2

            # Default color
            Color(1, 1, 1)

            # Labels
            if self.labels:
                for value, text in self.labels:
                    angle = self.begin - \
                            ((self.begin-self.end) / (self.maxi - self.mini) * value)
                    pos = ellipse(x0 + e_width,
                                  y0 + e_height,
                                  e_width - 30 ,
                                  e_height - 30,
                                  angle)
                    self._labels.append(Label(text = text,
                                        color = (1, 1, 1, .5),
                                        pos = pos,
                                        size = ('1dp', '1dp'), #self.texture_size,
                                        font_size='20sp',
                                        bold = True))
                    x1, y1 = ellipse(x0 + e_width,
                                     y0 + e_height,
                                     e_width,
                                     e_height,
                                     angle)
                    x2, y2 = ellipse(x0 + e_width,
                                     y0 + e_height,
                                     e_width - 10,
                                     e_height - 10,
                                     angle)
                    Line(points = [x1, y1, x2, y2],
                         width = 2,
                         #cap = 'round',
                         close = False)

            else:
                # Default : label on dizains
                for i in range(0, -self.mini + self.maxi + 1, 10):
                    angle = self.begin - \
                            ((self.begin-self.end) / (self.maxi - self.mini) * i)
                    pos = ellipse(x0 + e_width,
                                  y0 + e_height,
                                  e_width - 30 ,
                                  e_height - 30,
                                  angle)
                    self._labels.append(Label(text = '%d' % (i+self.mini),
                              color = (1, 1, 1, .5),
                              pos = pos,
                              size = ('1dp', '1dp'), #self.texture_size,
                              font_size='20sp',
                              bold = True))
                    x1, y1 = ellipse(x0 + e_width,
                                     y0 + e_height,
                                     e_width,
                                     e_height,
                                     angle)
                    x2, y2 = ellipse(x0 + e_width,
                                     y0 + e_height,
                                     e_width - 10,
                                     e_height - 10,
                                     angle)
                    Line(points = [x1, y1, x2, y2],
                         width = 2,
                         #cap = 'round',
                         close = False)

            # Graduations
            p = Point()

            if self.graduations:
                pass # XXX TODO

            else:
                # Default : point on units
                for i in range(0, -self.mini + self.maxi + 1):
                    angle = self.begin - \
                            ((self.begin-self.end) / (self.maxi - self.mini) * i)
                    if i % 10 == 0:
                        # Label, no graduation
                        continue
                    x, y = ellipse(x0 + e_width,
                                   y0 + e_height,
                                   e_width - 5,
                                   e_height - 5,
                                   angle)
                    p.add_point(x, y)

        # Save values used in update_values to display needle(s)
        self._e_width = e_width
        self._e_height = e_height
        self._scale = (self.begin-self.end) / (self.maxi - self.mini)
        self._x0, self._y0 = self.pos[0] + e_width, self.pos[1] + e_height
        self._ready = True

        # Display needle(s)
        self.update_values()

    def update_values(self, *args):

        if not self._ready:
            # Not fully initialized
            return

#        print('update_values:', self.values, end=' ')
#        t0 = time()
        for i, value in enumerate(self.values):
             if self._previous_values[i] == value:
                 continue
             self._previous_values[i] = value
             if self._needles[i] is not None:
                 self._needles[i].clear()
             needle = self._needles_props[i]
             x1, y1 = ellipse(self._x0,
                              self._y0,
                              (self._e_width - 20) * needle['length'],
                              (self._e_height - 20) * needle['length'],
                              self.begin - (self._scale * (value - self.mini)))
             self._needles[i] = InstructionGroup()
             self._needles[i].add(needle['color'])
             self._needles[i].add(Line(points = (x1,
                                                 y1,
                                                 self._x0,
                                                 self._y0),
                                     width = needle['width'],
                                     cap = 'round',
                                     close = False))
             self.canvas.add(self._needles[i])
#        print(' -> took: %.2f ms' % (1000 * (time() - t0)))

    def set_bgcolor(self, *args):

        if not self._ready:
            # Not fully initialized
            return

        # Set background color according to first value
        if self._alarm_value != self.values[0]:
            self._alarm_value = self.values[0]
            for l in self.alarms:
                if l[0] <= self.values[0] < l[1]:
                    self.bgcolor = l[2]
                    return


if __name__ == '__main__':

    from datetime import datetime

    from kivy.app import App
    from kivy.uix.gridlayout import GridLayout
    from kivy.clock import Clock

    class TestGauge(App):

        def build(self):
            box = GridLayout(cols=2)
            self.data = 0
            self.delta = 1

            # Gauge 1, default values
            self.g1 = CanvasGauge(values = (0, ))

            # Gauge 2, reversed, mini / maxi
            self.g2 = CanvasGauge(begin = -30,
                                  end = -150,
                                  mini = 50,
                                  maxi = 150,
                                  values = (0, ))

            # Gauge 3, right sided, with alarms
            self.g3 = CanvasGauge(begin = 120, 
                            end = -120,
                            mini = -40,
                            maxi = 140,
                            values = (0, ),
                            alarms = ( # mini, maxi, rgba
                                       (-1000, 20, (0, 0, 1, .5)),
                                       (21, 100, (0, 1, 0, .5)),
                                       (101, 200, (1, 0, 0, .5)),
                                      )
                        )

            # Clock !
            self.clock = CanvasGauge(begin = 90,
                               end = -270,
                               mini = 0,
                               maxi = 60,
                               values = (0, 0, 0),
                               labels = [(0, '')] + \
                                        [(h*5, str(h)) for h in range(1, 13)],
                               needles_props = ({'width': 3,
                                                 'length': .6,
                                                 'color': (.5, .5, .5)},
                                                {'width': 2,
                                                 'color': (.5, .5, .5)},
                                                {'width': 1}
                                                ))

            box.add_widget(self.g1)
            box.add_widget(self.clock)
            box.add_widget(self.g2)
            box.add_widget(self.g3)
            Clock.schedule_interval(self.set_clock, 1)
            Clock.schedule_interval(self.set_gx, .1)
            return box

        def set_clock(self, dt):
            now = datetime.now()
            self.clock.values = (((now.hour % 12) * 5 + (now.minute / 12)),
                                 now.minute + now.second / 60,
                                 now.second)

        def set_gx(self, dt):
            self.data += self.delta
            if self.data >= 100:
                self.delta = -1
            elif self.data <= 0:
                self.delta = 1
            self.g1.values = (self.data, )
            self.g2.values = (50 + self.data, )
            self.g3.values = (-40 + self.data * 1.80, )

    TestGauge().run()

