#!/usr/bin/env python3
"""Isolated functional checks; never touches live files or remote account."""
import json, os, pathlib, subprocess, sys, tempfile, unittest
P=pathlib.Path
SCRIPT=P(__file__).resolve().parents[1]/'scripts/manager.py'
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.base=P(self.tmp.name); self.env={**os.environ,'SKILL_MANAGER_HOME':str(self.base/'manager'),'HOME':str(self.base/'home'),'GIT_AUTHOR_NAME':'Skill Test','GIT_AUTHOR_EMAIL':'test@example.invalid','GIT_COMMITTER_NAME':'Skill Test','GIT_COMMITTER_EMAIL':'test@example.invalid'}; self.shared=self.base/'shared'; self.adapter=self.base/'adapter'; self.shared.mkdir(); self.adapter.mkdir(); self.env['PYTHONDONTWRITEBYTECODE']='1'
        # load manager directly, avoid recursive setup self-tests
        self.env['PYTHONPATH']=str(SCRIPT.parent)
        self.call("from manager import *; write(ROOT/'config.json',{'shared':str(P(os.environ['HOME']).parent/'shared'),'adapters':[str(P(os.environ['HOME']).parent/'adapter')]})")
    def call(self,code):
        r=subprocess.run([sys.executable,'-c',code],env=self.env,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stderr); return r.stdout
    def cli(self,*args):
        r=subprocess.run([sys.executable,str(SCRIPT),*args],env=self.env,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stderr); return json.loads(r.stdout)
    def fixture(self,n='sample',root=None,body='Return TEST_OK'):
        p=(root or self.base)/n; p.mkdir(parents=True); (p/'SKILL.md').write_text('---\nname: '+n+'\ndescription: Test fixture\n---\n'+body); return p
    def test_install_and_share(self):
        p=self.fixture(); out=self.cli('install',str(p),'--approved'); self.assertEqual(out['records'][0]['state'],'active'); self.assertTrue((self.shared/'sample').is_symlink()); self.assertEqual((self.shared/'sample').resolve(),(self.adapter/'sample').resolve()); self.assertIn('TEST_OK',(self.adapter/'sample'/'SKILL.md').read_text()); self.assertEqual([x['event'] for x in out['events']],['install-precheck','collected','install-postcheck'])
    def test_catalog(self):
        self.cli('install',str(self.fixture('first')),'--approved')
        out=self.cli('install',str(self.fixture('second')),'--approved')['catalog']
        self.assertEqual(out['total'],2); self.assertEqual(out['new'],1)
        self.assertEqual([r['name'] for r in out['rows'] if r['new']],['second'])
        out=self.cli('install',str(self.base/'second'),'--approved')['catalog']; self.assertEqual(out['new'],0)
        self.cli('disable','first'); out=self.cli('catalog')['catalog']; self.assertEqual(out['active'],1)
        self.fixture('pending',root=self.shared); out=self.cli('catalog')['catalog']; self.assertTrue(any(r['name']=='pending' and r['state']=='unmanaged' for r in out['rows']))
    def test_duplicate_and_conflict(self):
        p=self.fixture(); self.cli('install',str(p),'--approved'); out=self.cli('install',str(p),'--approved'); self.assertEqual(len(out['records']),1); (p/'SKILL.md').write_text('modified'); out=self.cli('install',str(p),'--approved'); self.assertTrue(any(x['event']=='conflict' for x in out['events'])); self.assertIn('TEST_OK',(self.shared/'sample'/'SKILL.md').read_text())
    def test_scan_and_adopt(self):
        p=self.fixture(root=self.shared); out=self.cli('sync'); self.assertEqual(out['records'],[]); out=self.cli('sync','--approve-import'); self.assertEqual(len(out['records']),1); self.assertTrue(p.is_symlink()); self.assertEqual(p.resolve(),(self.adapter/'sample').resolve())
    def test_delete_restore_tombstone(self):
        p=self.fixture(); self.cli('install',str(p),'--approved'); self.cli('delete','sample'); self.assertFalse((self.shared/'sample').exists()); out=self.cli('install',str(p),'--approved'); self.assertEqual(out['records'][0]['state'],'deleted'); self.cli('restore','sample'); self.assertTrue((self.shared/'sample').exists())
    def test_sensitive(self):
        p=self.fixture(); (p/'.env').write_text('TOKEN=test'); r=subprocess.run([sys.executable,str(SCRIPT),'install',str(p),'--approved'],env=self.env,capture_output=True,text=True); self.assertNotEqual(r.returncode,0); self.assertFalse((self.shared/'sample').exists())
    def test_project_isolation(self):
        p=self.fixture(root=self.base/'project'/'.agents/skills'); self.call("from manager import *; c=read(ROOT/'config.json',{}); c['projects']=[str(P(os.environ['HOME']).parent/'project')]; write(ROOT/'config.json',c)"); out=self.cli('sync','--approve-import'); self.assertEqual(out['records'],[]); self.assertTrue(any(x['event']=='project-local' for x in out['events']))
    def test_git_two_devices(self):
        remote=self.base/'remote.git'; subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True); self.call("from manager import *; import shutil; p=ROOT/'library'; run('git','clone',str(P(os.environ['HOME']).parent/'remote.git'),str(p));")
        p=self.fixture(); self.cli('install',str(p),'--approved'); self.env['SKILL_MANAGER_HOME']=str(self.base/'second'); self.call("from manager import *; ROOT.mkdir(); run('git','clone',str(P(os.environ['HOME']).parent/'remote.git'),str(ROOT/'library')); write(ROOT/'config.json',{'shared':str(P(os.environ['HOME']).parent/'shared2')})"); out=self.cli('sync'); self.assertEqual(len(out['records']),1); self.assertTrue((self.base/'shared2'/'sample').is_symlink()); self.cli('delete','sample'); self.env['SKILL_MANAGER_HOME']=str(self.base/'manager'); self.cli('sync'); self.assertFalse((self.shared/'sample').exists())
if __name__=='__main__':
    import io
    stream=io.StringIO(); suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests); result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite); print(json.dumps({'mode':'isolated','total':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors),'failed':len(result.failures)+len(result.errors),'details':stream.getvalue(),'unverified':['real Agent discovery and invocation','native installation hooks','actual GitHub account','cross-device scheduler','cloud account integration']},ensure_ascii=False,indent=2)); sys.exit(not result.wasSuccessful())
