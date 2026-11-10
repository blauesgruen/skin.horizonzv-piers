import xbmc,xbmcgui,json
from pathlib import Path
w=xbmcgui.Window(11194)
c=w.getControl(50)
cases=[('Both present', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_music.jpg', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_tvshows.jpg'), ('Empty fanart', '', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_tvshows.jpg'), ('Missing fanart', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_music.jpg.missing', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_tvshows.jpg'), ('Empty logo', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_music.jpg', ''), ('Missing logo', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_music.jpg', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_tvshows.jpg.missing'), ('Both present again', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_tvshows.jpg', 'C:/Users/zorno/AppData/Local/Temp/horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440/portable_data/testmedia/extrafanart/home_music.jpg')]
items=[]
for name,fanart,logo in cases:
 i=xbmcgui.ListItem(name);i.setArt({'fanart':fanart,'clearlogo':logo});items.append(i)
c.reset();c.addItems(items);w.setFocus(c)
rows=[]
for n,(name,fanart,logo) in enumerate(cases):
 c.selectItem(n);xbmc.sleep(1800)
 labels={k:xbmc.getInfoLabel(k) for k in ['ListItem.Label','ListItem.Art(fanart)','ListItem.Art(clearlogo)','Control.GetLabel(601)','Control.GetLabel(602)']}
 rows.append({'case':name,'expected_art':{'fanart':fanart,'clearlogo':logo},'labels':labels})
 xbmc.executebuiltin('TakeScreenshot("'+str(Path('D:\\Program Files\\Kodi22\\portable_data\\addons\\skin.horizonzv-piers\\results\\kodi22_runtime')/('image_fallback_'+str(n)+'.png'))+'")');xbmc.sleep(700)
Path('D:\\Program Files\\Kodi22\\portable_data\\addons\\skin.horizonzv-piers\\results\\kodi22_runtime','image_fallback_checks.json').write_text(json.dumps(rows,indent=2)+'\n')
