#!/usr/bin/env python3
"""Local-first SkillHub. Python 3.9+, Git optional for local-only mode."""
import argparse, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time, uuid, plistlib
from contextlib import contextmanager
from datetime import datetime, timezone
P=pathlib.Path
HOME=P.home()
ROOT=P(os.environ.get('SKILL_MANAGER_HOME',str(HOME/'.skill-manager'))).expanduser().resolve()
NAME=re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$')
def now(): return datetime.now(timezone.utc).isoformat()
def run(*args,cwd=None): return subprocess.run(args,cwd=cwd,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.strip()
def read(p,default): return json.loads(p.read_text()) if p.exists() else default
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True); q=p.with_name(p.name+'.tmp'); q.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n'); q.replace(p)
def valid(n):
    if not NAME.fullmatch(n) or n in ('.','..'): raise ValueError('Invalid skill name: '+n)
    return n
def entries(p):
    for f in sorted(p.rglob('*')):
        if '.git' not in f.relative_to(p).parts: yield f

def origin(p):
    if (p/'.git').exists():
        try:
            url=run('git','config','--get','remote.origin.url',cwd=p)
            if re.fullmatch(r'https://github\.com/[\w.-]+/[\w.-]+(?:\.git)?',url): return {'kind':'unknown','url':url,'evidence':'git-origin; authorship not confirmed'}
        except Exception: pass
    return {'kind':'unknown'}

def digest(p):
    h=hashlib.sha256()
    for f in entries(p):
        if f.is_symlink(): raise ValueError('Nested symlink: '+str(f))
        if f.is_file():
            rel=f.relative_to(p); h.update(str(rel).encode()+b'\0'); h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()
def inspect(p):
    if not (p/'SKILL.md').is_file(): raise ValueError('Missing SKILL.md: '+str(p))
    if p.is_symlink(): p=p.resolve(strict=True)
    for f in entries(p):
        if f.is_symlink() or (not f.is_file() and not f.is_dir()): raise ValueError('Unsafe file: '+str(f))
        if any(x.lower() in ('.git','.env','credentials.json','secrets.json','id_rsa','id_ed25519') or x.lower().endswith(('.pem','.key','.p12')) or x.lower().startswith('.env.') for x in f.relative_to(p).parts): raise ValueError('Sensitive file: '+str(f))
        if f.is_file():
            if f.stat().st_size>20_000_000: raise ValueError('Oversized file: '+str(f))
            b=f.read_bytes()
            if re.search(rb'-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16}',b): raise ValueError('Possible credential: '+str(f))
    return digest(p)
@contextmanager
def lock():
    ROOT.mkdir(parents=True,exist_ok=True); p=ROOT/'lock'
    try: p.mkdir()
    except FileExistsError: raise RuntimeError('Another operation active or stale lock: '+str(p))
    try: yield
    finally: p.rmdir()
class Manager:
    def __init__(self):
        self.cfg=read(ROOT/'config.json',{}); self.repo=ROOT/'library'; self.shared=P(self.cfg.get('shared',str(HOME/'.agents/skills'))).expanduser(); self.meta=self.repo/'records'; self.repo.mkdir(parents=True,exist_ok=True); self.meta.mkdir(exist_ok=True); (self.repo/'skills').mkdir(exist_ok=True); self.shared.mkdir(parents=True,exist_ok=True); self.events=[]
    def log(self,kind,**kw):
        e={'time':now(),'event':kind,**kw}; self.events.append(e)
        with (ROOT/'events.jsonl').open('a') as f: f.write(json.dumps(e,ensure_ascii=False)+'\n')
    def records(self):
        out={}
        for p in self.meta.glob('*.json'):
            r=read(p,{}); n=valid(p.stem)
            if r.get('name')!=n or r.get('state') not in ('active','disabled','deleted') or not re.fullmatch(r'[a-f0-9]{64}',r.get('hash','')): raise ValueError('Invalid record: '+n)
            out[n]=r
        return out
    def save(self,r): write(self.meta/(valid(r['name'])+'.json'),r)
    def target(self,n): return self.repo/'skills'/valid(n)
    def pull(self):
        # v0.4 is deliberately local-only, including for existing Git libraries.
        return
    def push(self):
        return
    def collect(self,p,scope='global',project=None,approved=False):
        p=P(p); n=valid(p.name); h=inspect(p); r=self.records().get(n); dest=self.target(n)
        if scope!='global':
            self.log('project-local',name=n,path=str(p),project=project); return 'local-only'
        if r and r['state']!='active': self.log('blocked-tombstone',name=n); return 'deleted-or-disabled'
        if r and r['hash']==h: return 'duplicate'
        if r: self.log('conflict',name=n,path=str(p),hash=h); return 'conflict'
        if not approved: self.log('pending-review',name=n,path=str(p)); return 'pending-review'
        if dest.exists(): raise RuntimeError('Unindexed destination: '+str(dest))
        dest.parent.mkdir(parents=True,exist_ok=True); shutil.copytree(p.resolve(),dest,ignore=shutil.ignore_patterns('.git'))
        self.save({'name':n,'hash':h,'scope':scope,'state':'active','first_seen':now(),'updated':now(),'source':'local-import','origin':origin(p)})
        self.log('collected',name=n,hash=h); return 'added'
    def expose(self):
        for n,r in self.records().items():
            dest=self.target(n); link=self.shared/n
            if r['state']!='active':
                if link.is_symlink() and link.resolve()==dest.resolve(): link.unlink()
                continue
            if not dest.is_dir() or inspect(dest)!=r['hash']: raise RuntimeError('Library integrity failure: '+n)
            if link.is_symlink() and link.resolve()==dest.resolve(): continue
            if link.exists() or link.is_symlink():
                self.log('existing-local',name=n,path=str(link)); continue
            try: link.symlink_to(dest,target_is_directory=True)
            except OSError as e: self.log('link-blocked',name=n,error=str(e))
        for path in self.cfg.get('adapters',[]):
            root=P(path).expanduser()
            if root.resolve()==self.shared.resolve(): continue
            if not root.is_dir(): self.log('adapter-unavailable',path=str(root)); continue
            for n,r in self.records().items():
                link=root/n; dest=self.target(n)
                if link.is_symlink() and link.resolve()==dest.resolve():
                    if r['state']!='active': link.unlink()
                elif r['state']=='active' and not link.exists() and not link.is_symlink():
                    try: link.symlink_to(dest,target_is_directory=True)
                    except OSError as e: self.log('link-blocked',name=n,error=str(e))
    def adopt(self,p):
        n=p.name; dest=self.target(n); r=self.records().get(n)
        if not r or r['state']!='active' or digest(p)!=r['hash']: return
        if p.resolve()==dest.resolve(): return
        backup=ROOT/'backups'/(n+'-'+uuid.uuid4().hex); backup.parent.mkdir(exist_ok=True)
        # rename within filesystem where possible; never remove original before link succeeds
        try: p.rename(backup)
        except OSError as e: self.log('adopt-blocked',name=n,error=str(e)); return
        try: p.symlink_to(dest,target_is_directory=True)
        except OSError as e: backup.rename(p); self.log('adopt-blocked',name=n,error=str(e)); return
        self.log('adopted',name=n,backup=str(backup))
    def scan(self,approved=False):
        for root in [self.shared,*map(P,self.cfg.get('adapters',[]))]:
            if not root.is_dir(): continue
            for p in sorted(root.iterdir()):
                if not (p/'SKILL.md').is_file(): continue
                if p.is_symlink() or p.name in ('skillhub','skill-manager'): continue # never ingest unknown link targets or manager itself
                try:
                    result=self.collect(p,approved=approved)
                    if approved and p.name not in ('skillhub','skill-manager') and result in ('added','duplicate'): self.adopt(p)
                except (ValueError,OSError) as e: self.log('scan-blocked',path=str(p),error=str(e))
        for path in self.cfg.get('projects',[]):
            root=P(path).expanduser()
            for folder in (root/'.agents/skills',root/'.codex/skills',root/'.claude/skills'):
                if folder.is_dir():
                    for p in folder.iterdir():
                        if (p/'SKILL.md').is_file(): self.log('project-local',name=p.name,path=str(p),project=str(root))
    def sync(self,approved=False):
        self.pull(); self.scan(approved); self.expose(); self.push()
    def install(self,src,kind='unknown',url=None):
        self.pull(); self.log('install-precheck',source=str(src)); result=self.collect(P(src),approved=True);
        if result=='added' and (kind!='unknown' or url): self.mark_origin(P(src).name,kind,url)
        self.expose(); self.push(); self.log('install-postcheck',result=result); return result
    def mark_origin(self,n,kind,url=None):
        if url and not re.fullmatch(r'https://[\w.-]+/[\w./-]+',url): raise ValueError('Use a public source URL without credentials or query')
        r=self.records()[valid(n)]; r['origin']={'kind':kind,'url':url,'evidence':'user or installation workflow confirmed'}; self.save(r)
    def state(self,n,state):
        if n in ('skillhub','skill-manager'): raise ValueError('Manage SkillHub itself manually')
        self.pull(); r=self.records()[valid(n)]; r.update(state=state,updated=now()); self.save(r); self.expose(); self.push(); self.log('state',name=n,state=state)
    def catalog(self):
        """Local inventory, not a claim of native Agent discovery."""
        rows=[]; records=self.records(); new={e['name'] for e in self.events if e['event']=='collected'}
        for n,r in sorted(records.items()):
            rows.append({'name':n,'scope':'global','state':r['state'],'new':n in new,'first_seen':r.get('first_seen'),'origin':r.get('origin',{'kind':'unknown'})})
        seen=set()
        roots=[(self.shared,'global',None)]+[(P(x).expanduser(),'global',None) for x in self.cfg.get('adapters',[])]
        for x in self.cfg.get('projects',[]):
            root=P(x).expanduser()
            roots.extend((root/f,'project',str(root)) for f in ('.agents/skills','.codex/skills','.claude/skills'))
        for root,scope,project in roots:
            if not root.is_dir(): continue
            for p in sorted(root.iterdir()):
                if not (p/'SKILL.md').is_file(): continue
                if scope=='global' and p.name in records and p.resolve()==self.target(p.name).resolve(): continue
                key=(scope,project,p.name,str(p.resolve()))
                if key in seen: continue
                seen.add(key)
                rows.append({'name':p.name,'scope':scope,'project':project,'state':'local-only' if scope=='project' else 'manager' if p.name=='skill-manager' else 'unmanaged','new':False,'first_seen':None,'origin':origin(p)})
        return {'rows':rows,'total':len(rows),'active':sum(r['state'] in ('active','local-only','manager','unmanaged') for r in rows),'new':sum(r['new'] for r in rows),'coverage':'managed library and configured local roots only'}
    def status(self): return {'library':str(self.repo),'shared':str(self.shared),'records':list(self.records().values()),'adapters':self.cfg.get('adapters',[]),'projects':self.cfg.get('projects',[]),'events':self.events,'catalog':self.catalog()}
def setup(a):
    cfg=read(ROOT/'config.json',{})
    if a.shared: cfg['shared']=str(P(a.shared).expanduser().resolve())
    candidates=[HOME/'.codex/skills',HOME/'.claude/skills',HOME/'.dsh/skills',HOME/'.zcode/skills']
    cfg['adapters']=sorted(set(cfg.get('adapters',[])+[str(P(x).expanduser().resolve()) for x in a.adapter]+[str(x) for x in candidates if x.is_dir()]))
    cfg['projects']=sorted(set(cfg.get('projects',[])+[str(P(x).expanduser().resolve()) for x in a.project]))
    if a.remote:
        raise ValueError('v0.4 is local-only; remote setup is unavailable')
    write(ROOT/'config.json',cfg); m=Manager(); m.sync(a.approve_import); return m.status()
def schedule(approved):
    if sys.platform=='win32':
        stable=ROOT/'runtime'; stable.mkdir(exist_ok=True); script=stable/'manager.py'; shutil.copy2(P(__file__).resolve(),script)
        # Task invokes pending-review scan only; no standing upload approval.
        command=subprocess.list2cmdline([sys.executable,str(script),'sync'])
        try:
            run('schtasks','/Create','/TN','SkillHub-Sync','/SC','MINUTE','/MO','5','/TR',command,'/IT','/F')
            return {'state':'registered','interval_seconds':300,'note':'Verify task execution on this device'}
        except subprocess.CalledProcessError as e: return {'state':'failed','reason':e.stderr}
    if sys.platform!='darwin': return {'state':'unsupported','reason':'Automatic scheduler in V1 is macOS only; use OS scheduler manually on other systems'}
    label='local.skill-manager.sync'; folder=HOME/'Library/LaunchAgents'; folder.mkdir(parents=True,exist_ok=True); p=folder/(label+'.plist')
    if p.exists(): return {'state':'existing','path':str(p),'note':'Existing schedule retained; inspect if configuration changed'}
    # preserve a stable script location independent of the downloaded archive
    stable=ROOT/'runtime'; stable.mkdir(exist_ok=True); script=stable/'manager.py'; shutil.copy2(P(__file__).resolve(),script)
    args=[sys.executable,str(script),'sync']
    data={'Label':label,'ProgramArguments':args,'StartInterval':300,'RunAtLoad':True,'EnvironmentVariables':{'SKILL_MANAGER_HOME':str(ROOT),'PATH':os.environ.get('PATH','/usr/bin:/bin')},'StandardOutPath':str(ROOT/'scheduler.out'),'StandardErrorPath':str(ROOT/'scheduler.err')}
    with p.open('wb') as f: plistlib.dump(data,f)
    try: run('launchctl','bootstrap','gui/'+str(os.getuid()),str(p))
    except subprocess.CalledProcessError as e: p.unlink(missing_ok=True); return {'state':'failed','reason':e.stderr}
    return {'state':'registered','interval_seconds':300,'path':str(p)}
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('setup'); s.add_argument('--remote'); s.add_argument('--confirm-private',action='store_true'); s.add_argument('--schedule',action='store_true'); s.add_argument('--shared'); s.add_argument('--adapter',action='append',default=[]); s.add_argument('--project',action='append',default=[]); s.add_argument('--approve-import',action='store_true')
    s=sub.add_parser('sync'); s.add_argument('--approve-import',action='store_true')
    s=sub.add_parser('install'); s.add_argument('source'); s.add_argument('--approved',action='store_true',required=True); s.add_argument('--origin',choices=['self','third-party','modified','unknown'],default='unknown'); s.add_argument('--source-url')
    s=sub.add_parser('origin'); s.add_argument('name'); s.add_argument('kind',choices=['self','third-party','modified','unknown']); s.add_argument('--source-url')
    for c in ('disable','delete','restore'): sub.add_parser(c).add_argument('name')
    sub.add_parser('list'); sub.add_parser('catalog'); sub.add_parser('test'); a=p.parse_args()
    if a.cmd=='test': subprocess.run([sys.executable,str(P(__file__).resolve().parents[1]/'tests/self_test.py')],check=True); return
    with lock():
        if a.cmd=='setup': out=setup(a)
        else:
            m=Manager()
            if a.cmd=='sync': m.sync(a.approve_import)
            elif a.cmd=='install': m.install(a.source,a.origin,a.source_url)
            elif a.cmd=='origin': m.pull(); m.mark_origin(a.name,a.kind,a.source_url); m.push()
            elif a.cmd in ('disable','delete','restore'): m.state(a.name,{'disable':'disabled','delete':'deleted','restore':'active'}[a.cmd])
            out=m.status()
    if a.cmd=='setup':
        r=subprocess.run([sys.executable,str(P(__file__).resolve().parents[1]/'tests/self_test.py')],capture_output=True,text=True); out['self_test']=json.loads(r.stdout) if r.stdout else {'error':r.stderr};
        if r.returncode==0 and a.schedule:
            out['scheduler']=schedule(a.approve_import)
        print(json.dumps(out,ensure_ascii=False,indent=2)); sys.exit(r.returncode)
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try: main()
    except Exception as e: print(str(e),file=sys.stderr); sys.exit(1)
