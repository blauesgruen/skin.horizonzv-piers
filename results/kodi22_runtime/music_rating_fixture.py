import xbmc,xbmcgui,json
from pathlib import Path
out=Path('D:\\Program Files\\Kodi22\\portable_data\\addons\\skin.horizonzv-piers\\results\\kodi22_runtime')
media='C:\\Users\\zorno\\AppData\\Local\\Temp\\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440\\portable_data\\testmedia\\skin-audit-silence.wav'
rows=[]
oldvinyl=xbmc.getCondVisibility('Skin.HasSetting(vinylview)')
oldradio=xbmc.getCondVisibility('Skin.HasSetting(radioview)')
xbmc.executebuiltin('Skin.Reset(radioview)')
try:
 for rating in [7,0,1,10]:
  item=xbmcgui.ListItem(label='Audit rating '+str(rating),path=media)
  tag=item.getMusicInfoTag();tag.setTitle('Audit rating '+str(rating));tag.setUserRating(rating)
  xbmc.Player().play(media,item);xbmc.sleep(1800)
  xbmc.executebuiltin('ActivateWindow(visualisation)');xbmc.sleep(800)
  for vinyl in [False,True]:
   xbmc.executebuiltin(('Skin.SetBool' if vinyl else 'Skin.Reset')+'(vinylview)');xbmc.sleep(1300)
   labels={k:xbmc.getInfoLabel(k) for k in ['MusicPlayer.Title','MusicPlayer.UserRating','Control.GetLabel(8911)','Control.GetLabel(8912)']}
   rows.append({'requested_rating':rating,'vinyl':vinyl,'labels':labels})
   xbmc.executebuiltin('TakeScreenshot("'+str(out/('music_rating_'+str(rating)+('_vinyl' if vinyl else '_standard')+'.png'))+'")');xbmc.sleep(600)
finally:
 xbmc.executebuiltin(('Skin.SetBool' if oldvinyl else 'Skin.Reset')+'(vinylview)')
 xbmc.executebuiltin(('Skin.SetBool' if oldradio else 'Skin.Reset')+'(radioview)')
 (out/'music_rating_checks.json').write_text(json.dumps(rows,indent=2)+'\n')
