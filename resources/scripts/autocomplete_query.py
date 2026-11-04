"""Encode this skin's keyboard query for the optional autocomplete plugin.

No input is logged or stored on disk. The window owns the transient value;
closing or reopening the keyboard invalidates the previous invocation.
"""
from urllib.parse import quote
from uuid import uuid4

import xbmc
import xbmcgui


OWNER = "HorizonzV.AutoCompletion.Owner"
QUERY = "HorizonzV.AutoCompletion.Query"


def main():
    keyboard = xbmcgui.Window(10103)
    owner = uuid4().hex
    keyboard.setProperty(OWNER, owner)
    monitor = xbmc.Monitor()
    previous = None
    try:
        while (xbmc.getCondVisibility("Window.IsVisible(virtualkeyboard)")
               and keyboard.getProperty(OWNER) == owner):
            encoded = ""
            if (xbmc.getCondVisibility("System.AddonIsEnabled(plugin.program.autocompletion)")
                    and not xbmc.getCondVisibility("System.HasHiddenInput")):
                try:
                    encoded = quote(keyboard.getControl(312).getText(), safe="")
                except RuntimeError:
                    # The native dialog may close between the visibility check
                    # and retrieving its edit control.
                    break
            if encoded != previous:
                keyboard.setProperty(QUERY, encoded)
                previous = encoded
            if monitor.waitForAbort(0.15):
                break
    finally:
        if keyboard.getProperty(OWNER) == owner:
            keyboard.clearProperty(QUERY)
            keyboard.clearProperty(OWNER)


if __name__ == "__main__":
    main()
