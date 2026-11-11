"""Run without Kodi: python results/test_edit_color.py."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


xbmc = SimpleNamespace(getSkinDir=Mock(return_value="skin.horizonzv"),
                       getInfoLabel=Mock(return_value="80112233"),
                       getLocalizedString=str, executebuiltin=Mock())
dialog = Mock()
sys.modules["xbmc"] = xbmc
sys.modules["xbmcgui"] = SimpleNamespace(Dialog=lambda: dialog, INPUT_ALPHANUM=0)
spec = importlib.util.spec_from_file_location(
    "edit_color", Path(__file__).resolve().parents[1] / "resources/scripts/edit_color.py")
editor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(editor)


class EditColorTests(unittest.TestCase):
    def setUp(self):
        xbmc.executebuiltin.reset_mock()
        xbmc.getSkinDir.return_value = "skin.horizonzv"
        xbmc.getInfoLabel.return_value = "80112233"
        dialog.reset_mock(side_effect=True)

    def test_normalize_and_reject_commands(self):
        self.assertEqual(editor.normalize_color(" #abcdef "), "FFABCDEF")
        self.assertEqual(editor.normalize_color("00112233"), "00112233")
        for value in ["", "FFF", "GG112233", "FF112233),Quit()", "FF112233\nQuit()"]:
            with self.assertRaises(ValueError):
                editor.normalize_color(value)

    def test_opacity_preserves_rgb(self):
        for percent, alpha in [("0", "00"), ("50", "80"), ("100", "FF")]:
            self.assertEqual(editor.with_opacity("99112233", percent), alpha + "112233")
        for value in ["-1", "101", "50.5", "x"]:
            with self.assertRaises(ValueError):
                editor.with_opacity("FF112233", value)

    def test_menu_and_input_cancel_preserve_setting(self):
        dialog.select.return_value = -1
        editor.main()
        xbmc.executebuiltin.assert_not_called()
        dialog.select.return_value = 0
        dialog.input.return_value = ""
        editor.main()
        xbmc.executebuiltin.assert_not_called()

    def test_invalid_then_valid_hex(self):
        dialog.select.return_value = 0
        dialog.input.side_effect = ["bad", "#123456"]
        editor.main()
        dialog.ok.assert_called_once()
        xbmc.executebuiltin.assert_called_once_with("Skin.SetString(MySkinColor,FF123456)")

    def test_invalid_then_valid_opacity(self):
        dialog.select.return_value = 1
        dialog.numeric.side_effect = ["101", "0"]
        editor.main()
        dialog.ok.assert_called_once()
        xbmc.executebuiltin.assert_called_once_with("Skin.SetString(MySkinColor,00112233)")

    def test_different_skin_is_untouched(self):
        xbmc.getSkinDir.return_value = "skin.metis"
        editor.main()
        dialog.select.assert_not_called()
        xbmc.executebuiltin.assert_not_called()


if __name__ == "__main__":
    unittest.main()
