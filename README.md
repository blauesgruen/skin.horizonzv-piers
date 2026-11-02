# Horizonz V für Kodi Piers

Dieser Checkout liegt unter `skin.horizonzv-piers`; die Add-on-ID lautet weiterhin `skin.horizonzv`. Das Manifest fordert `xbmc.gui` 5.18.0 an. Der Skin wird derzeit auf entfernte und veraltete Kodi-Schnittstellen geprüft und überarbeitet. Die bisherigen Laufzeittests verwenden eine getrennte Kodi-22-RC1-Installation.

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
- Skinhelper Colorpicker BG (`script.skin.helper.colorpicker.bg`)

Disc-Grafiken werden aus Kodis Artwork-Feldern `discart`, `disc` und `cdart` gelesen. Dafür ist keine direkte CDArt-Manager-Integration im Skin vorhanden.

## Kompatibilitätsprüfung

- [Überarbeitungsplan](results/ueberarbeitungsplan.md)
- [Quellen und Einzelbefunde](results/kodi22_compatibility_audit.md)
- [Kodi-Laufzeitprüfung und offene Testfälle](results/kodi22_runtime/PRUEFBERICHT.md)
- [Wake-on-LAN-Umbau](results/wol_ueberarbeitung.md)

Kodi-23-Angaben beziehen sich auf veröffentlichte Entwicklungsdokumentation. Offene Medien-, PVR-, Plattform- und Add-on-Tests sind im Prüfbericht ausgewiesen.

Der Skin geht auf die Horizonz-Mockups von xb2iris zurück.
