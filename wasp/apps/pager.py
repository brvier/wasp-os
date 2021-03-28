# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Pager applications
~~~~~~~~~~~~~~~~~~~~~

The pager is used to present text based information to the user. It is
primarily intended for notifications but is also used to provide debugging
information when applications crash.
"""

import wasp
import icons
import fonts
import io
import sys

phone_icon = (
    b"\x02"
    b"@@"
    b"?\xff\xff-@\x15AAAAAEAA1A"
    b"AAAJAA-AAAOA+AAA"
    b"QA)AAASA(AAUA&AA"
    b'WA%AAXA#AAAYA"AA'
    b"FAAAAQA!AAFAA\x02AA"
    b"PA AAFAA\x04AAOA\x1fAA"
    b"EAA\x07AANA\x1eAAEAA\tA"
    b"AMA\x1dAAEAA\x0bAAKAA\x1c"
    b"AAEAA\rAABABAAAAA"
    b"\x1dAAEAA7AEAA7AEAA"
    b"7AADAA7AADAA8AEA"
    b"8AADA\x80#\x817\x81ADAA8A"
    b"EA8AADA9AEA8AAEA"
    b"A7AGAA6AIAA3AAJA"
    b"A2ALAA1AMA0AAMA0"
    b"ANA0ANA0ANA0ANA0"
    b"ANA0ANA0ANA0ANA0"
    b"ANA0ANA0AALAA1AA"
    b"BADABAA?\xff\xff+"
)


class PagerApp:
    """Show a long text message in a pager."""

    NAME = "Pager"
    ICON = icons.app

    def __init__(self, msg):
        self._msg = msg
        self._scroll = wasp.widgets.ScrollIndicator()

    def foreground(self):
        """Activate the application."""
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN)
        self._redraw()

    def background(self):
        """De-activate the application."""
        self._chunks = None
        self._numpages = None

    def swipe(self, event):
        """Swipe to page up/down."""
        if event[0] == wasp.EventType.UP:
            if self._page >= self._numpages:
                wasp.system.navigate(wasp.EventType.BACK)
                return
            self._page += 1
        else:
            if self._page <= 0:
                wasp.watch.vibrator.pulse()
                return
            self._page -= 1
        self._draw()

    def _redraw(self):
        """Redraw from scratch (jump to the first page)"""
        self._page = 0
        self._chunks = wasp.watch.drawable.wrap(self._msg, 240)
        self._numpages = (len(self._chunks) - 2) // 9
        self._draw()

    def _draw(self):
        """Draw a page from scratch."""
        mute = wasp.watch.display.mute
        draw = wasp.watch.drawable

        mute(True)
        draw.set_color(0xFFFF)
        draw.fill()

        page = self._page
        i = page * 9
        j = i + 11
        chunks = self._chunks[i:j]
        for i in range(len(chunks) - 1):
            sub = self._msg[chunks[i] : chunks[i + 1]].rstrip()
            draw.string(sub, 0, 24 * i)

        scroll = self._scroll
        scroll.up = page > 0
        scroll.down = page < self._numpages
        scroll.draw()

        mute(False)


class NotificationApp(PagerApp):
    NAME = "Notifications"

    def __init__(self):
        super().__init__("")
        self.confirmation_view = wasp.widgets.ConfirmationView()

    def foreground(self):
        notes = wasp.system.notifications
        note = notes.pop(next(iter(notes)))

        self._title = note["title"] if "title" in note else "Untitled"
        self._src = note["src"] if "src" in note else ""
        self._body = note["body"] if "body" in note else ""

        if self._src == "call":
            wasp.system.request_tick(1000)

        wasp.system.request_event(wasp.EventMask.TOUCH)
        super().foreground()

    def tick(self, ticks):
        wasp.watch.vibrator.pulse(ms=wasp.system.notify_duration)

    def background(self):
        self.confirmation_view.active = False
        super().background()

    def swipe(self, event):
        if self.confirmation_view.active:
            if event[0] == wasp.EventType.UP:
                self.confirmation_view.active = False
                self._draw()
                return
            # if (event[0] == wasp.EventType.LEFT) or (event[0] == wasp.EventType.RIGHT):
            #    self.foreground()
            #    return
        else:
            if event[0] == wasp.EventType.DOWN and self._page == 0:
                self.confirmation_view.draw("Clear notifications?")
                return

        super().swipe(event)

    def touch(self, event):
        if self.confirmation_view.touch(event):
            if self.confirmation_view.value:
                wasp.system.notifications = {}
                wasp.system.navigate(wasp.EventType.BACK)
            else:
                self._draw()

    def _draw(self):
        """Draw the display from scratch."""
        mute = wasp.watch.display.mute
        draw = wasp.watch.drawable

        mute(True)
        draw.set_color(0xFFFF)
        draw.fill()

        if self._src == "call":
            draw.blit(phone_icon, 94, 10)
            s = 70
        else:
            s = 10
            self._body = self._body

        draw.set_font(fonts.sans24)
        src_idx = draw.wrap(self._src, 240)
        title_idx = draw.wrap(self._title, 240)
        draw.string(self._src[src_idx[0] : src_idx[1]], 0, s, width=240)
        draw.string(self._title[title_idx[0] : title_idx[1]], 0, s + 30, width=240)
        draw.set_font(fonts.sans24)
        s += 80
        chunks = draw.wrap(self._body, 240)
        for i in range(len(chunks) - 1):
            sub = self._body[chunks[i] : chunks[i + 1]]
            if s + 24 * i > 216:
                break
            draw.string(sub, 0, s + 24 * i, width=240)
        mute(False)


class CrashApp:
    """Crash handler application.

    This application is launched automatically whenever another
    application crashes. Our main job it to indicate as loudly as
    possible that the system is no longer running correctly. This
    app deliberately enables inverted video mode in order to deliver
    that message as strongly as possible.
    """

    def __init__(self, exc):
        """Capture the exception information.

        This app does not actually display the exception information
        but we need to capture the exception info before we leave
        the except block.
        """
        msg = io.StringIO()
        sys.print_exception(exc, msg)
        self._msg = msg.getvalue()
        msg.close()

    def foreground(self):
        """Indicate the system has crashed by drawing a couple of bomb icons.

        If you owned an Atari ST back in the mid-eighties then I hope you
        recognise this as a tribute a long forgotten home computer!
        """
        wasp.watch.display.invert(False)
        draw = wasp.watch.drawable
        draw.blit(icons.bomb, 0, 104)
        draw.blit(icons.bomb, 32, 104)

        wasp.system.request_event(
            wasp.EventMask.SWIPE_UPDOWN | wasp.EventMask.SWIPE_LEFTRIGHT
        )

    def background(self):
        """Restore a normal display mode.

        Conceal the display before the transition otherwise the inverted
        bombs get noticed by the user.
        """
        wasp.watch.display.mute(True)
        wasp.watch.display.invert(True)

    def swipe(self, event):
        """Show the exception message in a pager."""
        wasp.system.switch(PagerApp(self._msg))
