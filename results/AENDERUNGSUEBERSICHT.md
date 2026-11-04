# Bisherige Änderungen und gefundene Fehler

CU LRC mit aktivem Hintergrunddienst: Der Skin schloss das automatisch geöffnete Lyrics-Fenster am versteckten Start-Control zu früh. Diesen Schließaufruf entfernt und den Lyrics-Schalter beim Laden des CU-Fensters aktiviert. Die drei Skin-Einstiege verwenden einen laufenden CU-Dienst nun wieder: geschlossenes Fenster über dessen vorhandenes `culrc.force`-Signal anzeigen, sichtbares Fenster ohne weiteren Script-Start belassen. Andere konfigurierte Anbieter behalten ihren bisherigen RunScript-Aufruf. Automatische Anzeige, Wiederanzeige über MusicOSD/PlayerControls/Schalter, Stop und Neustart sowie manueller Modus mit lokalen LRC geprüft; keine Fehlerzeilen. Kein Kodi-/Add-on-Code korrigiert. [Quellen und Grenzen](kodi22_inventory/lyrics_background_review.json), [Hintergrunddienst](kodi22_runtime/lyrics_background_paths_checks.json), [manueller Modus](kodi22_runtime/lyrics_visualisation_checks.json).

Weitere KN-Switchtimer-Reste: Nicht mehr belieferte `t0:date/channel/title`-Abfragen aus Ausschaltmenü und SkinSettings entfernt. Dadurch entfallen die alte nächste-Umschalttimer-Zeile und ihr abhängiger Versatz. Native Kodi-PVR-Anzeigen und der KN-Gesamtzähler bleiben erhalten. Beide echten Fenster mit gesetzten alten Testwerten sichtbar geöffnet, Aufnahmen geprüft, keine Fehlerzeilen. Keine Schalt-/Timeraktion. [Beleg](kodi22_runtime/switchtimer_remaining_checks.json).

Aktuelle Ergänzung (4. November 2026): Die zehn KN-Switchtimer-Einzelmarkierungen lesen Fenster-Eigenschaften, die der veröffentlichte Matrix-Anbieter nicht liefert. Variable, PVR-Fallback und separates Eintragsbild entfernt; Gesamtzähler und native Kodi-Timerzweige erhalten. Sichtbarer Vorher-/Nachher-Ausdruckstest reproduziert außerdem ein falsches Symbol bei leeren Vergleichswerten; nachher bleibt das Eintragssymbol leer. Globaler Zähler 0/1/0 korrekt, keine Fehlerzeilen. Keine echte Timeranlage oder PVR-Umschaltung getestet. [Quellen](kodi22_inventory/switchtimer_property_contract_review.json), [Laufzeit](kodi22_runtime/switchtimer_marker_checks.json).

Stand: 4. November 2026. Gilt ausschließlich für `skin.horizonzv-piers` / Add-on-ID `skin.horizonzv`, Branch `refactor/kodi22-kompatibilitaet`.

Diese Übersicht gruppiert die bisherigen Änderungen nach Fehlerursache. „Laufzeit geprüft“ bezeichnet die im Prüfbericht genannten Teilfälle, keine vollständige Freigabe aller Geräte, Anbieter und Medien. Andere Add-ons und der Kodi-Core wurden nicht korrigiert.

## Entfernte, veraltete und ungültige Kodi-Schnittstellen

| Fund / Fehler | Umsetzung im Skin | Prüfstand / Grenze |
| --- | --- | --- |
| Entferntes `Player.DisplayAfterSeek` | Durch `Player.HasPerformedSeek(3)` ersetzt. Den zunächst verwendeten Dezimalwert nach Quellprüfung auf ganzzahlige Sekunden korrigiert. | Video-Seek und Intervallverhalten gezielt geprüft; weitere Kontexte offen. |
| Entferntes unqualifiziertes `IsEmpty(...)` | Durch `String.IsEmpty(...)` ersetzt. | Quellabgleich; echte GTO-Daten bleiben separat zu prüfen. |
| Nicht registriertes `Control.IsEmpty(...)` | Bewertungsbedingung auf `String.IsEmpty(ListItem.Rating)` umgestellt. | Statisch geprüft. |
| Ungültiges `Skin.HasAddon()` ohne Argument | Fehlerhafte redundante Debug-Bedingung entfernt. | Statisch geprüft. |
| Veraltetes `ListItem.Thumb` | Auf `ListItem.Art(thumb)` umgestellt. | Quellengeprüft; nicht alle Anbieteransichten zur Laufzeit geprüft. |
| Veraltetes `ListItem.AddonBroken` | Aktuelle Lifecycle-Typen und Beschreibungen, getrennte Warn-/Fehlerdarstellung. | Quellengeprüft; Lifecycle-Sonderfälle offen. |
| Alte Add-on-Status- und Herkunftsangaben sowie ungültige Seitenbedingungen | Status-/Herkunftsanzeige auf aktuelle Angaben umgestellt; Seitenbedingungen am tatsächlichen Text-Control ausgerichtet. | System/Manual/Repository und einseitige Texte nativ geprüft; positive Mehrseitenfälle und Lifecycle-Sonderfälle offen. |
| Veraltetes `Window.IsTopMost` | Durch `Window.IsDialogTopmost` ersetzt. | Musik-Hauptmenüziel → Widget-Einstellungen → Zurück → Home nativ geprüft. |
| Veraltetes `System.IsInhibit` | Durch `System.IdleShutdownInhibited` ersetzt. | Nativer Menü-Zustandswechsel false → true → false und passende Sichtbarkeit geprüft; Testwerte wiederhergestellt. |
| Veraltetes `PlayDVD()` | Durch `PlayDisc()` ersetzt. | Quellengeprüft; echte Disc-Wiedergabe offen. |
| Für künftige Entfernung markierte Fotofelder `PictureColour` / `PictureProcess` | Die zwei optionalen Metadatenzeilen entfernt; kein belegter Ersatz. | Bewusster Funktionsverlust dieser Angaben. |
| Kodi 23 entfernt `gamewindow/pixels` | Betroffene Speicherstand-Vorschaucontrols entfernt; Screenshot-Art und Platzhalter bleiben. Eigenständige Live-Spielvorschauen erhalten. | Quellengeprüft; alte/neue Speicherstände und Kodi-23-Laufzeit offen. |
| Nicht registriertes `Player.Mute` | Auf `Player.Muted` umgestellt. | Nativer Mute-Zustandswechsel und Enddarstellungen geprüft. |
| In Piers fehlendes `Player.StarRating` | Auf `MusicPlayer.UserRating` und vorhandene Zehn-Punkte-Grafiken umgestellt. | Bewertungen 0/1/7/10 jeweils Standard/Vinyl geprüft. |
| Nicht registriertes `RDS.IsClassical` | Vorhandene RDS-Layouts anhand verfügbarer Komponisten-/Dirigentendaten auswählen. | Quellengeprüft; kein Genre-Nachweis, echte RDS-Daten offen. |
| Ungültige Aktion `Activate(1155)` an einer Pause-Einstellung | Entfernt. Nicht in einen funktionierenden Aufruf des sachfremden Ersteinrichtungsdialogs umgewandelt. | Fokus-/Schalterprüfung und lokale Video-Pauseansichten bestanden. |
| Unregistriertes Fensterziel `shutdown` | Seitenleisten-Kurzbefehl auf `shutdownmenu` korrigiert. | Echter Menüaufruf und Back zu Videos geprüft; keine Energieaktion ausgeführt. |
| Unregistrierte Widget-Ziele `pvr`, `favourites`, `addons` | Timerziele nach TV/Radio und Regeln getrennt, Favoriten auf `favouritesbrowser`; Dashboard-Video-Fallback und GTO-Ziel korrigiert. | Namen/Zweige statisch sowie 21 kontrollierte Eingaben nativ geprüft; echte Widget-/Anbieteraktionen offen. |

## Weitere konkrete Skin-Fehler und Überarbeitungen

| Fund / Fehler | Umsetzung im Skin | Prüfstand / Grenze |
| --- | --- | --- |
| Extra-Fanart hängt Verzeichnisnamen an Plugin-Pfade | Leere Ergebniswerte für direkte Plugin-Pfade und leere Listenpfade; lokale/SMB-Ausdrücke erhalten. | Kontrollierte Eingaben/lokale Bilder und Standardprofil-Disney+-Film-/Serien-/Staffelnavigation geprüft; im beobachteten Lauf keine Extra-Fanart-/RouterError-Zeile. Sieben generische native Pfadfälle einschließlich kodierter Wrapper zusätzlich geprüft; Player, SMB und weitere Wrappervarianten offen. |
| Nicht unterstützter Button im fokussierten Home-Listenlayout | Wetter-Ausblendfunktion durch unterstützten Skin-Timer ersetzt; alte Alarm-Logik entfernt. | Standard-/eigene Wartezeit, Abbruch und fehlender Anbieter geprüft. |
| Artist Slideshow ohne zuverlässigen zentralen Start bei späterem Bedarf | Bedarfsabhängigen Skin-Timer für den Start eingeführt. | Unveränderte Anbieter-Version startet/beendet im Test; Datenabrufvarianten offen. |
| WOL an versionsabhängige Anbieterbefehle `wolN` gekoppelt | Native `WakeOnLan(mac)`-Aktionen, gemeinsamer Include für zehn Plätze, alte Statuswerte vor Abruf leeren und Rückmeldungen präzisieren. | Abgefangene Aktionen/Zehnerliste sowie echte Statuslieferung von Anbieter 4.1.2 mit lokalen Zielen, weniger Zielen und deaktiviertem Anbieter geprüft; echte WOL-Pakete, ältere Anbieter, Dienst-/Fehlerfälle offen. |
| Darsteller-Knopf verwendete native Extras-Control-ID 15 | Darsteller auf ID 5 korrigiert, Extras separat mit ID 15 erreichbar. | Cast/Plot, Schauspielerliste und Extras-Aufruf nativ geprüft. |
| Erstes Extra aus frisch leerem Manager führt im geprüften Kodi RC1 zum Absturz | Skin blendet diesen Aufruf aus, erklärt die Einschränkung und bietet Schließen; Timer korrigiert versteckten Fokus. | Absturz auch mit unverändertem Estuary reproduziert. Schutz/Schließen geprüft. Kein Kodi-Core-Fix; Schutz erst nach belegter Core-Korrektur zurücknehmen. |
| Videoversions-Manager mit ungültigem Fokusziel und wirkungslosem Rückweg | Explizite Verbindungen zwischen Liste und Knöpfen hergestellt. | Fokus, Hinzufügen, Standard-/Typwechsel, Wiedergabe und Entfernen nativ geprüft. Ungroup u. a. offen. |
| Große Versionsvorschau nutzte den falschen Artwork-Kontext | Ausgewählte Liste 50 bevorzugen, Fallback behalten. | Auswahlwechsel und Vorschau nativ geprüft. |
| Leerer Farbdialog und dauerhafte Farbänderung beim bloßen Fokus einer Pause-Einstellung | `Skin.SetBool(color_orange)` / `Skin.SelectBool(color_red)` an Fokusereignissen entfernt. Reguläre Farbauswahl erhalten. | Beide Pause-Schalter, Fokuswechsel und drei Pause-Darstellungen geprüft; Ausgangswerte wiederhergestellt. |
| `music`-Teilstring fing auch `musicvideo` ab; allgemeiner Filmvergleich verwendete `movies` | Exakter Musikvergleich und korrekter Filmtyp `movie`. | Native Variablenauswertung für Film und Musikvideo einschließlich Eintragswechsel geprüft. |
| PVR-Dialoge mit unpassenden Control-Bindungen bzw. TV/Radio-Anzeige | Betroffene Dialoge an Piers-Verträge angepasst; Toggle an `IsRadio` gebunden. | TV→Radio→TV mit 86/103 Sendern, befüllte Suchdialoge, TV-Phrasensuche, Filter-Verwerfen und Programminformation geprüft; dauerhafte Filter, Senderbearbeitung und Backend-Aktionen offen. |
| Zweimal `Conditional` als Operand einer Dashboard-Animationsbedingung | Fremde Operanden entfernt; vier Row-off-Bedingungen und Animationseigenschaften erhalten. | Quelle und lexikalische Nachprüfung; visueller Kombinationstest offen. |
| Verschachtelte `<visible>`-Bedingung in PVR-Include | Bedingung als direkten Text eingebunden. | Strukturprüfung bestanden. |
| Pauseknopf durch erstes `<enable>false</enable>` dauerhaft deaktiviert | Konstante Sperre entfernt, `Player.PauseEnabled` behalten. | Quellengeprüft; Live-TV-Pause offen. |
| Kapitellabel zeigte bei kapitellosem Video `00/00` | Nur bei positiver Kapitelanzahl anzeigen. | Ohne Kapitel und mit drei Kapiteln geprüft. |
| Variable `Panel3Cover` nutzte außerhalb eines Includes `$PARAM[viewid]` | Auf tatsächliche View-ID 302 korrigiert. | Fehler im Testlog nach Neustart nicht erneut aufgetreten; echte Season-Art offen. |
| Wetterbildpfad bei leerem Wettercode ungültig; Wetterwarnungsansicht nicht eingebunden | Leeren Fall abfangen, gemeinsame Bildvariable nutzen; Warnungsansicht wieder eingebunden. | Leerer Code und vorhandene Gismeteo-Aktuell-/Prognosedaten im Standardprofil geprüft; Warnungen und vollständige Detailnavigation offen. |
| Diashow-`<info>Diashow</info>` überschrieb den dynamischen Ordner | Ungültigen Override entfernt. | Ordnerwechsel mit Kontrollversuch im sichtbaren Kodi geprüft. |
| Fehlende Includes/Variablen, beschädigter Include-Verweis | Fehlenden lokalen Stil ergänzt, ungültige/no-op Verweise bereinigt, Untertitellabel und Dim-Variable ergänzt/korrigiert. | Statische Referenzprüfung ohne fehlende Includes/Variablen. |
| Schreibfehler bei Control-Typen `im age` / `ima ge` | Reales Bild-Control korrigiert; zwei Testartefakte entfernt. | Control-Registrierung statisch abgeglichen. |
| Fehlende Texturen und PCM-Codec-Grafiken | Vorhandene passende Assets/Fallbacks verwenden; Musikquellen-Icon ergänzt. | Ressourceninventur ohne fehlende statische Texturen; PCM mit zwei Audioformaten in Standard/Vinyl geprüft. |
| Fehlende Sprachkennungen und Font-Namen | Sechs Kennungen in 14 Sprachkatalogen ergänzt; fehlende Font-Definitionen ergänzt bzw. vorhandene Namen verwendet. | Statische Prüfung; nicht alle Sprachen/Layoutvarianten visuell geprüft. |
| Home-Hintergrundordner unvollständig, ungültige `label3`–`label9`, Custom9 zeigte Custom7-Art | Ordner einschließlich `onlyone` vervollständigt, unterstütztes `label2` verwendet, richtige Custom9-Grafik. | Grundfälle geprüft; ursprüngliche Ursache des bloßen `home_tvshows.jpg`-Logpfads bleibt ungeklärt. |
| Wiederverwendeter Textviewer konnte alten Zusatztext anzeigen | Zwei interne Aufrufer löschen die Zusatz-Property vor dem Öffnen. | Statisch geprüft; externe Aufrufer nicht verändert. |
| Systeminformation konnte zwei verschiedene Skin-IDs zusammenziehen | Nur Manifest-ID dieses Skins verwenden. | Statisch geprüft. |
| Doppelte Einzelwert-Tags, teilweise mit widersprüchlichen Werten | 14 identische Duplikate und fünf ignorierte spätere Werte entfernt; effektiv gelesene Werte erhalten. | Loader-Verhalten und Quellvergleich geprüft; kein Layoutumbau behauptet. |

## Entfernte Altlasten und bewusst entfallene Funktionen

| Fund / Fehler | Änderung / Auswirkung |
| --- | --- |
| Verwaiste Serienplaner-/Timeroberfläche mit ungültigen Include-Verweisen | Nicht mehr erreichbaren Skin-Code entfernt. |
| Veralteter Video-Versionen-Dialog | Auf den aktuellen nativen Dialog ausgerichtet; alten Skin-Dialog entfernt. |
| Archivierte Library-Data-Provider-Integration | Optionales Next-Episode-Widget, Einstellung und Installationsverweise entfernt. Kein gleichwertiger nativer Ersatz belegt; diese Funktion entfällt. |
| OpenELEC-Verknüpfung auf belegten Python-2-Stand | OpenELEC-spezifischen Skin-Eintrag entfernt. LibreELEC/CoreELEC bleiben getrennt erhalten. |
| Tempo-Schaltfläche und EventLog-Aufruf auf nicht vorhandene Skin-Fenster | Defekte Schaltfläche bzw. Fensteraktion entfernt; EventLog selbst bleibt. |
| Ungenutztes `LibraryEditorLabel` mit acht fehlenden Kennungen | Variable entfernt; separate Library-Node-Editor-Integration bleibt. |
| Zwei getrackte `.xml.org`-Sicherungen | Aus aktivem Arbeitsbestand entfernt; Wiederherstellungsinformationen dokumentiert. |
| Nicht belegte Support-/Empfehlungsangaben für Artwork Beef und CDArt Manager | Angaben bereinigt; generische Artwork-/CDArt-Anzeige bleibt erhalten. |

## Liedtext-Aufrufe: leeres Ziel nach Abbruch

- In MusicOSD und PlayerControls führten bisherige Auswahlketten nach Abbrechen noch `RunScript()` mit leerem Ziel aus. Im sichtbaren nativen Vergleich reproduziert: zwei Keymapping-Fehler vor der Korrektur, keine entsprechenden Diagnosezeilen für die korrigierten Ketten.
- Ohne Auswahl öffnet der Knopf jetzt nur den Add-on-Dialog. Nach bestätigter Auswahl startet ein weiterer Klick den Anbieter; dieser geänderte Ablauf ist beabsichtigt. MusicOSD-Start-/Stop-Schalter ohne Auswahl deaktiviert.
- `RunScript` für Lyrics ist weiterhin unterstützt. Kein fremdes Add-on geändert. Tatsächlicher Anbieterstart/-stop bei Musikwiedergabe bleibt offen; geprüft wurden kopierte Originalaktionen in einer nativen Skin-Testansicht. Beleg: `kodi22_inventory/lyrics_action_review.json`.

## Add-on-Details: nicht erzeugte Metadaten

- Fünf Zeilen für `Addon.Dependencies`, `Addon.License`, `Addon.Homepage`, `Addon.Provider` und `Addon.StarRating` entfernt. Die geprüfte native Kodi-Erzeugerkette liefert diese Properties nicht; der generische Property-Leser holt sie nicht aus dem Manifest nach.
- Belegte ID-/Status-Angaben und unterstützte dedizierte Labels bleiben erhalten. Kein historischer API-Entfernungsstand behauptet. Speziell von Dritten gesetzte Properties würden diese Extra-Zeilen nicht mehr anzeigen.
- Übrige Struktur unverändert, vier statische Prüfer und Inventur ohne fehlende Referenzen. Beleg: `kodi22_inventory/addon_metadata_property_review.json`.

## ExtendedInfo: Kommas und Anführungszeichen in Argumenten

- Sieben Skin-Aufrufe abgesichert: Zusammengesetzte YouTube-Suchtexte werden komplett per `$ESCVAR` geschützt, einzelne Titel/Seriennamen per `$ESCINFO`.
- Sichtbarer nativer Kodi-Vergleich: drei bisherige Suchtext-Varianten zerfallen bei Kommas; 16 korrigierte Argumentprüfungen bestehen mit Kommas, Quotes/Backslashes, Unicode und leeren Werten.
- Andere Add-ons unverändert. Die Probe prüft den Kodi-Argumenttransport; der echte Film-YouTube-Aufruf erreicht inzwischen ExtendedInfo 6.0.9 mit korrekter Suche; die Online-Abfrage scheitert an fehlender API-Identität. Weitere Add-on-Aktionen bleiben offen. Der Dialogkontext nach Close ist inzwischen für Film, Album und Titel nativ bestätigt (`dialog_context_checks.json`). Testprofil und Skin-Testkopie wiederhergestellt. Belege: `kodi22_inventory/argument_escaping_review.json`, `kodi22_runtime/argument_escape_native_checks.json`.

## Prüfwerkzeuge und Dokumentation

- Zukunftsabgleich erweitert: tatsächliche master-Registrierung mit Piers verglichen (30 InfoMap-Tabellen, acht Translate-Funktionskörper). Keine entfernten Namen; sechs Ergänzungen. Geänderte RetroPlayer-Parameter werden im Skin nicht verwendet, fanart-Konstante behält ihren Wert. Kein zusätzlicher Skin-Umbau nötig. Belege: `kodi22_inventory/master_info_compatibility_review.json`, `kodi_master_info_tables.json`.

- Fensterprüfung um Argumente in Bedingungen und expliziten Property-Fensterqualifikatoren erweitert: 1.020 Kontexte ohne Fund. Elf ungültige Prüffälle erkannt; XML-Dateinamensabfragen und dynamische Ziele gesondert behandelt. CLI meldet Funde mit Exitcode 1. Keine Änderung an fremder Keymap oder Add-ons. Belege: `kodi22_inventory/window_info_targets_review.json`, `window_info_validation_checks.json`.

- Kodi-Entfernungshistorie gezielt nachgeprüft: 39 dokumentierte Einträge, 35 zusätzliche Regeln im bestehenden Prüfer. 37 benannte Entfernungsfälle erkannt, neun unterstützte ähnliche Namen ohne Fehlalarm; on/off durch vorhandene Bedingungsatomprüfung abgedeckt. Acht explizit veraltete Namen in Piers/master unverändert und ohne aktiven Skin-Treffer. Beleg: `kodi22_inventory/info_deprecation_history_review.json`.

- Sichtbar geprüft: Dashboard mit ausgeschalteten Zusatzzeilen, allen vier Favoriten-Zeilen und nur Zeilen 2/4. Serverzähler kontrolliert mit 0/1/10 geprüft; kein echter Ping-Anbieter beteiligt. Testkopie/Profil vollständig zurückgesetzt, 164 XML stimmen überein, reguläres Kodi-Ende ohne ERROR-Zeilen. Belege: `kodi22_runtime/home_dashboard_cleanup.json` und zugehörige Bilder/Zustände.

- Control-Eigenschaften gegen ausgewählte Piers-Lader geprüft: 119 unterschiedliche direkte XML-Kindtags. Home-Serverzähler: Tippfehler `textwidht` zu unterstütztem `textwidth` korrigiert (Wert 40); dessen Breitenbegrenzung wird dadurch erstmals wirksam, kontrollierte Darstellung für 0/1/10 inzwischen geprüft, reale Statuslieferung bleibt offen. Ignoriertes RSS-`highlightcolor` sowie drei ignorierte `wraparound`-Angaben an Fixedlists entfernt. Unterstützte RSS-Farben und native Fixedlist-Navigation bleiben bestehen. Keine historische API-Entfernung behauptet. Drei gezielte Regeln im bestehenden Prüfer ergänzt. Beleg: `kodi22_inventory/control_property_review.json`.

- Elf unbenutzte Schriftdefinitionen entfernt: `ubuntu-r12u`, `impacted14`, `aaaiight20`, `lcd16`, `lcd18`, `clock-28b`, `clock-32b`, `Large`, `Medium`, `ubuntu-r26`, `clock-32`. Aktive Font-Tags ohne Beachtung der Groß-/Kleinschreibung, alle vier dynamischen Font-Parameter und installierte Nicht-Skin-Verbraucher geprüft. Sieben externe Teiltreffer für die zusätzlichen Namen als Datumsformat, Cover-Typ, Beschreibungsschlüssel oder Programmtitel eingeordnet, keine Font-Aufrufe. Alle nichtleeren aufgelösten Font-Namen bleiben definiert; Schriftdateien unverändert. 56 Definitionen verbleiben. Die allgemeine Teilzeichenfolgen-Heuristik hatte zunächst vier Kandidaten verdeckt. Beleg: `kodi22_inventory/dead_font_review.json`.

- Sechs unbenutzte Include-Definitionen entfernt: `FakeFocusButton555`, `PathID`, `ControlID`, `InfoListLeft`, `InfoListRight`, `SidePanelShortcutsBackground`. Dazu den vollständig auskommentierten alten Musiklayout-Block entfernt, der noch zwei dieser Namen enthielt. Direkte Aufrufe, die einzige dynamische Include-Auswahl und installierte externe Verbraucher geprüft. Die übrige aktive XML-Struktur ist unverändert. Das ist eine Bereinigung von Altlasten, keine Entfernung einer Kodi-API. Neue Inventur: 374 Includes, keine unbenutzten oder fehlenden Includes. Beleg: `kodi22_inventory/dead_include_cleanup.json`.

- Bestandsaufnahme, Quellenprüfung, Laufzeitprotokolle und offene Abnahmepunkte unter `results/` gepflegt.
- Lesende Prüfer für bekannte Kompatibilitätsfehler, Aktionen und Fensterziele ergänzt. Diese sind keine vollständigen Kodi-Validatoren.
- Namens-/Bedingungsprüfer ergänzt: 453 registrierte Methodennamen abgeglichen; 53 weitere Treffer als freie IDs/Property-Schlüssel eingeordnet. 8.863 statische Bedingungsatome und ausgewählte Parameterzahlen in 8.487 Fällen nachgeprüft; dynamische Fälle und Argumentsemantik ausgenommen.
- Aktueller begrenzter Abgleich: 165 XML-Dateien, 1.616 wörtliche Aktionsreferenzen, 64 verschachtelte Aktionsziele; 252 wörtliche Fensteraufrufe, elf Content-Ziele und 140 Zweige aus 19 Zielvariablen. Keine Funde in den jeweils implementierten Regeln nach Korrektur.
- Die kontrollierte Dashboard-Prüfansicht wurde ausgeführt: 21 Fälle, 63 erwartete Ausgaben. Echte Widget-/Provider-Aktionen sind damit nicht belegt; vier weiterhin leere Ergebnisse des allgemeinen Widgets ausdrücklich dokumentiert. Test-Helfer entfernt.

## Bewusst erhalten / weiterhin offen

- **Reboot from internal** bleibt auf ausdrücklichen Wunsch erhalten. Quellvertrag geprüft; Nutzer bestätigt die besprochenen CoreELEC-Funktionen als funktionsfähig. Weitere Geräteabfragen entfallen.
- Andere Add-ons werden nur zur Prüfung des Skin-Vertrags gelesen oder unverändert im getrennten Profil verwendet.
- Weitere Disney-Player-/DRM-/Wrapper-, SMB-, dauerhafte PVR-Suchdefinitionen/Filterkombinationen/Backend-, Wetterwarnungs- und WOL-Fälle bleiben offen. Standardprofil-Disney-Listen, Wetterdaten, PVR-Moduswechsel und grundlegende Suche/Programminfo sind teilweise geprüft; keine allgemeine Integrationsfreigabe.
- Entwickler-Keymap mit absoluten Pfaden und statisch ungenutzte Ressourcen nicht ohne geklärten Verwendungszweck gelöscht.
- Eine vollständige Kodi-23-Freigabe und nicht veröffentlichte künftige Änderungen sind damit nicht bewiesen.

Quellen und Detailbelege: [Kompatibilitätsaudit](kodi22_compatibility_audit.md), [Laufzeitbericht](kodi22_runtime/PRUEFBERICHT.md), [Überarbeitungsplan](ueberarbeitungsplan.md), [WOL-Überarbeitung](wol_ueberarbeitung.md).


### ExtendedInfo-Vertrag: wirkungsloser Parameter entfernt

Die fünf verwendeten Aktionen (`youtubebrowser`, `extendedinfo`, `extendedtvinfo`, `seasoninfo`, `extendedepisodeinfo`) sind im geprüften Maintainer-Quellcode vorhanden. `silent=True` wird in der Staffel-/Episoden-Aufrufkette nicht gelesen oder weitergereicht und wurde aus beiden Skin-Aufrufen entfernt. Keine Kodi-API-Entfernung und keine Änderung des Add-ons. Die addoninterne Entfernung von Anführungszeichen bleibt ausdrücklich dokumentiert; der native Argumenttest belegt nur den Kodi-Transport. Quellen und Grenzen: `kodi22_inventory/extendedinfo_interface_review.json`.


### Eingabeaktionen im veroeffentlichten Entwicklungsstand (2026-11-04)

Piers und aktueller master enthalten dieselben 219 Eingabeaktions-Zuordnungen; die geprueften ActionTranslator.cpp-Dateien sind bytegleich. Keine entfernten Namen oder geaenderten symbolischen Ziele. 35 im begrenzten Aktionsscan verwendete Eingabeaktionsnamen bleiben vorhanden. Der bisherige Piers-Pruefdatensatz hatte die zehn REMOTE-Ziffern-Aliase number0 bis number9 ausgelassen; Datensatz vervollstaendigt. Keine Skin-Aenderung daraus erforderlich. Handlerverhalten, variable Aktionswerte und externe Benutzer-Keymaps sind dadurch nicht vollstaendig geprueft. Belege: `kodi22_inventory/master_input_action_review.json`, `kodi_master_input_actions.json`.


## Lyrics: sofortiges Schließen und verstecktes Fokusziel korrigiert (2026-11-04)

Der echte Visualisierungs-Test findet einen zusätzlichen Skin-Fehler: Die direkten Startknöpfe MusicOSD 701 und PlayerControls 609 starten den Anbieter, lassen den Skin-Schalter Lyrics aber aus. Der versteckte Standardknopf 99 im skineigenen script-cu-lrclyrics-main.xml führt dann sofort Action(back) aus. Der unveränderte Anbieter findet die lokale LRC-Datei, sein Fenster schließt dennoch. Beide konfigurierten Startwege setzen jetzt Lyrics vor RunScript. Die leere Auswahl bleibt ein eigener Schritt; deren Abbruch startet weiterhin keinen Anbieter und setzt den Schalter nicht.

Zweiter belegter Fehler: Bei eingeschaltetem Lyrics-Schalter fokussierte Knopf 99 immer Control 101. Dieses Seiten-Control ist bei sichtbarer Lyrics-Liste ausgeblendet; Kodi protokollierte den ungültigen Fokus zweimal, einmal pro Einstieg. Diese Umleitung entfernt. CU LRC setzt selbst den Fokus auf die fertig gefüllte Liste 110. Die Bedingungen der Radio-Toggle-Kette 2401 bleiben unverändert: Kodi wählt die passenden Aktionen vor dem Toggle aus, sie dürfen nicht aufgrund einer angenommenen nachträglichen Neuauswertung vertauscht werden.

Finaler sichtbarer Test mit unverändertem CU LRC 6.7.6, stiller selbst erzeugter WAV und drei eigenen LRC-Zeilen bestanden: zunächst Lyrics aus, MusicOSD-Start aktiviert den Schalter und zeigt den Text. Nativer Stop 2402 schließt das Lyrics-Fenster und leert running/guirunning/Text/Quelle. Danach erneut Lyrics aus, PlayerControls 609 vom Hauptmenü gestartet; beim Rückwechsel in die Visualisierung erscheinen die lokalen Texte erneut. Fokus liegt auf 110. Kein aktiver Hintergrunddienst und keine Online-Scraper getestet. Der frühere Standardprofil-Fall mit bereits laufendem Dienst bleibt davon getrennt.

Finales Laufzeitlog ohne ERROR-Zeilen oder ungültige Control-101-Fokusmeldungen. Alle vier statischen Prüfer ohne Fund; neue Inventur ohne fehlende Includes, Variablen, Strings oder statische Texturen. 1.615 wörtliche Aktionsreferenzen im begrenzten Aktionsscan. Kodi beendet, Profil- und Anbieter-Testeinstellungen wiederhergestellt, alle 164 Skin-Testdateien abgeglichen. 223 Anbieter-/Abhängigkeitsdateien mit Originalen und Vorher-Hashes verglichen; keine Add-on-Korrektur. Frühere Fehlversuche des Testhelfers betrafen zusätzlich den Visualisierungs-Toggle, die lokale Dateisuchkonfiguration, den Container-Lesezugriff und den OSD-/PlayerControls-Aufrufkontext; diese sind keine weiteren Skin-Fehlernachweise.

Belege: `kodi22_inventory/lyrics_visibility_gate_review.json`, `kodi22_runtime/lyrics_visualisation_before_enable_fix.json`, `lyrics_visualisation_before_focus_fix.json`, final `lyrics_visualisation_checks.json` und `lyrics_visualisation.png`. Testhelfer: `run_lyrics_visualisation_probe.py`.


## Auto Completion: Skin-Anfrage URL-kodiert (2026-11-04)

Die bisher rohe Tastatureingabe in der Skin-URL wird jetzt im Skin mit urllib.parse.quote kodiert. Ein kleiner eigener Helfer unter resources/scripts/autocomplete_query.py läuft nur während der sichtbaren Tastatur. Er liest bei versteckter Eingabe oder deaktiviertem Anbieter keinen Text und veröffentlicht nur den kodierten Wert im Tastaturfenster. Öffnen/Schließen leert die temporären Werte und invalidiert ältere Aufrufe. Keine Texte als RunScript-Argumente und keine eigenen Log-/Dateiausgaben. Manifest ergänzt um die optionale Python-3-API-Abhängigkeit; Auto Completion bleibt optional.

Sichtbarer Test mit unverändertem AutoCompletion 2.1.2 und lokalem Wörterbuch bestanden: sechs Texte mit &, +, Prozentfolgen, Kommas, Quotes/Backslash und Unicode erhalten nach der Query-Dekodierung exakt ihren ursprünglichen Wert. Ein echter lokaler Vorschlag (help) wird weiterhin ins Eingabefeld übernommen. Bei versteckter Eingabe beziehungsweise deaktiviertem Anbieter starten Helfer und Anfrage nicht. Normaler Dialogschluss leert Query/Owner; Helfer endet regulär. Finale Prüfung ohne ERROR-Zeilen. Kodi beendet, Anbieter-Aktivierung und Testeinstellungen vollständig zurückgesetzt; 164 XML, Skin-Manifest und Helfer abgeglichen, Anbieterquellen unverändert.

Ein lediglich zur Beobachtung ergänztes, außerhalb des Bilds liegendes Label 1197 in der Testkopie liest die produktive Variable; es wurde danach entfernt. Der erste Versuch, $VAR direkt über JSON-RPC abzufragen, war kein gültiger Variablen-Test und ist separat als Draft erhalten. Vier statische Prüfungen ohne Fund, Inventur ohne fehlende Includes/Variablen/Strings/statische Texturen.

Abgrenzung: Die vom Anbieter selbst erzeugten selectautocomplete-URLs setzen search_string weiterhin roh ein. Dieser zweite Fehler liegt im unveränderten Anbieter; keine pauschale Freigabe solcher Auswahl-URLs mit reservierten Zeichen. Der normale lokale Auswahlfall ist geprüft. Kein externer Vorschlagsdienst getestet und kein anderes Add-on korrigiert. Quellen und Belege: kodi22_inventory/autocomplete_query_review.json, kodi22_runtime/autocomplete_query_checks.json, autocomplete_query_native.png und run_autocomplete_query_probe.py.


## Smartplaylists: zwei wirkungslose Knotenverweise entfernt (2026-11-04)

In `Videos_recently.xsp` und `TVShows_recent_tvshows.xsp` war jeweils eine Regel `field="playlist"` mit einer `library://video/recentlyadded….xml`-Adresse enthalten. Kodi sucht hier jedoch eine Benutzer-Smartplaylist anhand ihres Namens oder Dateinamens. Der Skin liefert keine entsprechend benannte Playlist. Bei nicht aufgelöstem Verweis setzt Kodi in diesen UND-Verknüpfungen SQL `'1'` ein. Die Regeln begrenzten die Ergebnisse somit nicht auf den Bibliotheksknoten. Dies ist ein ungültiger Skin-Verweis, keine entfernte Kodi-Schnittstelle. Eine eigens passend benannte Benutzer-Playlist könnte den alten Literalwert ausnahmsweise auflösen.

Nur diese zwei Regeln entfernt; Typ, Gesehen-Filter, Sortierung und Limit bleiben erhalten. Insbesondere bleibt die Serienliste vom Typ `tvshows`. Alle elf ausgelieferten XSPs wurden im sichtbaren Kodi 22 abgefragt. Sechs Vorher-/Nachher-Vergleiche mit eigenen Film-/Seriendaten bestehen, auch nach nativem Wechsel des Gesehen-Status. Gruppierte Musiklisten liefern weiterhin Alben. Inprogress-Listen lieferten ohne Resume-Testdaten leere Ergebnisse; positive Resume-Filter, die Grenze von zehn Treffern und Zufallsverteilung sind damit nicht getestet.

Die vier geprüften Funktionen GetFields, GetOrders, GetGroups und GetWhereClause unterscheiden sich zwischen Piers und dem am Prüftag veröffentlichten master nur durch gleichwertige Content-Konstanten und Formatierung. Keine vollständige Freigabe einer künftigen Kodi-Version. Quellen und Inventar: [smartplaylist_review.json](kodi22_inventory/smartplaylist_review.json), insbesondere [Kodi-Playlistregeln](https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/playlists/SmartPlayList.cpp), [Namensauflösung und Gruppierung](https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/filesystem/SmartPlaylistDirectory.cpp) und [master-Konstanten](https://github.com/xbmc/xbmc/blob/master/xbmc/utils/ContentNames.h).

Die eigenen Testserien/-episoden wurden ausschließlich offline in gesicherte isolierte Testdatenbanken eingetragen; Gesehen-Wechsel liefen anschließend nativ über Kodi. Danach wurden Dateibestand und Bytes der ursprünglichen Mediendatenbanken sowie Profileinstellungen wiederhergestellt. Kein anderer Add-on-Code korrigiert. Finaler Lauf ohne ERROR-Zeilen. Belege: `kodi22_runtime/smartplaylist_checks.json` (sechs Vergleiche, elf Abfragen, Bereinigung bestanden), `smartplaylist_recent_movie.png`, Helfer `run_smartplaylist_probe.py`. Die Draft-Berichte dokumentieren korrigierte Testaufbaufehler, keine zusätzlichen Skin-Defekte. Der Helfer verwendet jetzt eine feste Git-Baseline, prüft zusätzlich den wiederhergestellten DB-Dateibestand und gibt eine kompakte Zusammenfassung aus; diese Nachbearbeitung erforderte keinen erneuten Kodi-Lauf.

Die vorhandene ZIP-Prüfung entstand vor diesen zwei XSP-Änderungen; ihre Dateigleichheit gilt für den damaligen Paketstand.


## Wetterbild-Auswahl: doppelter Add-on-Start entfernt (2026-11-04)

SkinSettings-Knopf 438 führte denselben `RunScript(script.image.resource.select,property=weatherfanart&type=resource.images.weatherfanart)`-Aufruf zweimal aus. Der native Vergleich der kopierten Aktionsketten bestätigt zwei Anbieterstarts pro bisherigem Klick und einen nach Entfernen des zweiten onclick. Keine Behauptung zweier nacheinander sichtbarer Dialoge und keine Kodi-API-Entfernung. Die dokumentierten Argumente bleiben unverändert.

Mit unverändertem Image Resource Select 3.0.2 sechs native Phasen bestanden: Abbruch mit alter und neuer Kette, Auswahl von Weather Fanart Multi und Weather Icons Outline sowie jeweils Zurücksetzen über „Keine“. Pfad, Dateiendung und Multi-Schalter entsprechen dem Anbieter-Vertrag. 559 Original-/Testdateien unverändert, Profil zurückgesetzt, Kodi beendet; keine ERROR-Zeilen. Getrennte sichtbare WindowXML-Probe, keine vollständige Wetter-/SkinSettings-Darstellungsabnahme. Zwei Drafts dokumentieren Testhelfer-Korrekturen. Der Helfer prüft die nachträglich aus dem finalen Log bestätigten Startzahlen jetzt ebenfalls ausdrücklich.

Quellen/Vertrag: `kodi22_inventory/image_resource_contract_review.json`; Laufzeit: `kodi22_runtime/image_resource_checks.json`, Helfer `run_image_resource_probe.py`. Offizielle [Anleitung](https://gitlab.com/ronie/script.image.resource.select/-/raw/master/README.txt) und [Implementierung](https://gitlab.com/ronie/script.image.resource.select/-/raw/master/lib/select.py). Keine anderen Add-ons korrigiert.


## Aktualisierter Paketbeleg (2026-11-04)

Das neue Test-ZIP enthält 294 Dateien. CRC-Prüfung bestanden; alle enthaltenen Dateien stimmen bytegenau mit dem aktuellen Workspace überein. Manifest, 164 Skin-XML, elf XSP und eigener Auto-Completion-Helfer sind vorhanden; XML/XSP parsebar. Gegenüber dem früheren Test-ZIP unterscheiden sich nur README, die beiden Smartplaylists und SkinSettings. Kein frischer ZIP-Installationstest. Belege: `kodi22_inventory/package_followup_context.json` und `package_followup_review.json`. Das Archiv liegt ausschließlich in einem neuen TEMP-Verzeichnis; kein bestehendes Repository-Paket überschrieben.

Für den lokalen Checkpoint wird nur per Git-Aufruf ein leeres Hooks-Verzeichnis verwendet: Der vorhandene globale post-commit-Hook würde sonst ein gleichnamiges Repository-ZIP überschreiben. Derselbe globale Paketbauer wurde zuvor mit getrenntem TEMP-Ausgabeziel und Testausschlüssen ausgeführt und sein Ergebnis geprüft. Weder Hook noch globale Git-Konfiguration wurden geändert.


## Global-Search-Skinvertrag (2026-11-04)

Unbenutztes Legacy-Layout `script-globalsearch-main.xml` durch den aktuellen Dateinamen und Control-Vertrag ersetzt. Native Vorher-/Nachher-Prüfung bestätigt den Wechsel vom Add-on-Fallback zum Skin-Layout; Film-Treffer, beide Ansichten, Ansichtstaste, Kategorie-Navigation, Info, Abbruch und Leersuche geprüft. Ein bereits im Ausgangsfall vorhandener AVI-Verzeichnisfehler bleibt dokumentiert; weitere Medienkategorien sind offen. Kein Anbieter-Code geändert. Quellen und Grenzen: `kodi22_inventory/globalsearch_contract_review.json`, Details im [Laufzeitbericht](kodi22_runtime/PRUEFBERICHT.md). Neue begrenzte Vertragsregeln mit sechs Prüffällen; aktuelle Inventur ohne fehlende statische Referenzen. Der bisherige Paketbeleg liegt vor dieser Layout-Umstellung.


Paket-/Checkpoint-Ergänzung zum Global-Search-Umbau: Neues Test-ZIP mit 294 Dateien geprüft; sämtliche Einträge bytegleich zum Workspace, XML/XSP parsebar, neuer Layoutname vorhanden und Legacy-Datei nicht mehr enthalten (`kodi22_inventory/globalsearch_package_review.json`). Damit ist der zuvor genannte Paketvorbehalt für die Dateiumstellung erledigt; ein frischer ZIP-Installationstest bleibt aus. Lokaler Commit verwendet wie beim vorherigen Checkpoint ein nur pro Aufruf leeres Hooks-Verzeichnis, da der globale Paketbauer bereits in TEMP ausgeführt und geprüft wurde. Der globale Hook und veröffentlichte Pakete bleiben unverändert.


## Filmset-Quelle bei normalen Filmen gesperrt (2026-11-04)

Der AVI-Verzeichnisfehler beim Global-Search-Infoaufruf stammt von der zunächst nur ausgeblendeten Filmset-Liste im Skin. Beide Filmset-Includes erhalten jetzt nur für ListItem.IsCollection eine Verzeichnisquelle. Vorheriger Fehler reproduziert, Estuary-Gegenprobe fehlerfrei, finaler Global-Search- und Filmset-Lauf fehlerfrei. Echte Set-Cover-/Textliste und anschließender normaler Film geprüft; keine Add-on-Korrektur. Quellen und Grenzen: `kodi22_inventory/movie_set_content_review.json`, [Laufzeitbericht](kodi22_runtime/PRUEFBERICHT.md). Frühere unbekannte Fehlerzuordnung ist damit für diesen Fall überholt. Frühere Global-Search-Seitenverhältnisangabe im Vertragsbeleg auf die tatsächlich 720×480 großen Aufnahmen begrenzt; der neue Set-Lauf bestätigt 16:9 ausdrücklich.


Paket-/Checkpoint-Ergänzung zur Filmset-Quelle: Neues TEMP-Test-ZIP mit 294 bytegleichen Einträgen und gültigen XML/XSP geprüft. Gegenüber dem Global-Search-Paket unterscheiden sich ausschließlich Variables.xml und Includes_SetInformation.xml (`kodi22_inventory/movie_set_content_package_review.json`). Kein frischer ZIP-Installationstest. Der lokale Commit verwendet wie zuvor nur pro Aufruf ein leeres Hooks-Verzeichnis, da der globale Paketbauer bereits separat mit TEMP-Ziel ausgeführt und geprüft wurde; globale Hook-Konfiguration und veröffentlichte Pakete bleiben unverändert.


## Verzeichnisquellen: 3-Panel und PVR (2026-11-04)

Zwei weitere Quellen nur für echte Ordner und ohne Parent-Eintrag belegt. Unaufgelösten PVR-Sortierparameter entfernt, bisherige aufsteigende Datumssortierung erhalten. Acht native Vorher-/Nachherphasen mit zwei kopierten content-Verträgen bestanden, nachher ohne ERROR-Zeilen. Kein echter PVR-Backendtest oder vollständiger View-Test. 14 dynamische Definitionen inventarisiert; Quellen/Grenzen: `kodi22_inventory/folder_content_review.json`, `dynamic_directory_sources_review.json`, Details im [Laufzeitbericht](kodi22_runtime/PRUEFBERICHT.md). Keine Add-on-Korrektur.


Ergänzung zum Ordnerquellen-Stand: Das neue TEMP-Test-ZIP enthält 294 bytegleiche Dateien; gegenüber dem Filmset-Paket unterscheiden sich ausschließlich Variables.xml, Includes_PVR.xml und View_Movie_302_3Panel.xml (`kodi22_inventory/folder_content_package_review.json`). Kein frischer ZIP-Installationstest. Ein zusätzlicher Sortierfall mit gegensätzlicher alphabetischer/Datumsreihenfolge ist vorbereitet, noch nicht ausgeführt: Die Standard-Kodi-Instanz lief beim Versuch und bei der Nachprüfung, daher blieb sie unberührt. Der bestehende native Beleg verwendet early.avi/late.avi und bestätigt dieselbe Reihenfolge vor/nachher; allein dadurch wäre Datumssortierung nicht von Namenssortierung zu unterscheiden. Der aufsteigende Fallback ist unabhängig durch Piers/master-Quellen belegt. Für den ergänzenden sichtbaren Lauf wurde nach einem freien Zeitfenster gefragt. Der lokale Checkpoint nutzt wie zuvor nur pro Git-Aufruf ein leeres Hooks-Verzeichnis, da der globale Paketbauer bereits getrennt in TEMP ausgeführt wurde; globale Hooks und veröffentlichte Pakete unverändert.


## Fehlende viewid-Weitergabe korrigiert (2026-11-04)

Neun Include-Aufrufe in vier View-Dateien ergänzt; dadurch werden 21 nach Auflösung leere Control.HasFocus-Argumente zu gültigen View-IDs. Aufrufbedingungen und übrige XML-Struktur unverändert. Quellenbasierte Expansion und sieben sichtbare Video-/Musik-Fokusfälle mit Animation an bestanden; finales Log ohne ERROR-Zeilen. Quellen/Grenzen: `kodi22_inventory/include_viewid_forwarding_review.json`, [Laufzeitbericht](kodi22_runtime/PRUEFBERICHT.md). Keine vollständige Animationskurven-/Medienartenfreigabe. Der ergänzende Ordner-Sortierfall mit gegensätzlicher Namens-/Datumsfolge ist nun ebenfalls nativ bestanden (`folder_content_checks.json`); echter PVR-Backendtest bleibt offen.


Paket-/Checkpoint-Ergänzung zur viewid-Weitergabe: Neues TEMP-Test-ZIP mit 294 bytegleichen Einträgen und gültigen XML/XSP geprüft. Gegenüber dem Ordnerquellen-Paket unterscheiden sich nur die vier betroffenen View-Dateien (`kodi22_inventory/include_viewid_package_review.json`). Kein frischer ZIP-Installationstest. Lokaler Commit wie zuvor mit ausschließlich pro Aufruf leerem Hooks-Verzeichnis, da der globale Paketbauer bereits separat in TEMP ausgeführt und geprüft wurde. Globale Hooks und veröffentlichte Pakete bleiben unverändert.
