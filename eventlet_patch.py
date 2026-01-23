"""
Eventlet monkey patching for Socket.IO.
This MUST be imported before any other modules.
"""

import eventlet

eventlet.monkey_patch()
