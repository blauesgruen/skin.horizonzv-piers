"""Exercise the production widget include using source-defined window targets."""
import copy
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    assert subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], text=True).strip() == "0"
    profile = root / "portable_data"
    xml = profile / "addons/skin.horizonzv/xml"
    work = Path(tempfile.mkdtemp(prefix="review-widget-source-target-", dir=root))
    folder = work / "untyped-folder"
    folder.mkdir()
    (folder / "README.txt").write_text("Navigation fixture; no playback.\n", encoding="utf-8")
    backups = {p:p.read_bytes() for p in [profile/"userdata/guisettings.xml",profile/"userdata/addon_data/skin.horizonzv/settings.xml"]}
    for i,data in enumerate(backups.values()):
        (work/('settings-'+str(i)+'.xml')).write_bytes(data)
    database = profile / "userdata/Database"
    db = {p.name:p.read_bytes() for p in database.iterdir() if p.is_file()}
    saved = work / "database"
    saved.mkdir()
    for name,data in db.items():
        (saved/name).write_bytes(data)
    for p in (repo/"xml").glob('*.xml'):
        assert p.read_bytes() == (xml/p.name).read_bytes(), p.name
    addon = profile / "addons/plugin.program.horizonzv.navigationprobe"
    assert not addon.exists()
    addon.mkdir()
    (addon/"addon.xml").write_text('<addon id="'+addon.name+'" name="HorizonzV source target probe" version="0.0.1" provider-name="Local fixture"><requires><import addon="xbmc.python" version="3.0.0" /></requires><extension point="xbmc.python.pluginsource" library="default.py"><provides>video executable</provides></extension><extension point="xbmc.addon.metadata"><summary lang="en_GB">Local folder navigation</summary><description lang="en_GB">No network or media playback.</description><platform>all</platform><license>MIT</license></extension></addon>',encoding='utf-8')
    (addon/"default.py").write_text('import sys,xbmcgui,xbmcplugin\nfrom urllib.parse import parse_qs\nitem=xbmcgui.ListItem(label="Local test folder",path='+repr(folder.as_posix()+'/')+')\nxbmcplugin.addDirectoryItem(int(sys.argv[1]),item.getPath(),item,True)\nnode=parse_qs(sys.argv[2].lstrip("?")).get("node",[""])[0]\nif node: xbmcplugin.setProperty(int(sys.argv[1]),"node.target",node)\nxbmcplugin.endOfDirectory(int(sys.argv[1]),True,cacheToDisc=False)\n',encoding='utf-8')
    calls = {}
    for inc in ET.parse(repo/'xml/Includes_Widget_Param.xml').getroot().iter('include'):
        if inc.get('content') == 'HomePageWidget_list':
            params = {p.get('name'):p.get('value') or p.text or '' for p in inc.findall('param')}
            calls[int(params['HomePageWidget_list_id'])] = inc
    cases = [
        ('standard_video',218,None,None,10025,False,False),
        ('standard_music',210,None,None,10502,False,False),
        ('custom_music_to_video',214,'music','Video',10025,False,False),
        ('custom_picture',248,'picture','Pictures',10002,False,False),
        ('custom_video',250,'custom1','Video',10025,False,False),
        ('custom_music',250,'custom1','Music',10502,False,False),
        ('custom_pictures',250,'custom1','Pictures',10002,False,False),
        ('custom_games',250,'custom1','Games',10821,False,False),
        ('secondary_content',218,None,None,10025,True,False),
        ('provider_target_override',218,None,None,10502,False,True),
    ]
    fixtures = []
    for index,case in enumerate(cases):
        name,cid,menu,category,expected,secondary,node = case
        window = ET.Element('window',{'id':str(1180+index)})
        ET.SubElement(window,'defaultcontrol',{'always':'true'}).text = str(cid)
        controls = ET.SubElement(window,'controls')
        bg = ET.SubElement(controls,'control',{'type':'image'})
        for tag,value in [('width','100%'),('height','100%'),('texture','BlackBack.png')]:
            ET.SubElement(bg,tag).text=value
        label = ET.SubElement(controls,'control',{'type':'label'})
        for tag,value in [('left','40'),('top','420'),('width','1800'),('height','65'),('font','font24'),('label','HorizonzV: '+name)]:
            ET.SubElement(label,tag).text=value
        inc = copy.deepcopy(calls[cid])
        inc.attrib.pop('condition',None)
        params = {p.get('name'):p for p in inc.findall('param')}
        def param(key,value):
            if key not in params:
                params[key] = ET.SubElement(inc,'param',{'name':key})
            params[key].text=None
            params[key].set('value',value)
        uri = 'plugin://'+addon.name+'/' + ('?node=music' if node else '')
        param('HomePageWidget_content','' if secondary else uri)
        param('HomePageWidget_content2',uri if secondary else '')
        for key in ['HomePageWidget_list_visible','HomePageWidget_list_visible2','HomePageWidget_list_visible3']:
            param(key,'true')
        param('HomePageWidget_list_onfocus','')
        param('HomePageWidget_list_onunfocus','')
        controls.append(inc)
        path = xml/('Custom_'+str(1180+index)+'_SourceTargetAudit.xml')
        assert not path.exists()
        ET.ElementTree(window).write(path,encoding='utf-8',xml_declaration=True)
        fixtures.append(path)
    sys.path.insert(0,str(root))
    sys.path.insert(0,str(root.parent/'horizonzv-standard-integration-20261103'))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient
    def result(method,params=None):
        r=rpc(method,params)
        assert 'result' in r,r
        return r['result']
    def wait(fn,expected,seconds=15):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            value=fn()
            if value==expected:
                return
            time.sleep(.2)
        raise AssertionError((value,expected))
    def wid():
        return result('GUI.GetProperties',{'properties':['currentwindow']})['currentwindow']['id']
    report={'scope':'Full production HomePageWidget_list include with actual caller target parameters. Only directory inputs, visibility and focus callbacks adapted for isolated local fixtures. No network, media playback or real PVR backend action.','rows':[]}
    process=client=None
    failure=None
    try:
        startup=subprocess.STARTUPINFO()
        startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow=1
        process=subprocess.Popen([str(root/'kodi.exe'),'-p','-w'],cwd=root,startupinfo=startup)
        for _ in range(80):
            try:
                result('JSONRPC.Ping')
                break
            except Exception:
                assert process.poll() is None
                time.sleep(.25)
        result('Addons.SetAddonEnabled',{'addonid':addon.name,'enabled':True})
        client=XBMCClient(name='HorizonzV source target navigation',uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        for index,case in enumerate(cases):
            name,cid,menu,category,expected,secondary,node=case
            if menu:
                for kind in ['Video','Music','Pictures','File','Games','Code']:
                    client.send_action('Skin.Reset(Home_'+menu+'_Custom_Category_'+kind+')')
                client.send_action('Skin.SetBool(Home_'+menu+'_Custom_Category_'+category+')')
                wait(lambda:result('XBMC.GetInfoBooleans',{'booleans':['Skin.HasSetting(Home_'+menu+'_Custom_Category_'+category+')']})['Skin.HasSetting(Home_'+menu+'_Custom_Category_'+category+')'],True)
            client.send_action('ActivateWindow('+str(11180+index)+')')
            wait(wid,11180+index)
            wait(lambda:result('XBMC.GetInfoLabels',{'labels':['Container('+str(cid)+').NumItems']})['Container('+str(cid)+').NumItems'],'1')
            client.send_action('Control.SetFocus('+str(cid)+')')
            wait(lambda:result('XBMC.GetInfoBooleans',{'booleans':['Control.HasFocus('+str(cid)+')']})['Control.HasFocus('+str(cid)+')'],True)
            time.sleep(.8)
            if index==0:
                shot=repo/'results/kodi22_runtime/widget_source_target.png'
                shot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("'+shot.as_posix()+'")')
                wait(shot.exists,True)
            result('Input.Select')
            wait(wid,expected)
            wait(lambda:result('XBMC.GetInfoLabels',{'labels':['Container.FolderPath']})['Container.FolderPath'].rstrip('/\\').replace('\\','/'),folder.as_posix())
            report['rows'].append({'case':name,'source_caller':cid,'target_parameter':calls[cid].find("param[@name='HomePageWidget_target']").get('value'),'expected_window':expected,'actual_window':wid(),'folder_opened':True})
    except Exception as exc:
        failure=repr(exc)
        report.update(failure=failure,trace=traceback.format_exc())
    finally:
        if process and process.poll() is None:
            try:
                result('Application.Quit')
                process.wait(timeout=30)
            except Exception as exc:
                report['shutdown_error']=repr(exc)
        if client:
            client.close()
        cleanup={'process_exited':process is None or process.poll() is not None}
        if cleanup['process_exited']:
            for path,data in backups.items():
                path.write_bytes(data)
            extra=work/'new-database-files'
            extra.mkdir()
            for path in database.iterdir():
                if path.is_file() and path.name not in db:
                    path.rename(extra/path.name)
            for name,data in db.items():
                (database/name).write_bytes(data)
            assert root.resolve() in addon.resolve().parents and root.resolve() in work.resolve().parents
            addon.rename(work/'fixture-addon')
            for path in fixtures:
                path.rename(work/path.name)
            cleanup.update(settings_restored=all(p.read_bytes()==d for p,d in backups.items()),databases_restored={p.name:p.read_bytes() for p in database.iterdir() if p.is_file()}==db,skin_xml_match={p.name:p.read_bytes() for p in xml.glob('*.xml')}=={p.name:p.read_bytes() for p in (repo/'xml').glob('*.xml')})
        report['cleanup']=cleanup
        report['errors']=[line for line in (profile/'kodi.log').read_text(encoding='utf-8',errors='replace').splitlines() if ' error ' in line.lower() or 'fatal' in line.lower()]
        (repo/'results/kodi22_runtime/widget_source_target_checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'failure':failure,'cases':len(report['rows']),'errors':report['errors'],'cleanup':cleanup}))
    return int(bool(failure) or bool(report['errors']) or not all(cleanup.values()))


if __name__=='__main__':
    sys.exit(main())
