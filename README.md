# HorizonzV für Kodi Piers

Dieser Checkout liegt unter `skin.horizonzv-piers`; die Add-on-ID lautet weiterhin `skin.horizonzv`. Das Manifest fordert `xbmc.gui` 5.18.0 an. Der Skin wird auf entfernte und veraltete Kodi-Schnittstellen geprüft und überarbeitet. Sichtbare Laufzeittests verwenden eine getrennte Kodi-22-RC1-Installation sowie für ausdrücklich freigegebene Integrationen die Standardinstallation.

## Optionale Integrationen und Hilfs-Add-ons

Im Skin sind unter anderem folgende Integrationen beziehungsweise Verwaltungs-/Installationsoptionen vorhanden. Die Auflistung ist keine vollständige Laufzeitfreigabe aller Add-on-Versionen.

- Auto Completion (`plugin.program.autocompletion`)
- Artist Slideshow (`script.artistslideshow`)
- Extended Info (`script.extendedinfo`)
- Global Search (`script.globalsearch`)
- Fritz Smart Home (`script.program.fritzact`)
- German Telecast Offers (`script.service.gto`)
- KN Switchtimer Service (`service.kn.switchtimer`)
- Library Node Editor (`plugin.library.node.editor`)
- Skinhelper Ping (`script.skinhelper.ping`)
- TMDbHelper (`plugin.video.themoviedb.helper`), unter anderem für Anbieterangaben
- Bildressourcen-Auswahl (`script.image.resource.select`)

Die eigene Akzentfarbe nutzt Kodis nativen Farbdialog im HorizonzV-Design. Hex-Eingabe (RGB oder ARGB) und Deckkraft sind ohne Colorpicker-Add-on verfügbar; vorhandene MySkinColor-Werte bleiben erhalten.

Disc-Grafiken werden aus Kodis Artwork-Feldern `discart`, `disc` und `cdart` gelesen. Dafür ist keine direkte CDArt-Manager-Integration im Skin vorhanden.

Für Auto Completion kodiert ein eigener Skin-Helfer die Tastatureingabe als URL-Parameter. Er verwendet die optionale Python-3-API und läuft während der Tastatureingabe bei aktiviertem Anbieter. Versteckte Eingaben sind ausgeschlossen; temporäre Werte werden beim Schließen geleert. Der Anbieter selbst wird nicht verändert. Die Grenze bei dessen eigenen Auswahl-URLs mit Sonderzeichen ist im Prüfbericht dokumentiert.

## Kompatibilitätsprüfung

- [Aktueller Abnahmestand](results/ABNAHMESTAND.md)
- [Änderungen und gefundene Fehler](results/AENDERUNGSUEBERSICHT.md)
- [Überarbeitungsplan](results/ueberarbeitungsplan.md)
- [Quellen und Einzelbefunde](results/kodi22_compatibility_audit.md)
- [Kodi-Laufzeitprüfung und offene Testfälle](results/kodi22_runtime/PRUEFBERICHT.md)
- [Wake-on-LAN-Umbau](results/wol_ueberarbeitung.md)

Die bekannten korrigierten API-Namen und ausgewählte XML-Strukturfehler lassen sich ohne Kodi mit `python -I tools/check_skin_compatibility.py` erneut prüfen (Python 3, nur Standardbibliothek). Optional kann ein anderer Skin-Ordner als Argument angegeben werden. Die Prüfung liest ausschließlich `addon.xml` und `xml/*.xml`, verändert keine Dateien und liefert bei einem Fund Exitcode 1. Sie ist keine vollständige API-/Schema- oder Laufzeitprüfung. Regeln und Quellen sind im Werkzeug hinterlegt.

Kodi-23-Angaben beziehen sich auf veröffentlichte Entwicklungsdokumentation. Offene Medien-, PVR-, Plattform- und Add-on-Tests sind im Prüfbericht ausgewiesen.

Der Skin geht auf die Horizonz-Mockups von xb2iris zurück.
