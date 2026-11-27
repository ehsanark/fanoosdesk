from pathlib import Path
import os
import tempfile,subprocess,shutil,sys
from defaults import render_defaults
root=Path.cwd()
commit='a7f2260203befb7e9c70b585219f0f0b5ca57703'
with tempfile.TemporaryDirectory(prefix='fanoos-upstream-') as td:
 source=Path(td)/'source';source.mkdir()
 def git(*args):subprocess.run(['git',*args],cwd=source,check=True)
 git('init');git('config','core.autocrlf','false');git('remote','add','origin','https://github.com/rustdesk/rustdesk.git')
 git('fetch','--depth','1','origin',commit);git('checkout','--detach','FETCH_HEAD')
 git('-c','core.autocrlf=false','submodule','update','--init','--depth','1')
 for p in source.iterdir():
  if p.name=='.git':continue
  if p.name=='.github':
   for child in p.iterdir():
    if child.name=='workflows':continue
    target=root/'.github'/child.name
    if child.is_dir():shutil.copytree(child,target,dirs_exist_ok=True)
    else:shutil.copy2(child,target)
  elif p.is_dir():
   shutil.copytree(p,root/p.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git'))
  else:shutil.copy2(p,root/p.name)
 subprocess.run(['git','apply','--check','build/fanoos.patch'],cwd=root,check=True)
 subprocess.run(['git','apply','build/fanoos.patch'],cwd=root,check=True)
 patch = render_defaults((root/'build/identity.patch').read_text(encoding='utf-8'))
 subprocess.run(['git','apply','--directory=libs/hbb_common','-'],input=patch.encode('utf-8'),cwd=root,check=True)
 (root/'flutter/assets').mkdir(exist_ok=True)
 for dest in ('flutter/assets/icon.png', 'res/128x128@2x.png'):
  shutil.copy2(root/'build/fanoos.png', root/dest)
 shutil.copy2(root/'build/fanoos.ico',root/'flutter/windows/runner/resources/app_icon.ico')
print('Loaded pinned RustDesk source with Fanoos Desk changes')


subprocess.run([sys.executable, 'build/redesign.py'], cwd=root, check=True)

subprocess.run(['git', 'apply', 'build/desktop-ui.patch'], cwd=root, check=True)
shutil.copytree(root/'build/fonts', root/'flutter/assets/fonts', dirs_exist_ok=True)
common = root/'flutter/lib/common.dart'
source = common.read_text(encoding='utf-8')
build_number = int(os.environ.get('GITHUB_RUN_NUMBER', '0'))
assert source.count('__FANOOS_BUILD_NUMBER__') == 1
common.write_text(source.replace('__FANOOS_BUILD_NUMBER__', str(build_number)), encoding='utf-8')
