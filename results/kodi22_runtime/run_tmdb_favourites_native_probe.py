"""Visible standard Kodi: skin-owned Favourites lifecycle, installed provider unchanged.

Tests Kodi builtin dispatch with the installed TMDb Helper version, not 6.21.5
service execution or real online watch-provider delivery. Restores both settings.
"""
import base64
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time
import traceback
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


def main():
    repo = Path(__file__).resolve().parents[2]
    kodi = repo.parents[2]
    profile = kodi / 'portable_data'
    assert kodi == Path('D:/Program Files/Kodi22')
    assert subprocess.check_output(['powershell.exe', '-NoProfile', '-Command',
                                   '@(Get-Process kodi -ErrorAction SilentlyContinue).Count'], text=True).strip() == '0'
    files = [profile / 'userdata/guisettings.xml',
             profile / 'userdata/addon_data/skin.horizonzv/settings.xml']
    original = {p: p.read_bytes() for p in files}
    work = Path(tempfile.mkdtemp(prefix='horizonzv-tmdb-native-'))
    for i, data in enumerate(original.values()):
        (work / f'original-{i}.xml').write_bytes(data)
    sys.path.insert(0, 'C:/Users/zorno/AppData/Local/Temp/horizonzv-standard-integration-20261103')
    from xbmcclient import XBMCClient
    # Read connection settings from the saved snapshot once. Kodi can rewrite
    # guisettings.xml during startup; the RPC client must not parse that file.
    connection_settings = {e.get('id'): e.text or '' for e in
                           ET.fromstring(original[files[0]]).iter('setting')}
    auth = base64.b64encode((connection_settings.get('services.webserverusername', '') + ':'
                            + connection_settings.get('services.webserverpassword', '')).encode()).decode()
    endpoint = 'http://127.0.0.1:' + connection_settings['services.webserverport'] + '/jsonrpc'

    def raw_rpc(method, params=None):
        body = {'jsonrpc': '2.0', 'id': 1, 'method': method}
        if params is not None:
            body['params'] = params
        request = Request(endpoint, data=json.dumps(body).encode(),
                          headers={'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'})
        return json.loads(urlopen(request, timeout=3).read())
    provider = profile / 'addons/plugin.video.themoviedb.helper'
    provider_hashes = {p.relative_to(provider).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in provider.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    version = ET.parse(provider / 'addon.xml').getroot().get('version')
    report = {'scope': __doc__, 'checked_on': '2026-11-10', 'provider_version': version,
              'skin_sha256': hashlib.sha256((repo / 'xml/MyFavourites.xml').read_bytes()).hexdigest(),
              'cases': [], 'backup_directory': str(work), 'passed': False}
    process = client = None

    def rpc(method, params=None):
        result = raw_rpc(method, params)
        assert 'result' in result, result
        return result['result']

    def labels():
        names = ['Window(10060).Property(TMDbHelper.WidgetContainer)',
                 'Window(Home).Property(TMDbHelper.WidgetContainer)']
        return rpc('XBMC.GetInfoLabels', {'labels': names})

    def boolean(condition):
        return rpc('XBMC.GetInfoBooleans', {'booleans': [condition]})[condition]

    def wait(predicate, seconds=15):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            assert process.poll() is None, 'Owned Kodi exited'
            if predicate():
                return
            time.sleep(.2)
        raise AssertionError('Timed out waiting for native condition')

    try:
        tree = ET.parse(files[0])
        node = tree.find("setting[@id='lookandfeel.skin']")
        report['previous_skin'] = node.text
        node.text = 'skin.horizonzv'
        node.attrib.pop('default', None)
        tree.write(files[0], encoding='utf-8', xml_declaration=True)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        process = subprocess.Popen([str(kodi / 'kodi.exe'), '-p', '-w'], cwd=kodi, startupinfo=startup)
        report['pid'] = process.pid
        deadline = time.monotonic() + 25
        while True:
            assert process.poll() is None, 'Owned Kodi exited before RPC'
            try:
                rpc('JSONRPC.Ping')
                break
            except Exception:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.3)
        assert rpc('Settings.GetSettingValue', {'setting': 'lookandfeel.skin'})['value'] == 'skin.horizonzv'
        assert boolean('System.AddonIsEnabled(plugin.video.themoviedb.helper)'), 'Installed provider disabled'
        client = XBMCClient(name='HorizonzV TMDb Favourites lifecycle', uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.3)
        rpc('GUI.ActivateWindow', {'window': 'home'})
        wait(lambda: boolean('Window.IsActive(home)'))
        for local in (False, True):
            client.send_action(('Skin.SetBool' if local else 'Skin.Reset') + '(TMDbHelper.UseLocalWidgetContainer)')
            wait(lambda: boolean('Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)') == local)
            rpc('GUI.ActivateWindow', {'window': 'favouritesbrowser'})
            wait(lambda: boolean('Window.IsActive(favouritesbrowser)'))
            wait(lambda: set(labels().values()) == {'0'})
            case = {'local_widget_mode': local, 'onload_properties': labels(),
                    'receiver_visible': boolean('Control.IsVisible(99950)')}
            shot = repo / 'results/kodi22_runtime' / ('tmdb_favourites_local.png' if local else 'tmdb_favourites_global.png')
            previous_mtime = shot.stat().st_mtime_ns if shot.exists() else None
            client.send_action('TakeScreenshot("' + shot.as_posix() + '")')
            wait(lambda: shot.exists() and shot.stat().st_mtime_ns != previous_mtime)
            case['screenshot'] = shot.name
            rpc('GUI.ActivateWindow', {'window': 'home'})
            wait(lambda: boolean('Window.IsActive(home)'))
            wait(lambda: set(labels().values()) == {''})
            case['onunload_properties'] = labels()
            report['cases'].append(case)
        report['passed'] = True
    except Exception as exc:
        report['failure'] = repr(exc)
        report['trace'] = traceback.format_exc()
    finally:
        if process is not None and process.poll() is None:
            try:
                rpc('Application.Quit')
                process.wait(timeout=25)
            except Exception:
                process.terminate()
                process.wait(timeout=10)
        if client:
            client.close()
        for path, data in original.items():
            path.write_bytes(data)
        after = {p.relative_to(provider).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in provider.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        report['cleanup'] = {'owned_process_exited': process is None or process.poll() is not None,
                             'settings_restored': all(p.read_bytes() == data for p, data in original.items()),
                             'provider_files_unchanged': after == provider_hashes}
        report['limits'] = ['Installed provider version only; no 6.21.5 runtime test.',
                            'No actual online provider-icon delivery asserted.',
                            'Standard-profile background services may execute normally; no provider code edited.']
        (repo / 'results/kodi22_runtime/tmdb_favourites_native_checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('passed', 'cases', 'cleanup')}, ensure_ascii=True))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
