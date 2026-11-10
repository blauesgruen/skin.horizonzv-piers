"""ASM display contract: original writer methods and real skin variables in visible Kodi.

Selects pure display-writing methods from installed ASM without importing its
service entry point. No playback, live recognition, QF request or addon edit.
"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import traceback
import xml.etree.ElementTree as ET


def inside_kodi(config_path):
    import xbmc
    import xbmcgui

    config = json.loads(Path(config_path).read_text(encoding='utf-8'))
    provider = Path(config['provider'])
    home = xbmcgui.Window(10000)
    namespace = {'WINDOW': home, 're': re}
    constants = ast.parse((provider / 'constants.py').read_text(encoding='utf-8-sig'))
    prop_class = next(n for n in constants.body if isinstance(n, ast.ClassDef) and n.name == 'PropertyNames')
    exec(compile(ast.Module(body=[prop_class], type_ignores=[]), '<original ASM property constants>', 'exec'), namespace)
    namespace['_P'] = namespace['PropertyNames']
    tree = ast.parse((provider / 'service.py').read_text(encoding='utf-8-sig'))
    keys = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == '_DISPLAY_TEXT_KEYS' for t in n.targets))
    exec(compile(ast.Module(body=[keys], type_ignores=[]), '<original ASM display keys>', 'exec'), namespace)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RadioMonitor')
    names = {'set_property_safe', '_normalize_display_text', '_sanitize_station_text'}
    nodes = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    nodes += [n for n in cls.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == '_BULLET_KEYS' for t in n.targets)]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<unchanged ASM display methods>', 'exec'), namespace)
    spec = importlib.util.spec_from_file_location('horizonzv_probe_text_encoding', provider / 'text_encoding.py')
    encoding = importlib.util.module_from_spec(spec)
    previous_bytecode_setting = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(encoding)
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
    namespace['_normalize_text'] = encoding.normalize_text
    publisher = type('DisplayPublisher', (), {name: namespace[name] for name in names | {'_BULLET_KEYS'}})()
    fields = ['ArtistDisplay', 'Station', 'QF.Response.StationUsed', 'Title', 'FirstRelease',
              'Genre', 'Logo', 'BandFormed', 'BandMembers', 'Album']
    old = {field: home.getProperty('RadioMonitor.' + field) for field in fields}
    result = {'scope': __doc__, 'python_assertions_enabled': __debug__,
              'language': xbmc.getLanguage(), 'cases': [], 'passed': False}
    ui = None

    def values():
        # The Python ControlLabel wrapper does not expose resolved XML info-label
        # text through getLabel(). Query the actual native control description.
        return {name: xbmc.getInfoLabel('Control.GetLabel(' + str(cid) + ')')
                for name, cid in config['control_ids'].items()}

    try:
        for field in fields:
            home.clearProperty('RadioMonitor.' + field)
        ui = xbmcgui.WindowXMLDialog(config['window'], config['skin'])
        ui.show()
        xbmc.sleep(1200)
        baseline = values()
        full = {'ArtistDisplay': 'Probe Artist', 'Station': 'Probe Station A (128 kbps)',
                'Title': 'Probe Song', 'FirstRelease': '2001', 'Genre': 'Probe Genre',
                'Logo': 'special://skin/icon.png', 'BandFormed': '1990',
                'BandMembers': 'Member A / Member B', 'Album': 'Probe Album'}
        cases = [('plain', '', full), ('bullet', '[COLOR green]\u2022[/COLOR] ', full),
                 ('genre_qf_fallback', '', {'ArtistDisplay': 'Probe Artist', 'QF.Response.StationUsed': 'Probe QF Station', 'Station': 'Probe Station A'}),
                 ('qf_station', '', {'QF.Response.StationUsed': 'Probe QF Station', 'Station': 'Probe Station A'}),
                 ('station', '', {'Station': 'Probe Station B'}), ('cleared', '', {})]
        for name, prefix, data in cases:
            for field in fields:
                home.clearProperty('RadioMonitor.' + field)
            publisher._bullet_prefix = prefix
            for field, value in data.items():
                publisher.set_property_safe('RadioMonitor.' + field, value)
            xbmc.sleep(700)
            actual = values()
            expected = dict(baseline)
            if name in ('plain', 'bullet'):
                expected.update(title=prefix + 'Probe Artist', label=prefix + 'Probe Song (2001)',
                                genre=prefix + 'Probe Genre', poster='special://skin/icon.png',
                                band=prefix + 'Probe Artist (1990)[COLOR=grey] - Member A / Member B[/COLOR]',
                                album=xbmc.getLocalizedString(558) + ': ' + prefix + 'Probe Album')
            elif name == 'genre_qf_fallback':
                expected.update(title='Probe Artist', genre='Probe QF Station', band='Probe Artist')
            elif name == 'qf_station':
                expected.update(title='Probe QF Station', band='Probe QF Station')
            elif name == 'station':
                expected.update(title='Probe Station B', band='Probe Station B')
            album_visible = xbmc.getCondVisibility('Control.IsVisible(9806)')
            compare = set(expected) - (set() if album_visible else {'album'})
            mismatches = {key: {'expected': expected[key], 'actual': actual[key]}
                          for key in compare if expected[key] != actual[key]}
            if album_visible != bool(data.get('Album')):
                mismatches['album_visible'] = album_visible
            shot = Path(config['output']) / ('asm_display_' + name + '.png')
            previous = shot.stat().st_mtime_ns if shot.exists() else None
            xbmc.executebuiltin('TakeScreenshot("' + shot.as_posix() + '")')
            import time
            deadline = time.monotonic() + 8
            while not (shot.exists() and shot.stat().st_mtime_ns != previous):
                if time.monotonic() > deadline:
                    raise RuntimeError('Screenshot not written')
                xbmc.sleep(100)
            result['cases'].append({'name': name, 'values': actual, 'album_visible': album_visible,
                                    'mismatches': mismatches, 'screenshot': shot.name})
            if mismatches:
                raise RuntimeError('Display mismatch: ' + name)
        result['passed'] = True
    except Exception as exc:
        result.update(failure=repr(exc), trace=traceback.format_exc())
    finally:
        if ui:
            ui.close()
        for field, value in old.items():
            if value:
                home.setProperty('RadioMonitor.' + field, value)
            else:
                home.clearProperty('RadioMonitor.' + field)
        result['home_properties_restored'] = all(home.getProperty('RadioMonitor.' + f) == v for f, v in old.items())
        Path(config['result']).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


def main():
    sys.dont_write_bytecode = True
    from visible_standard_kodi import VisibleKodi

    repo = Path(__file__).resolve().parents[2]
    provider = repo.parent / 'service.audio.stream.monitor'
    output = repo / 'results/kodi22_runtime'
    fixture = repo / 'xml/review-asm-display-native.xml'
    if fixture.exists():
        raise RuntimeError('Fixture already exists')
    session = VisibleKodi(repo, 'HorizonzV ASM display contract')
    expressions = {'title': '$VAR[HomeOSDTitle]', 'label': '$VAR[HomeOSDLabel]',
                   'genre': '$VAR[RadioDE_Genre]', 'poster': '$VAR[NowPlayingPosterVar]'}
    music = ET.parse(repo / 'xml/MusicVisualisation.xml').getroot()
    expressions['band'] = next(n.text for n in music.iter('label') if 'RadioMonitor.BandFormed' in (n.text or ''))
    expressions['album'] = next(n.text for n in music.iter('label') if 'RadioMonitor.Album)' in (n.text or ''))
    ids = {name: 9801 + index for index, name in enumerate(expressions)}

    def hashes():
        return {p.relative_to(provider).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in provider.rglob('*') if p.is_file() and '__pycache__' not in p.parts}

    before = hashes()
    report = {'checked_on': '2026-11-10', 'scope': __doc__, 'passed': False,
              'provider_version': ET.parse(provider / 'addon.xml').getroot().get('version'),
              'source_files': {name: hashlib.sha256((provider / name).read_bytes()).hexdigest()
                               for name in ('service.py', 'constants.py', 'text_encoding.py')},
              'skin_files': {name: hashlib.sha256((repo / 'xml' / name).read_bytes()).hexdigest()
                             for name in ('Variables.xml', 'MusicVisualisation.xml')},
              'label_expressions': expressions, 'previous_skin': session.previous_skin}
    try:
        window = ET.Element('window', {'type': 'dialog'})
        controls = ET.SubElement(window, 'controls')
        background = ET.SubElement(controls, 'control', {'type': 'image'})
        ET.SubElement(background, 'width').text = '1920'
        ET.SubElement(background, 'height').text = '1080'
        ET.SubElement(background, 'texture', {'colordiffuse': 'FF202020'}).text = 'White.png'
        for index, (name, expression) in enumerate(expressions.items()):
            control = ET.SubElement(controls, 'control', {'type': 'label', 'id': str(ids[name])})
            for tag, text in {'left': '60', 'top': str(70 + index * 100), 'width': '1740',
                              'height': '70', 'font': 'bebas36', 'label': expression}.items():
                ET.SubElement(control, tag).text = text
            if name == 'album':
                ET.SubElement(control, 'visible').text = '!String.IsEmpty(Window(Home).Property(RadioMonitor.Album))'
        ET.ElementTree(window).write(fixture, encoding='utf-8', xml_declaration=True)
        session.start()
        report['pid'] = session.process.pid
        if session.rpc('Player.GetActivePlayers'):
            raise RuntimeError('Unexpected active player; no playback changed')
        result = session.work / 'result.json'
        config = session.work / 'config.json'
        config.write_text(json.dumps({'provider': str(provider), 'window': fixture.name,
                                      'skin': str(repo), 'output': str(output), 'control_ids': ids,
                                      'result': str(result)}), encoding='utf-8')
        session.run_script(Path(__file__), config)
        session.wait(result.exists, seconds=30)
        report['native'] = json.loads(result.read_text(encoding='utf-8'))
        if not report['native']['passed'] or not report['native']['home_properties_restored']:
            raise RuntimeError('Native display check failed')
        report['passed'] = True
    except Exception as exc:
        report.update(failure=repr(exc), trace=traceback.format_exc())
    finally:
        report['cleanup'] = session.close()
        fixture.unlink(missing_ok=True)
        report['cleanup'].update(fixture_removed=not fixture.exists(), provider_files_unchanged=before == hashes())
        report['limits'] = ['Original pure display setters with authored data only; no live service entry point imported.',
                            'No radio playback, metadata recognition, online artwork or QF backend verification.',
                            'No code change justified solely by supported names or passing controlled data.']
        (output / 'asm_display_native_checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('passed', 'cleanup')}, ensure_ascii=True))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--inside-kodi':
        inside_kodi(sys.argv[2])
    else:
        main()
