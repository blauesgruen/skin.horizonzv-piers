"""Edit the skin accent's ARGB value using Kodi dialogs, without an add-on."""
import re

import xbmc
import xbmcgui


def normalize_color(value):
    """Accept RGB or ARGB hex; RGB means fully opaque."""
    value = value.strip().removeprefix("#")
    if not re.fullmatch(r"(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", value):
        raise ValueError("Expected six or eight hexadecimal digits")
    return ("FF" + value if len(value) == 6 else value).upper()


def with_opacity(color, percent):
    if not re.fullmatch(r"[0-9]{1,3}", percent) or int(percent) > 100:
        raise ValueError("Expected an opacity between 0 and 100")
    alpha = (int(percent) * 255 + 50) // 100
    return f"{alpha:02X}" + normalize_color(color)[2:]


def main():
    # Keep both data and translated labels owned by this skin.
    if xbmc.getSkinDir() != "skin.horizonzv":
        return
    dialog = xbmcgui.Dialog()
    localize = xbmc.getLocalizedString
    try:
        current = normalize_color(xbmc.getInfoLabel("Skin.String(MySkinColor)"))
    except ValueError:
        current = "FFFFFFFF"
    mode = dialog.select(localize(31394), [localize(31954), localize(31955)])
    if mode not in (0, 1):
        return
    while True:
        if mode == 0:
            value = dialog.input(localize(31954), current, type=xbmcgui.INPUT_ALPHANUM)
        else:
            percent = str((int(current[:2], 16) * 100 + 127) // 255)
            value = dialog.numeric(0, localize(31955), percent)
        if not value:
            return
        try:
            color = normalize_color(value) if mode == 0 else with_opacity(current, value)
        except ValueError:
            dialog.ok(localize(31394), localize(31957 if mode == 0 else 31958))
            continue
        # Only validated eight-digit hex reaches the built-in command.
        if xbmc.getSkinDir() == "skin.horizonzv":
            xbmc.executebuiltin(f"Skin.SetString(MySkinColor,{color})")
        return


if __name__ == "__main__":
    main()
