# Wake-on-LAN: konkreter Skin-Umbau

Stand: 1. November 2026. Gilt ausschließlich für `skin.horizonzv` in diesem Checkout. Im Skin implementiert; gezielte abgefangene Aktionstests durchgeführt. Echte Netzwerk-/Anbieterprüfung und vollständige visuelle Abnahme bleiben offen.

## Belegtes Problem

Der Skin zeigt fünf feste Geräteplätze und startet diese über `RunScript(script.skinhelper.ping,wolN)`. Die installierte Version 4.1.2 liefert zehn Plätze. Der bereits untersuchte ältere Stand 4.0.1 wertet bei `wol10` nur die letzte Ziffer aus. Eine Erweiterung auf zehn Skriptaufrufe wäre deshalb ohne zusätzlichen Vertrag unsicher. Die Anzeige „Alle starten“ verwendet zudem `servercount` (konfigurierte IP-Adressen), obwohl nur fünf Plätze geprüft werden und ein IP-Eintrag keine MAC-Adresse garantiert.

## Implementierter Ansatz

1. Das Ping-Add-on bleibt ausschließlich Lieferant der bestehenden Geräte-/Status-Properties und Ziel des Einstellungsdialogs. Keine Änderungen an seinem Code, Profil oder Versionsvergleich.
2. Wecken über `WakeOnLan($INFO[Window(Home).Property(SkinHelperPING.macN)])` statt `RunScript(...,wolN)`. Kodi Piers registriert den Built-in; sein Handler übergibt die MAC-Adresse an die Netzwerkimplementierung. Damit entfällt die unterschiedliche Auswertung der Platznummern im Skript.
3. Beim Öffnen des Skin-Dialogs die vom Dialog verwendeten `SkinHelperPING`-Properties für Plätze 1–10 und die Summen leeren und danach genau einmal den vorhandenen `status`-Aufruf anfordern, wenn das Add-on aktiviert ist. Das verhindert insbesondere, dass übrig gebliebene Plätze 6–10 nach einem Versionswechsel angezeigt werden, bevor der aktuelle Anbieter sie neu liefert. Ein ausgefallener Anbieter soll keine alten Ziele verfügbar lassen. Auswirkungen auf gleichzeitig sichtbare Home-Statusangaben prüfen.
4. Zehn mögliche, identisch aufgebaute Listeneinträge; nur neu gelieferte konfigurierte Einträge anzeigen. Bei leerer MAC keine Weckaktion und keine entsprechende Anforderungsnachricht. Einträge mit nur IP/Name können weiterhin ihren Status anzeigen. Liste auf den Platz oberhalb der Detailzeilen begrenzen und bei mehr Einträgen scrollen lassen.
5. „Alle“ verarbeitet dieselben zehn MAC-Felder wie die Einzelaktionen. `servercount` weder als Zahl der WOL-Ziele noch als Sichtbarkeitsnachweis verwenden. Keine Namen von Einträgen ohne Weckaktion in die Sammelbestätigung aufnehmen. Danach höchstens eine zusätzliche Statusaktualisierung anfordern, statt für jeden Weckauftrag den gesamten Status erneut abzurufen.
6. Meldung ausdrücklich als Anforderung formulieren. Kodis Built-in gibt dem Skin weder einen erfolgreichen Gerätestart noch den Rückgabewert der Netzwerkfunktion als auswertbare Bestätigung zurück. Unbekannte oder ungültige MAC-Werte sind deshalb keine belegten erfolgreichen Weckvorgänge.
7. Einstellungen und Aktualisierung bei deaktiviertem/fehlendem Anbieter konsistent behandeln. UI-Texte lokalisieren; keine neuen fest eingebauten deutschen Statussätze.

## Vor Übernahme prüfen

- Kodi-Parser/Include-Expansion für alle zehn Einzelaktionen und den Sammelpfad.
- Status mit fünf, zehn, null und lückenhaft belegten Plätzen; weniger Plätze nach vorher zehn. Alte Plätze dürfen nach dem Öffnen nicht als Ziele stehen bleiben.
- Anbieter fehlt, ist deaktiviert, liefert keine Werte oder beendet sich mit Fehler. Kein Weckauftrag aus alten Properties.
- Name/IP ohne MAC, MAC ohne IP und ungültige MAC; sichtbare Darstellung und präzise Rückmeldung.
- Ein gemeinsamer Aufruf zur Statusaktualisierung nach einer Sammelanforderung. Einzel- und Sammelpfad verwenden dieselben Zielbedingungen.
- Navigation bei zehn Geräten und Hilfsaktionen, Detailzeilen, Sprachwechsel.
- Vor einem echten Netzwerk-Wecktest zuerst Zielauflösung und Bedingungen ohne Netzwerkpakete prüfen; danach ein ausdrücklich gewähltes Testgerät verwenden.

Die Existenz des nativen Built-ins löst den Platznummern-Vertrag, beweist aber allein weder frische Properties noch einen funktionierenden Gerätestart. Die oben genannten Laufzeittests bleiben erforderlich.

## Quellen

- Kodi Piers RC1, Registrierung und Handler: https://raw.githubusercontent.com/xbmc/xbmc/22.0rc1-Piers/xbmc/interfaces/builtins/ApplicationBuiltins.cpp
- Offizielle Built-in-Dokumentation: https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/page__list_of_built_in_functions.html
- Aktueller Skin: `xml/Custom_1151_WOL.xml`.
- Installiertes Add-on 4.1.2, ausschließlich lesend geprüft: `../script.skinhelper.ping/default.py` (`Hosts`, `DEVICE_SLOT_COUNT`, MAC-/Status-Properties) und dessen `addon.xml`/`README.md`. Frühere Versionen und ihre Grenzen sind im Hauptaudit dokumentiert.

## Umsetzungs- und Teststand

`Custom_1151_WOL.xml` verwendet zehn Aufrufe des gemeinsamen `WOLDeviceItem`-Includes in `Includes_Buttons_and_Lists.xml`. Einzel- und Sammelaktionen rufen den nativen Built-in auf. Die Liste ist 440 Pixel hoch und überschneidet damit nicht mehr die ab 620/640 angeordneten Trenn-/Detailzeilen. Die Beschriftung nennt explizit Geräte mit MAC-Adresse und zeigt keine irreführende IP-Anzahl. Neue Texte 31950–31952 sind auf Deutsch/Englisch vorhanden; andere Sprachen verwenden den englischen Fallback. Ein leerer Dialog zeigt eine entsprechende Meldung.

Im getrennten Kodi wurde mit unverändertem Anbieter-Gating eine vorab gesetzte MAC von Platz 10 beim Öffnen gelöscht; ohne installierten Anbieter blieb die Liste leer. Für einen zweiten Test wurden ausschließlich in der Skin-Testkopie Anbieterbedingungen auf wahr gesetzt und native Weck-/Statusbefehle durch `SetProperty`-Markierungen ersetzt. Die Testwerte wurden nach der normalen Onload-Bereinigung gesetzt: Platz 1 und 10 mit unterschiedlichen MAC-Adressen, Platz 2 nur mit Name/IP. Ergebnis: Platz 2 löst weder Weckmarkierung noch Statusanforderung aus, die Einzelaktion für Platz 10 markiert ausschließlich dessen MAC, die Sammelaktion markiert 1 und 10 und lässt 2 aus. Es wurden dabei keine WOL-Pakete gesendet und kein externes Add-on verändert.

Der erste Testlauf nahm eine feste anfängliche Auswahlposition an und beschriftete deshalb seine Fälle falsch. Er liegt nur als `wol_intercepted_draft.json` vor. Die erfolgreiche Nachprüfung sucht den tatsächlichen Listeneintrag anhand von Platznummer oder Beschriftung; Beleg `wol_intercepted_actions.json`. Anschließend wurden sämtliche Teständerungen entfernt, die Skin-Kopie vollständig per SHA-256 abgeglichen und Kodi beendet (`wol_copy_check.json`).

Offen: Statuslieferung mit den echten älteren/neuen Anbieterständen, Dienst-/Fehlerfälle und Änderung von Einstellungen während des offenen Dialogs; lange Gerätenamen, weitere Sprachen/Seitenverhältnisse nach der inzwischen geprüften Standard-Zehnerliste; ein ausgewähltes echtes Testgerät für MAC-Validierung und Paketwirkung. Der native Handler und die abgefangenen Zieltests ersetzen diese Prüfungen nicht.

## Nachprüfung: vollständige Liste

Der bisher offene Grundfall „zehn Geräte plus Hilfsaktionen, Scrollen ohne Überlagerung der Details“ ist mit eingespeisten Testdaten im sichtbaren Kodi geprüft. Alle 13 Einträge erreicht, Daten der Auswahl abgeglichen, Aufnahmen visuell geprüft. Die ursprüngliche Startauswahl war Einstellungen, nicht Platz 1. Netzwerk-/Status-/Einstellungsaktionen wurden in der Testkopie neutralisiert und nicht angeklickt. Quelle/Log/Testabweichungen und Bereinigung stehen im Laufzeitbericht (`wol_ten_*`). Lange Namen/andere Sprachen/Seitenverhältnisse, echte Statusanbieter und echte Gerätewirkung bleiben offen.


## Echte Ping-Statusanbindung (2026-11-04)

Unveränderten installierten Anbieter 4.1.2 in das getrennte Kodi-Profil kopiert, keine Benutzereinstellungen übernommen. Testdaten nur 127.0.0.1 auf Platz 1 und 10, Namen „Audit Loopback“, sämtliche MAC-Felder leer und Hintergrunddienst aus. Der produktive WOL-Onload ruft den echten Statusanbieter auf. Beide Ziele werden mit Status on und servercount/serveron=2 angezeigt, daneben Settings/Refresh; kein Sammelweck-Eintrag ohne MAC. Ein eingespeister Altwert auf Platz 5 verschwindet.

Zweiter regulärer Start mit nur Platz 1: servercount/serveron=1, Platz 10 leer und aus der Liste entfernt. Danach Anbieter deaktiviert und den Dialog neu geöffnet: nur Settings, Zähler und zuvor gesetzter Altwert auf Platz 10 leer. Keine Gerätezeile ausgewählt und kein WakeOnLan-Aufruf. Die beiden Laufzeitlogs enthalten keine ERROR-Zeile und enden regulär.

Beide Kodi-Prozesse beendet, temporäre Anbieter-Konfiguration entfernt, Profileinstellungen bytegleich wiederhergestellt und 164 XML-Dateien mit dem Projekt abgeglichen. 17 kopierte Anbieter-/Ressourcendateien sowie die Originaldateien stimmen mit den vorher erfassten SHA-256-Werten überein. Anbieter bleibt unverändert nur als zusätzliche Testinstallation vorhanden. Belege: `kodi22_runtime/ping_provider_checks.json`, `ping_provider_two.png`, `ping_provider_one.png`, `run_ping_provider_probe.py`.

Grenzen: kein echter Weckauftrag, keine MAC-/Paketwirkung, kein Hintergrundintervall, keine fehlgeschlagene Probe und kein live bearbeiteter Einstellungsdialog. Ältere Anbieterstände bleiben ungeprüft. Der Anbieter 4.1.2 räumt fehlende Plätze selbst auf; die erfolgreiche Statusaktualisierung belegt hier Skin und Anbieter zusammen, nicht allein den Skin-Clear-Schritt.
