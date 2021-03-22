# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Gadgetbridge/Bangle.js protocol

Currently implemented messages are:

 * t:"notify", id:int, src,title,subject,body,sender,tel:string - new
   notification
 * t:"notify-", id:int - delete notification
 * t:"alarm", d:[{h,m},...] - set alarms
 * t:"find", n:bool - findDevice
 * t:"vibrate", n:int - vibrate
 * t:"weather", temp,hum,txt,wind,loc - weather report
 * t:"musicstate", state:"play/pause",position,shuffle,repeat - music
   play/pause/etc
 * t:"musicinfo", artist,album,track,dur,c(track count),n(track num) -
   currently playing music track
 * t:"call", cmd:"accept/incoming/outgoing/reject/start/end", name: "name", number: "+491234" - call
"""

import io
import json
import sys
import wasp

# JSON compatibility
null = None
true = True
false = False


def _info(msg):
    json.dump({"t": "info", "msg": msg}, sys.stdout)
    sys.stdout.write("\r\n")


def _error(msg):
    json.dump({"t": "error", "msg": msg}, sys.stdout)
    sys.stdout.write("\r\n")


def GB(cmd):
    task = cmd["t"]
    del cmd["t"]

    try:
        if task == "find":
            wasp.watch.vibrator.pin(not cmd["n"])
        elif task == "notify":
            id = cmd["id"]
            del cmd["id"]
            wasp.system.notify(id, cmd)
            wasp.watch.vibrator.pulse(ms=wasp.system.notify_duration)
            if wasp.system.sleep_at == None:
                wasp.system.wake()
                wasp.system.switch(wasp.system.notifier)
        elif task == "call":
            if "incoming" in cmd["cmd"]:
                cmd["src"] = "call"
                if "name" in cmd:
                    cmd["title"] = cmd["name"]
                if "number" in cmd:
                    cmd["body"] = cmd["number"]
                wasp.system.notify(0, cmd)
                wasp.watch.vibrator.pulse(ms=wasp.system.notify_duration)
                if wasp.system.sleep_at == None:
                    wasp.system.wake()
                    wasp.system.switch(wasp.system.notifier)

        elif task == "notify-":
            wasp.system.unnotify(cmd["id"])
        elif task == "musicstate":
            wasp.system.toggle_music(cmd)
        elif task == "musicinfo":
            wasp.system.set_music_info(cmd)
        else:
            _info('Command {} "{}" is not implemented'.format(task, cmd))
            # pass
    except Exception as e:
        msg = io.StringIO()
        sys.print_exception(e, msg)
        _error(msg.getvalue())
        msg.close()
