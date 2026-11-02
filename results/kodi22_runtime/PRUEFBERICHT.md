# Kodi-22-Laufzeitprüfung – 1. November 2026

Geprüft wurde die getrennte temporäre Kodi-22-RC1-Installation mit Add-on-ID `skin.horizonzv`, Version 1.22.0.1, aus diesem Checkout. Das Log bestätigt den getrennten `special://home`-Pfad und das Laden der Ziel-Skin-Dateien. Die ursprüngliche Kodi-Installation und ihr Profil wurden nicht verändert. Vor dem Start wurden 1.058 Skin-Dateien per SHA-256 abgeglichen; spätere Korrekturen wurden gezielt in die Testkopie übernommen.

## Durchgeführt

- Ersteinrichtung und Startseite geladen; Skin-ID zusätzlich per `GUI.GetProperties` bestätigt.
- Add-on-Browser, Skin-Einstellungen, Wetterfenster, Systeminformation, Videos, Musik und Einstellungen geöffnet. Screenshots wurden über Kodi erzeugt und geprüft. Fenstergröße: 720 × 480; dies belegt keine Darstellung in sämtlichen unterstützten Seitenverhältnissen.
- Favoriten über den von Kodi gemeldeten JSON-RPC-Namen `favouritesbrowser` geöffnet. Der erste Versuch mit `favourites` war ein ungültiger Testaufruf; `favourites.png` zeigt deshalb das vorherige Wetterfenster. Nur `favourites_actual.png` ist eine Favoritenaufnahme.
- Nach zwei Korrekturen Kodi neu gestartet und Wetter, Videos, Musik sowie Skin-Einstellungen erneut geöffnet. JSON-RPC-Zustände stehen in `window_checks.json` und `after_checks.json`; ausgewählte Logzeilen in `before_fix.log` und `after_fix.log`.

## Reproduzierte und korrigierte Skin-Fehler

1. `Panel3Cover` enthielt außerhalb einer Include-Definition zwei nicht auflösbare `$PARAM[viewid]`-Bedingungen. Beim Öffnen von Videos meldete Kodi `Misplaced [` und Fehler beim Parsen der Bedingungen. Beide verwenden jetzt die tatsächliche Ansichts-ID 302. Nach Neustart und erneutem Öffnen trat dieser Fehler im neuen Testlog nicht mehr auf. Ein zusätzlicher XML-Scan fand keine `$PARAM`-Verweise in den direkt unter `<includes>` definierten Variablen. Die Bildauswahl mit echten Staffelpostern steht noch aus.
2. Ohne Wetterdaten erzeugten zwei aktuelle Wetterbild-Controls den Pfad `resource://resource.images.weathericons.default/.png/` und Verzeichnisfehler. `WeatherIcon` liefert jetzt bei leerem `Current.FanartCode` einen leeren Wert, und das Wetterfenster nutzt diese gemeinsame Variable. Nach Neustart und erneutem Öffnen trat diese Pfadabfrage im neuen Testlog nicht mehr auf. Die Darstellung mit echtem Wetteranbieter und animierten Icons steht noch aus.

## Verbleibende Funde

- Die anfangs reproduzierte Warnung `Trying to add unsupported control type 7` wurde durch den unten beschriebenen Skin-Timer-Ersatz beseitigt.
- `DefaultMusicSources.png` wird von Kodi angefordert, ist im Skin aber nicht auffindbar. Die statische Texturinventur erfasst diese vom Kern gelieferten Dateinamen nicht vollständig. Beim Öffnen der Musiknavigation wird der fehlende Pfad protokolliert.
- Der ursprüngliche dynamische Ursprung des bloßen Pfads `home_tvshows.jpg` bleibt ungeklärt. Die Pfadbildung wurde abgesichert; siehe Nachprüfung unten.
- Die anfangs fehlende `Timers.xml` ist jetzt mit dem Wetter-Ausblendetimer vorhanden; die Ladewarnung trat im neuen Testlauf nicht mehr auf.
- Netzwerk-/Repositoryfehler, Audio-Gerätewarnungen und die JSON-RPC-Typwarnung wurden ebenfalls protokolliert. Sie sind durch diesen Test keinem Skin-Codefehler zugeordnet.

## Noch nicht bewiesen

Disney+- und andere Plugin-Pfade, lokale/SMB-Extra-Fanart mit echten Medien, PVR, Videoversionen, Wiedergabe/Seek/Pause, Spielstände, Artist Slideshow und andere optionale Integrationen benötigen weitere Testdaten bzw. installierte Anbieter im isolierten Profil. Das leere Wetterfenster belegt keine Wetteranbieter-Kompatibilität. Die geprüften leeren Medienansichten belegen keine korrekte Darstellung aller Metadaten. Die Aufgabe ist damit nicht abgeschlossen.

## Nachprüfung: Hauptmenü-Wettertimer

Der nicht unterstützte Button wurde aus dem fokussierten Hauptmenü-Listenlayout entfernt. `xml/Timers.xml` steuert jetzt den bestehenden Fokuswechsel zu Control 666: Start nur auf der Startseite, mit Fokus auf dem Wetter-Menüpunkt, eingeschalteter Ausblendeoption und nicht leerem Wetteranbieter. Abbruch bei Verlassen dieser Bedingungen; Ablauf nach zehn Sekunden ohne eigenen Wert beziehungsweise nach `Skin.Numeric(hidehomemenu_timer)`. Die alte Alarm-Variable und ihre CancelAlarm-Aufrufe wurden entfernt.

Die erste Timerfassung mit gemischter Groß-/Kleinschreibung wurde beim Prüfen verworfen: Bedingungen lösten den Namen kleingeschrieben auf, sodass Kodi den Timer beim Ablaufvergleich nicht fand. Die geprüfte Fassung verwendet durchgehend `homeweatherautohide`. `weather_timer_draft_case_error.json` dokumentiert ausschließlich diesen fehlgeschlagenen Entwurf.

Folgende Fälle wurden anschließend im laufenden Kodi geprüft:

- Leerer eigener Wartezeitwert: Fokus wechselt nach ungefähr zehn Sekunden von 9000 zu 666; `weather_timer_default.json`.
- Eigener Wert `2`: Fokus wechselt nach ungefähr zwei Sekunden zu 666; `weather_timer_custom.json`.
- Wetter-Menüpunkt vor Ablauf verlassen: Timer stoppt, Fokus bleibt auch nach Ablauf der ursprünglich eingestellten Zeit im Menü; ebenfalls `weather_timer_custom.json`.
- Wetter-Menüpunkt ohne ausgewählten Anbieter: Timer bleibt aus, Menü behält den Fokus; `weather_timer_no_provider.json`.
- Zurücknavigation aus Control 666 ins Hauptmenü funktioniert. `home_weather_hidden.png` zeigt die ausgeblendete Menüleiste.
- `timer_after.log` enthält weder die frühere Button-Warnung noch Fehler beim Laden oder Auflösen des neuen Timers.

Für die positiven Timerfälle wurde ausschließlich im getrennten Testprofil ein synthetischer, nicht installierter Wetteranbietername als nicht leerer Einstellungswert gesetzt und anschließend wieder geleert. Es wurden keine Wetterdaten und kein Wetter-Add-on installiert oder verändert. Damit ist die Timer-/Fokuslogik belegt, nicht die Integration eines echten Anbieters. Deaktivieren der Ausblendeoption während eines laufenden Timers und weitere Eingabegeräte/Seitenverhältnisse bleiben ergänzende Prüfungen.

Quellen: https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/addons/gui/skin/SkinTimerManager.cpp und https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/addons/gui/skin/SkinTimer.cpp.

## Nachprüfung: Ressourcen und Home-Menüeinträge

`DefaultMusicSources.png` ist jetzt eine unveränderte Kopie des vorhandenen `DefaultFolder.png`. Nach Neustart und Öffnen von Home und Musik enthält `resources_after.log` keine Meldung für dieses fehlende Symbol und keinen bloßen `home_tvshows.jpg`-Pfad. `resource_checks.json` bestätigt den Ziel-Skin und die geöffneten Fenster. Das beweist noch nicht die ursprüngliche Ursache des Home-Pfadfehlers.

Die Variable `backgroundfolder` liefert jetzt auch bei `onlyone` einen vollständigen Ordner und besitzt einen Standard-Fallback, wenn noch kein Hintergrundpaket gewählt ist. Die eigentliche Auswahl des gemeinsamen Hintergrunds bleibt in der bisherigen `background`-Variable. Die sieben von Kodi ignorierten Tags `label3` bis `label9` in den statischen Home-Einträgen wurden durch `label2` ersetzt. Im Sortierdialog verwendet Eintrag 9 jetzt sein eigenes Hintergrundbild und seine eigene benutzerdefinierte Grafik statt der Werte von Eintrag 7.

Laufzeittest mit aktiviertem `onlyone`, Gambit-Paket und eingeblendeten Custom-Einträgen 3–9: Alle sieben liefern über `Container(9000).ListItem.Label2` ihren vollständigen eigenen Pfad. Auch die anderen angetroffenen Menüeinträge liefern vollständige Pfade. Die aufgelösten Dateien existieren im Checkout. Beleg: `home_background_checks.json`. Die zusätzlich aktivierten Testoptionen wurden anschließend im isolierten Profil zurückgesetzt und Kodi beendet. Der vollständige Dateiabgleich der Skin-Testkopie steht in `resource_copy_check.json`. Die visuelle Prüfung jedes Hintergrundpakets und eigener Grafiken im Sortierdialog steht noch aus.

Primärquelle für die gelesenen Tags statischer Einträge: https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/guilib/GUIStaticItem.cpp. Dies sind Skin-Fehler beziehungsweise fehlende Ressourcen; eine Entfernung dieser Tags in Kodi 22 ist damit nicht belegt.

## Nachprüfung: lokale Audiowiedergabe

Im isolierten Profil wurde eine 90 Sekunden lange stumme Mono-WAV-Datei (22.050 Hz, 16-Bit-PCM) erzeugt und mit dem internen Audioplayer abgespielt. Geprüft wurden Visualisierung, Pause, ein relativer Suchsprung um 35 Sekunden, Fortsetzen, Öffnen des Musik-OSD, Stoppen und Rückkehr zur Startseite. Kodi bestätigte während der Pause `Player.Paused=true`; nach dem Suchsprung bestätigte es `Player.HasPerformedSeek(2.5)=true`. Der Sprung beendete in diesem Test die Pause; die unmittelbar zurückgegebene Suchzeit war noch der alte Wert, die spätere Abfrage lag bei ungefähr 37 Sekunden. Daraus wird kein Fehler des Skins abgeleitet.

`music_paused.png` wurde visuell geprüft: Standardcover, Dateiname, Laufzeit und Pauseanzeige sind sichtbar. Kodi bestätigt das Musik-OSD als Fenster 10120 in `music_osd_checks.json`; eine eigene OSD-Aufnahme wurde trotz akzeptiertem Screenshot-Aufruf nicht erzeugt. Deshalb ist dessen vollständige visuelle Prüfung weiterhin offen. `music_playback_checks.json` enthält die ersten Wiedergabe-/Pause-/Suchabfragen; `music_playback.log` enthält das Laufzeitlog einschließlich des zweiten OSD-Versuchs.

Neuer Ressourcenfund: `MusicPlayer.Codec` liefert für diese Datei `pcm_s16le`; die zwei entsprechenden dynamischen Codec-Bildpfade in `MusicVisualisation.xml` erwarten `flagging/audio/pcm_s16le.png`, das fehlt. Eine bestehende Datei `pcm_s16be.png` zeigt tatsächlich das AIFF-Logo und ist daher kein sachlich korrekter pauschaler Ersatz für PCM. Ebenso wäre das WAV-Logo als allgemeines PCM-Codec-Symbol nicht eindeutig, weil der Codec nicht das Containerformat bestimmt. Entscheidung im Überarbeitungsplan: Codec- und Containerdarstellung trennen beziehungsweise eine korrekte PCM-Grafik mit einem sinnvollen Fallback für unbekannte Codecs vorsehen; noch nicht umgesetzt. Dies ist ein Ressourcen-/Darstellungsfund, keine belegte Kodi-Entfernung.

Keine XML-/Bedingungsparsefehler und keine Warnung über nicht unterstützte Controls wurden beim Laden von Visualisierung und Musik-OSD gefunden. Das prüft keine Video-Wiedergabe, kein PVR, keine echten Musikmetadaten und keine Artist-Slideshow-Daten. Die Testinstanz wurde anschließend beendet.

## Nachprüfung: nativer WOL-Umbau

Im Skin auf Kodis `WakeOnLan(mac)` umgestellt; zehn mögliche Einträge verwenden ein gemeinsames Include, der Sammelpfad dieselben MAC-Felder. Beim Öffnen werden alte Anbieter-Properties für die zehn Plätze gelöscht, danach einmal Status angefordert. Die Liste endet vor den Detailzeilen; leere Listen erhalten einen Hinweis. Neue Rückmeldungen bestätigen nur die Anforderung.

`wol_no_provider.json`/`.log`: tatsächliches Anbieter-Gating unverändert, Anbieter fehlt. Ein zuvor über einen ausschließlich in der Testkopie ergänzten Home-Onload gesetzter Platz-10-MAC-Wert ist nach Öffnen des Dialogs leer. Liste hat null Einträge; die Leerzustandsbedingung ist wahr.

`wol_intercepted_actions.json`/`.log`: ausschließlich in der Testkopie Anbieter-Aktivierung als wahr eingesetzt und Weck-/Statusaktionen durch SetProperty-Markierungen ersetzt; danach Platz 1 und 10 mit MAC und Platz 2 nur mit IP/Name eingesetzt. Die Auswahl erfolgte anhand des tatsächlichen Eintrags. Klick auf 2 erzeugt keine Aktion, Klick auf 10 ausschließlich dessen Weckmarkierung, Sammelklick markiert 1 und 10 und lässt 2 aus. Keine WOL-Pakete und keine Änderung eines externen Add-ons. Der vorausgehende Versuch mit fälschlich angenommener anfänglicher Fokusposition ist ausschließlich als `wol_intercepted_draft.json`/`.log` aufbewahrt und beweist die falsch bezeichneten Fälle nicht.

Die geprüften Logs enthalten keine Parse-, Include- oder Unsupported-Control-Meldung zu diesem Umbau. Alle Teständerungen wurden anschließend entfernt, die Skin-Dateien vollständig mit der Testkopie abgeglichen und Kodi beendet; `wol_copy_check.json`. Vollständige visuelle Zehnerlistenprüfung, echte Statuslieferung älterer/neuerer Anbieter, Fehler-/Dienstfälle, MAC-Validierung und Gerätestart stehen aus. Quelle und konkrete Abnahmekriterien: `../wol_ueberarbeitung.md`.

## Nachprüfung: Diashow-Info-Override

Der Multiimage-Control des Home-Diashow-Widgets enthielt `<info>Diashow</info>`. Kodi Piers behandelt `info` auch beim Einlesen von `imagepath` als Vorrang vor dem eigentlichen Label. Die konfigurierte dynamische Ordnerangabe wurde dadurch nur einmal als Fallback ausgewertet. Der ungültige Eintrag ist aus dem Produktions-Control entfernt.

Für die Laufzeitprüfung wurde ausschließlich in der isolierten Skin-Kopie ein temporäres Fenster mit einer Kopie dieses Controls, angepassten Abmessungen und zwei Ordnerwahl-Buttons angelegt. `imagepath`, Spiegelung, Maske und Multiimage-Zeiten wurden aus dem Produktions-Control übernommen. Zwei lokale Testordner enthielten je ein unverändert kopiertes vorhandenes Skin-Hintergrundbild. Der korrigierte Control zeigte zunächst Ordner A, nach `Skin.SetString` Ordner B und beim Zurückschalten wieder A; alle drei Screenshots wurden visuell geprüft (`slideshow_initial.png`, `slideshow_changed.png`, `slideshow_returned.png`). `slideshow_switch_checks.json` bestätigt die zugehörigen Skin-String-Werte.

Gegenversuch: Nur im Test-Control den alten `info`-Tag wieder eingesetzt. Der Skin-String wechselte erneut nach B (`slideshow_before_checks.json`), die Aufnahme zeigte jedoch weiterhin das erste Bild aus A (`slideshow_before_changed.png`, visuell geprüft). Das reproduziert den Fehler und grenzt die Korrektur auf den Info-Override ein. Logs: `slideshow_before.log` und `slideshow_after.log`.

Danach Kodi beendet, temporäres Fenster entfernt, Home-Datei und vorherige Test-Skin-Einstellungen wiederhergestellt und die vollständige Skin-Kopie abgeglichen (`slideshow_copy_check.json`). Kein externes Add-on geändert. Der Test bestätigt die dynamische Bildquelle, nicht die vollständige Home-Widget-Anordnung. Leere/nicht lesbare Ordner, viele Bilder und schnelles Wechseln während eines laufenden Ladevorgangs bleiben ergänzende Fälle.

Die separat geprüften `imagepath`-Attribute `border`, `diffuse`, `flipx`, `colordiffuse` und `fallback` werden von Piers gelesen und bleiben erhalten. Vollständige direkte Multiimage-Inventur: `../kodi22_inventory/multiimage_review.json`.

## Nachprüfung: Video, Suchzeitfenster und lokaler Fanart-Ordner

Eine 90 Sekunden lange AVI-Datei mit unkomprimiertem 160×90-Bild, fünf Frames pro Sekunde und ohne Audio wurde im getrennten Testprofil erzeugt. Die wechselnden Farbbalken sind synthetische Testdaten; vorhandene Medien wurden nicht verändert. Kodi meldete den internen Videoplayer und Vollbildfenster 12005. Pause, relativer Suchsprung, Seekbar und Video-OSD wurden geöffnet; `video_paused.png`, `video_seek.png` und `video_osd.png` visuell geprüft. Kodi bestätigte Pause, Video ohne Audio, sichtbare Seekbar und den kürzlichen Suchvorgang; dieser Zustand wurde später falsch. Die Seekbar blieb wegen der weiterhin aktiven Pause sichtbar. Belege: `video_playback_checks.json`, `video_playback.log`. Für die OSD-Aufnahme war ausschließlich in der Testkopie ein verzögerter Screenshot-Onload ergänzt; dieser ist entfernt.

Wichtige Korrektur am Skin: Die frühere Übernahme von `HasPerformedSeek(2.5)` erhält keine 2,5 Sekunden. Piers liest den Parameter als Integer und verwendet nur den Präfix 2. Acht Bedingungen verwenden nun `HasPerformedSeek(3)`, entsprechend dem vorhandenen Seekbar-Fenster. Laufzeitvergleich nach einem relativen Fünfsekundensprung: `2` und `2.5` waren in allen Abfragen identisch; `3` blieb länger wahr und wurde danach ebenfalls falsch (`seek_interval_checks.json`, `seek_interval.log`). Die gemessenen Abfragezeiten beginnen mit der RPC-Antwort, nicht mit dem späteren Abschluss des Suchvorgangs; daraus werden keine genaueren Fristen abgeleitet.

Der erste Video-Lauf erzeugte Abfragefehler für den nicht vorhandenen lokalen Ordner `testmedia/extrafanart`. Anschließend wurde dort ein Ordner mit zwei unverändert kopierten Skin-Bildern angelegt. Die produktive Variable `PlayerExtraFanartPath` und Control 2016 wurden unverändert verwendet: Kodi meldete ein tatsächlich geladenes JPG aus diesem Ordner, Control 2016 sichtbar und Hintergrundvideo-Control 2015 unsichtbar. Die Aufnahme `local_extrafanart_home.png` zeigt das Bild als Home-Hintergrund. Nach Stoppen sind `Player.FolderPath` und `Control.GetLabel(2016)` leer. Belege: `local_extrafanart_checks.json`, `local_extrafanart.log`; dort kein fehlender Fanart-Ordner mehr.

In diesem zweiten Lauf wurde außerdem ein falsch geformter absoluter `Player.Seek`-Testaufruf mit `Invalid params` abgelehnt. Er liefert ausdrücklich keinen Suchnachweis und ist kein Skin-Fehler. Die erfolgreichen relativen Aufrufe sind getrennt in den Video-/Intervallbelegen enthalten. Netzwerk-Verbindungsfehler sind weiterhin sichtbar und durch diese Tests keinem Skin-Defekt zugeordnet.

Keine Parse- oder Unsupported-Control-Meldungen beim Laden der geprüften Videofenster gefunden. Nach allen Versuchen Kodi beendet und die vollständige Skin-Kopie abgeglichen (`video_copy_check.json`). Ungeprüft bleiben unter anderem Tonspuren, Kapitel, Untertitel, PVR, Plugin-/Disney+-Pfade, SMB, schnelle Medienwechsel und weitere Seitenverhältnisse. Der vorhandene lokale Fanart-Ordner bestätigt keine Verhinderung von Plugin-Aufrufen.

Primärquellen für die Intervalldefinition: https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/guilib/guiinfo/PlayerGUIInfo.cpp und https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/cores/DataCacheCore.cpp. AVI-Testdateiformat: https://learn.microsoft.com/en-us/windows/win32/directshow/avi-riff-file-reference.

## Nachprüfung: Kapitelanzeige und unterstützte Zahlenbedingungen

Die vorige Aufnahme zeigte bei der kapitel-losen Testdatei „Chapter 00/00“. Die Ursache war eine zweite Kapitelzeile in `DialogSeekBar.xml` ohne Sichtbarkeitsbedingung. Sie hat jetzt `Integer.IsGreater(Player.ChapterCount,0)`. Andere vorhandene Bedingungen mit direktem `Player.ChapterCount` bleiben bestehen: Piers liefert den Wert als Integer und verwendet bei fehlender spezieller Bool-Auswertung einen Wert ungleich null als wahr. Dieser Gebrauch ist somit unterstützt und kein Entfernungsfund.

Erneuter Wiedergabetest mit derselben Datei: Kapitel/Anzahl jeweils `00`, direkte und explizite Zahlenbedingung beide falsch, Pause und Seekbar aktiv (`chapter_checks.json`). `video_no_chapters.png` wurde visuell geprüft und zeigt die Pauseanzeige ohne „00/00“. Keine Parse-/Unsupported-Control-Meldung im zugehörigen Log gefunden. Kodi beendet und Kopie vollständig abgeglichen (`chapter_copy_check.json`). Der positive Darstellungsfall mit echten Kapiteln steht weiterhin aus.

Auch `Window.Is(window)` ist in Piers ein eigener unterstützter Kontextvergleich und wird nicht pauschal durch `Window.IsActive` ersetzt. Quellen und Prüfgrenzen: `../kodi22_inventory/boolean_type_review.json`.

## Nachprüfung am 2. November: Artist-Slideshow-Anforderung

Der Start wird jetzt durch einen zentralen Skin-Timer ausgelöst; der alte MusicVisualisation-Onload-Aufruf ist entfernt. Erst wenn Audiowiedergabe, sichtbare Visualisierung, aktivierter Anbieter und mindestens eine passende Skin-Option zusammenkommen, fordert der Timer den Start an. Das deckt auch nachträgliches Einschalten während eines bereits offenen Fensters ab. Die vorhandene Provider-Running-Property verhindert im Normalfall einen unnötigen Aufruf; aus ihr wird keine atomare Sperre für beliebige externe Aufrufer abgeleitet.

Kodi wurde mit normal sichtbarem Fenster gestartet und über AppActivate in den Vordergrund geholt (Ergebnis erfolgreich, Fenster-Handle und Sitzung in `artist_timer_visibility.json`). Tests ausschließlich in der getrennten Skin-Kopie, zunächst mit echter Add-on-Prüfung und fehlendem Anbieter: Biografie eingeschaltet, Timer bleibt aus (`artist_timer_no_provider.json`/`.log`).

Für die anschließenden Zustandsprüfungen ersetzte nur die Testkopie den Startbefehl durch eine Property-Markierung und die Anbieter-Bedingung durch einen steuerbaren Testschalter. Eine temporäre sichtbare Dialogansicht schaltete die vier tatsächlichen Skin-Einstellungen. Geprüft: Fanart/Biografie/Alben/ähnliche Künstler jeweils einzeln einschalten; Markierung löschen und dieselbe Option aus-/wiedereinschalten, ohne dass sie erneut gesetzt wird; Rücksetzen beim Verlassen, gemeldeter laufender Anbieter ohne neue Markierung, neuer Kontext mit neuer Anforderung, Deaktivieren/Reaktivieren des Anbieters sowie Wiedergabestopp. Erfolgreiche Einzelzustände sind in `artist_timer_assertions.json` zusammengefasst; Rohzustände stehen in `artist_timer_intercepted.json`, Log in `artist_timer_intercepted.log`.

Die Prüfsteuerung musste zwei Beobachtungsfehler korrigieren: Ein erster Fensterwechsel ließ den modalen Testdialog noch offen (`artist_timer_draft_initial_state.json`); später lief die 90-Sekunden-Testdatei während einer Unterbrechung aus, sodass eine erwartete aktive Visualisierung bereits Home war. Zusätzlich wurden Zwischenzustände vor dem nächsten GUI-Durchlauf beobachtet. Die endgültigen Assertions schließen den Dialog explizit, warten auf beobachtete Zustände und starten den zweiten Abschnitt mit erneut laufender Audiodatei. Die vorherigen Wartezustände sind Diagnosematerial, keine erfolgreichen Assertions.

Keine Parse-, Include-, Unsupported-Control- oder Timerauflösungsfehler in den geprüften Logs gefunden. Danach Kodi beendet, Testdialog entfernt, Home/Visualisierung/Timer und Testprofil-Einstellungen wiederhergestellt; vollständiger Skin-Dateiabgleich in `artist_timer_copy_check.json`. Keine externe Add-on-Implementierung geändert oder im Test gestartet.

Zum Abschluss der abgefangenen Tests stand der echte Start noch aus; die folgende Prüfung ergänzt diesen Nachweis. Offen bleiben Abruf und Darstellung echter Künstlerdaten, bereits aktivierte Optionen beim Eintritt mit echtem Anbieter, Anbieterabsturz und Radio-/PVR-Sonderfälle. Der Timer verfolgt die Startanforderung, nicht den Erfolg der Datenbeschaffung. Er bleibt nach dem Ausschalten aller Optionen bis zum Kontextende aktiv und beendet das externe Skript nicht.

## Nachprüfung am 2. November: tatsächlicher Artist-Slideshow-Start

Für diesen Lauf wurden Artist Slideshow 4.2.1 und sieben benötigte Python-Module unverändert aus der vorhandenen Installation in die getrennte Testinstallation kopiert und dort aktiviert. Keine Einstellungen/API-Schlüssel aus dem Originalprofil übernommen. SHA-256-Abgleich aller 460 kopierten Quelldateien vor dem Start und erneut nach dem Lauf: keine Abweichung (`artist_actual_dependency_copy.json`); vom Interpreter erzeugte Cachedateien sind dabei ausgenommen. Die Kopien bleiben nur im isolierten Testprofil installiert.

Kodi normal sichtbar gestartet und erfolgreich in den Vordergrund geholt (`artist_actual_visibility.json`). Die produktive Timerbedingung und der echte `RunScript`-Aufruf waren unverändert. Eine temporäre Testansicht enthielt ausschließlich Buttons zum Setzen/Zurücksetzen der tatsächlichen Biografie-Skin-Einstellung.

Vor Aktivierung: Audio läuft, Anbieter aktiviert, Biografie aus, Timer aus und Running-Property leer. Nach Aktivierung während der offenen Visualisierung: Timer aktiv; das echte Add-on setzt `ArtistSlideshowRunning=True`. Das Log meldet Version 4.2.1 und „music playing“. Nach Aus-/Wiedereinschalten bleibt das Skript aktiv; im gesamten Lauf genau ein entsprechender Skriptstart-Eintrag. Belege: `artist_actual_start.json`, `artist_actual_addons.json`, `artist_actual.log`.

Nach Stoppen der Audiodatei: Skin-Timer aus, Running-Property wieder leer, `ArtistSlideshow.CleanupComplete=True` (`artist_actual_stop.json`). Der Anbieter hat damit seine eigene normale Bereinigung ausgeführt; der Skin hat ihn nicht mit StopScript beendet. In diesem Lauf keine Python-Exception, Parsing- oder Unsupported-Control-Meldung gefunden.

Die stumme WAV-Datei hat keinen Künstlernamen; `MusicPlayer.Artist` und die Biografie bleiben leer. Dieser Lauf belegt Skript-/Modulimport, echten Start durch den Skin, ausbleibenden Wiederholungsstart bei diesen Schaltvorgängen und normales Beenden. Er belegt keinen erfolgreichen Internetabruf und keine Darstellung echter Künstler-/Album-/Ähnlichkeitsdaten.

Anschließend Kodi beendet, Testfenster entfernt, Home/Visualisierung und vorherige Test-Skin-Einstellungen wiederhergestellt sowie vollständige Skin-Kopie abgeglichen (`artist_actual_copy_check.json`). Originalprofil und externe Original-Add-on-Dateien wurden nicht geändert.

## Nachprüfung am 2. November: PCM-Kennzeichnung im Skin

Der zuvor protokollierte fehlende Pfad `flagging/audio/pcm_s16le.png` wird nicht mehr direkt gebildet. Beide Musik-Codec-Controls verwenden die gemeinsame Skin-Variable `MusicCodecTexture`. Für `pcm` oder einen `pcm_`-Codec wird die vorhandene Grafik `flagging/audio/pcm_bluray.png` gewählt; deren Bildinhalt wurde geprüft und lautet „PCM“, ohne Containerlogo. Andere Codecs behalten den bisherigen dynamischen Grafikpfad. Die Controls haben zusätzlich die vorhandene Unknown-Grafik als Fallback. Keine Add-on-Änderung und keine Bildbearbeitung.

Testdaten: vorhandene stumme WAV-Datei und neu erzeugte Sun-AU-Datei, beide 90 Sekunden, mono, 22.050 Hz und 16 Bit. Kodi meldet `pcm_s16le` beziehungsweise `pcm_s16be`. Standard- und Vinylansicht wurden je mit beiden Dateien im sichtbaren Vordergrundfenster geprüft (Prozessstarts mit normalem Fenster, AppActivate erfolgreich). Zum Auslesen des tatsächlich gewählten Bildpfads waren nur in der Testkopie die beiden Bildcontrols mit IDs 731/732 versehen; der Bildpfad war in beiden Ansichten für beide Dateien `flagging/audio/pcm_bluray.png`. Die bloße IsVisible-Abfrage eines Kindes wird nicht als Nachweis der gesamten Elternsichtbarkeit verwendet.

Alle vier Aufnahmen visuell geprüft: `pcm_standard_wav.png`, `pcm_standard_au.png`, `pcm_vinyl_wav.png`, `pcm_vinyl_au.png`. JSON-Abfragen: `pcm_standard_checks.json`/`pcm_vinyl_checks.json`; Logs: `pcm_standard.log`/`pcm_vinyl.log`. Keine Meldung zu fehlenden Texturen, Parsefehlern oder nicht unterstützten Controls in diesen Logs gefunden. Anschließend Kodi beendet, zusätzliche IDs entfernt, ursprüngliche Test-Skin-Einstellungen wiederhergestellt und vollständige Skin-Kopie abgeglichen (`pcm_copy_check.json`).

Dies korrigiert einen Skin-Ressourcen-/Zuordnungsfehler, keine nachgewiesene entfernte Kodi-API. Weitere Nicht-PCM-Formate und der erzwungene Unknown-Fallback wurden in diesem Durchlauf nicht zur Laufzeit geprüft. Primärquelle für die Codec-Bezeichnungen: https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/codec_desc.c; Sun-AU-Format und PCM-Zuordnung: https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/au.c.
