"""Bounded source-protocol check, not a Kodi runtime or online-provider test.

Executes selected unchanged upstream AST nodes with a small in-memory Kodi API.
Pinned public sources are downloaded unless --source-dir supplies their cache.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
from urllib.request import urlopen
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
TMDB = '7f0c7a2cfd81351f03405f91fcd22e1ac06fe568'
JURIAL = '8a3e7c64a7545b00d3833c73fab12b3d628c5120'
SOURCES = {
    'poller.py': f'https://raw.githubusercontent.com/jurialmunkey/plugin.video.themoviedb.helper/{TMDB}/resources/tmdbhelper/lib/monitor/poller.py',
    'utils.py': f'https://raw.githubusercontent.com/jurialmunkey/plugin.video.themoviedb.helper/{TMDB}/resources/tmdbhelper/lib/monitor/utils.py',
    'window.py': f'https://raw.githubusercontent.com/jurialmunkey/script.module.jurialmunkey/{JURIAL}/resources/modules/jurialmunkey/window.py',
}


def selected(source, predicate, namespace):
    tree = ast.parse(source)
    tree.body = [node for node in tree.body if predicate(node)]
    exec(compile(tree, '<unchanged upstream AST selection>', 'exec'), namespace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path)
    args = parser.parse_args()
    sources = {name: (args.source_dir.joinpath(name).read_text(encoding='utf-8')
                      if args.source_dir else urlopen(url, timeout=30).read().decode('utf-8'))
               for name, url in SOURCES.items()}
    windows = {}
    state = {'local': False, 'disabled': False}

    class Window:
        def __init__(self, window_id):
            self.properties = windows.setdefault(window_id, {})

        def getProperty(self, key):
            return self.properties.get(key, '')

    def visibility(condition):
        if condition == 'Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)':
            return state['local']
        if condition == '!Skin.HasSetting(TMDbHelper.Service)':
            return state['disabled']
        # Fixture has no modal/info dialog, screensaver, scroll or fullscreen.
        return False

    namespace = {'xbmcgui': SimpleNamespace(Window=Window),
                 'try_type': lambda value, kind: kind(value),
                 'get_condvisibility': visibility, 'get_infolabel': lambda _: ''}
    selected(sources['window.py'], lambda n: isinstance(n, ast.FunctionDef)
             and n.name == 'get_property', namespace)
    checker = next(n for n in ast.parse(sources['window.py']).body
                   if isinstance(n, ast.ClassDef) and n.name == 'WindowChecker')
    method = next(n for n in checker.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'get_window_property')
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<upstream getter>', 'exec'), namespace)

    class WindowChecker:
        current_window = 10060
        current_base_window = 10060
        get_window_property = namespace['get_window_property']

        def get_current_window(self):
            return self.current_window

        def get_current_base_window(self):
            return self.current_base_window

        def is_current_window_xml(self, names):
            return 'MyFavourites.xml' in names

        is_current_base_window_xml = is_current_window_xml

    namespace['WindowChecker'] = WindowChecker
    selected(sources['poller.py'], lambda n: not isinstance(n, (ast.Import, ast.ImportFrom)), namespace)
    selected(sources['utils.py'], lambda n: isinstance(n, ast.FunctionDef)
             and n.name in ('widget_id', 'container'), namespace)
    poller = namespace['Poller']()
    xml_path = ROOT / 'xml/MyFavourites.xml'
    skin = ET.parse(xml_path).getroot()
    hooks = [n for n in skin if n.tag in ('onload', 'onunload')
             and 'TMDbHelper.WidgetContainer' in (n.text or '')]
    assert len(hooks) == 4

    def lifecycle(event, enabled=True):
        for node in hooks:
            if node.tag != event:
                continue
            if node.get('condition'):
                assert node.get('condition') == 'System.AddonIsEnabled(plugin.video.themoviedb.helper)'
                if not enabled:
                    continue
            command, arguments = node.text.rstrip(')').split('(', 1)
            parts = arguments.split(',')
            target = {'Home': 10000, 'favouritesbrowser': 10060}[parts[-1]]
            properties = windows.setdefault(target, {})
            if command == 'SetProperty':
                assert len(parts) == 3
                properties[parts[0]] = parts[1]
            else:
                assert command == 'ClearProperty' and len(parts) == 2
                properties.pop(parts[0], None)

    cases = []
    for local in (False, True):
        windows.clear()
        state.update(local=local, disabled=False)
        assert not poller.is_on_listitem and poller.is_on_clear
        lifecycle('onload')
        assert poller.is_on_listitem
        widget = namespace['widget_id'](10060)
        assert widget == 0 and namespace['container'](widget) == 'Container.'
        state['disabled'] = True
        assert poller.is_on_disabled
        state['disabled'] = False
        lifecycle('onunload')
        assert not any(windows.values())
        assert not poller.is_on_listitem and poller.is_on_clear
        cases.append({'local_widget_mode': local, 'before_not_polled': True,
                      'after_polled': True, 'native_default_container': True,
                      'service_disabled_guard_retained': True, 'unload_cleared': True})
    lifecycle('onload', enabled=False)
    assert not any(windows.values())
    before = subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}',
                                      'show', 'a6a5cd4:xml/MyFavourites.xml'], cwd=ROOT)
    for node in hooks:
        skin.remove(node)

    def semantic(node):
        return (node.tag, node.attrib, (node.text or '').strip(), tuple(map(semantic, node)))

    assert semantic(skin) == semantic(ET.fromstring(before))
    report = {'checked_on': '2026-11-10', 'passed': True,
              'scope': 'Original pinned upstream AST with mocked Kodi property/window API; not native Kodi execution.',
              'source_sha256': {n: hashlib.sha256(s.encode()).hexdigest() for n, s in sources.items()},
              'sources': SOURCES, 'cases': cases, 'disabled_addon_no_opt_in': True,
              'only_four_lifecycle_actions_added_to_skin_tree': True,
              'skin_sha256': hashlib.sha256(xml_path.read_bytes()).hexdigest(),
              'limits': ['Kodi builtin dispatch and onload/onunload timing not executed.',
                         'Receiver visibility, item delivery and actual online icons not tested.',
                         'No addon modified or installed.']}
    output = Path(__file__).with_name('tmdb_favourites_protocol_checks.json')
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'output': str(output), 'mode_cases': len(cases)}))


if __name__ == '__main__':
    main()
