"""Native source-expression/provider checks; no actual PVR backend is simulated."""
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe","-NoProfile","-Command","@(Get-Process kodi -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-folder-content-",dir=root))
    media = work / "media-root"; folder = media / "folder"; folder.mkdir(parents=True)
    ordinary = media / "ordinary.avi"
    video = root / "portable_data/testmedia/skin-audit-video.avi"
    shutil.copy2(video,ordinary)
    for name, stamp in [("z_early.avi",1767225600),("a_late.avi",1767312000)]:
        p = folder / name; shutil.copy2(video,p); os.utime(p,(stamp,stamp))
    cases = [("ordinary_file",ordinary.as_posix(),False),("directory",folder.as_posix()+"/",True),("parent",media.as_posix()+"/",True),("ordinary_file_again",ordinary.as_posix(),False)]
    (work/"cases.json").write_text(json.dumps(cases),encoding="utf-8")
    rels = ("userdata/guisettings.xml","userdata/addon_data/skin.horizonzv/settings.xml")
    backups = {rel:(root/"portable_data"/rel).read_bytes() for rel in rels}
    database = root / "portable_data/userdata/Database"; db_backup = work/"database"; db_backup.mkdir()
    for pattern in ("MyVideos*.db*","MyMusic*.db*"):
        for p in database.glob(pattern):shutil.copy2(p,db_backup/p.name)
    xml = root / "portable_data/addons/skin.horizonzv/xml"
    for p in (repo/"xml").glob("*.xml"):shutil.copy2(p,xml/p.name)
    before = {}
    for filename,cid in (("View_Movie_302_3Panel.xml","303"),("Includes_PVR.xml","5000")):
        source = subprocess.check_output(["git","-c","safe.directory="+repo.as_posix(),"show","9a60d46:xml/"+filename])
        old = ET.fromstring(source).find(".//control[@id='"+cid+"']/content")
        new = ET.parse(repo/"xml"/filename).getroot().find(".//control[@id='"+cid+"']/content")
        before[cid] = (old,new)

    def control(parent,kind,values,cid=None):
        c = ET.SubElement(parent,"control",{"type":kind,**({"id":str(cid)} if cid else {})})
        for key,value in values.items():ET.SubElement(c,key).text=str(value)
        return c

    layout = work / "resources/skins/Default/1080i"; layout.mkdir(parents=True)
    for phase in ("before","after"):
        doc = ET.Element("window");ET.SubElement(doc,"views").text="50";ET.SubElement(doc,"defaultcontrol",{"always":"true"}).text="50"
        controls = ET.SubElement(doc,"controls")
        control(controls,"label",dict(left=30,top=15,width=1850,height=60,font="font24",label="HorizonzV: folder directory inputs ("+phase+")"))
        main_list=control(controls,"list",dict(left=30,top=100,width=1800,height=220),50)
        ET.SubElement(main_list,"viewtype",{"label":"535"}).text="list"
        for tag in ("itemlayout","focusedlayout"):
            row=ET.SubElement(main_list,tag,{"width":"1800","height":"45"})
            control(row,"label",dict(width=1800,height=45,font="font16",textcolor="orange" if tag=="focusedlayout" else "white",label="$INFO[ListItem.Label]"))
        for cid,left in (("303",30),("5000",960)):
            content=before[cid][0 if phase=="before" else 1]
            control(controls,"label",dict(left=left,top=350,width=900,height=90,font="font16",label=content.text),int(cid)+10000)
            items=control(controls,"list",dict(left=left,top=470,width=900,height=350),cid)
            for tag in ("itemlayout","focusedlayout"):
                row=ET.SubElement(items,tag,{"width":"900","height":"55"})
                control(row,"label",dict(width=900,height=55,font="font16",label="$INFO[ListItem.Label]"))
            ET.SubElement(items,"content",content.attrib).text=content.text
        ET.ElementTree(doc).write(layout/(phase+".xml"),encoding="utf-8",xml_declaration=True)
    script=work/"fixture.py"
    script.write_text('''import json,sys,xbmcgui
from pathlib import Path
ROOT=Path(__file__).parent
class Probe(xbmcgui.WindowXML):
 def onInit(self):
  items=[]
  for name,path,folder in json.loads((ROOT/'cases.json').read_text()):
   item=xbmcgui.ListItem(label='..' if name=='parent' else name,path=path,offscreen=True)
   item.setIsFolder(folder)
   item.setProperty('case',name)
   items.append(item)
  self.addItems(items)
  (ROOT/(sys.argv[1]+'_bound')).write_text('ready')
 def onAction(self,action):
  if action.getId() in (9,10,92,216): self.close()
w=Probe(sys.argv[1]+'.xml',str(ROOT),'Default','1080i',True)
w.doModal()
del w
''',encoding="utf-8")
    sys.path.insert(0,str(root));sys.path.insert(0,str(root.parent/"horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method,params=None):
        value=raw_rpc(method,params);assert "result" in value,value;return value["result"]
    def label(expr):return rpc("XBMC.GetInfoLabels",{"labels":[expr]})[expr]
    def boolean(expr):return rpc("XBMC.GetInfoBooleans",{"booleans":[expr]})[expr]
    def wait(probe,expected):
        for _ in range(120):
            actual=probe()
            if actual==expected:return actual
            time.sleep(.1)
        raise AssertionError({"expected":expected,"actual":actual})
    def log():return (root/"portable_data/kodi.log").read_text(encoding="utf-8",errors="replace").splitlines()
    report={"scope":"Copied production content expressions/attributes in always-visible native probe providers. This forces provider evaluation independently of production parent visibility; not a full 3-panel/PVR layout or backend test.","rows":[]}
    process=client=None;failure=None
    try:
        config=ET.parse(root/"portable_data/userdata/guisettings.xml")
        for setting,value in (("input.enablemouse","false"),("debug.showloginfo","false"),("window.width","1280"),("window.height","720")):
            node=config.getroot().find("setting[@id='"+setting+"']");assert node is not None;node.text=value;node.attrib.pop("default",None)
        config.write(root/"portable_data/userdata/guisettings.xml",encoding="utf-8",xml_declaration=True)
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=1
        process=subprocess.Popen([str(root/"kodi.exe"),"-p","-w"],cwd=root,startupinfo=startup);report["pid"]=process.pid
        for _ in range(60):
            try:rpc("JSONRPC.Ping");break
            except Exception:assert process.poll() is None;time.sleep(.3)
        client=XBMCClient(name="HorizonzV folder directory guards",uid=secrets.randbits(32));client.connect(port=9777);time.sleep(.2)
        for phase in ("before","after"):
            offset=len(log());client.send_action('RunScript("'+script.as_posix()+'",'+phase+')')
            wait(lambda:(work/(phase+'_bound')).exists(),True)
            client.send_action("Container.SetViewMode(50)");client.send_action("Control.SetFocus(50)");time.sleep(.2)
            wait(lambda:label("Container(50).NumItems"),"4")
            for name,path,is_folder in cases:
                for _ in range(8):
                    if label("ListItem.Property(case)")==name:break
                    rpc("Input.Down");time.sleep(.15)
                wait(lambda:label("ListItem.Property(case)"),name)
                sources={cid:label("Control.GetLabel("+str(int(cid)+10000)+")") for cid in ("303","5000")}
                expected=path if phase=="before" or name=="directory" else ""
                assert all(v.replace('\\','/')==expected for v in sources.values()),sources
                assert boolean("ListItem.IsFolder")==is_folder
                assert boolean("ListItem.IsParentFolder")==(name=="parent")
                if name=="directory":
                    for cid in ("303","5000"):wait(lambda:label("Container("+cid+").NumItems"),"2")
                time.sleep(.3)
                pvr_items=[label("Container(5000).ListItemAbsolute("+str(i)+").Label") for i in range(int(label("Container(5000).NumItems") or 0))]
                report["rows"].append({"phase":phase,"case":name,"is_folder":is_folder,"is_parent":name=="parent","sources":sources,"pvr_items":pvr_items})
                if name=="directory":
                    assert pvr_items==["z_early.avi","a_late.avi"],pvr_items
                    shot=repo/"results/kodi22_runtime"/("folder_content_"+phase+".png");shot.unlink(missing_ok=True);client.send_action('TakeScreenshot("'+shot.as_posix()+'")');wait(shot.exists,True)
            rpc("Input.Back");wait(lambda:label("ListItem.Property(case)")=="ordinary_file_again",False);time.sleep(.3)
            report[phase+"_errors"]=[s for s in log()[offset:] if " error " in s.lower() or "fatal" in s.lower()]
        assert report['before_errors'] and not report['after_errors'],report
    except Exception as exc:
        failure=repr(exc);report['failure']=failure;report['failure_trace']=traceback.format_exc()
    finally:
        if process:
            try:raw_rpc("Input.Back");time.sleep(.2);raw_rpc("Application.Quit");process.wait(timeout=20)
            except Exception:pass
        if client:client.close()
        exited=process is None or process.poll() is not None;cleanup={"process_exited":exited}
        if exited:
            for rel,data in backups.items():(root/"portable_data"/rel).write_bytes(data)
            cleanup['profile_restored']=all((root/"portable_data"/rel).read_bytes()==data for rel,data in backups.items())
            for pattern in ("MyVideos*.db*","MyMusic*.db*"):
                for p in database.glob(pattern):assert p.resolve().parent==database.resolve();p.unlink()
            for p in db_backup.iterdir():shutil.copy2(p,database/p.name)
            cleanup['media_databases_restored']=all(p.read_bytes()==(database/p.name).read_bytes() for p in db_backup.iterdir())
            cleanup['test_skin_xml_match_production']={p.name:p.read_bytes() for p in xml.glob('*.xml')}=={p.name:p.read_bytes() for p in (repo/'xml').glob('*.xml')}
        report['cleanup']=cleanup
        (repo/'results/kodi22_runtime/folder_content_checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({"failure":failure,"rows":report['rows'],"before_errors":report.get('before_errors'),"after_errors":report.get('after_errors'),"cleanup":cleanup},ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__=='__main__':sys.exit(main())
