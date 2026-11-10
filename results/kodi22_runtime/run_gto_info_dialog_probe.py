"""Actual GTO-named skin dialog with controlled provider-contract properties.

The unchanged provider is registered disabled for its labels. No provider action,
service, channel switch, timer or network scraper is executed.
"""
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET


def main():
    missing = '--expect-missing' in sys.argv
    canonical_mode = '--canonical' in sys.argv
    repo = Path(__file__).resolve().parents[2]
    if missing: assert not (repo/'xml/skin.horizonzv-piers.script-gto-info.xml').exists(), 'Baseline requires source checkpoint c937f88 without the checkout entry'
    expected_filename = ('skin.horizonzv' if canonical_mode else 'skin.horizonzv-piers') + '.script-gto-info.xml'
    root = Path(r'C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440').resolve()
    assert subprocess.check_output(['powershell.exe','-NoProfile','-Command','@(Get-Process kodi -ErrorAction SilentlyContinue).Count'],text=True).strip() == '0'
    profile = root/'portable_data'
    addons = profile/'addons'
    canonical = addons/'skin.horizonzv'
    checkout = addons/'skin.horizonzv-piers'
    provider = addons/'script.service.gto'
    assert canonical.exists() and not checkout.exists() and not provider.exists()
    work = Path(tempfile.mkdtemp(prefix='review-gto-info-',dir=root))
    settings = {p:p.read_bytes() for p in [profile/'userdata/guisettings.xml',profile/'userdata/addon_data/skin.horizonzv/settings.xml']}
    saved = work/'settings';saved.mkdir()
    for i,data in enumerate(settings.values()):
        (saved/(str(i)+'.xml')).write_bytes(data)
    database = profile/'userdata/Database'
    db = {p.name:p.read_bytes() for p in database.iterdir() if p.is_file()}
    saved_db = work/'database';saved_db.mkdir()
    for name,data in db.items():
        (saved_db/name).write_bytes(data)
    for p in (repo/'xml').glob('*.xml'):
        shutil.copy2(p,canonical/'xml'/p.name)
    predicates = [n.text for n in ET.parse(repo/'xml/Home.xml').getroot().iter('visible') if 'Window.IsVisible(skin.horizonzv.script-gto-info.xml)' in (n.text or '')]
    assert len(predicates)==1
    backdrop_predicate=predicates[0]
    hashes = {}
    for p in (repo.parent/'script.service.gto').rglob('*'):
        if not p.is_file() or any(x in p.parts for x in ['.git','__pycache__','.codex']):
            continue
        name = p.relative_to(repo.parent/'script.service.gto')
        data = p.read_bytes();hashes[name.as_posix()]=hashlib.sha256(data).hexdigest()
        target = provider/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Only the isolated registry is changed, then restored byte for byte below.
    connection = sqlite3.connect(database/'Addons33.db')
    connection.execute("INSERT OR REPLACE INTO installed(addonID,enabled,installDate,origin,disabledReason) VALUES(?,0,datetime('now'),'',1)",('script.service.gto',))
    connection.commit();connection.close()
    assert canonical.resolve().parent == addons.resolve() == checkout.resolve().parent
    if not canonical_mode: canonical.rename(checkout)
    cases = [
        {'name':'future_unmapped','running':'','future':'True','channel':'False','broadcast':'','timer':'','cast':'Author A / Author B','switch':False,'record':False},
        {'name':'running_unmapped','running':'True','future':'','channel':'False','broadcast':'','timer':'','cast':'Author A / Author B','switch':False,'record':False},
        {'name':'running_mapped','running':'True','future':'','channel':'17','broadcast':'','timer':'','cast':'Author A / Author B','switch':True,'record':False},
        {'name':'recordable','running':'','future':'True','channel':'17','broadcast':'31','timer':'False','cast':'Author A / Author B','switch':False,'record':True},
        {'name':'existing_timer_without_cast','running':'','future':'True','channel':'17','broadcast':'31','timer':'True','cast':'','switch':False,'record':False},
    ]
    (work/'cases.json').write_text(json.dumps(cases),encoding='utf-8')
    script = work/'dialog.py'
    script.write_text('''import json,os
from pathlib import Path
import xbmc,xbmcgui,xbmcvfs
root=Path(__file__).parent
home=xbmcgui.Window(10000)
case=json.loads((root/'selected.json').read_text())
values={'Title':'GTO fixture: '+case['name'],'Description':'Authored programme description for the actual HorizonzV GTO dialog. No provider or backend action is executed.','Channel':'Fixture TV','ChannelID':case['channel'],'Date':'05.11.2026 20:15','EndTime':'21:45','RunTime':'90','Genre':'Fixture genre','Year':'2026','Cast':case['cast'],'isRunning':case['running'],'isInFuture':case['future'],'BroadcastID':case['broadcast'],'hasTimer':case['timer'],'Item':'0','Picture':'','Logo':''}
old={k:home.getProperty('GTO.Info.'+k) for k in values}
for k,v in values.items():home.setProperty('GTO.Info.'+k,v)
filename=xbmcvfs.translatePath('special://skin').split(os.sep)[-2]+'.script-gto-info.xml'
result={'filename':filename,'skin':xbmc.getSkinDir()}
try:
 ui=xbmcgui.WindowXMLDialog(filename,str(PROVIDER))
 (root/'stage.json').write_text(json.dumps(dict(result,stage='constructed')))
 ui.doModal()
 del ui
 result['stage']='closed'
except RuntimeError as exc:
 result.update(stage='missing',error_type=type(exc).__name__)
finally:
 for k,v in old.items():
  if v:home.setProperty('GTO.Info.'+k,v)
  else:home.clearProperty('GTO.Info.'+k)
 (root/'stage.json').write_text(json.dumps(result))
'''.replace('PROVIDER',repr(str(provider))),encoding='utf-8')
    sys.path.insert(0,str(root))
    sys.path.insert(0,str(root.parent/'horizonzv-standard-integration-20261103'))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient
    def result(method,params=None):
        r=rpc(method,params);assert 'result' in r,r
        return r['result']
    def wait(fn,expected,seconds=15):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            value=fn()
            if value==expected:return
            time.sleep(.2)
        raise AssertionError((value,expected))
    def boolean(expr):
        return result('XBMC.GetInfoBooleans',{'booleans':[expr]})[expr]
    stage = work/'stage.json'
    def state():
        return json.loads(stage.read_text()) if stage.exists() else {}
    report={'scope':'Actual WindowXMLDialog filename rule and full skin GTO dialog in '+('canonical folder' if canonical_mode else 'checkout folder')+'. Authored properties follow the GTO contract; provider/router/backend not executed.','rows':[],'provider_file_hashes':hashes,'home_backdrop_predicate':backdrop_predicate}
    process=client=None;failure=None
    try:
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=1
        process=subprocess.Popen([str(root/'kodi.exe'),'-p','-w'],cwd=root,startupinfo=startup)
        for _ in range(80):
            try:result('JSONRPC.Ping');break
            except Exception:
                assert process.poll() is None;time.sleep(.25)
        details=result('Addons.GetAddonDetails',{'addonid':'script.service.gto','properties':['enabled','version']})['addon']
        assert details['enabled'] is False,details
        report['provider']=details
        client=XBMCClient(name='HorizonzV GTO dialog integration',uid=secrets.randbits(32));client.connect(port=9777);time.sleep(.2)
        for case in cases[:1] if missing else cases:
            stage.unlink(missing_ok=True)
            (work/'selected.json').write_text(json.dumps(case),encoding='utf-8')
            client.send_action('RunScript("'+script.as_posix()+'")')
            if missing:
                wait(lambda:state().get('stage'),'missing')
                assert state()['filename']==expected_filename,state()
                report['rows'].append({'case':case['name'],**state()});break
            wait(lambda:boolean('Window.IsVisible('+expected_filename+')'),True)
            wait(lambda:state().get('stage'),'constructed')
            assert state()['filename']==expected_filename and state()['skin']=='skin.horizonzv',state()
            wait(lambda:boolean('Control.IsEnabled(21)'),case['switch'])
            wait(lambda:boolean('Control.IsEnabled(22)'),case['record'])
            wait(lambda:boolean(backdrop_predicate),True)
            labels=result('XBMC.GetInfoLabels',{'labels':['Control.GetLabel(21)','Control.GetLabel(22)','Control.GetLabel(23)']})
            assert all(labels.values()),labels
            time.sleep(.8)
            if not canonical_mode and case['name'] in ['running_mapped','existing_timer_without_cast']:
                shot=repo/'results/kodi22_runtime'/('gto_info_'+case['name']+'.png');shot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("'+shot.as_posix()+'")');wait(shot.exists,True)
            report['rows'].append({'case':case['name'],'switch_enabled':boolean('Control.IsEnabled(21)'),'record_enabled':boolean('Control.IsEnabled(22)'),'home_backdrop_condition':boolean(backdrop_predicate),'button_labels':labels,**state()})
            result('Input.Back');wait(lambda:state().get('stage'),'closed')
    except Exception as exc:
        failure=repr(exc);report.update(failure=failure,trace=traceback.format_exc())
    finally:
        if process and process.poll() is None:
            try:result('Application.Quit');process.wait(timeout=30)
            except Exception as exc:report['shutdown_error']=repr(exc)
        if client:client.close()
        cleanup={'process_exited':process is None or process.poll() is not None}
        if cleanup['process_exited']:
            for path,data in settings.items():path.write_bytes(data)
            extra=work/'new-database-files';extra.mkdir()
            for path in database.iterdir():
                if path.is_file() and path.name not in db:path.rename(extra/path.name)
            for name,data in db.items():(database/name).write_bytes(data)
            assert checkout.resolve().parent == addons.resolve() == canonical.resolve().parent
            if not canonical_mode: checkout.rename(canonical)
            assert root in provider.resolve().parents and root in work.resolve().parents
            provider.rename(work/'unchanged-provider')
            cleanup.update(settings_restored=all(p.read_bytes()==v for p,v in settings.items()),all_databases_restored={p.name:p.read_bytes() for p in database.iterdir() if p.is_file()}==db,skin_folder_restored=canonical.exists() and not checkout.exists(),standard_provider_unchanged=all(hashlib.sha256((repo.parent/'script.service.gto'/n).read_bytes()).hexdigest()==v for n,v in hashes.items()),test_provider_unchanged=all(hashlib.sha256((work/'unchanged-provider'/n).read_bytes()).hexdigest()==v for n,v in hashes.items()),skin_xml_match={p.name:p.read_bytes() for p in (canonical/'xml').glob('*.xml')}=={p.name:p.read_bytes() for p in (repo/'xml').glob('*.xml')})
        report['cleanup']=cleanup
        report['errors']=[line for line in (profile/'kodi.log').read_text(encoding='utf-8',errors='replace').splitlines() if ' error ' in line.lower() or 'fatal' in line.lower()]
        name='gto_info_missing_before.json' if missing else ('gto_info_canonical_checks.json' if canonical_mode else 'gto_info_dialog_checks.json')
        (repo/'results/kodi22_runtime'/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'failure':failure,'rows':report['rows'],'errors':report['errors'],'cleanup':cleanup}))
    return int(bool(failure) or not all(cleanup.values()) or (bool(report['errors']) and not missing))


if __name__=='__main__':sys.exit(main())
