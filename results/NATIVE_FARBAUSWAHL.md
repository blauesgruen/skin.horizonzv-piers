# Native Farbauswahl in HorizonzV

Stand: 11. November 2026. Ersetzt die zuvor dokumentierte direkte Unterstützung von Skin Helper ColorPicker BG.

Die Palettenauswahl in SkinSettings verwendet jetzt `Skin.SetColor(MySkinColor,31394,FFFFFFFF)`. Der vorhandene `DialogColorPicker.xml` bleibt unverändert und liefert das HorizonzV-Design. Die Standardpalette kommt aus Kodi; es werden keine Metis-Layouts oder Farblisten kopiert. Bestehende `MySkinColor`-Werte werden beim Start nicht verändert.

„Farbe bearbeiten“ öffnet die Auswahl zwischen Hex-Eingabe und Deckkraft. Der Skin-Helfer `resources/scripts/edit_color.py` verwendet dafür Kodi-Dialoge. Sechsstellige RGB-Eingaben erhalten volle Deckkraft; achtstellige ARGB-Eingaben behalten ihren Alpha-Wert. Deckkraft von 0 bis 100 Prozent ändert ausschließlich Alpha. Ungültige Eingaben werden zurückgewiesen, Abbruch speichert nichts. Die Palette selbst bietet diese zusätzlichen Eingaben nicht.

Entfernt sind die Installations-/Aktivierungsaufrufe, beide Einträge in der Liste unterstützter Add-ons, der BG-spezifische Dialog und seine Titelvariable. README und direkte Unterstützungsübersicht sind angepasst. Andere Add-ons und Metis wurden nicht verändert.

## Prüfung

- `python -B results/test_edit_color.py`: sechs erfolgreiche Tests für RGB/ARGB, Eingabevalidierung einschließlich Befehlsfragmenten, Deckkraftgrenzen, Abbruch und Schutz anderer Skins.
- `python tools/check_skin_compatibility.py`: 166 Dateien, keine Fehler oder Warnungen; begrenzte statische Prüfung.
- Sichtbarer Kodi-Test in der bestehenden getrennten Installation: 162 Palettenfarben und Titel vorhanden; Auswahl gespeichert; Abbruch erhält die Farbe; Hex-Eingabe `40123456` gespeichert; 50 Prozent Deckkraft ergibt `80123456`; Abbruch des Bearbeitungsmenüs erhält den Wert. [Ergebnisse](kodi22_runtime/native_accent_checks.json), [Palette](kodi22_runtime/native_accent_palette.png), [Bearbeitungsmenü](kodi22_runtime/native_accent_edit_menu.png), [Deckkraft](kodi22_runtime/native_accent_opacity.png).
- Testprozess beendet, Testeinstellungen und kopierte Test-Skin-Dateien bytegleich wiederhergestellt. Der erfolgreiche Lauf enthält keine ERROR-/FATAL-Logzeilen. Mausbedienung und weitere Sprachen wurden nicht nativ geprüft; neue Texte liegen auf Deutsch und Englisch vor.

Die drei vorherigen Testversuche sind als `native_accent_*_probe_failure.json` erhalten. Zwei verwendeten falsche Fensterkennungen; der dritte bediente die numerische Eingabe ohne vorheriges Löschen des vorbelegten Wertes. Das sind Fehler des Testhelfers, keine nachgewiesenen Produktfehler. Der abschließende Helfer verwendet die korrekten Kennungen und die tatsächlichen Ziffern-/Löschtasten.

## Grundlagen

- Lokaler Metis-Aufruf: `xml/Generated_Settings.xml` verwendet `Skin.SetColor`; Metis wurde ausschließlich gelesen.
- [Kodi Piers: SkinBuiltins.cpp](https://github.com/xbmc/xbmc/blob/Piers/xbmc/interfaces/builtins/SkinBuiltins.cpp): Einstellung, numerische Titel-ID, Vorauswahl und optionale Farbdatei; Speicherung nach Bestätigung.
- [Kodi Piers: GUIDialogColorPicker.cpp](https://github.com/xbmc/xbmc/blob/Piers/xbmc/dialogs/GUIDialogColorPicker.cpp): nativer Dialog und Rückgabe der ausgewählten ARGB-Farbe.
