# Standardprofil: Integrationstests am 3. November 2026

Der Nutzer hat die Standardinstallation für Disney+ und weitere offene Integrationstests freigegeben. Frühere Aussagen über ein unverändertes Originalprofil beschreiben die vorherigen getrennten Tests. Für diesen Lauf wurden Skin und Screenshot-Pfad vorübergehend geändert und anschließend einschließlich ihrer Default-Attribute zurückgestellt. Andere Add-on-/Core-Quellen wurden nicht bearbeitet. Keine direkte Datenbankbearbeitung und keine Sender-/Gruppenänderungsaktion; normale Kodi-/Anbieter-Caches sind damit nicht als byteweise unverändert zugesichert.

## Ausgangszustand und Skinwechsel

Ausgangsskin `skin.horizonzVI`, keine Wiedergabe. Kodi bestätigt für `skin.horizonzv` den Pfad dieses Checkouts. Private Sicherung der Ausgangseinstellungen und localhost-RPC-Helfer liegen nur im temporären Verzeichnis, keine Zugangsdaten im Repository.

Der erste Laufzeit-Skinwechsel endete nach dem Bestätigungsablauf in einem Absturz. Neuer Dump und ein älterer Standardprofil-Dump vor diesem Test zeigen c0000005 bei kodi.exe+4bd469 mit unterschiedlichen Leseadressen. Keine symbolische Ursache und keine Skin-/Add-on-Schuldzuweisung bewiesen. Dies ist eine andere Fehleradresse als beim früher untersuchten leeren Extras-Manager. Beleg: `standard_skin_switch_crash.json`.

Anschließend Zielskin direkt beim Start geladen: PID 36364, stabiler Testlauf und reguläre Beendigung. Für weitere Tests ist damit der direkte Start ein erprobter Weg; die Ursache des Laufzeitwechsels bleibt offen.

## Disney+

Installierte Version 0.20.33 bietet mit vorhandenem Profilzustand das Menü einschließlich Abmelden. Ohne neue Anmeldung oder Kontoeingabe Movies → Empfehlungen (37 Einträge), Series → Empfehlungen (49 Einträge) und eine Staffelliste (11 Einträge) nativ geöffnet. `Container.Content` jeweils movies/tvshows/seasons, `ListItem.Path` jeweils direkter Plugin-Pfad. Extended Art war bereits an, `no_extrafanart` aus.

16 schnelle Film-Auswahlwechsel sowie Serien-/Staffelwechsel und Wartezeit geprüft. INFO-Log des direkten Startlaufs bis Shutdown: null extrafanart-, RouterError- und ERROR-Zeilen. Das bestätigt den beobachteten Navigationsfall, keine vollständige Netzwerk-Trace-Garantie für jeden Pfad. Keine Wiedergabe gestartet: Disney-Player-Fanart, DRM/Wiedergabe und Wrapper bleiben offen.

Belege: `standard_disney_initial.json`, `standard_disney_movies.json`, `standard_disney_movie_items.json`, `standard_disney_movie_navigation.json`, `standard_disney_series.json`, `standard_disney_seasons.json`, `standard_disney_log_counts.json`, `standard_disney_movies_es.png`.

Eine direkte VAR-Abfrage über GetInfoLabels wurde als ungeeigneter Probeaufruf verworfen. Keine Variablen-Ausgabe aus diesem Probeaufruf behauptet. Ein erneuter Aufruf der Filmliste brauchte länger als die anfänglich feste Wartezeit; anschließend wurde der tatsächliche Content-Zustand geprüft. Die Screenshot-Datei entstand ebenfalls asynchron und wurde erst nach bestätigter Existenz inspiziert.

## Wetter

Gismeteo 0.6.4+matrix.1 liefert Weather.IsFetched, aktuelle Bedingung/Temperatur und FanartCode 26. Daily/Hourly/Weekend/36Hour-Properties sind befüllt, Alerts.IsFetched fehlt. Wetteransicht mit befüllter Prognose und Seitenleiste inspiziert. Die erste Aufnahme war stark abgedunkelt; `standard_weather_awake.png` ist für die Sichtprüfung maßgeblich.

Ein zusätzlicher Fokusversuch auf die Detail-Liste beobachtete Home statt Wetter und gilt ausdrücklich nicht als bestandener Detailansichts-/Fokustest. Keine Wetterkonfiguration geändert; Warnungen mit echten Daten und vollständige Ansichtswechsel bleiben offen. Belege: `standard_weather_pvr_readiness.json`, `standard_weather_properties.json`, `standard_weather_daily_checks.json`.

## PVR

SAT>IP Client 0.1.15 meldet verfügbare PVR-Daten, 86 TV-/103 Radiosender, eine TV-Gruppe, null Aufnahmen/Timer. Keine Aufnahme/Scan aktiv.

Im Sendermanager 10604 native TV→Radio→TV-Umschaltung an Control 34:

- Liste 20: 86→103→86.
- IsRadio: leer→true→leer.
- Button: Radiosender→TV-Sender→Radiosender.

Im Gruppenmanager 10603 entsprechend Liste 12 mit 86→103→86, Nichtgruppiert 0, Gruppenliste 1 und passende Radio-/TV-Beschriftung. Beide Dialoge per Back geschlossen; keine Bearbeitungs-/Speicheraktion gewählt. Bilder inspiziert: `standard_pvr_channels_radio.png`, `standard_pvr_groups_radio.png`.

Dies prüft vorhandene Senderdaten und die korrigierte Skin-Umschaltung, keinen Live-Empfang oder Verwaltungs-Schreibvorgang. Filter, EPG-/Aufnahme-/RDS- und Backend-Aktionen bleiben separat offen. Belege: `standard_pvr_channel_manager_initial.json`, `standard_pvr_channel_toggle_checks.json`, `standard_pvr_group_toggle_checks.json`.

## Folgelauf: PVR-Suchfilter und Programminformation

Zielskin erneut direkt und sichtbar in der Standardinstallation gestartet, PID 35700. Für diesen Lauf eigene frische private Sicherung der Ausgangseinstellungen angelegt. Der erste TV-Sender liefert über Kodi 102 EPG-Einträge. TV-Suche 10704 nativ geöffnet und den Eintrag `pvr://search/search_dialog` / „Neue Suche …“ ausgewählt. Damit übergibt der aufrufende Kodi-Suchbildschirm einen temporären Filter; es handelt sich nicht um die frühere Direktaktivierung eines leeren Dialogs.

Dialog 10605 zeigt nun die übergebenen Daten: Start-/Enddatum, Genre/Dauern, Sendergruppe und „Alle TV-Sender“. Senderauswahl 23 nativ auf „Das Erste HD“ gesetzt. Text in Edit 9 über den nativen Keyboarddialog eingegeben; tatsächlichen Text und Datenfelder mit `Control.GetLabel(id).index(1)` geprüft. Der einfache GetLabel-Aufruf liefert beim Edit die Beschriftung, nicht dessen Eingabetext. Belege: `standard_pvr_search_initial.json`, `standard_pvr_search_filter_initial.json`, `standard_pvr_search_filter_edit.json`, `standard_pvr_search_populated.png`.

Unquotiertes `In aller Freundschaft` ergibt 23 Listeneinträge einschließlich zweier Verwaltungszeilen. Die zusätzlichen Titel sind durch Kodis Standard-ODER-Suche erklärt, nicht als Skin-Fehler bewertet. Anschließend dieselbe Suche mit Anführungszeichen ausgeführt: vier Listeneinträge, davon zwei Verwaltungszeilen und zwei EPG-Treffer mit der Phrase, einschließlich des zuvor aus den EPG-Daten gewählten Programms. Senderfilter bleibt „Das Erste HD“. Beim erneuten Bearbeiten sind Suchtext und Sender weiter vorhanden. Keine Suchdefinition über „Speichern“ angelegt. Belege: `standard_pvr_search_results.json`, `standard_pvr_search_phrase.json`.

Verwerfen geprüft: temporären Text `HZV-CANCEL-20261103` eingegeben, per Back abgebrochen und erneut geöffnet. Vorherige Phrase und Senderfilter sind wieder vorhanden (`standard_pvr_search_cancel_checks.json`). Eine anfänglich zu frühe Textprobe wurde nicht als Fehler des Skins gewertet; maßgeblich sind die später bestätigten tatsächlichen Feldwerte und Fensterzustände.

Ersten EPG-Treffer ausgewählt und native Info-Aktion ausgeführt: Programminformation 10600 enthält passenden Titel, Sender, lokale Start-/Endzeit und Dauer. Back führt nach Ende der Schließanimation wieder zu 10704. Erstes Bild war während der Öffnungsanimation aufgenommen; maßgeblich für die Layoutsichtung ist `standard_pvr_program_info_settled.png` nach vollständigem Einblenden. Daten und bestätigtes Schließen in `standard_pvr_program_info_checks.json`. Keine Erinnerungs-, Umschalt-, Timer- oder Aufnahmeaktion betätigt.

Radio-Suche 10709 ebenfalls über „Neue Suche …“ geöffnet. Derselbe Dialog zeigt leeren neuen Suchtext und „Alle Radiosender“, danach per Back abgebrochen. Keine Radiosuche ausgeführt oder gespeichert (`standard_pvr_radio_search_initial.json`).

Quellen: [Suchfenster und temporäre Filterkopie](https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/pvr/windows/GUIWindowPVRSearch.cpp), [Dialog-IDs und Übernahme der Felder](https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/pvr/dialogs/GUIDialogPVRGuideSearch.cpp), [ODER-Suche und Phrasen](https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/pvr/epg/EpgSearchFilter.cpp), [Textsuchparser](https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/utils/TextSearch.cpp).

Abschluss dieses Folgelaufs: keine Player, Aufnahme oder Scan aktiv; natives Quit und Prozessende, keine neue Dump-Datei. Ausgangsskin/Screenshot-Pfad einschließlich Default-Attribute wiederhergestellt. Sämtliche globalen Settingwerte stimmen mit der frischen Ausgangssicherung überein, keine zusätzlichen Setting-Schlüssel. Null ERROR-Zeilen im beobachteten INFO-Log. Keine rohen Original-Logs kopiert (`standard_pvr_search_cleanup.json`).

Damit sind Grundbefüllung TV/Radio, Bearbeiten des Suchtexts/Senderfilters, positive TV-Phrasensuche, Verwerfen und befüllte Programminformation geprüft. Nicht geprüft sind dauerhafte Suchdefinitionen, alle weiteren Filterkombinationen, Aufnahme-/Timer-/Erinnerungsaktionen oder Live-Empfang. Normale Kodi-Caches werden weiterhin nicht als byteweise unverändert zugesichert.

## Folgelauf: Disney-Wiedergabevoraussetzung

Standardinstallation sichtbar mit dem Zielskin aus `skin.horizonzv-piers` gestartet (PID 11752). Aus der Disney-Filmliste einen Wiedergabeversuch ausgelöst. Statt eines aktiven Players erschien Dialog 12000 mit dem Titel „Verfügbare Widevine CDM-Versionen“ und zwölf Einträgen. Dialogdarstellung im Skin geprüft; keine CDM-Version ausgewählt. Per Back abgebrochen und Rückkehr zu Videos 10025 bestätigt. Vor und nach Abbruch keine aktiven Player.

Damit bleibt die eigentliche Disney-Wiedergabe einschließlich DRM und Player-Fanart ungeprüft. Der Dialog belegt eine Einrichtungsvoraussetzung, keinen nachgewiesenen Skin-Fehler. Keine Add-on-Quelltexte verändert. Belege: `standard_disney_playback_prerequisite.json` und `standard_disney_playback_prerequisite.png`.

Natives Quit und Prozessende bestätigt. Ausgangsskin wiederhergestellt; alle globalen Settingwerte entsprechen der frischen privaten Sicherung, keine zusätzlichen Setting-Schlüssel. Kein neuer Crash-Dump. Im beobachteten INFO-Log null extrafanart-/RouterError-Zeilen, aber eine ERROR-Zeile: `script.module.slyguy - PROXY ERROR: File not found: stop.m3u8?mimetype=application%2foctet-stream`. Ursache und Zusammenhang mit dem Abbruch nicht abschließend geprüft; daher kein fehlerfreier Wiedergabetest behauptet. Keine rohen Logs kopiert. Beleg: `standard_disney_playback_cleanup.json`.

## SMB

Quellenprotokolle enthalten hier nur https; alle 36 über Kodi abgefragten Filmdateien sind local/other. In diesen Beständen ist kein SMB-Testpfad nachgewiesen. Daraus folgt keine Aussage über unregistrierte Freigaben im Netzwerk. Für einen echten SMB-Test wird weiterhin ein geeigneter Pfad benötigt. Nur aggregierte Protokollzahlen gespeichert, keine Medienpfade mit möglichen Zugangsdaten.

## Aufnahme und Abschluss

Screenshot-Aufnahme zusätzlich über den schon aktivierten lokalen EventServer und den [offiziellen Piers-Python-Client](https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/tools/EventClients/lib/python/xbmcclient.py) im privaten temporären Verzeichnis. Kein Test-Add-on installiert und kein Skin-/Add-on-Quellcode instrumentiert. Bilder können den normalen Verbindungshinweis enthalten.

Abschluss: keine aktiven Player, natives Quit, Prozessende und Exiting-Meldung bestätigt. Ausgangsskin und Screenshot-Pfad samt Attributen wiederhergestellt; keine neue Dump-Datei nach dem direkten Start. Keine rohen Standardprofil-Logs, Provider-Header oder Zugangsdaten ins Repository kopiert; nur Zustände, Bilder und Log-Zähler. Belege: `standard_integration_final_counts.json`, `standard_integration_cleanup.json`.

Der zuvor begonnene Dashboard-Animationstest im getrennten Profil wurde ohne Änderung der vier Row-Einstellungen unterbrochen. Nur All-off angesehen; ein zweiter Zustand ist nicht bestanden (`dashboard_animation_before.json`, `dashboard_animation_partial.json`, `dashboard_all_off.png`).

## Wetter-Detailansichten: abgeschlossener Folgelauf

Standard-Kodi sichtbar direkt mit Zielskin gestartet, PID 38744. Wetterfenster 12600 und Weather.IsFetched vor jedem Test bestätigt. Tägliche Ansicht: Sidebar 302 → Rechts → Liste 51 fokussiert, sieben Einträge. Stundenansicht: Sidebar 305, View hourly und Liste 52 mit elf Einträgen; ein zu früher Rechts-Aufruf während des Ansichtswechsels blieb auf 305. Nach beobachtetem fertigen Wechsel erneut Rechts, Fokus 52 bestätigt. Kein Skin-Fokusfehler daraus abgeleitet. 36-Stunden- und Wochenendansicht mit vorhandenen Daten ebenfalls angezeigt und Bilder inspiziert; keine vollständige Fokusfreigabe der statischen Detailgruppen behauptet. Belege: `standard_weather_details_daily.json`, `standard_weather_details_hourly.json`, `standard_weather_details_other.json` und zugehörige PNG-Dateien.

Zusatzfund separat abgelegt: installierter Gismeteo liefert Niederschlagsmenge mit Einheit, Weather.Data hängt nach seinem Formatvertrag % an; beobachtet 0.0 mm gegenüber 0.0 mm%. Kein entfernter API-Aufruf und kein Anbieter-/Core-Quellcode verändert. Kein zusätzlicher Skin-Sonderumbau begonnen (`standard_weather_precipitation_observation.json`). Karten und Warnungen mangels Daten nicht geprüft.

Reguläres Quit/Prozessende, keine aktiven Player/Aufnahme/Scan; Ausgangsskin und sämtliche globalen Settingwerte zur frischen privaten Sicherung identisch, keine neuen Setting-Schlüssel. Null ERROR-Zeilen, kein neuer Dump, keine rohen Logs kopiert (`standard_weather_details_cleanup.json`).

## Liedtext-Anbieter: echter Einstieg, Grenzen des Stop-Nachweises

Standard-Kodi sichtbar mit Zielskin gestartet (PID 35828), aktueller CU LRC Lyrics 6.7.6 aktiviert. Eigene stille WAV über natives PlayMedia gespielt; Audioplayer 0 bestätigt. MusicOSD 10120 geöffnet, bei leerem Skin-Ziel Auswahl 12000 aufgerufen und CU LRC Lyrics gewählt. Nach Auswahl bleibt das OSD geöffnet; erst der weitere Klick auf 701 erreicht den Anbieter und setzt culrc.force von leer auf TRUE. culrc.running war bereits beim Start true; kein neuer Worker-Start daraus behauptet. Im anschließend geöffneten Untermenü sind 2401/2402 sichtbar, aktiviert und 2401 fokussiert. Die unmittelbar nach Auswahl erfolgte Abfrage im versteckten Untermenü ist kein endgültiger Enable-Nachweis.

Keine Lyrics-GUI erschienen. Der Test öffnete das OSD über Home; der gelesene Anbieter prüft in proceed() den Visualisierungs-Kontext. Vollständige Anzeige mit geeigneten Musik-/Lyrics-Daten bleibt deshalb offen. Stop über nativen Control 2402 ausgelöst; running-Property in 30 Beobachtungen weiter true. Das INFO-Protokoll beweist keinen Worker-Stop, und eine persistierende Property beweist umgekehrt nicht allein, dass der Worker weiterläuft. Kein Anbieterfehler oder erfolgreicher Stop behauptet. Belege: lyrics_standard_initial/launch/submenu/stop JSON-Dateien. Keine Add-on-Quelltexte oder -Einstellungen korrigiert.

Audiowiedergabe beendet, keine Player aktiv, natives Quit und Prozessende. Ausgangsskin und ausgewählter Lyrics-Pfad samt Attributen wiederhergestellt; sämtliche globalen und Skin-Settingwerte entsprechen der frischen Sicherung, keine hinzugefügten Setting-IDs. Das Log enthält 57 ERROR-Einträge bei Prüfung der tatsächlichen Logstufe ohne Beachtung der Groß-/Kleinschreibung: 20 Window-Translator-, 25 CCurlFile-, elf Demux- und einen Exception-Eintrag. Kein fehlerfreier Gesamtlauf behauptet; keine rohen Standardprofil-Logs ins Repository kopiert.

Die zehn unterschiedlichen nicht erkannten Fensternamen wurden den gleichnamigen Abschnitten in userdata/keymaps/keyboard.xml zugeordnet; im Skin-XML keine Treffer. Diese externe Keymap bleibt unverändert. Weitere Fehlerursachen werden durch diese Zuordnung nicht geklärt. Bereinigung/aggregierte Belege: lyrics_standard_cleanup.json.
