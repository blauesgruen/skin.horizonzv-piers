"""Unmodified TMDb Helper 6.21.5: native receiver and Favourites polling checks.

Runs only in the explicitly owned isolated profile. Uses a public movie-details
directory, no playback, account login or external addon correction.
"""
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import xml.etree.ElementTree as ET


def inspect_poller(config_path):
    import xbmc
    import xbmcaddon

    config = json.loads(Path(config_path).read_text(encoding='utf-8'))
    for path in config['module_paths']:
        sys.path.insert(0, path)
    result = {'passed': False}
    try:
        from tmdbhelper.lib.monitor.poller import Poller
        poller = Poller()
        result.update(provider_version=xbmcaddon.Addon('plugin.video.themoviedb.helper').getAddonInfo('version'),
                      local_mode=xbmc.getCondVisibility('Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)'),
                      media_window=poller.is_on_mediawindow,
                      local_widget=poller.is_on_localwidgetcontainer,
                      global_widget=poller.is_on_globalwidgetcontainer,
                      listitem_polling=poller.is_on_listitem)
        if not result['listitem_polling']:
            raise RuntimeError('Original native Poller does not activate in Favourites')
        result['passed'] = True
    except Exception as exc:
        result.update(failure=repr(exc), trace=traceback.format_exc())
    Path(config['result']).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


def main():
    sys.dont_write_bytecode = True
    from visible_standard_kodi import VisibleKodi

    repo = Path(__file__).resolve().parents[2]
    root = Path(json.loads((repo / 'results/kodi22_runtime/fresh_package_probe_setup.json').read_text())['root'])
    session = VisibleKodi(repo, 'HorizonzV TMDb 6.21.5 integration', test_root=root)
    profile = root / 'portable_data'
    addons = profile / 'addons'
    setup = json.loads((repo / 'results/kodi22_runtime/tmdb_current_addon_setup.json').read_text())
    provider_ids = [record['id'] for record in setup['addons']]

    def fingerprints():
        return {addon: {p.relative_to(addons / addon).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (addons / addon).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
                for addon in provider_ids}

    before = fingerprints()
    favourites = profile / 'userdata/favourites.xml'
    old_favourites = favourites.read_bytes() if favourites.exists() else None
    details_url = 'plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=movie&tmdb_id=603'
    # A plugin entry script lives in resources, but the external inspection
    # script has no plugin script-directory path injected by Kodi.
    module_paths = [str(addons / 'plugin.video.themoviedb.helper/resources')]
    for addon in setup['required_ids_seen']:
        base = addons / addon if (addons / addon).exists() else root / 'addons' / addon
        if not (base / 'addon.xml').exists():
            continue
        for node in ET.parse(base / 'addon.xml').getroot().findall("extension[@point='xbmc.python.module']"):
            module_paths.append(str(base / node.get('library', '')))
    report = {'checked_on': '2026-11-10', 'scope': __doc__, 'passed': False,
              'test_root': str(root), 'cases': [], 'details_url': details_url,
              'skin_files': {name: hashlib.sha256((profile / 'addons/skin.horizonzv/xml' / name).read_bytes()).hexdigest()
                             for name in ('Startup.xml', 'MyVideoNav.xml', 'MyFavourites.xml', 'Includes.xml')}}

    def labels(expressions):
        return session.rpc('XBMC.GetInfoLabels', {'labels': expressions})

    def label(expression):
        return labels([expression])[expression]

    def boolean(expression):
        return session.rpc('XBMC.GetInfoBooleans', {'booleans': [expression]})[expression]

    def receiver():
        expressions = ['Container(99950).ListItem.Property(base_label)',
                       'Container(99950).ListItem.Title', 'Container(99950).ListItem.Property(tmdb_id)',
                       'Window(Home).Property(TMDbHelper.monitor.tmdb_id)']
        expressions += ['Container(99950).ListItem.Property(Provider.' + str(i) + '.Icon)' for i in range(1, 9)]
        return labels(expressions)

    try:
        tree = ET.Element('favourites')
        ET.SubElement(tree, 'favourite', {'name': 'TMDb current details 603'}).text = 'ActivateWindow(Videos,"' + details_url + '",return)'
        ET.ElementTree(tree).write(favourites, encoding='utf-8', xml_declaration=True)
        session.start()
        report['pid'] = session.process.pid
        details = session.rpc('Addons.GetAddonDetails', {'addonid': 'plugin.video.themoviedb.helper', 'properties': ['version', 'enabled']})['addon']
        report['provider'] = details
        if details['version'] != '6.21.5' or not details['enabled']:
            raise RuntimeError('Current unmodified provider is not enabled')
        session.wait(lambda: boolean('Skin.HasSetting(TMDbHelper.Service)'))
        if label('Skin.String(TMDbHelper.MonitorContainer)') != '99950':
            raise RuntimeError('Wrong receiver selector')
        session.rpc('GUI.ActivateWindow', {'window': 'videos', 'parameters': [details_url]})
        session.wait(lambda: label('Container.NumItems') not in ('', '0'), seconds=40)
        if label('ListItem.Label') == '..':
            session.rpc('Input.Down')
        session.wait(lambda: label('ListItem.UniqueID(tmdb)') == '603', seconds=40)
        report['selected_item'] = labels(['ListItem.Label', 'ListItem.DBType', 'ListItem.UniqueID(tmdb)'])
        session.wait(lambda: label('Container(99950).ListItem.Property(base_label)') != '', seconds=40)
        case = {'name': 'video_details_receiver', 'receiver': receiver(),
                'receiver_visible': boolean('Control.IsVisible(99950)')}
        report['cases'].append(case)
        icons = [value for key, value in case['receiver'].items() if '.Icon)' in key and value]
        report['received_icon_count'] = len(icons)
        report['online_icon_delivery_proven'] = bool(icons)
        session.client.send_action('Container.SetViewMode(503)')
        time.sleep(2)
        shot = repo / 'results/kodi22_runtime/tmdb_current_video_receiver.png'
        previous = shot.stat().st_mtime_ns if shot.exists() else None
        session.client.send_action('TakeScreenshot("' + shot.as_posix() + '")')
        session.wait(lambda: shot.exists() and shot.stat().st_mtime_ns != previous)
        case['screenshot'] = shot.name
        for local in (False, True):
            session.rpc('GUI.ActivateWindow', {'window': 'home'})
            session.client.send_action(('Skin.SetBool' if local else 'Skin.Reset') + '(TMDbHelper.UseLocalWidgetContainer)')
            session.wait(lambda: boolean('Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)') == local)
            session.rpc('GUI.ActivateWindow', {'window': 'favouritesbrowser'})
            session.wait(lambda: boolean('Window.IsActive(favouritesbrowser)'))
            session.wait(lambda: label('Window(Home).Property(TMDbHelper.WidgetContainer)') == '0')
            config = session.work / ('poller-local.json' if local else 'poller-global.json')
            result = session.work / ('poller-local-result.json' if local else 'poller-global-result.json')
            config.write_text(json.dumps({'module_paths': module_paths, 'result': str(result)}), encoding='utf-8')
            session.run_script(Path(__file__), config)
            session.wait(result.exists)
            observed = json.loads(result.read_text(encoding='utf-8'))
            if not observed['passed']:
                report['poller_failure'] = observed
                raise RuntimeError('Original native Poller check failed')
            session.wait(lambda: label('Container(99950).ListItem.Property(base_label)') != 'The Matrix')
            case = {'name': 'favourites_local' if local else 'favourites_global', 'poller': observed,
                    'selected_item': labels(['ListItem.Label', 'ListItem.DBType', 'ListItem.UniqueID(tmdb)']),
                    'receiver': receiver()}
            if case['receiver']['Container(99950).ListItem.Property(base_label)'] != case['selected_item']['ListItem.Label']:
                raise RuntimeError('Receiver does not match current favourite')
            if any(value for key, value in case['receiver'].items() if '.Icon)' in key):
                raise RuntimeError('Previous movie icons remain on untyped favourite')
            session.rpc('GUI.ActivateWindow', {'window': 'home'})
            session.wait(lambda: label('Window(Home).Property(TMDbHelper.WidgetContainer)') == '')
            report['cases'].append(case)
        report['passed'] = True
    except Exception as exc:
        report.update(failure=repr(exc), trace=traceback.format_exc())
        if session.process and session.process.poll() is None:
            try:
                report['failure_context'] = labels(['System.CurrentWindow', 'Container.NumItems', 'ListItem.Label', 'ListItem.DBType', 'ListItem.UniqueID(tmdb)'])
                report['receiver_at_failure'] = receiver()
            except Exception:
                pass
    finally:
        report['cleanup'] = session.close()
        if old_favourites is None:
            favourites.unlink(missing_ok=True)
        else:
            favourites.write_bytes(old_favourites)
        report['cleanup'].update(favourites_restored=(favourites.read_bytes() == old_favourites if old_favourites is not None else not favourites.exists()),
                                 addon_source_files_unchanged=before == fingerprints())
        report['limits'] = ['No playback, Disney+ or account-authenticated provider test.',
                            'Favourites SDK inspection uses original Poller with actual Kodi API; no addon monkeypatch.',
                            'Non-empty online icons are reported separately; passing receiver/poller checks alone does not prove them.']
        (repo / 'results/kodi22_runtime/tmdb_current_native_checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('passed', 'cases', 'cleanup')}, ensure_ascii=True))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--inside-kodi':
        inspect_poller(sys.argv[2])
    else:
        main()
