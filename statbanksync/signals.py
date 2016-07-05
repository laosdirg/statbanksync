"""
Signals for status reporting
"""

from blinker import signal

progress = signal('progress')
subprogress = signal('subprogress')
