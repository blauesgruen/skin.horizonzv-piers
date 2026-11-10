"""Visible FritzAct state/focus check with original skin layouts and local data.

The fixture removes provider content and click actions. It runs no router/device
command and restores its XML files, skin settings and previous startup skin.
"""
import base64
import copy
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


def inside_kodi(config_file):
    import xbmc
    import xbmcaddon
    import xbmcgui

    config = json.loads(Path(config_file).read_text(encoding='utf-8'))
    addon = xbmcaddon.Addon('script.program.fritzact')
    states = [addon.getLocalizedString(30031), addon.getLocalizedString(30030), '']
    result = {'provider_states': states, 'language': xbmc.getLanguage(),
              'python_assertions_enabled': __debug__, 'cases': [], 'mismatches': []}
    ui = None
    try:
        if not (states[0] and states[1] and states[0] != states[1]):
            raise RuntimeError('Provider translations empty or identical')

        class Review(xbmcgui.WindowXMLDialog):
            def onInit(self):
                panel = self.getControl(9821)
                panel.reset()
                for label, state in zip(('ON fixture', 'OFF fixture', 'EMPTY fixture'), states):
                    item = xbmcgui.ListItem(label=label)
                    for key, value in {'state': state, 'mode': 'local data', 'type': 'switch',
                                       'temperature': '21 C', 'power': '3 W', 'energy': '1 kWh'}.items():
                        item.setProperty(key, value)
                    item.setArt({'icon': 'DefaultAddon.png'})
                    panel.addItem(item)
                self.setFocusId(9899)

        ui = Review(config['window'], config['skin'])
        ui.show()
        xbmc.sleep(1800)
        for name, index, focused in [('unfocused', 0, False), ('on', 0, True),
                                     ('off', 1, True), ('empty', 2, True)]:
            ui.getControl(9821).selectItem(index)
            ui.setFocusId(9821 if focused else 9899)
            xbmc.sleep(800)
            actual_state = xbmc.getInfoLabel('Container(9821).ListItem.Property(state)')
            color_flags = {}
            for color, condition in config['conditions'].items():
                # Outside a list-item renderer, explicitly supply its container.
                qualified = condition.replace('ListItem.Property', 'Container(9821).ListItem.Property')
                color_flags[color] = xbmc.getCondVisibility(qualified)
            actual_focus = xbmc.getCondVisibility('Control.HasFocus(9821)')
            if (actual_state != states[index] or actual_focus != focused
                    or color_flags != {'green': index == 0, 'red': index == 1}):
                result['mismatches'].append(name)
            shot = Path(config['output']) / ('fritz_widget_' + name + '.png')
            previous = shot.stat().st_mtime_ns if shot.exists() else None
            xbmc.executebuiltin('TakeScreenshot("' + shot.as_posix() + '")')
            deadline = time.monotonic() + 8
            while not (shot.exists() and shot.stat().st_mtime_ns != previous):
                if time.monotonic() >= deadline:
                    raise RuntimeError('Screenshot not written')
                xbmc.sleep(100)
            result['cases'].append({'name': name, 'selected_state': actual_state,
                                    'state_conditions': color_flags, 'panel_has_focus': focused,
                                    'screenshot': shot.name})
        if result['mismatches']:
            raise RuntimeError('State/focus mismatches: ' + ', '.join(result['mismatches']))
        result['passed'] = True
    except Exception as exc:
        result.update(passed=False, failure=repr(exc), trace=traceback.format_exc())
    finally:
        if ui:
            ui.close()
        Path(config['result']).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


def main():
    repo = Path(__file__).resolve().parents[2]
    kodi = repo.parents[2]
    assert kodi == Path('D:/Program Files/Kodi22')
    assert subprocess.check_output(['powershell.exe', '-NoProfile', '-Command',
                                   '@(Get-Process kodi -ErrorAction SilentlyContinue).Count'], text=True).strip() == '0'
    profile = kodi / 'portable_data'
    work = Path(tempfile.mkdtemp(prefix='horizonzv-fritz-widget-native-'))
    output = repo / 'results/kodi22_runtime'
    source = repo / 'xml/Includes_Dash_FritzDect.xml'
    xml = ET.parse(source).getroot()
    original_panel = xml.find("include[@name='FritzDect']/control")
    panel = copy.deepcopy(original_panel)
    # Keep actual layouts and nested parameter forwarding; remove all data
    # acquisition and click actions from the fixture only.
    removed = []
    for child in list(panel):
        if child.tag in ('content', 'onclick') or child.text == 'FritzdectContent':
            removed.append(ET.tostring(child, encoding='unicode'))
            panel.remove(child)
    panel.find('left').text = '60'
    panel.find('top').text = '180'
    assert all(ET.tostring(panel.find(tag)) == ET.tostring(original_panel.find(tag))
               for tag in ('itemlayout', 'focusedlayout'))
    conditions = {n.findtext('colordiffuse'): n.findtext('visible')
                  for n in original_panel.findall('itemlayout/control/control')
                  if n.findtext('colordiffuse') in ('green', 'red')}
    assert set(conditions) == {'green', 'red'}
    fixture_name = 'review-fritz-widget-native.xml'
    include_name = 'review-fritz-widget-native-includes.xml'
    fixture = repo / 'xml' / fixture_name
    include = repo / 'xml' / include_name
    assert not fixture.exists() and not include.exists()
    includes = repo / 'xml/Includes.xml'
    settings = [profile / 'userdata/guisettings.xml', profile / 'userdata/addon_data/skin.horizonzv/settings.xml']
    saved = {p: p.read_bytes() for p in [includes, *settings]}
    for i, data in enumerate(saved.values()):
        (work / f'original-{i}.xml').write_bytes(data)
    provider = profile / 'addons/script.program.fritzact'

    def provider_hashes():
        return {p.relative_to(provider).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in provider.rglob('*') if p.is_file() and '__pycache__' not in p.parts}

    before_provider = provider_hashes()
    connection = {n.get('id'): n.text or '' for n in ET.fromstring(saved[settings[0]]).iter('setting')}
    auth = base64.b64encode((connection.get('services.webserverusername', '') + ':'
                            + connection.get('services.webserverpassword', '')).encode()).decode()

    def rpc(method, params=None):
        body = {'jsonrpc': '2.0', 'id': 1, 'method': method}
        if params is not None:
            body['params'] = params
        request = Request('http://127.0.0.1:' + connection['services.webserverport'] + '/jsonrpc',
                          data=json.dumps(body).encode(), headers={'Authorization': 'Basic ' + auth,
                                                                  'Content-Type': 'application/json'})
        result = json.loads(urlopen(request, timeout=3).read())
        assert 'result' in result, result
        return result['result']

    report = {'checked_on': '2026-11-10', 'scope': __doc__, 'passed': False,
              'provider_version': ET.parse(provider / 'addon.xml').getroot().get('version'),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'fixture_layouts_equal_source': True, 'removed_fixture_nodes': removed,
              'backup_directory': str(work)}
    process = client = None
    try:
        definition = ET.Element('includes')
        ET.SubElement(definition, 'include', {'name': 'ReviewFritzWidget'}).append(panel)
        ET.ElementTree(definition).write(include, encoding='utf-8', xml_declaration=True)
        includes.write_bytes(saved[includes].replace(b'</includes>',
                             ('<include file="' + include_name + '"/></includes>').encode()))
        home_actions = [copy.deepcopy(n) for n in ET.parse(repo / 'xml/Home.xml').getroot()
                        if n.tag in ('onload', 'onunload') and 'HorizonzV.FritzAct.State' in (n.text or '')]
        assert len(home_actions) == 4
        action_xml = ''.join(ET.tostring(n, encoding='unicode') for n in home_actions)
        fixture.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<window type="dialog"><defaultcontrol>9899</defaultcontrol>HOME_ACTIONS<controls>
<control type="image"><width>1920</width><height>1080</height><texture colordiffuse="FF202020">White.png</texture></control>
<control type="label"><left>60</left><top>40</top><width>1700</width><height>60</height><font>bebas36</font><label>FritzAct: original skin layouts, local data, no device actions</label></control>
<include content="ReviewFritzWidget"><param name="id" value="9821"/><param name="visible" value="true"/></include>
<control type="button" id="9899"><left>60</left><top>340</top><width>650</width><height>60</height><label>Focus outside the widget</label><onclick>noop</onclick></control>
</controls></window>'''.replace('HOME_ACTIONS', action_xml), encoding='utf-8')
        assert 'RunScript' not in ET.tostring(definition, encoding='unicode')
        tree = ET.parse(settings[0])
        node = tree.find("setting[@id='lookandfeel.skin']")
        report['previous_skin'] = node.text
        node.text = 'skin.horizonzv'
        node.attrib.pop('default', None)
        tree.write(settings[0], encoding='utf-8', xml_declaration=True)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        process = subprocess.Popen([str(kodi / 'kodi.exe'), '-p', '-w'], cwd=kodi, startupinfo=startup)
        report['pid'] = process.pid
        deadline = time.monotonic() + 30
        while True:
            assert process.poll() is None, 'Owned Kodi exited before RPC'
            try:
                rpc('JSONRPC.Ping')
                break
            except Exception:
                assert time.monotonic() < deadline, 'No RPC after startup'
                time.sleep(.3)
        assert rpc('Settings.GetSettingValue', {'setting': 'lookandfeel.skin'})['value'] == 'skin.horizonzv'
        sys.path.insert(0, 'C:/Users/zorno/AppData/Local/Temp/horizonzv-standard-integration-20261103')
        from xbmcclient import XBMCClient
        client = XBMCClient(name='HorizonzV Fritz widget display test', uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.3)
        result_path = work / 'result.json'
        config = work / 'config.json'
        config.write_text(json.dumps({'window': fixture_name, 'skin': str(repo), 'output': str(output),
                                      'result': str(result_path), 'conditions': conditions}), encoding='utf-8')
        log = profile / 'kodi.log'
        log_offset = log.stat().st_size
        client.send_action('RunScript("' + Path(__file__).as_posix() + '",--inside-kodi,"' + config.as_posix() + '")')
        deadline = time.monotonic() + 35
        while not result_path.exists():
            assert process.poll() is None, 'Owned Kodi exited during fixture'
            assert time.monotonic() < deadline, 'Fixture did not finish'
            time.sleep(.2)
        result = json.loads(result_path.read_text(encoding='utf-8'))
        report['native'] = result
        log_delta = log.read_bytes()[log_offset:].decode('utf-8', errors='replace')
        parser_errors = [line for line in log_delta.splitlines()
                         if 'ERROR' in line and ('Control.HasFocus' in line or '$PARAM[fritzid]' in line
                                                 or fixture_name in line or include_name in line)]
        report['relevant_parser_error_count'] = len(parser_errors)
        assert result['passed'] and not parser_errors, 'Native fixture or relevant parser check failed'
        # Exercise the production Home lifecycle itself, in addition to the
        # identical actions copied into the isolated display fixture.
        property_names = ['Window(Home).Property(HorizonzV.FritzAct.StateOn)',
                          'Window(Home).Property(HorizonzV.FritzAct.StateOff)']
        transitions = []
        for window, expected in [('settings', ['', '']), ('home', result['provider_states'][:2]),
                                 ('settings', ['', ''])]:
            rpc('GUI.ActivateWindow', {'window': window})
            deadline = time.monotonic() + 8
            while True:
                values = rpc('XBMC.GetInfoLabels', {'labels': property_names})
                if [values[name] for name in property_names] == expected:
                    break
                assert time.monotonic() < deadline, 'Home translation-property lifecycle failed'
                time.sleep(.2)
            transitions.append({'window': window, 'properties': values})
        report['production_home_lifecycle'] = transitions
        report['passed'] = True
    except Exception as exc:
        report.update(failure=repr(exc), trace=traceback.format_exc())
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
        for path, data in saved.items():
            path.write_bytes(data)
        for path in (fixture, include):
            assert path.parent == repo / 'xml'
            if path.exists():
                path.unlink()
        report['cleanup'] = {'owned_process_exited': process is None or process.poll() is not None,
                             'settings_and_includes_restored': all(p.read_bytes() == data for p, data in saved.items()),
                             'fixture_xml_removed': not fixture.exists() and not include.exists(),
                             'provider_files_unchanged': provider_hashes() == before_provider}
        report['limits'] = ['Controlled widget data only; no device/provider backend verification.',
                            'Current installed language only; foreign-language differences retain source evidence.',
                            'No real FritzAct content acquisition or click action in the fixture.']
        (output / 'fritz_widget_native_checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('passed', 'cleanup')}, ensure_ascii=True))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--inside-kodi':
        inside_kodi(sys.argv[2])
    else:
        main()
