# HorizonZV Piers: Überarbeitung und Prüfung

Geltungsbereich: dieser Skin (`skin.horizonzv` im Checkout `skin.horizonzv-piers`). Andere Add-ons werden nicht geändert. Der ausführliche Quellennachweis und die Einschränkungen stehen in `kodi22_compatibility_audit.md`.

## Bereits bearbeitet

- Entfernte oder ungültige Kodi-Aufrufe und dokumentiert veraltete Labels wurden im Skin ersetzt oder entfernt. Für Kodi 23 wurden die entfernten `gamewindow`-`pixels`-Elemente entfernt; die vorhandene Screenshot-Anzeige blieb erhalten.
- Extra-Fanart liefert für `plugin://` und bei leerem Listenpfad keinen Verzeichnispfad. Lokale und SMB-Pfade behalten den bestehenden Ausdruck.
- Veraltete oder nicht erreichbare Teile wurden entfernt, darunter die Serienplaner-Oberfläche, der alte Video-Versionen-Dialog und das optionale Next-Episode-Widget des archivierten Library Data Provider. Letzteres ist ein Funktionsverlust; eine gleichwertige native Alternative wurde nicht nachgewiesen.
- PVR-Kanalmanager, Programmsuche, Informationsdialog und Videomanager wurden mit ausgewählten Kodi-Piers-Control-IDs abgeglichen und angepasst. Die Änderungen sind noch nicht zur Laufzeit geprüft.

## Entscheidungen zu den wichtigsten Funden

| Bereich | Entscheidung im Skin | Noch zu prüfen |
| --- | --- | --- |
| Entfernte Bedingungen | `Player.DisplayAfterSeek` und `IsEmpty` durch dokumentierte Alternativen ersetzen; ungültige Bedingungen korrigieren. | Suche, Pause und betroffene Ansichten in Kodi. |
| Veraltete InfoLabels | Beispielsweise `ListItem.Thumb` und veraltete Add-on-Statusangaben auf aktuelle Labels umstellen. Fotometadaten ohne belegten Ersatz wurden entfernt. | Untertitel, Wetter, Add-on-Browser und Informationsdialog mit echten Einträgen. |
| Kodi 23 | Die zwei Speicherstand-`gamewindow`-Controls mit dem entfernten `pixels`-Tag entfernt; Screenshot-Art und Platzhalterbild bleiben. Kodi 22 setzt einen JPEG-Pfad für gespeicherte Spielstände, erzeugt aber nicht in jedem Fall ein Bild. Die übrigen Live-Vorschauen bleiben erhalten. | Alte Spielstände mit eingebetteten Bilddaten und fehlendem JPEG, neue und überschriebene Spielstände sowie den Platzhalter unter Kodi 22 und einer geeigneten Kodi-23-Version prüfen; Software- und Hardware-Rendering berücksichtigen. |
| Extra-Fanart | Direkte `plugin://`-Pfade und leere Listenpfade abfangen; lokale und SMB-Pfade beibehalten. | Logvergleich und schnelle Wechsel; umhüllte URLs sind nicht durch die Präfixprüfung belegt. |
| Aufgegebene Integrationen | Serienplaner-Oberfläche und Provider-Widget entfernen; der Next-Episode-Ersatz ist nicht nachgewiesen. | Funktionsverlust akzeptieren und verbleibende Widgets in Kodi prüfen. |
| PVR und Videoversionen | Kodi-Control-IDs und fehlende Bedienflächen anpassen. | Darstellung, Fokus, gespeicherte Filter und Aktionen mit Testdaten. |

Die Entscheidungen sind im ausführlichen Audit mit Fundstellen und Quellen belegt. Sie sind keine Aussage, dass alle dynamischen oder externen Aufrufpfade bereits verifiziert sind.

## Noch offene Entscheidungen im Skin

1. **Externe Integrationen:** Für jede tatsächlich genutzte Integration den Skin-Aufruf und den Vertrag der konkret eingesetzten Add-on-Version prüfen. Ist eine Schnittstelle nicht mehr nutzbar, den Aufruf im Skin ersetzen oder die zugehörige Oberfläche entfernen; einen möglichen Funktionsverlust ausdrücklich dokumentieren. Fehlende Add-ons oder fehlende Laufzeittests allein belegen noch keine Inkompatibilität.
2. **Plattformaktionen:** Die verbleibenden Startaufrufe für CoreELEC und LibreELEC mit den tatsächlich eingesetzten Versionen prüfen. Der spezielle OpenELEC-Aufruf wurde nach Prüfung des offiziellen Python-2-Quellstands entfernt; siehe Ergänzung unten. Den NAND-Neustart nur auf einem geeigneten Testgerät und mit bekanntem Bootaufbau überprüfen; Add-on-Präsenz allein belegt die Verfügbarkeit des aufgerufenen Skripts nicht. Falls eine Aktion nicht verlässlich unterstützt wird, die entsprechende Skin-Option überarbeiten oder entfernen.
3. **Entwickler-Tastenkürzel:** `keymaps/keyboard.xml` enthält absolute Pfade zu einer anderen Kodi-Installation und wird nach dem geprüften Kodi-Loader nicht automatisch aus dem Skin geladen. F7 verweist auf Fenster 16606; ein entsprechendes Fenster ist im Skin nicht nachgewiesen, ein extern registriertes Fenster aber nicht ausgeschlossen. Vor einer Entfernung den beabsichtigten manuellen Einsatz und das F7-Ziel klären; ein portabler Ersatz für F3/F4 ist bisher nicht belegt.
4. **Restbestände:** Die sieben statisch ungenutzten Schriften und verbleibende Integrationsbedingungen auf dynamische Nutzung und externe Aufrufer prüfen, bevor sie entfernt werden. Die statische Inventur allein reicht dafür nicht aus.
5. **Bibliothekseditor-Beschriftungen:** Die ungenutzte Variable `LibraryEditorLabel` samt acht fehlenden Kennungen 42205–42212 wurde entfernt. Die dynamischen Variablenzugriffe verwenden ausschließlich andere Namenspräfixe; eine Suche in den installierten XML-/Python-/JavaScript-Quellen fand ebenfalls nur die frühere Definition. Die getrennte Library-Node-Editor-Integration bleibt erhalten. Beleg: `kodi22_inventory/dead_variable_review.json`.

6. **Wake-on-LAN:** Der Skin verwendet jetzt native `WakeOnLan(mac)`-Aufrufe statt versionsabhängiger `wolN`-Befehle. Zehn mögliche Geräteplätze teilen einen Include; vor dem Statusabruf werden alte Werte gelöscht. Abgefangene Zieltests und der Fall ohne Anbieter sind geprüft. Echte Statuslieferung mit älteren/neuen Anbietern, Dienst-/Fehlerfälle, vollständige Zehnerlisten-Darstellung und ein echter Gerätestart bleiben offen. Details und Abnahmekriterien: `wol_ueberarbeitung.md`. Andere Add-ons wurden nicht geändert.

## Vor Abschluss erforderlich

Die getrennte Kodi-22-RC1-Laufzeitprüfung ist erfolgt: Ziel-Skin geladen, mehrere Grundfenster geöffnet, Video-/Wetterpfadfehler korrigiert und nach Neustart erneut geprüft. Der nicht unterstützte Button im fokussierten Hauptmenü-Listenlayout wurde durch einen Skin-Timer ersetzt; Standardwartezeit, eigener Wert, Abbruch beim Menüwechsel und fehlender Wetteranbieter wurden zur Laufzeit geprüft. Einzelheiten und Grenzen stehen in `kodi22_runtime/PRUEFBERICHT.md`. Die danach bearbeiteten Ressourcenfunde und ihre Nachprüfung sind im letzten Abschnitt dokumentiert. Der ursprüngliche Auslöser des bloßen `home_tvshows.jpg`-Pfads bleibt ungeklärt.

1. **Ziel-Skin laden:** Das Laden dieses Checkouts wurde im getrennten Kodi-22-Testprofil bestätigt. Bei weiteren Änderungen die Testkopie aktualisieren und erneut prüfen. Für Tests mit Medien und Integrationen weiterhin geeignete Testdaten verwenden; der erfolgreiche Start allein bestätigt diese Funktionen nicht.
2. **Log und Navigation prüfen:** Skin laden, Fenster und Einstellungen öffnen, Add-on-Browser durchlaufen und das Kodi-Debuglog auf ungültige Includes, Bedingungen, Aktionen, fehlende Controls und Ressourcenfehler prüfen. Änderungen im Suchdialog und den PVR-/Video-Infodialogen auf Lesbarkeit, Fokus und Fernbedienung prüfen.
3. **Extra-Fanart prüfen:** Plugin-Pfad einschließlich Disney+, leeren Eintrag, lokale Medien und SMB-Medien durchgehen; auch schnelle Wechsel sowie Wiedergabestart und -ende mit gegebenenfalls leerem Player-Pfad berücksichtigen. Das Log darf für Plugin-Pfade keine vom Skin erzeugte `/extrafanart/`-Abfrage zeigen; lokale und SMB-Fanart muss weiterhin funktionieren.
4. **Medien und PVR prüfen:** Suchen und Pausieren, Musikbewertung, Untertitel- und Wetterbilder, PVR-Suchfilter mit gespeicherten Einstellungen, Senderverwaltung mit Testsender, Aufnahme-/Programminformation sowie Videoversionen mit Testmedien prüfen. Den Radio-RDS-Dialog mit normalen, Komponisten-, Dirigenten- und gemischten Daten auf Inhalt und Darstellung prüfen. Datenbankändernde Aktionen nur an geeigneten Testdaten ausführen.

   Zusätzlich die Filmgenre-Ansichten mit dem reflektierten Icon-Paket und unterschiedlichen Dateiendungen für Film- und Musikgenre-Pakete prüfen; zwei Pfade verwenden jetzt die Filmgenre-Endung. Den Poster-Debugtext bei Episoden und gemischten Einträgen mit dem tatsächlich gewählten Bildpfad vergleichen. Die dynamischen Bild-Fallbacks in `View_722_RightList.xml` und `View_Music_741_CoverWall.xml` mit vorhandenem, leerem und nicht ladbarem Primärbild sowie beim Eintragswechsel testen.

   Die wieder eingebundene Wetterwarnungsansicht mit einem Anbieter prüfen, der die erwarteten Fenster-Properties tatsächlich setzt: keine und mehrere Warnungen, Fokusnavigation sowie ein Anbieter ohne Warnungsdaten. Derzeit werden Anbieter mit ausschließlich nummerierten Warnungsfeldern nicht angezeigt. Für NOAA 2.0.9-b2 vor einer Unterstützung insbesondere Anbietererkennung, Aktualität und unvollständig bereinigte Felder prüfen; eine feste Höchstzahl darf weitere Meldungen nicht unbemerkt abschneiden. Wechsel von Anbieter und Ort, weniger Warnungen als zuvor und fehlgeschlagene Aktualisierung testen.
5. **Optionale Integrationen prüfen:** Für installierte und deaktivierte Add-ons Sichtbarkeit und Aufrufe prüfen. Im Wake-on-LAN-Dialog einzelne Einträge und „Alle starten“ mit aktiviertem und deaktiviertem Ping-Add-on sowie vorhandenen und leeren MAC-Adressen prüfen; die Benachrichtigung bestätigt nur die angeforderte Aktion, keinen erfolgreichen Gerätestart. Bei Artist Slideshow die Informationsoptionen einzeln bei ausgeschaltetem Fanart, ein fehlendes oder deaktiviertes Add-on sowie das Umschalten während der offenen Visualisierung testen. Die Albumliste und die Liste ähnlicher Künstler mit unterschiedlich vielen Einträgen sowie jeweils ausgeblendeter Nachbarliste testen; der automatische Bildlauf muss von der eigenen Liste abhängen. Bei ExtendedInfo insbesondere in Musik- und Videoinformation testen, ob der YouTube-Aufruf nach dem Schließen des Dialogs den richtigen Titel und Künstler beziehungsweise das richtige Jahr erhält; die Reihenfolge der Aktionen allein belegt den verwendeten ListItem-Kontext nicht. Auf CoreELEC die Plattform-Einstellungen nur mit dem tatsächlich installierten Dienst testen. Der interne Neustart hängt zusätzlich von Gerät und Bootkonfiguration ab; die Existenz und Wirkung seines Skripts sind nicht belegt.
6. **Erneut inventarisieren:** Nach Änderungen XML, Includes, Variablen, Ressourcen und lokalisierte Texte prüfen; danach die noch offenen Fälle im ausführlichen Audit bewerten. Dynamische Ausdrücke, Include-Erweiterung und externe Skriptfenster sind durch die statische Inventur nicht vollständig abgedeckt.

Für einen getrennten Windows-Test kann eine eigene Kodi-Installation mit eigener `portable_data`-Struktur und einer Kopie dieses Skins vorbereitet werden. Der geprüfte Piers-Quellcode leitet bei `--portable` den Datenordner vom Kodi-Installationsverzeichnis ab; `--settings` bezeichnet dagegen eine zusätzliche Einstellungsdatei im Kodi-Systemordner und ist kein frei wählbarer Profilpfad. Kodi 22 verwendet einen vom Datenpfad abgeleiteten Mutex. Die Trennung muss vor dem Start anhand der tatsächlichen Pfade und danach im Testlog geprüft werden. Für Disney+, SMB und PVR benötigt das Testprofil zusätzlich geeignete Testdaten bzw. Zugänge; eine leere Installation prüft diese Fälle nicht. Quellen: https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/application/AppParamParser.cpp, https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/platform/win32/WIN32Util.cpp und https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/platform/win32/WinMain.cpp.

## Zukunftskompatibilität

Kodi 23 ist anhand des veröffentlichten Entwicklungsstands geprüft, nicht gegen eine garantierte endgültige Schnittstelle. Neue offizielle Änderungen müssen vor einer Kodi-23-Freigabe erneut abgeglichen und der Skin dort getestet werden. „Alle zukünftigen Entfernungen“ lassen sich nicht vorhersagen.

## Ergänzung: Home-Hintergründe und Musikquellen-Symbol

Korrigiert und gezielt nachgeprüft: fehlendes Musikquellen-Symbol, vollständiger Hintergrundordner einschließlich `onlyone`, gültige `label2`-Metadaten für Custom-Einträge 3–9 und eigene Vorschaugrafik für Custom9 im Sortierdialog. Die ursprüngliche Ursache des bloßen `home_tvshows.jpg`-Logpfads ist weiterhin nicht abschließend zugeordnet. Offen bleiben visuelle Vergleiche der drei Hintergrundpakete, eigener Grafiken und des Sortierdialogs; Quellen und Laufzeitbelege im Prüfbericht.

## Ergänzung: unterstützte Controls in Listenlayouts

Die Typen sämtlicher wörtlich angegebener Controls in den 164 Skin-XML-Dateien wurden mit der Registrierung in Kodi Piers RC1 abgeglichen: kein unbekannter Typ. Zusätzlich wurden 243 `itemlayout`-/`focusedlayout`-Elemente mit 356 rekursiv aufgelösten Include-Aufrufen geprüft: kein weiterer für Listengruppen nicht unterstützter Control-Typ und kein unaufgelöster Include-Aufruf. Bei 443 statischen Items wurden nach der Label-Korrektur keine weiteren unerwarteten direkten Kind-Tags gefunden.

Belege: `kodi22_inventory/control_types.json` und `kodi22_inventory/list_layout_controls.json`. Grenzen: keine vollständige XML-Schemaprüfung, keine Auswertung von Sichtbarkeitsbedingungen oder Parametersubstitution und kein Nachweis der Laufzeitfunktion aller Controls. Die zehn vom allgemeinen Inventurskript gemeldeten Auffälligkeiten sind gesondert zu bewerten; sie belegen keine zehn entfernten Kodi-Schnittstellen.

## Ergänzung: Wiedergabe und Codec-Bilder

Lokale stumme WAV-Datei im isolierten Kodi abgespielt, pausiert, relativ durchsucht und gestoppt; Visualisierung und Musik-OSD geladen. Pausezustand und `Player.HasPerformedSeek(2.5)` sind durch JSON-RPC belegt, die Pauseansicht zusätzlich visuell. Das ist keine Verifikation des Video-Seek-Overlays. Das Musik-OSD ist als geladen bestätigt, seine vollständige visuelle Prüfung steht aus.

Der Ressourcenfehler für `pcm_s16le.png` ist inzwischen im Skin korrigiert: Eine gemeinsame Variable ordnet `pcm`/`pcm_...` der bereits vorhandenen echten PCM-Grafik zu; andere Codec-Pfade bleiben dynamisch und erhalten einen Unknown-Fallback. Mit WAV und Sun AU in Standard- und Vinylansicht zur Laufzeit geprüft. Es wird kein AIFF-/WAV-Containerlogo als allgemeines PCM-Symbol verwendet. Belege und Grenzen im Laufzeitbericht.

## Konkretisierung: Wake-on-LAN ohne versionsabhängige Platzbefehle

Der neue Entwurf in `wol_ueberarbeitung.md` verwendet Kodis belegtes natives `WakeOnLan(mac)` und lässt den Ping-Anbieter die Geräte-/Statuswerte liefern. Dadurch ist kein Vergleich von Versionszeichenketten und kein `wol10`-Aufruf an ältere Skripte nötig. Er umfasst das Leeren alter Platzwerte beim Öffnen, zehn mögliche Einträge, konsistente Einzel-/Sammelziele und Rückmeldungen als Anforderung. Inzwischen im Skin implementiert und mit abgefangenen Zielaktionen geprüft; Anbieterfehler, echte Statuslieferung und die Auswirkungen der Aktualisierung auf andere Statusanzeigen bleiben offen. Die zuvor genannten Freigabelisten-/Delegationsvarianten sind damit Alternativen zum jetzt bevorzugten nativen Ansatz.

Die veröffentlichte Kodi-23-Skinning-Änderungsseite wurde am 1. November erneut gelesen (generiert am 31. Oktober 2026). Sie nennt weiterhin die Entfernung des `pixels`-Tags und `ListItem.Art(screenshot)` als Alternative. Aus dieser Seite ergibt sich keine weitere angekündigte Entfernung; das ist keine Garantie für die endgültige Kodi-23-Schnittstelle.

### WOL-Umsetzung

Die native Variante ist umgesetzt. Der gemeinsame Include bietet zehn mögliche Plätze; „Alle“ verarbeitet dieselben MAC-Bedingungen. Alte Statuswerte werden vor dem Statusabruf geleert, Rückmeldungen nennen eine WOL-Anforderung. Die bisherige irreführende IP-Anzahl entfällt. Aktionsprüfungen mit abgefangenen Befehlen sowie der Fall ohne Anbieter waren erfolgreich; es wurden keine WOL-Pakete gesendet. Der vollständige Stand einschließlich noch offener echter Anbieter-, Netzwerk- und Darstellungstests steht in `wol_ueberarbeitung.md` und im Laufzeitbericht.

## Supportangaben abgeglichen

CDArt Manager war nur in README und Manifest als unterstützt genannt; ein direkter Add-on-Aufruf wurde im Checkout nicht gefunden. Die Angabe wurde entfernt, die allgemeine Anzeige der Artwork-Felder `discart`, `disc` und `cdart` bleibt. Die README benennt jetzt die tatsächlichen optionalen Integrationen/Hilfsangebote und den aktuellen Prüfstand. Daraus wird weder eine Kodi-Entfernung des Art-Typs noch ein allgemeiner Defekt des externen Add-ons abgeleitet.

## Multiimage-Aufrufe und Diashow

Alle 30 direkt definierten Multiimage-Controls auf ihre `imagepath`-Attribute und Info-Overrides geprüft. Die verwendeten Texturattribute werden von Kodi Piers gelesen; sie sind kein Altlastenfund. Der ungültige Eintrag `<info>Diashow</info>` im Diashow-Widget wurde entfernt, weil er die dynamische Ordnerangabe überschreibt und nur deren vorher ausgewerteten Wert als Fallback zurücklässt. Ein Live-Wechsel zwischen zwei Ordnern und zurück ist inzwischen in einer isolierten Testansicht mit dem kopierten Produktions-Control bestätigt, einschließlich vorhandener Maske/Spiegelung. Ein Gegenversuch mit dem alten `info`-Tag blieb beim ersten Ordnerbild. Leerer Ordner, erneutes Öffnen und die vollständige Home-Widget-Anordnung bleiben ergänzende Laufzeitfälle. Quelle und vollständige Fundliste: `kodi22_inventory/multiimage_review.json`.

## OpenELEC-Altintegration entfernt

Der offizielle Quellstand von `service.openelec.settings` fordert Python-API 2.1.0 und verwendet im Einstiegsskript Python-2-Syntax (`except Exception, e`). Kodi Piers stellt `xbmc.python` 3.1.0 mit ABI 3.0.0 bereit. Der spezielle OpenELEC-Startknopf und die zugehörige Präsenzprüfung/Plattformbeschriftung wurden deshalb aus dem Skin entfernt. Ein möglicher inoffizieller Python-3-Fork wurde damit nicht bewertet; dessen spezielle Skin-Abkürzung entfällt ebenfalls.

Die LibreELEC- und CoreELEC-Einträge bleiben getrennt vorhanden. Der gemeinsame gespeicherte Schalter `SubMenu_music_NoLibreelecButton` bleibt bestehen, damit vorhandene Einstellungen für diese beiden Einträge weitergelten. Keine explizite Fokusreferenz auf den entfernten Knopf wurde im Checkout gefunden; die übergeordnete Grouplist ordnet ihre Kinder an. Die echte Plattformfunktion der verbleibenden Einträge ist weiterhin auf dem jeweiligen Zielgerät zu prüfen. Quellen und statische Belege: `kodi22_inventory/openelec_review.json`.

## Video-Seek und lokale Extra-Fanart nachgeprüft

Mit einer erzeugten stummen Videodatei wurden Vollbild, Pause, Seekbar und Video-OSD geladen und die Aufnahmen visuell geprüft. Dabei wurde die Argumentprüfung vertieft: `HasPerformedSeek` liest in Piers ganze Sekunden und akzeptiert `2.5` lediglich als `2`. Die acht zuvor übernommenen Dezimalwerte verwenden jetzt ausdrücklich `3`, passend zum bestehenden Seekbar-Zeitfenster. Ein Laufzeitvergleich bestätigt identische Zustände für `2`/`2.5` und ein längeres Fenster für `3`; die Zeitstempel sind keine exakte Messung ab dem asynchronen Suchabschluss.

Lokale Fanart mit vorhandenem Ordner wurde über den tatsächlichen Player-Ordner und Control 2016 geladen und visuell auf Home bestätigt. Nach Wiedergabeende sind die beiden abgefragten Pfadlabels leer. Ohne lokalen Ordner protokollierte Kodi zuvor dessen fehlgeschlagene Abfrage; mit vorhandenem Ordner trat sie im neuen Lauf nicht auf. Plugin-/Disney+- und SMB-Fälle bleiben gesondert offen, ebenso Videos mit Ton, Kapiteln und PVR.

## Kapitelanzeige und Typprüfung

Die ungeschützte zweite Kapitelzeile der Seekbar zeigt bei null Kapiteln jetzt keine „00/00“-Angabe mehr; mit der kapitel-losen Testdatei visuell geprüft. Eine echte Datei mit Kapiteln bleibt der positive Abnahmefall. Direkte `Player.ChapterCount`-Bedingungen sind durch Kodis Integer-Fallback unterstützt und bleiben erhalten. Auch `Window.Is` ist ein unterstützter eigener Kontextvergleich. Diese geprüften Stellen dürfen nicht als entfernte APIs behandelt werden; Quellen im Typprüfungsbeleg.

## Artist-Slideshow-Start während offener Visualisierung

Der einmalige Onload-Aufruf wurde durch `artistslideshowrequest` in `Timers.xml` ersetzt. Start nur bei sichtbarer Visualisierung, Audiowiedergabe, aktiviertem Add-on und mindestens einer der vier Optionen (Fanart, Biografie, Alben, ähnliche Künstler). Ist `ArtistSlideshowRunning` bereits wahr, erfolgt keine erneute Anforderung. Nach der ersten Anforderung bleibt der Timer innerhalb dieses Visualisierungs-/Audiokontexts verriegelt, auch wenn die Optionen vorübergehend ausgeschaltet werden; dadurch führen schnelle Einstellungswechsel nicht zu mehreren Startaufrufen. Der Timer endet beim Verlassen, Wiedergabeende oder deaktivierten Anbieter. Er beendet nicht eigenständig das externe Skript und ist kein automatischer Fehler-Watchdog.

Im sichtbaren Kodi-Fenster mit abgefangener Startaktion geprüft: alle vier Optionen einzeln nachträglich einschalten, Aus-/Wiedereinschalten ohne weiteren Aufruf, laufender Anbieter, Verlassen, deaktivierter/wieder aktivierter Anbieter und Wiedergabeende. Ein fehlender Anbieter wurde mit unveränderter echter Add-on-Bedingung geprüft. Die echten Künstlerdaten und Metadaten-/Bildlisten sowie Verhalten bei Add-on-Absturz bleiben offen. Kein externes Add-on wurde geändert. Belege und Testgrenzen im Laufzeitbericht.

### Artist Slideshow: echter Start und Bereinigung bestätigt

Zusätzlich zum abgefangenen Zustandsmodell wurde die unveränderte Version 4.2.1 mit ihren Modulen in der isolierten Installation aktiviert. Der produktive Timer startet das echte Skript nach nachträglichem Einschalten der Biografie; Aus-/Wiedereinschalten erzeugt im geprüften Lauf keinen zweiten Start. Nach Audiostopp leert das Add-on seine Running-Property und meldet abgeschlossene Bereinigung. Das sichtbare Kodi-Fenster war im Vordergrund. Da die Testdatei keinen Künstlernamen enthält, bleiben echter Datenabruf, vollständige Darstellung und die weiteren Sonderfälle offen. Quellen/Kopie unverändert geprüft; Details im Laufzeitbericht.

## PCM-Codecs in der Musikvisualisierung

Die zwei Codec-Bildcontrols verwenden jetzt `MusicCodecTexture`: `pcm` und `pcm_...` zeigen `flagging/audio/pcm_bluray.png`, dessen Bildinhalt tatsächlich „PCM“ lautet. Weitere Codec-Namen verwenden den bisherigen dynamischen Pfad; bei fehlender Grafik ist `flagging/audio/unknown.png` als Fallback gesetzt. Es wurden keine neuen Bilder und kein Add-on-Code verändert.

Sichtbare Kodi-Prüfung: WAV mit `pcm_s16le` und Sun AU mit `pcm_s16be`, jeweils Standard- und Vinylansicht. Alle vier zeigen die PCM-Grafik; die Logs enthalten keine fehlenden Texturen. Test-IDs und Test-Skin-Einstellungen wurden entfernt/zurückgesetzt. Ein erzwungener unbekannter Codec und weitere Nicht-PCM-Formate wurden nicht neu zur Laufzeit geprüft.
