# Automatisch erzeugte Bestandsaufnahme

Erzeugt von `tools/analyze_skin.py`. Alle Detaillisten liegen als CSV (Trennzeichen `;`) in diesem Ordner.

## Kennzahlen

| Kennzahl | Wert |
|---|---|
| xml_dateien | 164 |
| xml_zeilen | 23036 |
| xml_parsefehler | 0 |
| fenster | 95 |
| custom_fenster | 19 |
| includes_definiert | 374 |
| includes_unbenutzt | 0 |
| includes_fehlend | 0 |
| includes_doppelt | 0 |
| variablen | 281 |
| variablen_unbenutzt | 55 |
| variablen_fehlend | 0 |
| konstanten | 59 |
| expressions | 0 |
| skin_bools | 432 |
| skin_bools_nur_gelesen | 42 |
| skin_bools_nur_geschrieben | 8 |
| skin_strings | 174 |
| skin_strings_nur_gelesen | 24 |
| skin_strings_nur_geschrieben | 0 |
| skinsettings_optionen | 129 |
| skinsettings_ohne_beschreibung | 89 |
| sprachen | 14 |
| strings_definiert | 295 |
| strings_benutzt | 265 |
| strings_fehlend | 0 |
| strings_unbenutzt | 30 |
| media_dateien | 758 |
| xbt_eintraege | 757 |
| texturen_referenziert | 310 |
| texturen_fehlend | 0 |
| texturen_vermutlich_unbenutzt | 2 |
| fontsets | 1 |
| fonts | 56 |
| fonts_unbenutzt | 0 |
| farben_benannt | 24 |
| farben_hex_hartkodiert | 17 |
| addons_referenziert | 32 |
| views | 51 |
| auffaelligkeiten | 8 |
| zahlen_statt_konstanten | 4 |
| dynamisch_nicht_ausgewertet | 3 |

## Fenster (XML-Dateien mit `<window>`)

| Datei | ID | Typ | Defaultcontrol | Controls | Includes | Zeilen |
|---|---|---|---|---|---|---|
| AddonBrowser.xml | 20 | window | 50 | 12 | 22 | 80 |
| Custom_1100_Artistslideshow_Artistinfo.xml | 1000 | dialog |  | 20 | 5 | 447 |
| Custom_1101_Artistinfos_Settings.xml | 1101 | dialog | 1101 | 10 | 2 | 94 |
| Custom_1102_TextViewer.xml | 1102 | dialog | 61 | 9 | 8 | 78 |
| Custom_1104_SettingsList.xml | 1104 | dialog | 11000 | 24 | 22 | 206 |
| Custom_1141_refesh_videodb.xml | 1141 | dialog | 11 | 5 | 6 | 67 |
| Custom_1142_refesh_musicdb.xml | 1142 | dialog | 11 | 5 | 6 | 67 |
| Custom_1151_WOL.xml | 1151 | dialog | 36110 | 13 | 13 | 182 |
| Custom_1152_Steelbox.xml | 1152 | buttonmenu | 100 | 26 | 7 | 202 |
| Custom_1154_SkinSettingReset.xml | 1154 | dialog | 11 | 5 | 6 | 70 |
| Custom_1155_FirstRun.xml | 1155 | dialog | 10 | 7 | 5 | 162 |
| Custom_1200_Dashboard.xml | 1200 | dialog | 8006 | 12 | 13 | 171 |
| Custom_1301_HomeMenuItemsPosition.xml | 1301 | window | 13000 | 15 | 6 | 340 |
| Custom_1400_MusicOverlay.xml | 1400 | dialog | 2 | 23 | 5 | 186 |
| Custom_1401_VideoOverlay.xml | 1401 | dialog | 2 | 17 | 5 | 131 |
| Custom_1500_WidgetSettings.xml | 1500 | dialog | 36000 | 97 | 149 | 1124 |
| Custom_1501_HomemenuTargets.xml | 1501 | dialog | 36001 | 3 | 22 | 138 |
| Custom_1600_Overlay.xml | 1600 | dialog |  | 3 | 0 | 63 |
| Custom_1700_Wetterwarnung.xml | 1700 | dialog | 17000 | 11 | 3 | 104 |
| Custom_1800_UsedAddons.xml | 1800 | dialog | 18000 | 3 | 4 | 38 |
| DialogAddonInfo.xml |  | window | 9000 | 33 | 20 | 282 |
| DialogAddonSettings.xml |  | window | 5 | 11 | 11 | 134 |
| DialogBusy.xml |  | window |  | 7 | 1 | 54 |
| DialogButtonMenu.xml |  | window | 9000 | 29 | 12 | 349 |
| DialogColorPicker.xml |  | window | 6 | 14 | 4 | 112 |
| DialogConfirm.xml |  | window |  | 5 | 6 | 71 |
| DialogContextMenu.xml |  | window | 996 | 7 | 2 | 63 |
| DialogExtendedProgressBar.xml | 151 | window |       | 7 | 2 | 61 |
| DialogFullScreenInfo.xml | 142 | dialog | 603 | 31 | 7 | 166 |
| DialogGameControllers.xml |  | window | 3 | 0 | 4 | 15 |
| DialogKeyboard.xml |  | window | 300 | 85 | 70 | 653 |
| DialogMediaSource.xml |  | window | 10 | 16 | 12 | 183 |
| DialogMusicInfo.xml |  | window | 9000 | 46 | 26 | 438 |
| DialogMusicScan.xml | 112 | window | 401 | 5 | 2 | 44 |
| DialogNotification.xml | 107 | window |  | 8 | 3 | 70 |
| DialogNumeric.xml |  | window | 21 | 20 | 17 | 218 |
| DialogPVRChannelGuide.xml |  | window | 11 | 12 | 4 | 114 |
| DialogPVRChannelManager.xml |  | window | 20 | 37 | 18 | 366 |
| DialogPVRChannelsOSD.xml |  | window | 11 | 27 | 4 | 216 |
| DialogPVRGroupManager.xml |  | window | 13 | 33 | 17 | 275 |
| DialogPVRGuideSearch.xml |  | window | 9 | 10 | 28 | 294 |
| DialogPVRInfo.xml | 601 | window | 9000 | 18 | 13 | 223 |
| DialogPVRRadioRDSInfo.xml |  | window | 10 | 79 | 5 | 843 |
| DialogPictureInfo.xml |  | window | 5 | 15 | 6 | 140 |
| DialogPlayerProcessInfo.xml |  | window | 5553 | 39 | 4 | 284 |
| DialogSeekBar.xml |  | window |  | 88 | 6 | 537 |
| DialogSelect.xml |  | window | 3 | 0 | 8 | 17 |
| DialogSettings.xml |  | window | 5 | 6 | 12 | 116 |
| DialogSlider.xml |  | window | 11 | 5 | 2 | 51 |
| DialogSubtitles.xml |  | dialog |  | 44 | 0 | 400 |
| DialogTextViewer.xml | 147 | window | 61 | 9 | 8 | 77 |
| DialogVideoInfo.xml |  | window | 5000 | 76 | 44 | 874 |
| DialogVideoManager.xml |  | window |  | 14 | 15 | 303 |
| DialogVideoScan.xml | 133 | window | 401 | 6 | 0 | 49 |
| DialogVolumeBar.xml |  | window |  | 7 | 1 | 69 |
| EventLog.xml |  | window | 50 | 26 | 22 | 200 |
| FileBrowser.xml |  | window | 450 | 16 | 12 | 170 |
| FileManager.xml |  | window | 20 | 32 | 10 | 201 |
| GameOSD.xml |  | window | 1103 | 20 | 5 | 174 |
| Home.xml |  | window | 9000 | 47 | 33 | 494 |
| LoginScreen.xml | 29 | window | 52 | 16 | 8 | 138 |
| MusicOSD.xml |  | window | 99 | 55 | 24 | 652 |
| MusicVisualisation.xml |  | window |  	 | 193 | 40 | 1396 |
| MyFavourites.xml |  | window | 777 | 10 | 22 | 79 |
| MyGames.xml |  | window | 50 | 8 | 20 | 65 |
| MyMusicNav.xml | 502 | window | 777 | 14 | 26 | 105 |
| MyMusicPlaylistEditor.xml |  | window | 6 | 27 | 12 | 218 |
| MyPVRChannels.xml |  | window | 777 | 5 | 17 | 43 |
| MyPVRGuide.xml |  | window | 777 | 6 | 17 | 47 |
| MyPVRRecordings.xml |  | window | 777 | 5 | 17 | 43 |
| MyPVRSearch.xml |  | window | 777 | 5 | 17 | 43 |
| MyPVRTimers.xml |  | window | 777 | 5 | 17 | 43 |
| MyPics.xml | 2 | window | 50 | 13 | 24 | 93 |
| MyPlaylist.xml |  | window | 50 | 8 | 18 | 69 |
| MyPrograms.xml | 1 | window | 777 | 11 | 23 | 84 |
| MyVideoNav.xml |  | window | 50 | 19 | 32 | 157 |
| MyWeather.xml |  | window | 9000 | 41 | 36 | 417 |
| PlayerControls.xml |  | dialog | 100 | 34 | 6 | 431 |
| Pointer.xml | 105 | window |  | 4 | 0 | 38 |
| Settings.xml |  | window | 9000 | 15 | 12 | 211 |
| SettingsCategory.xml |  | window | 3 | 49 | 18 | 344 |
| SettingsProfile.xml |  | window | 2 | 24 | 15 | 221 |
| SettingsScreenCalibration.xml |  | window | 8 | 9 | 2 | 116 |
| SettingsSystemInfo.xml |  | window | 95 | 58 | 7 | 321 |
| SkinSettings.xml | 56 | window | 8000 | 206 | 161 | 2035 |
| SlideShow.xml |  | window |  | 1 | 0 | 14 |
| SmartPlaylistEditor.xml |  | window | 22 | 17 | 21 | 238 |
| SmartPlaylistRule.xml |  | window | 9001 | 7 | 11 | 103 |
| Startup.xml |  | window | 10 | 4 | 2 | 40 |
| VideoFullScreen.xml |  | window |  | 51 | 10 | 330 |
| VideoOSD.xml | 2901 | window | 99 | 53 | 18 | 726 |
| VideoOSDBookmarks.xml |  | window | 2 | 17 | 2 | 159 |
| script-cu-lrclyrics-main.xml |  | window | 99 | 27 | 2 | 286 |
| script-globalsearch.xml |  | window |  | 26 | 5 | 236 |
| skin.horizonzv.script-gto-info.xml | 1900 | window | 10 | 16 | 9 | 145 |

### Fenster, die Estuary (Kodi 22) hat, dieser Skin aber nicht

- `dialogpvrguidecontrols.xml`
- `mypvrproviders.xml`

### Custom-Fenster-IDs, die aufgerufen werden, aber keine Datei haben

- keine

## Includes

- per `<include file=…>` eingebundene Dateien: 66
- `$PARAM[...]` im Einsatz: ja – dynamisch erzeugte Include-Namen sind möglich, "unbenutzt" ist daher nur ein Hinweis

### Unbenutzte Includes

| Include | Datei |
|---|---|

### Fehlende Includes (verwendet, aber nicht definiert)

| Include | Verwendungen |
|---|---|

### Mehrfach definierte Includes

| Include | Dateien |
|---|---|

## Variablen

### Unbenutzte Variablen

| Variable | Datei |
|---|---|
| BackgroundOverlayColorWidget | Variables.xml |
| BackgroundOverlayTransition | Variables.xml |
| ChannelListEPGIconVar | Variables.xml |
| FlagDimension_Label_Color | Includes_Flagging.xml |
| HomeWidget_custom1_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom2_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom3_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom4_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom5_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom6_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom7_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom8_Currentpath | Variables_HomemenuCustomItems.xml |
| HomeWidget_custom9_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom1_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom1_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom2_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom2_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom3_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom3_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom4_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom4_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom5_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom5_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom6_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom6_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom7_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom7_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom8_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom8_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_custom9_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_custom9_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_games_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_games_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_movies_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_movies_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_music_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_music_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_musicvideo_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_musicvideo_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_picture_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_picture_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_tvshow_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_tvshow_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| Home_videos_Currentpath | Variables_HomemenuCustomItems.xml |
| Home_videos_SubCategory_Label | Variables_HomemenuCustomItems.xml |
| PVRTimerLabel | Variables.xml |
| Panel3Content | View_Movie_302_3Panel.xml |
| PosterThumbDebugLabel | Variables.xml |
| SelectBack | Variables.xml |
| SelectedColor | Variables.xml |
| TMDbhelperVisibleCondi | Variables.xml |
| ViewIDs | Variables.xml |
| fsk_logo | Variables_MediaFurniture.xml |
| playcount_var | Variables.xml |
| pvrsignal | Variables.xml |

### Fehlende Variablen

| Variable | Verwendungen |
|---|---|

## Skin-Settings

432 Bool-Settings, 174 String-Settings, 129 Bedienelemente im Skin-Einstellungsdialog.

### Bools, die nur abgefragt, aber nirgends gesetzt werden (toter Code oder extern gesetzt)

| Setting | Abfragen | Dateien |
|---|---|---|
| autoscroll | 1 | Includes_PVR.xml |
| coverwallfull | 2 | Custom_1400_MusicOverlay.xml, Custom_1401_VideoOverlay.xml |
| fsk | 1 | Variables_MediaFurniture.xml |
| fsk_dual | 1 | Variables_MediaFurniture.xml |
| fsk_original | 1 | Variables_MediaFurniture.xml |
| home_custom1_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom1_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom2_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom2_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom3_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom3_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom4_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom4_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom5_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom5_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom6_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom6_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom7_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom7_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom8_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom8_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_custom9_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_custom9_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_games_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_games_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_movies_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_movies_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_music_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_music_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_musicvideo_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_musicvideo_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_picture_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_picture_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_seriesbutton | 8 | Custom_1500_WidgetSettings.xml, Includes_Widget_Param.xml |
| home_tvshow_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_tvshow_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| home_videos_custom_subcategory_games | 1 | Variables_HomemenuCustomItems.xml |
| home_videos_custom_subcategory_pictures | 1 | Variables_HomemenuCustomItems.xml |
| homemenuno_movies_sbutton | 10 | Custom_1500_WidgetSettings.xml, Includes_HomeContent.xml |
| homemenuvideostofiles | 2 | Includes_HomeContent.xml |
| label_flagging | 1 | Includes_Flagging.xml |
| no_extrafanart | 1 | Includes.xml |

### Bools, die gesetzt, aber nie abgefragt werden (sinnfreie Optionen)

| Setting | Schreibzugriffe | Dateien |
|---|---|---|
| context_ad | 2 | Custom_1155_FirstRun.xml |
| firstrun1_horizonzv | 1 | SkinSettings.xml |
| hideinfopanel | 2 | Custom_1155_FirstRun.xml |
| hidenavarrow | 1 | Custom_1155_FirstRun.xml |
| hidesysteminfo | 2 | Custom_1155_FirstRun.xml |
| standardnowplaying | 4 | MusicOSD.xml, SkinSettings.xml |
| startvolume | 1 | SkinSettings.xml |
| tmdbhelper.service | 1 | Startup.xml |

### Strings, die nur gelesen, aber nie gesetzt werden

| Setting | Lesezugriffe | Dateien |
|---|---|---|
| addon_fav10_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav10_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav1_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav1_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav2_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav2_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav3_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav3_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav4_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav4_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav5_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav5_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav6_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav6_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav7_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav7_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav8_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav8_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav9_icon | 1 | Includes_Dash_Addonpath_Fav.xml |
| addon_fav9_label | 1 | Includes_Dash_Addonpath_Fav.xml |
| customcolor | 1 | Variables.xml |
| homemenugames | 23 | Includes_HomeContent.xml |
| musicgenreicons.ext | 2 | Variables.xml |
| musicgenreicons.name | 6 | Variables.xml |

### Strings, die gesetzt, aber nie gelesen werden

| Setting | Schreibzugriffe | Dateien |
|---|---|---|

### Optionen im Skin-Einstellungsdialog

| Kategorie | ID | Typ | Label | Setting(s) | Beschreibung |
|---|---|---|---|---|---|
| Shutdown Menu | 110 | radiobutton | verberge "Verlassen" Schalter | Shutdown_noexit | nein |
| Shutdown Menu | 111 | radiobutton | verberge "Ausschalten" Schalter | Shutdown_noshutdown | nein |
| Shutdown Menu | 112 | radiobutton | verberge "Benutzerdefinierter Ausschalttimer" Schalter | Shutdown_notimer | nein |
| Shutdown Menu | 113 | radiobutton | verberge "Bereitschaft" Schalter | Shutdown_nosuspent | nein |
| Shutdown Menu | 114 | radiobutton | verberge "Ruhezustand" Schalter | Shutdown_nohibernate | nein |
| Shutdown Menu | 115 | radiobutton | verberge "Neustart" Schalter | Shutdown_noreboot | nein |
| Shutdown Menu | 116 | radiobutton | verberge "Ausschalten bei Leerlauf verhindern" Schalter | shutdown_noinhibitidle | nein |
| Shutdown Menu | 117 | radiobutton | verberge "Ausschalten bei Leerlauf erlauben" Schalter | shutdown_noallowidle | nein |
| Shutdown Menu | 121 | radiobutton | zeige "KODI APP neu starten" Schalter | shutdown_restart | nein |
| Shutdown Menu | 122 | radiobutton | zeige "Skin neu laden" Schalter | shutdown_reload | nein |
| Shutdown Menu | 123 | radiobutton | zeige "Neustart von Nand" Schalter | shutdown_nand | nein |
| Shutdown Menu | 124 | radiobutton | Addon | shutdown_addon | nein |
| Shutdown Menu | 125 | button | - Addon wählen | shutdown_addon1 | nein |
| Shutdown Menu | 126 | button | - eigenes Label festlegen | shutdown_addon1_label | nein |
| Shutdown Menu | 127 | radiobutton | Videobibliothek exportieren (einzelne NFO, ohne Bilder, alte Daten überschreiben) | videolibrary_export | nein |
| Admin | 202 | radiobutton | Aktiviere Gitter | DebugGrid | nein |
| Admin | 204 | radiobutton | Debug Information | DebugInfo | nein |
| Admin | 208 | radiobutton | Ersten Start aktivieren | firstrun_horizonzv, firstrun1_horizonzv | nein |
| Admin | 210 | button | wähle deine Systemleistung |  | nein |
| Admin | 212 | button | Skin-Einstellungen Zurücksetzen |  | nein |
| Admin | 214 | radiobutton | Mauszeiger | mousearrow | nein |
| Admin | 216 | radiobutton | Kiosk Mode | kioskmode | nein |
| Hauptmenü Schaltflächen | 299 | button | Positionen festlegen |  | nein |
| Hauptmenü Schaltflächen | 301 | button | Focus verschieben | homemenufocus | nein |
| Hauptmenü Schaltflächen | 302 | button | $VAR[Home_music_Label] |  | ja |
| Hauptmenü Schaltflächen | 303 | button | $VAR[Home_videos_Label] |  | ja |
| Hauptmenü Schaltflächen | 304 | button | $VAR[Home_movies_Label] |  | nein |
| Hauptmenü Schaltflächen | 305 | button | Spiele |  | nein |
| Hauptmenü Schaltflächen | 306 | button | Dashboard |  | nein |
| Hauptmenü Schaltflächen | 307 | button | $VAR[Home_tvshow_Label] |  | nein |
| Hauptmenü Schaltflächen | 308 | button | $VAR[Home_musicvideo_Label] |  | nein |
| Hauptmenü Schaltflächen | 309 | button | $VAR[Home_picture_Label] |  | nein |
| Hauptmenü Schaltflächen | 310 | radiobutton | Wetter | HomeMenuNoWeatherButton | nein |
| Hauptmenü Schaltflächen | 432 | radiobutton | - Hauptmenü automatisch ausblenden | HomeMenuWeatherFadeout | nein |
| Hauptmenü Schaltflächen | 434 | button | - Zeit bis zum ausblenden | hidehomemenu_timer | nein |
| Hauptmenü Schaltflächen | 436 | radiobutton | - Wetter Fanarts | WeatherFanartHome | nein |
| Hauptmenü Schaltflächen | 438 | button | Wetterfanart ... |  | nein |
| Hauptmenü Schaltflächen | 311 | button | Disk |  | nein |
| Hauptmenü Schaltflächen | 314 | button | $VAR[Home_custom1_Label] |  | nein |
| Hauptmenü Schaltflächen | 315 | button | $VAR[Home_custom2_Label] |  | nein |
| Hauptmenü Schaltflächen | 316 | button | $VAR[Home_custom3_Label] |  | nein |
| Hauptmenü Schaltflächen | 317 | button | $VAR[Home_custom4_Label] |  | nein |
| Hauptmenü Schaltflächen | 318 | button | $VAR[Home_custom5_Label] |  | nein |
| Hauptmenü Schaltflächen | 319 | button | $VAR[Home_custom6_Label] |  | nein |
| Hauptmenü Schaltflächen | 320 | button | $VAR[Home_custom7_Label] |  | nein |
| Hauptmenü Schaltflächen | 321 | button | $VAR[Home_custom8_Label] |  | nein |
| Hauptmenü Schaltflächen | 322 | button | $VAR[Home_custom9_Label] |  | nein |
| Hauptmenü Schaltflächen | 326 | button | System |  | nein |
| Hauptmenü Schaltflächen | 327 | button | TV |  | nein |
| Hauptmenü Schaltflächen | 328 | button | Radiosender |  | nein |
| Untermenü Schaltflächen | 910 | button | Videos |  | nein |
| Untermenü Schaltflächen | 911 | button | Filme |  | nein |
| Untermenü Schaltflächen | 912 | button | Musikvideos |  | nein |
| Untermenü Schaltflächen | 913 | button | Serien |  | nein |
| Untermenü Schaltflächen | 914 | button | Musik |  | nein |
| Untermenü Schaltflächen | 915 | button | System |  | nein |
| Untermenü Schaltflächen | 930 | radiobutton | Filme | SubMenu_videos_No_movies_sButton | nein |
| Untermenü Schaltflächen | 931 | radiobutton | Serien | SubMenu_videos_No_tvshow_Button | nein |
| Untermenü Schaltflächen | 932 | radiobutton | Musikvideos | SubMenu_videos_No_music_videoButton | nein |
| Untermenü Schaltflächen | 933 | radiobutton | Bibliothek | SubMenu_videos_NoLibraryButton | nein |
| Untermenü Schaltflächen | 934 | radiobutton | Addons | SubMenu_videos_NoVideoAddonButton | nein |
| Untermenü Schaltflächen | 935 | radiobutton | Filmreihen | SubMenu_movies_NoSetButton | nein |
| Untermenü Schaltflächen | 936 | radiobutton | Titel | SubMenu_movies_NoTitleButton | nein |
| Untermenü Schaltflächen | 937 | radiobutton | Genre | SubMenu_movies_NoGenreButton | nein |
| Untermenü Schaltflächen | 938 | radiobutton | Jahre | SubMenu_movies_NoYearButton | nein |
| Untermenü Schaltflächen | 939 | radiobutton | Darsteller | SubMenu_movies_NoActorButton | nein |
| Untermenü Schaltflächen | 940 | radiobutton | Addons | SubMenu_movies_NoAddonButton | nein |
| Untermenü Schaltflächen | 941 | radiobutton | Titel | SubMenu_musicvideo_NoTitleButton | nein |
| Untermenü Schaltflächen | 942 | radiobutton | Genre | SubMenu_musicvideo_NoGenreButton | nein |
| Untermenü Schaltflächen | 943 | radiobutton | Titel | SubMenu_tvshow_NoTitleButton | nein |
| Untermenü Schaltflächen | 944 | radiobutton | Genre | SubMenu_tvshow_NoGenreButton | nein |
| Untermenü Schaltflächen | 945 | radiobutton | Jahre | SubMenu_tvshow_NoYearButton | nein |
| Untermenü Schaltflächen | 946 | radiobutton | Darsteller | SubMenu_tvshow_NoActorButton | nein |
| Untermenü Schaltflächen | 947 | radiobutton | Partymodus | SubMenu_music_NoPartymodeButton | nein |
| Untermenü Schaltflächen | 948 | radiobutton | Interpreten | SubMenu_music_NoArtistButton | nein |
| Untermenü Schaltflächen | 949 | radiobutton | Alben | SubMenu_music_NoAlbumButton | nein |
| Untermenü Schaltflächen | 950 | radiobutton | Titel | SubMenu_music_NoSongsButton | nein |
| Untermenü Schaltflächen | 951 | radiobutton | Bibliothek | SubMenu_music_NoLibraryButton | nein |
| Untermenü Schaltflächen | 952 | radiobutton | Addons | SubMenu_music_NoAddonButton | nein |
| Untermenü Schaltflächen | 953 | radiobutton | Skin | SubMenu_music_NoSkinSettingButton | nein |
| Untermenü Schaltflächen | 954 | radiobutton | LibreELEC / CoreELEC | SubMenu_music_NoLibreelecButton | nein |
| Untermenü Schaltflächen | 955 | radiobutton | Dateimanager | SubMenu_music_NoFilemanagerButton | nein |
| Untermenü Schaltflächen | 956 | radiobutton | Profile | SubMenu_music_NoProfileButton | nein |
| Untermenü Schaltflächen | 957 | radiobutton | Systeminformationen | SubMenu_music_NoSystemInfoButton | nein |
| Funktionen | 503 | radiobutton | Hintergrund Video | BackgroundVideo | ja |
| Funktionen | 507 | button | Wähle das Land der Alterfreigabe | 31305 | ja |
| Funktionen | 508 | radiobutton | Trailer NICHT im Fenster abspielen | WindowedTrailer | ja |
| Funktionen | 524 | radiobutton | Audiovisualisierung (Hauptmenü) | ShowBackgroundVis | ja |
| Funktionen | 525 | radiobutton | Next Track Playlist | playlist | ja |
| Funktionen | 542 | button | Lege Startlautstärke fest | start_volume, startvolume | ja |
| Funktionen | 543 | radiobutton | Deaktiviere alphanummerischer Sprungleiste | HideJumpSMSBar | ja |
| Funktionen | 546 | radiobutton | Wake on lan Schalter in \'Zentrale\' verbergen | hidewolhome | ja |
| Funktionen | 549 | radiobutton | Eigene Playlist beim Start | Use_Startup_Playlist | ja |
| Funktionen | 550 | button | - Pfad: | Startup_Playlist_Path | nein |
| Funktionen | 553 | radiobutton | Statistic im Hauptmenu anzeigen | statistic | ja |
| Funktionen | 555 | radiobutton | \'Zentrale\' deaktivieren | hide_central | ja |
| Funktionen | 556 | radiobutton | Zeige Profilnamen | profilname | nein |
| Funktionen | 557 | radiobutton | Zeige Ladestand der Batterie | BatteryLevel | ja |
| Widgets | 602 | radiobutton | Cover dimmen | WidgetDim | ja |
| Widgets | 604 | radiobutton | keine Progressbar im Widget (grüner Balken auf dem Cover) | WidgetNoPercentPlayedBar | ja |
| Design / Leistung | 802 | radiobutton | Animationen (hohe CPU-Last) | animation | ja |
| Design / Leistung | 804 | radiobutton | Navigationsinformationen | NavInfo | ja |
| Design / Leistung | 806 | radiobutton | Verberge Datumsanzeige | NoDate | ja |
| Design / Leistung | 808 | radiobutton | Fanart | fanart | ja |
| Design / Leistung | 810 | radiobutton | Nur ein Hintergrundbild | onlyone | ja |
| Design / Leistung | 812 | button | - Bild / Pfad | Home_Custom_Back_picture_OnlyOne | ja |
| Design / Leistung | 814 | radiobutton | - Diashow statt Standbild | Home_Custom_Back_picture_OnlyOne, Home_Custom_Back_picture_OnlyOne_Path | nein |
| Design / Leistung | 816 | radiobutton | Fanart-Diashow | HomeFanartDiashow | ja |
| Design / Leistung | 820 | button | Hintergrund dimmen | 31257 | ja |
| Design / Leistung | 822 | button | Farb Akzente | 31324 | ja |
| Design / Leistung | 824 | button | - ColorPicker |  | nein |
| Design / Leistung | 825 | button | - ColorPicker |  | ja |
| Design / Leistung | 826 | radiobutton | Seitenzähler | CommonPageCount | ja |
| Design / Leistung | 828 | radiobutton | abgerundete Ecken | roundcorner | nein |
| Design / Leistung | 830 | radiobutton | Neon Slide | NeonSlide | ja |
| Design / Leistung | 832 | button | Hintergrundtheme | 31324 | ja |
| Design / Leistung | 840 | radiobutton | Struktur im Hauptmenü | BackgroundDiffuseOverlay | ja |
| Design / Leistung | 842 | radiobutton | Player Controls | HidePlayerControlsHome | ja |
| Design / Leistung | 844 | radiobutton | Kleine Wetter-Informationen | homepageNOWeatherinfo | ja |
| Design / Leistung | 854 | radiobutton | Radio Ansicht deaktivieren | noradioviz, radioview, vinylview | ja |
| Design / Leistung | 856 | button | Musik Visualisierung | 31280 | ja |
| Design / Leistung | 858 | button | Musik Visualisierung | vinylview, radioview | ja |
| Design / Leistung | 860 | radiobutton | Titelinformationen | musicoverlay_stream | ja |
| Design / Leistung | 870 | radiobutton | Leichte Version des Pausebildschirms | pause_light | ja |
| Design / Leistung | 872 | radiobutton | verberge Videodetails | pause_light_hideinfos | ja |
| Design / Leistung | 873 | radiobutton | zeige größere Schrift im Plot | BigPlotText | nein |
| Design / Leistung | 876 | radiobutton | TV-Logo-Hintergrund Deaktivieren | no_tvlogo_back | nein |
| Extra Arts | 1004 | radiobutton | lade Artworks | EnableExtendedArt | ja |
| Extra Arts | 1008 | button | CD Style | 31331 | ja |

## Sprachdateien

| Sprache | Einträge | übersetzt | Status |
|---|---|---|---|
| cs_cz | 291 | 291 | 98 % (31 identisch mit Englisch) |
| da_dk | 291 | 291 | 98 % (40 identisch mit Englisch) |
| de_de | 295 | 295 | 100 % (38 identisch mit Englisch) |
| el_gr | 291 | 291 | 98 % (65 identisch mit Englisch) |
| en_gb | 295 | 295 | Quelle |
| es_es | 291 | 291 | 98 % (9 identisch mit Englisch) |
| fi_fi | 291 | 291 | 98 % (64 identisch mit Englisch) |
| fr_fr | 291 | 291 | 98 % (23 identisch mit Englisch) |
| it_it | 291 | 291 | 98 % (8 identisch mit Englisch) |
| nb_no | 291 | 291 | 98 % (28 identisch mit Englisch) |
| nl_nl | 291 | 291 | 98 % (29 identisch mit Englisch) |
| pl_pl | 291 | 291 | 98 % (12 identisch mit Englisch) |
| sv_se | 291 | 291 | 98 % (22 identisch mit Englisch) |
| uk_ua | 291 | 291 | 98 % (11 identisch mit Englisch) |

### Probleme in den .po-Dateien

| Sprache | Problem |
|---|---|
| resource.language.cs_cz | Header-ID skin.horizonzv |
| resource.language.cs_cz | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.da_dk | Header-ID skin.horizonzv |
| resource.language.da_dk | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.de_de | Header-ID skin.horizonzv |
| resource.language.de_de | 285 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.el_gr | Header-ID skin.horizonzv |
| resource.language.el_gr | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.en_gb | Header-ID skin.horizonzv |
| resource.language.es_es | Header-ID skin.horizonzv |
| resource.language.es_es | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.fi_fi | Header-ID skin.horizonzv |
| resource.language.fi_fi | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.fr_fr | Header-ID skin.horizonzv |
| resource.language.fr_fr | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.it_it | Header-ID skin.horizonzv |
| resource.language.it_it | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.nb_no | Header-ID skin.horizonzv |
| resource.language.nb_no | 1 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.nl_nl | Header-ID skin.horizonzv |
| resource.language.nl_nl | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.pl_pl | Header-ID skin.horizonzv |
| resource.language.pl_pl | 3 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.sv_se | Header-ID skin.horizonzv |
| resource.language.sv_se | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |
| resource.language.uk_ua | Header-ID skin.horizonzv |
| resource.language.uk_ua | 284 Eintraege ohne englische msgid (nicht Weblate/Transifex-kompatibel) |

### Verwendete, aber nicht definierte Skin-Strings (0)

keine

### Definierte, aber unbenutzte Skin-Strings (30)

| ID | Englisch | Deutsch |
|---|---|---|
| 31012 | Memory used | Speichernutzung |
| 31035 | Search YouTube | YouTube durchsuchen |
| 31054 | Created | Erstellt |
| 31064 | Watch as 2D | In 2D ansehen |
| 31065 | Change mode | Modus ändern |
| 31069 | Select your Kodi user profile to login and continue | Bitte Kodi-Benutzerprofil auswählen um fortzufahren |
| 31209 | To use this function, the addon \'Global Search\' from the official repository is required. | Um diese Funktion nutzen zu können wird das Addon \'Global Search\' aus dem offiziellen Repository benötigt. |
| 31211 | Shows the favourites below the main menu instead of directly the \'Central\'. [CR]These are otherwise accessible via the \'Central\'. | Zeigt unterhalb des Hauptmenüs die Favoriten, statt direkt die \'Zentrale\'.[CR]Diese sind ansonten über die \'Zentrale\' erreichbar. |
| 31241 | Enables all PVR available artwork.[CR][COLOR=white]\'Skin Helper Service\' is required.[/COLOR] | Aktiviert alle verfügbaren PVR Artwork.[CR][COLOR=white]\'Skin Helper Service\' wird benötigt.[/COLOR] |
| 31242 | Select a background picture. | Wähle ein Hintergrundbild |
| 31243 | Reset | Zurücksetzen |
| 31250 | no defined favourites | Keine Favouriten vorhanden |
| 31253 | Set Information | Mehr Informationen |
| 31254 | Concerts | Konzerte |
| 31256 | Flags in text form | Flags in Textform |
| 31272 | Perspective | Perspective |
| 31281 | Music extra arts | Musik Extra Arts |
| 31311 | - Path | - Ordner |
| 31312 | Globalsearch in contextmenu | Globalsearch im Contextmenü |
| 31314 | Show favorites window in main menu | zeige Favoritenfenster im Hauptmenü |
| 31360 | Set the position of each mein menu fixed points.[CR]Using position numbers from 1 - 22. | Lege hier die Position der einzelnen Hauptmenüpunkte fest.[CR]Verwende Positionsnummern von 1 - 22. |
| 31361 | go directly to video files | direkt zu Videodateien springen |
| 31370 | In order to set an Timer the \'KN Switcher Service\' is required. Download via Kodinerds repository. | Um einen Umschalttimer setzen zu können wird der \'KN Switcher Service\' benötigt. Download über Kodinerds Repository. |
| 31371 | delete all timers | alle Timer löschen |
| 31372 | delete | löschen |
| 31373 | administration | verwalten |
| 31374 | Switchtimer | Umschalttimer |
| 31375 | Timer overview | Timer Übersicht |
| 31400 | starting ... | wird gestartet ... |
| 35500 | Location | Ort |

### Sprachliche Fehler im englischen Quelltext

| ID | Fehler | Korrektur | Text |
|---|---|---|---|
| 31201 | scrapper | scraper | Select the country for the age rating (defined in the scrapper).[CR]Supported are DE, US,  |
| 31239 | scrapper | scraper | Show all available movie & series artworks.[CR][COLOR=white]Since Kodi 19 artworks are loa |
| 31309 | Dectivate | Deactivate | Dectivate alphanumeric jumpbar |
| 31313 | Statistic show | Show statistics | Statistic show in mainmenu |
| 31360 | mein menu | main menu | Set the position of each mein menu fixed points.[CR]Using position numbers from 1 - 22. |

### Strings fremder Addons, die per `$ADDON[...]` genutzt werden

- `script.cu.lrclyrics` (1×)
- `script.globalsearch` (1×)
- `script.service.gto` (3×)

## Grafiken

- Lose Dateien in `media/`: 758
- Einträge in `media/Textures.xbt`: 757
- Nur in XBT, nicht lose: 0; nur lose, nicht in XBT: 1
- Dynamisch adressierte Ordner (über `$INFO`/`$VAR`): [color=ffffa500].verifiedsourceby[/, [color=ffffa500].verifiedsourceconfidence[/, [color=ffffa500].verifiedsourceurl[/, [color=grey] - [/, [color=red]nächster umschalttimer: [/, [color=white].sourceswapstatus[/, buttons/, masks/, playmedia(musicdb://albums/, runplugin(plugin://, sources://video/, videodb://movies/actors/, videodb://movies/countries/, videodb://movies/directors/, videodb://movies/genres/, videodb://movies/studios/, videodb://movies/tags/, videodb://movies/years/, videodb://musicvideos/artists/, videodb://musicvideos/countries/, videodb://musicvideos/directors/, videodb://musicvideos/genres/, videodb://musicvideos/sets/, videodb://musicvideos/studios/, videodb://musicvideos/tags/, videodb://musicvideos/years/, videodb://tvshows/actors/, videodb://tvshows/genres/, videodb://tvshows/studios/, videodb://tvshows/tags/, videodb://tvshows/titles/, videodb://tvshows/years/

### Referenzierte, aber fehlende Texturen

| Referenz | Verwendungen |
|---|---|

### Groß-/Kleinschreibung weicht ab (Problem auf Linux/Android ohne XBT)

| Referenz | Datei |
|---|---|

### Vermutlich unbenutzte Grafiken (2)

| Datei |
|---|
| PVR-HasTimer2.png |
| icons/Player.png |

### Nur lose vorhanden (fehlt im XBT – wird ggf. nicht geladen)

| Datei |
|---|
| defaultmusicsources.png |

## Fonts

- Fontsets: default
- Font-Definitionen: 56, TTF-Dateien: Acens.ttf, Bebas.ttf, BigDots.ttf, BigSquareDots.ttf, Impacted.ttf, SegoeUISymbol.ttf, aaaiight.ttf, ubuntu-r.ttf
- Ungenutzte TTF-Dateien: Acens.ttf, BigDots.ttf, BigSquareDots.ttf, Impacted.ttf
- Unbenutzte Font-Namen: keine
- Verwendete, aber undefinierte Fonts: font24


## Farben

- Farbdateien: Defaults.xml
- Benannte Farben: 24, davon unbenutzt: blackdiffuse, description_dark
- Hartkodierte Hex-Farben (unterschiedliche Werte): 17

| Farbe | Verwendungen |
|---|---|
| black | 378 |
| grey | 328 |
| white | 312 |
| description | 169 |
| grey3 | 160 |
| selected | 134 |
| grey2 | 126 |
| fanartdiffuse | 117 |
| menudiffuse | 105 |
| grey1 | 80 |
| selectedhome | 38 |
| red | 23 |
| focused | 21 |
| dustdiffuse | 12 |
| orange | 7 |
| green | 3 |
| green2 | 3 |
| reddiffuse | 2 |
| blue | 1 |
| selectedcolor | 1 |
| darkgold | 0 |
| background | 0 |
| blackdiffuse | 0 |
| description_dark | 0 |

## Referenzierte Addons

| Addon | Referenzen | Dateien |
|---|---|---|
| resource.images.languageflags.colour | 187 | DialogSubtitles.xml, DialogVideoInfo.xml, Includes_SkinAddonsContent.xml, Variables.xml |
| script.service.gto | 61 | Custom_1500_WidgetSettings.xml, Includes_Dash_GTO.xml, Includes_Dashboard.xml, Includes_SkinAddonsContent.xml, skin.horizonzv.script-gto-info.xml |
| script.skinhelper.ping | 43 | Custom_1151_WOL.xml, Home.xml, Includes_Buttons_and_Lists.xml, Includes_SkinAddonsContent.xml, SkinSettings.xml |
| script.program.fritzact | 29 | Custom_1500_WidgetSettings.xml, Includes_Dash_FritzDect.xml, Includes_Dashboard.xml, Includes_SkinAddonsContent.xml |
| script.image.resource.select | 20 | Custom_1500_WidgetSettings.xml, Includes_SkinAddonsContent.xml, Includes_Submenu.xml, MyVideoNav.xml, MyWeather.xml, SkinSettings.xml |
| plugin.video.themoviedb.helper | 13 | Includes_SkinAddonsContent.xml, MyFavourites.xml, MyVideoNav.xml, Startup.xml, Variables.xml, View_Movie_503_MediaInfo.xml |
| script.artistslideshow | 12 | Custom_1100_Artistslideshow_Artistinfo.xml, Includes.xml, Includes_SkinAddonsContent.xml, MusicOSD.xml, Timers.xml |
| script.skin.helper.colorpicker.bg | 12 | Includes_SkinAddonsContent.xml, SkinSettings.xml |
| script.extendedinfo | 10 | DialogMusicInfo.xml, DialogVideoInfo.xml, Variables.xml |
| service.coreelec.settings | 8 | DialogButtonMenu.xml, Includes_Submenu.xml, Settings.xml, SkinSettings.xml |
| script.globalsearch | 8 | Home.xml, Includes_SkinAddonsContent.xml, script-globalsearch.xml |
| service.kn.switchtimer | 6 | Includes_SkinAddonsContent.xml |
| service.libreelec.settings | 5 | Includes_Submenu.xml, Settings.xml, SkinSettings.xml |
| resource.images.moviegenreicons.xzener | 4 | Variables.xml |
| service.audio.stream.monitor | 3 | Includes_SkinAddonsContent.xml |
| plugin.library.node.editor | 3 | Includes_SkinAddonsContent.xml |
| resource.images.weatherfanart.multi | 3 | Includes_SkinAddonsContent.xml |
| plugin.program.autocompletion | 3 | DialogKeyboard.xml, Variables.xml |
| resource.images.weathericons.outline | 2 | Home.xml, Includes_SkinAddonsContent.xml |
| resource.images.studios.coloured | 2 | Variables.xml |
| resource.images.studios.white | 2 | Variables.xml |
| resource.images.moviegenreicons.coloured | 2 | Variables.xml |
| resource.images.moviegenreicons.filmstrip | 2 | Variables.xml |
| resource.images.moviegenreicons.grey | 2 | Variables.xml |
| resource.images.moviegenreicons.poster | 2 | Variables.xml |
| resource.images.moviegenreicons.transparent | 2 | Variables.xml |
| resource.images.moviegenreicons.white | 2 | Variables.xml |
| resource.images.musicgenreicons.grey | 2 | Variables.xml |
| resource.images.musicgenreicons.poster | 2 | Variables.xml |
| resource.images.musicgenreicons.text | 2 | Variables.xml |
| special | 1 | Custom_1301_HomeMenuItemsPosition.xml, DialogColorPicker.xml, DialogKeyboard.xml, DialogPictureInfo.xml, Includes.xml, Includes_BackgroundBuilding.xml, Includes |
| resource.images.weathericons.default | 1 | Variables.xml |

## Views

Freigegebene View-IDs je Bereich (`<views>`):

| Bereich | IDs |
|---|---|
| Addons | 50,550,551,722 |
| Audio | 50,58,505,506,509,512,515,550,551,562,570,722,741 |
| Pictures | 50,510,514,516,550,551,722 |
| Video | 50,57,302,401,402,500,502,503,505,515,550,551,562,721,722,742,740 |

Eingebundene View-Includes:

| Bereich | Include | Datei | View-ID | Viewtype | Label |
|---|---|---|---|---|---|
| Audio | View_50_List | View_50_List.xml | 50 | list | 50 → "?" |
| Audio | View_58_BannerMusic | View_Music_058_Banner.xml | 58 | fixedlist | Banner |
| Audio | View_505_Wide | View_Movie_505_Wide.xml | 505 | list | $LOCALIZE[539] |
| Audio | View_506_InfoListMusic | View_Music_506_InfoList.xml | 506 | list | $LOCALIZE[544] |
| Audio | View_509_FanartMusic | View_Music_509_Fanart.xml | 509 | wrap | 20445 → "Fanart" |
| Audio | View_512_MediaListArtist | View_Music_512_ArtistMediaList.xml | 512 | list | $LOCALIZE[544] |
| Audio | View_515_Episode | View_515_Episode.xml | 515 | list | 20359 → "Episode" |
| Audio | View_550_InfoListAddon | Views_Addon_Browser.xml | 550 | info | $LOCALIZE[31268] |
| Audio | View_551_InfoThumbAddon | Views_Addon_Browser.xml | 551 | thumbview | $LOCALIZE[31269] |
| Audio | View_562_Showcase | View_562_Showcase.xml | 562 | fixed | 562 → "Jahr" |
| Audio | View_570_DiscFlowMusic | View_Music_570_DiscFlow.xml | 570 | fixed | DiscFlow |
| Audio | View_722_RightListAddons | View_722_RightList.xml | 722 | list | View_721_RightList |
| Audio | View_741_CoverWallMusic | View_Music_741_CoverWall.xml | 741 | list | Cover Wall |
| Video | View_50_List | View_50_List.xml | 50 | list | 50 → "?" |
| Video | View_562_Showcase | View_562_Showcase.xml | 562 | fixed | 562 → "Jahr" |
| Video | View_57_Banner | View_Movie_057_Banner.xml | 57 | list | 57 → "Jul" |
| Video | View_503_MediaList | View_Movie_503_MediaInfo.xml | 503 | list | $LOCALIZE[544] |
| Video | View_505_Wide | View_Movie_505_Wide.xml | 505 | list | $LOCALIZE[539] |
| Video | View_401_Fanart | View_Movie_401_Fanart.xml | 401 | fixed | 401 → "Temperatur" |
| Video | View_402_FanartEpisode | View_Movie_402_Fanart_Episode.xml | 402 | fixed | 20445 → "Fanart" |
| Video | View_500_PanelMovie | View_Movie_500_Panel.xml | 500 | panel | Panel |
| Video | View_502_Don | View_Movie_502_Don.xml | 502 | list | $LOCALIZE[539] |
| Video | View_302_3Panel | View_Movie_302_3Panel.xml | 302 | panel | 3 Panel |
| Video | View_515_Episode | View_515_Episode.xml | 515 | list | 20359 → "Episode" |
| Video | View_721_RightList | View_Movie_721_RightList.xml | 721 | list | View_721_RightList |
| Video | View_742_CoverWall | View_Movie_742_Wall.xml | 742 |  |  |
| Video | View_740_CoverWallBig | View_Movie_740_BigWall.xml | 740 |  |  |
| Video | View_550_InfoListAddon | Views_Addon_Browser.xml | 550 | info | $LOCALIZE[31268] |
| Video | View_551_InfoThumbAddon | Views_Addon_Browser.xml | 551 | thumbview | $LOCALIZE[31269] |
| Video | View_722_RightListAddons | View_722_RightList.xml | 722 | list | View_721_RightList |
| Pictures | View_50_List | View_50_List.xml | 50 | list | 50 → "?" |
| Pictures | View_510_WrapViewPicture | Views_Pictures.xml | 510 | wrap | 31014 → "Reihenfolge" |
| Pictures | View_514_ThumbViewPicture | Views_Pictures.xml | 514 | list | $LOCALIZE[31013] |
| Pictures | View_516_WallViewPicture | Views_Pictures.xml | 516 | list | $LOCALIZE[31013] |
| Pictures | View_550_InfoListAddon | Views_Addon_Browser.xml | 550 | info | $LOCALIZE[31268] |
| Pictures | View_551_InfoThumbAddon | Views_Addon_Browser.xml | 551 | thumbview | $LOCALIZE[31269] |
| Pictures | View_722_RightListAddons | View_722_RightList.xml | 722 | list | View_721_RightList |
| Addons | View_50_List | View_50_List.xml | 50 | list | 50 → "?" |
| Addons | View_550_InfoListAddon | Views_Addon_Browser.xml | 550 | info | $LOCALIZE[31268] |
| Addons | View_551_InfoThumbAddon | Views_Addon_Browser.xml | 551 | thumbview | $LOCALIZE[31269] |
| Addons | View_722_RightListAddons | View_722_RightList.xml | 722 | list | View_721_RightList |
| PVR | View_9_LiveTVChannelPanel | Views_PVR_Channels.xml | 9 | panel | panel |
| PVR | View_14_LiveTVChannelIcons | Views_PVR_Channels.xml |  | panel | Icons |
| PVR | View_15_LiveTVChannelList | Views_PVR_Channels.xml | 15 | list | 535 → "Liste" |
| Guide | View_10_PVRGuideTimeline | Views_PVR_Guide.xml |  | list | 19032 → "Zeitlinie" |
| Guide | View_11_PVRGuideNow | Views_PVR_Guide.xml | 11 | list | 535 → "Liste" |
| Guide | View_12_PVRGuideNext | Views_PVR_Guide.xml | 12 | list | 19031 → "Als Nächstes" |
| Guide | View_13_PVRGuideChannel | Views_PVR_Guide.xml | 13 | list | 19029 → "Sender" |
| Recordings | View_50_LiveTVRecordings | Views_PVR_Recordings.xml | 50 | list | 535 → "Liste" |
| Timers | View_21_LiveTVTimers | Views_PVR_Timers.xml | 21 | list | 535 → "Liste" |
| Search | View_50_LiveTVSearch | Views_PVR_Search.xml | 50 | list | 535 → "Liste" |

## Technische Auffälligkeiten

| Datei | Art | Detail |
|---|---|---|
| Home.xml | Alte Skin-ID referenziert | skin.horizonzv.script-gto-info.xml |
| Includes_DebugInfo.xml | Viel auskommentierter Code | 4 Kommentarbloecke mit <control> |
| Includes_SidePanel.xml | Viel auskommentierter Code | 4 Kommentarbloecke mit <control> |
| Includes_Systeminfo.xml | Alte Skin-ID referenziert | skin.horizonzv |
| Includes_Systeminfo.xml | Alte Skin-ID referenziert | skin.horizonzv |
| MyVideoNav.xml | Viel auskommentierter Code | 3 Kommentarbloecke mit <control> |
| keymaps/keyboard.xml | Hartkodierter Windows-Pfad (Entwickler-Keymap) | D:\Program Files\Kodi21\portable_data\addons\skin.horizonzv-omega\scripts\RunSetKodiWindow_min.bat\ |
| keymaps/keyboard.xml | Hartkodierter Windows-Pfad (Entwickler-Keymap) | D:\Program Files\Kodi21\portable_data\addons\skin.horizonzv-omega\scripts\RunSetKodiWindow_min.bat\ |
