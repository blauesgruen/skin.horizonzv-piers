# Prüfung der Widget-Breiten

Stand: 11. November 2026. Anlass: Widgets erhalten laut Nutzer teilweise erst beim Fokussieren ihre richtige Breite. Produktionscode wurde für diese Prüfung nicht geändert; inzwischen ist ein konkreter Breitenfehler beim ausgew?hlten Mehr-Eintrag nachgewiesen (Nachtrag unten).

## Codebefund

`xml/Includes_Widget_Param.xml`, Include `Widget_Listlayout`, definiert zwei Kachelbreiten: 184 und 245 bei Höhe 240. Video-, Film-, Set-, Serien-, Staffel-, Episoden- und Musikvideo-Typen verwenden den schmalen Zweig. Andere beziehungsweise leere Typen verwenden den breiten Zweig. Normales und fokussiertes Layout haben dieselben Typbedingungen und jeweiligen Breiten. Die Typabfragen nennen ausdrücklich die ID des jeweiligen Widget-Containers.

Das umgebende `HomePageWidget_list` verwendet dieselbe Typunterscheidung für seine Verschiebungen bei wenigen Einträgen. Seine Containerbreite ist separat mit `auto`, Minimum 0 und Maximum 736 definiert. Kachelbreite und gesamte Containerbreite sind deshalb getrennt zu betrachten.

Die beiden bedingten Layout-Zweige sind bereits im Git-Stand `0f4b1dd` vorhanden. Das passt zur Angabe des Nutzers, dass das Verhalten schon vor dem Umbau auftrat; es beweist noch nicht die konkrete Ursache.

Nebenbefund: Ein `onfocus` im äußeren Include referenziert `Widget_Listlayout_id`, obwohl dort `HomePageWidget_list_id` übergeben wird. Die damit gesetzte Eigenschaft `Widget_Content_Info` hat laut Suche im aktuellen XML keine Leser. Ein Zusammenhang mit der Breite ist daher nicht nachgewiesen; die Zeile wurde nicht als vermeintliche Breitenkorrektur verändert.

## Sichtbare Laufzeitprüfung

Die laufende Standardinstallation mit aktivem HorizonzV wurde verwendet. Eigene temporäre Testdialoge verwenden den tatsächlichen Include `Widget_Listlayout` aus dem geladenen Skin. Es wurden keine Add-ons, Skin-Einstellungen oder Medien verändert und die Wiedergabe wurde nicht gestoppt. Die Dialoge schließen sich nach der Probe.

Erste Probe: Drei Film- und drei Album-Einträge erscheinen schon ohne Fokus mit unterschiedlichen Kachelformaten. Die gesamte Listenbreite bleibt in beiden Fällen 736; dieser Python-Wert allein misst also nicht die Kachelbreite.

Zweite Probe: Je zwölf Einträge, tatsächliche Fokus-ID und Seitenanzahl geprüft. Film-Liste: drei Seiten; Album-Liste: vier Seiten. Die Seitenanzahlen bleiben beim Fokuswechsel gleich. Beim Zurücksetzen und Befüllen der unfokussierten Film-Liste mit Alben wechselt sie auf vier Seiten; beim erneuten Befüllen mit Filmen zurück auf drei. Damit ist in diesen Fällen kein notwendiger Fokuswechsel zur Formatanpassung beobachtet. [Messwerte](kodi22_runtime/widget_width_dynamic_checks.json).

Zusätzliche kurze Home-Abfrage: Fokus auf Hauptmenü 9000. Mehrere befüllte Widget-Container liefern bereits ohne Widget-Fokus `album`, `movie`, `tvshow` beziehungsweise `episode`. Einige andere Quellen liefern einen leeren Typ; daraus folgt allein kein Fehler. Danach wurde die vorherige Audiovisualisierung wieder geöffnet.

## Noch erforderlich

Der gemeldete Fehler ist mit diesen Fällen nicht reproduziert. Die Probe deckt weder die vollständige Home-Gruppierung und ihre Verschiebungen noch jeden dynamischen Anbieter, gemischte Listen, Quellenwechsel oder verzögert gelieferte Metadaten ab. Benötigt wird ein konkretes betroffenes Widget einschließlich Home-Menüpunkt und Quelle; möglichst auch, ob die Kachel selbst oder der gesamte Widget-Bereich die falsche Breite hat. Eine Änderung der Typentscheidung ohne diesen Gegenversuch wäre nicht ausreichend belegt.

## Quellen

- Lokaler Skin-Code und historischer Git-Stand, wie oben benannt.
- [Kodi Piers: GUIBaseContainer.cpp](https://github.com/xbmc/xbmc/blob/Piers/xbmc/guilib/GUIBaseContainer.cpp): Auswahl bedingter Layouts, Aktualisierung bei Bedingungswechsel und Berechnung der Seitenaufteilung.
- [Kodi Piers: GUIInfoHelper.cpp](https://github.com/xbmc/xbmc/blob/Piers/xbmc/guilib/guiinfo/GUIInfoHelper.cpp): Auflösung eines ausdrücklich genannten Container-Eintrags.

## Nachtrag: Mehr-Eintrag und Musikwechsel

Nutzerhinweis: Nach einem Musikwidget und anschlie?endem Scrollen durch das Hauptmen? werden Filmcover teilweise breit; gleichzeitig f?llt ein Mehr-Ordner auf.

Quellenbefund: Kodi erzeugt bei begrenzten dynamischen Listen mit passendem Ziel standardm??ig selbst einen Mehr-Eintrag, wenn weitere Ergebnisse vorhanden sind. Dieser hat `node.type=target_folder`, aber keinen Video-Medientyp. Der Skin muss dieses Element nicht selbst erzeugen. [Kodi DirectoryProvider.cpp](https://github.com/xbmc/xbmc/blob/Piers/xbmc/guilib/listproviders/DirectoryProvider.cpp), insbesondere `CDirectoryJob::DoWork`.

Zus?tzlicher sichtbarer Test mit dem tats?chlichen Widget-Include: elf Filme plus ein entsprechender typfreier Ordner. Bei ausgew?hltem Film ergeben zw?lf Eintr?ge drei Seiten. Nach Auswahl von Mehr ergeben dieselben zw?lf Eintr?ge vier Seiten: Die gesamte Liste verwendet jetzt die breite Variante. Wechsel zum Musikwidget und danach zu einem Button au?erhalb der Listen erh?lt diesen falschen Zustand. Nach Auswahl des ersten Films werden es wieder drei Seiten. Der erste Filmeintrag bleibt in allen Phasen als `movie` verf?gbar. [Messwerte](kodi22_runtime/widget_width_more_checks.json).

Damit ist die Abh?ngigkeit der ganzen Widget-Breite vom ausgew?hlten Mehr-Eintrag als konkreter Skin-Fehler nachgewiesen. Nicht nachgewiesen ist bisher, wodurch in jedem vollst?ndigen Home-Ablauf gerade dieser Eintrag ausgew?hlt wird oder ob weitere Fehler beteiligt sind. Die Anwesenheit von Mehr allein beweist keinen Breitenfehler; der Eintrag ist grunds?tzlich eine regul?re Kodi-Navigationsfunktion.

Korrekturansatz: Der typfreie Mehr-Eintrag darf die Medienformat-Entscheidung nicht ?berschreiben. Ein R?ckgriff auf einen tats?chlichen Medien-Eintrag muss f?r Layout und die zugeh?rigen Verschiebungen ?bereinstimmend erfolgen. Normale gemischte Inhalte und reine Ordnerlisten m?ssen dabei ber?cksichtigt werden. Noch keine Produktions?nderung vorgenommen.

## Umsetzung: automatisch erzeugtes Mehr entfernen

Auf Nutzerwunsch verwenden beide `content`-Zweige im gemeinsamen `HomePageWidget_list` jetzt `browse="never"`: der optionale erste Eintrag mit Limit 1 und die eigentliche Widget-Quelle. Damit erzeugt Kodis DirectoryProvider keinen zus?tzlichen Mehr-Ordner. Limits, Sortierung, Quellen, Fensterziele und die beiden Kachelbreiten sind unver?ndert. Die ?nderung umfasst zwei Attribute; andere Add-ons werden nicht ver?ndert. Ein ausdr?cklich von einem Plugin gelieferter eigener Seitenwechsel-Eintrag ist davon zu unterscheiden.

Sichtbarer Gegenversuch mit echten Kodi-Verzeichnisanbietern und dem tats?chlichen Widget-Layout: Dieselbe Filmquelle liefert bei Limit 10 mit browse=auto elf Eintr?ge einschlie?lich eines target_folder. Mit browse=never liefert sie genau zehn Filme ohne target_folder; Limit 1 liefert genau einen Film ohne zus?tzlichen Ordner. Die Musikquelle bleibt ebenfalls ohne automatisch erzeugtes Mehr. Nach Fokuswechsel Film ? Musik ? au?erhalb ? Film bleibt die Film-Liste schmal (zehn Filme, drei Seiten). [Abschlie?ende Messwerte](kodi22_runtime/widget_no_more_checks.json).

Die statische Pr?fung meldet f?r 166 Dateien keine Fehler oder Warnungen. Vorherige Testhelfer-Versuche verwendeten zun?chst Python-ControlList.size() f?r dynamische Kodi-Inhalte und danach einen ?berschatteten Variablennamen; diese Versuche belegen kein Produktverhalten. Der erfolgreiche Lauf liest native Container-InfoLabels. Vollst?ndiges schnelles Scrollen durch alle Home-Men?punkte und alle Add-on-Quellen ist damit nicht abgedeckt.
