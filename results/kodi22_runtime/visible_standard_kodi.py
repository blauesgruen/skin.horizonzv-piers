"""Owned visible Kodi session for bounded skin probes.

Uses existing local RPC/EventServer settings, preserves startup/skin settings,
and stops only the process it started. Supports the standard installation or an
explicitly validated owned TEMP runtime. It never installs or edits an addon.
"""
import base64
import json
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


class VisibleKodi:
    def __init__(self, repo, name, test_root=None):
        self.repo = Path(repo).resolve()
        self.root = Path(test_root).resolve() if test_root else self.repo.parents[2]
        if test_root:
            if self.root.parent != Path(tempfile.gettempdir()).resolve() or not self.root.name.startswith('horizonzv-kodi-test-'):
                raise RuntimeError('Unexpected owned test root')
        elif self.root != Path('D:/Program Files/Kodi22'):
            raise RuntimeError('Unexpected standard Kodi root')
        count = subprocess.check_output(['powershell.exe', '-NoProfile', '-Command',
                                         '@(Get-Process kodi -ErrorAction SilentlyContinue).Count'], text=True).strip()
        if count != '0':
            raise RuntimeError('Another Kodi process is running')
        self.profile = self.root / 'portable_data'
        self.files = [self.profile / 'userdata/guisettings.xml',
                      self.profile / 'userdata/addon_data/skin.horizonzv/settings.xml']
        self.saved = {path: path.read_bytes() for path in self.files}
        self.work = Path(tempfile.mkdtemp(prefix='horizonzv-visible-probe-'))
        for index, data in enumerate(self.saved.values()):
            (self.work / f'original-{index}.xml').write_bytes(data)
        self.settings = {n.get('id'): n.text or '' for n in ET.fromstring(self.saved[self.files[0]]).iter('setting')}
        self.previous_skin = self.settings['lookandfeel.skin']
        credentials = self.settings.get('services.webserverusername', '') + ':' + self.settings.get('services.webserverpassword', '')
        self.auth = base64.b64encode(credentials.encode()).decode()
        self.name = name
        self.process = self.client = None

    def rpc(self, method, params=None):
        body = {'jsonrpc': '2.0', 'id': 1, 'method': method}
        if params is not None:
            body['params'] = params
        request = Request('http://127.0.0.1:' + self.settings['services.webserverport'] + '/jsonrpc',
                          data=json.dumps(body).encode(), headers={'Authorization': 'Basic ' + self.auth,
                                                                  'Content-Type': 'application/json'})
        response = json.loads(urlopen(request, timeout=3).read())
        if 'result' not in response:
            raise RuntimeError('Kodi RPC failed: ' + method)
        return response['result']

    def wait(self, predicate, seconds=20):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError('Owned Kodi exited')
            if predicate():
                return
            time.sleep(.2)
        raise RuntimeError('Native probe condition timed out')

    def start(self):
        tree = ET.fromstring(self.saved[self.files[0]])
        node = tree.find("setting[@id='lookandfeel.skin']")
        node.text = 'skin.horizonzv'
        node.attrib.pop('default', None)
        ET.ElementTree(tree).write(self.files[0], encoding='utf-8', xml_declaration=True)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        self.process = subprocess.Popen([str(self.root / 'kodi.exe'), '-p', '-w'], cwd=self.root, startupinfo=startup)
        deadline = time.monotonic() + 30
        while True:
            if self.process.poll() is not None:
                raise RuntimeError('Owned Kodi exited before RPC')
            try:
                self.rpc('JSONRPC.Ping')
                break
            except Exception:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.3)
        if self.rpc('Settings.GetSettingValue', {'setting': 'lookandfeel.skin'})['value'] != 'skin.horizonzv':
            raise RuntimeError('Unexpected active skin')
        if not self.rpc('Addons.GetAddonDetails', {'addonid': 'skin.horizonzv', 'properties': ['enabled']})['addon']['enabled']:
            raise RuntimeError('Configured skin is disabled; settings value alone does not prove loading')
        sys.path.insert(0, 'C:/Users/zorno/AppData/Local/Temp/horizonzv-standard-integration-20261103')
        from xbmcclient import XBMCClient
        self.client = XBMCClient(name=self.name, uid=secrets.randbits(32))
        self.client.connect(port=int(self.settings.get('services.esport') or '9777'))
        time.sleep(.3)

    def run_script(self, script, config):
        self.client.send_action('RunScript("' + Path(script).as_posix() + '",--inside-kodi,"' + Path(config).as_posix() + '")')

    def close(self):
        if self.process is not None and self.process.poll() is None:
            try:
                self.rpc('Application.Quit')
                self.process.wait(timeout=25)
            except Exception:
                self.process.terminate()
                self.process.wait(timeout=10)
        if self.client:
            self.client.close()
        for path, data in self.saved.items():
            path.write_bytes(data)
        return {'owned_process_exited': self.process is None or self.process.poll() is not None,
                'settings_restored': all(p.read_bytes() == data for p, data in self.saved.items())}
