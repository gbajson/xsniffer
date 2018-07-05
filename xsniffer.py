#!/usr/bin/env python

import sys
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

local_dpy = display.Display()
record_dpy = display.Display()

def lookup_keysym(keysym):
    for name in dir(XK):
        if name[:3] == "XK_" and getattr(XK, name) == keysym:
            if name[3:] == 'period':
                return '.'
            if name[3:] == 'BackSpace':
                return '\b'

            return name[3:]
    return "[%d]" % keysym

def record_callback(reply):
    if reply.category != record.FromServer:
        return
    if reply.client_swapped:
        print("* received swapped protocol data, cowardly ignored")
        return
    if not len(reply.data) or reply.data[0] < 2:
        # not an event
        return

    line = ''
    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, record_dpy.display, None, None)

        if event.type == X.KeyPress:
            keysym = local_dpy.keycode_to_keysym(event.detail, 0)
            if not keysym:
                print (f"KeyCode {event.detail}")
            else:
                if lookup_keysym(keysym) == 'Return':
                    sys.stdout.write('\n')
                else:
                    line += lookup_keysym(keysym)
                    sys.stdout.write(line)
                    sys.stdout.flush()


# Check if the extension is present
if not record_dpy.has_extension("RECORD"):
    print("RECORD extension not found")
    sys.exit(1)
r = record_dpy.record_get_version(0, 0)

# Create a recording context; we only want key and mouse events
ctx = record_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.KeyPress, X.MotionNotify),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
        }])

# Enable the context; this only returns after a call to record_disable_context,
# while calling the callback function in the meantime
record_dpy.record_enable_context(ctx, record_callback)

# Finally free the context
record_dpy.record_free_context(ctx)
