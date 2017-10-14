

from datetime import datetime
from random import randint

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

from __init__ import CanvasGauge


class TestGauges(FloatLayout):
    hour = 0
    minute = 0
    second = 0

    def __init__(self):
        super().__init__()
        Clock.schedule_interval(self.set_clock, 1)

    def set_clock(self, dt):
        now = datetime.now()
        self.clock.values = (((now.hour % 12) * 5 + (now.minute / 12)),
                             now.minute + now.second / 60,
                             now.second)

    def tank_changed(self, val):
        if val < 5:
            self.tank_label.text = 'Tank is empty!'
        elif val > 95:
            self.tank_label.text = 'Tank is full!'
        else:
            self.tank_label.text = 'Tank is %.1f %% full' % val


class TestGaugesApp(App):
    # Will automatically load KV file 'testgauges.kv'

    def build(self):
        Clock.schedule_interval(self.set_gx, .1)
        self.gauges = TestGauges()
        return self.gauges

    def set_gx(self, dt):
        x = self.gauges.g1.values[0] + randint(-10, 10)
        if x > 100:
            self.gauges.g1.values = (100, )
        elif x < 0:
            self.gauges.g1.values = (0, )
        else:
            self.gauges.g1.values = (x, )

        x = self.gauges.g3.values[0] + randint(-20, 20)
        if x > 140:
            self.gauges.g3.values = (150, )
        elif x < -50:
            self.gauges.g3.values = (-50, )
        else:
            self.gauges.g3.values = (x, )

TestGaugesApp().run()

