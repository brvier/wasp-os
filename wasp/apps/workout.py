# Author: Benoit HERVIER (b@rvier.fr)
# Licence: GNU GPLv3

"""Workout App
~~~~~~~~~~~~~~~~~~~~~

A simple workout app tracking steps and hearthrate.

.. figure:: res/HeartApp.png
    :width: 179
"""

import wasp
import machine
import ppg
import fonts
import icons

try:
    from utime import localtime
except:
    # mockup for simulator
    def localtime(t):
        import time

        t = time.localtime()
        return t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, 0, t.tm_zone


MONTH = "JanFebMarAprMayJunJulAugSepOctNovDec"

LIKE_ICON = (
    b"\x02"
    b"\x18\x18"
    b"?%@\xbbAAAAAA\x04AAAAA"
    b"A\x07AADAA\x02AADAA\x05AH"
    b"AAGAA\x03AAHBHAA\x02AT"
    b"A\x02ATA\x02ATA\x02ATA\x02AT"
    b"A\x02AARAA\x03ARA\x04AAPA"
    b"A\x05AANAA\x07AALAA\tAA"
    b"JAA\x0b\x80\xb4\x81AAFAA\xc0\xc2\xc1\x0e"
    b"AADAA\x11AABAA\x14AA#"
)


SHOES_ICON = (
    b"\x02"
    b"\x13\x18"
    b"\x02@\xa8AAAAA\rAACAA\x0cA"
    b"EA\x0bAFAA\nAGA\x04AAA\x03"
    b"AGA\x03ABAA\x02AGA\x02ADA"
    b"A\x01HA\x02AEA\x01GAA\x01AAF"
    b"AGA\x02AGAAEAA\x02AGAA"
    b"EA\x03AGAAEA\x03AHAE\x04A"
    b"AG\x01AD\x05AFA\x01AD\x05AAE"
    b"A\x01AD\x06AEA\x01ACA\x06AEA"
    b"\x01AAAAA\x07EA\x02AAA\x08DA"
    b"\x0eACA\x0eDA\x0eACA\x0eAAAA"
    b"A\x01"
)


class WorkoutApp:
    """Workout monitor application."""

    NAME = "Wrkout"
    ICON = (
        b"\x02"
        b"`@"
        b"?\xff\xd4@\xc6AAAAAAA?\x19AA"
        b"EAA?\x17AHAA?\x15AJAA?"
        b"\x14AKA?\x13ALA?\x13ALA?\x13"
        b"ALA?\x13ALA?\x14AKA?\x14A"
        b"JAA?\x15AHAA?\x17AAEAA"
        b"?\x08AAJA\x80\\\x81\xc0\x15\xc1\xc1\x01AA"
        b"AAAAA?\x08AAJA\x81\xc3\xc1\xc1@"
        b"#A?\x0c\x80\xc6\x81\x81\x8b\xc0[\xc1@\x15FA"
        b"A\x0c\x81\x81\x81\x81\x819\x81\x8b\x81AB\x808\x81"
        b"\xc0\xa3\xc1@\xc6A\xc1\x81\x80\x15\x81\x81\nAAD"
        b"A7AAK\xc0[\xc1\x82@8A\x80\xc6\x81\x84"
        b"\xc0\xa3\xc1A\t\x81\x81\x85\x816\x81\x81\x8b\x81@\x15"
        b"AB\x80\x7f\x81\xc0\xc6\xc6\xc1\xc1\xc1\x06\xc1\xc1\xc6\xc1"
        b"6\xc1\xc5\xc1\xc1\xc1\xc1\xc1\xc1\xc1@[A\x80\x15\x83"
        b"\xc0\xa2\xc1@\xc6HAAA\x03AAFAA5"
        b"AADAA\x05\x81\x81\x83\x80\x7f\x81JAAA"
        b"AGAA5AAEA\x06\xc0\x15\xc1\xc4@8"
        b"A\x80\xc6\x81\x8b\x81\x87\x81\x816\x81\x85\x81\x81\x05\xc1"
        b"\xc1\xc5A\xc0\x7f\xc1\x81\x8f\x81\x817\x81\x81\x84\x81\x81"
        b"\x06@\x15AHA\x80\\\x81\xc0\xa3\xc1@\xc6AK"
        b"AA8AEA\x06\x80\x15\x81\x81\x89\x81\x81AA"
        b"AHAA9AACAA\x06\x81\x8a\x81\x03A"
        b"AAEAA;AAAAA\x06\x81\x81\x89\x81"
        b"\x81\x06AAAAAA?\x08\x81\x8a\x81?\x14\xc0"
        b"#\xc1\x81\x89\x81\x81?\x14\x81\x8a@\x14A\x80\x0e\x81"
        b"\x81A?\x12\xc0\x15\xc1\xc9\xc1\x81\x82\x81\x81\x81?\x0f"
        b"\xc1\xcaA\x85\x81\x81\x81?\r\xc1\xc9\xc1\x81\x87\x81\xc1"
        b"?\x0b\xc1\xc1\xc9A\x89\x81?\x0b\xc1\xc9A\x8a\x81?"
        b"\n\xc1\xc1\xc8\xc1\x81\x89\x81?\x0b\xc1\xc9A\x87\x81\x81"
        b"\x81\x01?\n\xc1\xc1\xc8A\x85\x81\x81\x81\xc1?\r\xc1"
        b"\xc8\xc1\x81\x81\x81\x81\x81\x81?\x10\xc1\xc1\xc8A\x81\x81"
        b"\x81?\x13\xc1\xc8\xc1\x81?\x15\xc1\xc1\xc7\xc1\xc1?\x16"
        b"\xc1\xc7\xc1\xc1?\x17\xc1\xc7\xc1?\x17\xc1\xc7\xc1@#"
        b"A?\x17\xc1\xc6\xc1\xc1?\x17\xc1\xc6\xc1\xc1?\x18\xc1"
        b"\xc6\xc1?\x18\xc1\xc1\xc5\xc1\xc1?\x18\xc1\xc5\xc1\xc1?"
        b"\x19\xc1\xc5\xc1?\x1a\xc1\xc4\xc1A?\x1a\xc1\xc1\xc2\xc1"
        b"\xc1?\x1c\xc1\xc1\xc1\xc1?\xff\xe1"
    )

    def __init__(self):
        self._start_time = None
        self._steps_count = None
        self._steps_previous = None
        self._steps_time = None
        self._hr_avg_value = 0
        self._hr_avg_count = 0
        self._steps_avg_value = 0
        self._steps_avg_count = 0
        self._page = -1
        self._data = []

    def foreground(self):
        """Activate the application."""
        wasp.watch.hrs.enable()
        wasp.system.request_event(wasp.EventMask.BUTTON)
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN)
        wasp.system.keep_awake()

        self._hrdata = ppg.PPG(wasp.watch.hrs.read_hrs())
        self._draw()

        wasp.system.request_tick(1000 // 8)

    def _draw(self):
        if self._page == -1:
            # There is no delay after the enable because the redraw should
            # take long enough it is not needed
            draw = wasp.watch.drawable
            draw.fill()

            draw.blit(LIKE_ICON, 20, 135, fg=0xF800)
            draw.blit(SHOES_ICON, 130, 135, fg=0xF800)

            self._draw_current()
        else:
            self._draw_wrkout()
        wasp.system.bar.clock = True
        wasp.system.bar.draw()

    def _draw_wrkout(self):
        draw = wasp.watch.drawable
        draw.fill()

        d = self._data[self._page]
        # Format the month as text
        year, month, mday, hour, minute, _, _, _ = localtime(d[0])

        # Draw the date/time
        draw.set_font(fonts.sans24)
        # draw.string("{} {} {}".format(mday, month, year), 0, 50, width=240)
        # draw.string("{:02d}:{:02d}".format(hour, minute), 0, 80, width=240)
        draw.string("{:02d}/{:02d} {:02d}:{:02d}".format(mday, month, hour, minute), 0, 50)

        e = round(d[1] - d[0])
        draw.set_font(fonts.sans36)
        draw.set_color(wasp.system.theme("bright"))
        h = e // 3600
        m = (e - h * 3600) // 60
        draw.set_font(fonts.sans36)
        draw.set_color(wasp.system.theme("bright"))
        draw.string("{:02d}.{:02d}".format(h, m), 0, 120, width=180, right=True)
        draw.set_font(fonts.sans24)
        draw.string(".{:02d}".format(e % 60), 180, 135)

        draw.string("{:03d}".format(d[2]), 100, 180)
        draw.string("{:05d}".format(d[3]), 80, 210)

    def background(self):
        wasp.watch.hrs.disable()
        del self._hrdata

    def _subtick(self, ticks):
        """Notify the application that its periodic tick is due."""
        self._hrdata.preprocess(wasp.watch.hrs.read_hrs())

    def press(self, event_type, status):
        if not status:
            if self._start_time is None:
                self._start_time = wasp.watch.rtc.time()
                self._steps_count = wasp.watch.accel.steps
                self._steps_time = wasp.watch.rtc.time()
                self._steps_previous = wasp.watch.accel.steps
                self._steps_avg_value = 0
                self._steps_avg_count = 0
                self._hr_avg_count = 0
                self._hr_avg_value = 0
            else:
                self._data.append([self._start_time, wasp.watch.rtc.time(), self._steps_count, int(self._hr_avg_value)])
                self._start_time = None

    def swipe(self, event):
        if event[0] == wasp.EventType.DOWN:
            if self._page == -1:
                return
            self._page -= 1
        else:
            self._page = min(self._page + 1, len(self._data) - 1)

        # mute = wasp.watch.display.mute
        # mute(True)
        self._draw()
        # mute(False)

    def _draw_current(self):
        draw = wasp.watch.drawable

        if self._start_time:
            e = round(wasp.watch.rtc.time() - self._start_time)
            draw.set_font(fonts.sans36)
            draw.set_color(wasp.system.theme("bright"))
            h = e // 3600
            m = (e - h * 3600) // 60
            draw.set_font(fonts.sans36)
            draw.set_color(wasp.system.theme("bright"))
            draw.string("{:02d}.{:02d}".format(h, m), 0, 60, width=180, right=True)
            draw.set_font(fonts.sans24)
            draw.string(".{:02d}".format(e % 60), 180, 75)
            if len(self._hrdata.data) >= 240:
                draw.set_color(wasp.system.theme("bright"))
                draw.set_font(fonts.sans24)
                hrm = min(self._hrdata.get_heart_rate(), 999)
                draw.set_font(fonts.sans24)
                draw.string("{:03d}".format(hrm), 60, 140, width=60)
                if self._start_time:
                    if self._hr_avg_value == 0:
                        self._hr_avg_value = hrm
                        self._hr_avg_count = 1
                    else:
                        # avg
                        self._hr_avg_count += 1
                        self._hr_avg_value = (self._hr_avg_value * (self._hr_avg_count - 1) + hrm) / self._hr_avg_count

            # 30s
            if self._steps_time:
                if wasp.watch.rtc.time() - self._steps_time > 5:
                    steps = wasp.watch.accel.steps
                    count = (steps - self._steps_previous) * 60 / (wasp.watch.rtc.time() - self._steps_time)
                    self._steps_previous = steps
                    self._steps_time = wasp.watch.rtc.time()
                    draw.set_color(wasp.system.theme("bright"))
                    draw.set_font(fonts.sans24)
                    self._steps_avg_count += 1
                    self._steps_avg_value = min(
                        self._steps_avg_value + (count - self._steps_avg_value) / min(self._steps_avg_count, 2), 999
                    )  # moving_avg approximation

                    draw.string("{:03.0f}".format(self._steps_avg_value), 170, 140)

                    draw.string("{:5.0f} steps".format(min(99999, steps - self._steps_count)), 0, 200, width=240)

        else:
            draw.set_font(fonts.sans36)
            draw.set_color(wasp.system.theme("bright"))
            draw.string("00.00", 0, 60, width=180, right=True)
            draw.set_font(fonts.sans24)
            draw.string(".00", 180, 75)
            draw.string("000", 60, 140)
            draw.string("000", 170, 140)
            draw.string("00000", 0, 200, width=240)

    def tick(self, ticks):
        """This is an outrageous hack but, at present, the RTC can only
        wake us up every 125ms so we implement sub-ticks using a regular
        timer to ensure we can read the sensor at 24Hz.
        """
        t = machine.Timer(id=1, period=8000000)
        t.start()
        self._subtick(1)
        wasp.system.keep_awake()

        # should be done 1 by minute
        wasp.system.bar.update()

        while t.time() < 41666:
            pass
        self._subtick(1)

        while t.time() < 83332:
            pass
        self._subtick(1)

        t.stop()
        del t

        if self._page == -1:
            self._draw_current()
