"""Exercise the Colab dependency-restart boundary in real isolated interpreters."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


HARNESS = r'''
import ast, csv, json, os, platform, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

root, fixture, phase = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
notebook = json.loads((root/'notebooks/01_sar_water_mapping.ipynb').read_text())
cells = {cell['id']: cell['source'] for cell in notebook['cells']}
repo = fixture/'repo'
sys.path.insert(0, str(fixture/'dependencies'))
os.chdir(repo)
marker = fixture/'restart.json'
namespace = dict(Path=Path, datetime=datetime, timezone=timezone, json=json,
                 os=os, sys=sys, perf_counter=perf_counter)
timer = ast.parse(cells['sar-water-01'])
definitions = [node for node in timer.body if isinstance(node, ast.FunctionDef)]
exec(compile(ast.Module(body=definitions, type_ignores=[]), '<notebook timer>', 'exec'), namespace)
begin = namespace.get('begin_notebook_run')
assert begin is not None, 'Notebook must preserve the original clock across the dependency restart'
if phase == 'install':
    clock, started, stages, pending = begin(marker, perf_counter()-120)
else:
    saved = json.loads(marker.read_text())
    if phase == 'same-kernel':
        saved['kernel_pid'] = os.getpid()
        marker.write_text(json.dumps(saved))
        try: begin(marker, perf_counter())
        except RuntimeError as error: assert 'restart' in str(error).lower()
        else: raise AssertionError('Run All without a kernel restart must stop')
        assert marker.exists()
        sys.exit(0)
    clock, started, stages, pending = begin(marker, perf_counter())
    assert clock == saved['notebook_start']
    assert started == saved['started_utc']
    assert perf_counter()-clock >= 120
namespace.update(NOTEBOOK_START=clock, STARTED_UTC=started, STAGES=stages,
                 PENDING_RESTART=pending, RESTART_STATE_PATH=marker)
exec(compile(cells['sar-water-03'], '<notebook config>', 'exec'), namespace)
namespace.update(REPO=repo, REPOSITORY='https://example.test/reviewed.git', REPO_REF='a'*40)
if phase != 'install':
    assert namespace['RUN_ID'] == saved['run_id']
    if phase == 'changed-source': namespace['REPO_REF']='b'*40
import numpy
assert numpy.__version__ == ('1.0' if phase == 'install' else '2.0')
calls=[]
def run(command, **kwargs):
    calls.append(command)
    if command[1:4] == ['-m','pip','install'] and '-r' in command:
        deps=fixture/'dependencies'
        (deps/'numpy/__init__.py').write_text("__version__='2.0'\ndef use_core():\n    from ._core import current\n    return current\n")
        (deps/'numpy/_core.py').write_text("current='fresh installed core'\n")
        (deps/'numpy-1.0.dist-info/METADATA').write_text('Name: numpy\nVersion: 2.0\n')
def check_output(command, **kwargs):
    if command[-3:]==['remote','get-url','origin']: return 'https://example.test/reviewed.git\n'
    if command[-2:]==['status','--porcelain']: return ''
    if 'rev-parse' in command: return 'a'*40+'\n'
    raise AssertionError(command)
namespace['subprocess']=SimpleNamespace(run=run, check_output=check_output)
try:
    exec(compile(cells['sar-water-04'], '<notebook setup>', 'exec'), namespace)
except RuntimeError as error:
    if phase == 'install':
        assert 'restart' in str(error).lower()
        assert marker.is_file()
        state=json.loads(marker.read_text())
        assert state['notebook_start']==clock
        assert state['run_id']==namespace['RUN_ID']
        assert len([c for c in calls if c[1:4]==['-m','pip','install']])==2
        try: numpy.use_core()
        except ImportError as mixed: assert 'legacy' in str(mixed)
        else: raise AssertionError('Fixture must expose the mixed old/new import failure')
    elif phase == 'changed-source':
        assert marker.exists()
        assert not any(c[1:4]==['-m','pip','install'] for c in calls)
    else: raise
else:
    assert phase == 'resume', 'Setup must stop before numerical imports when installed NumPy replaces loaded NumPy'
    from sar_water import data
    assert data.CHECKOUT_MARKER=='fresh installed core'
    assert not marker.exists()
    assert namespace['STAGES']['pre_restart_installation_seconds']>=0
    assert namespace['STAGES']['dependency_restart_wait_seconds']>=0
    assert namespace['RUNTIME_SETUP_EVIDENCE']['dependency_restart_count']==1
    assert namespace['RUNTIME_SETUP_EVIDENCE']['setup_pass_count']==2
    # The next independent Run All starts a fresh measurement.
    now=perf_counter()
    new_start, _, new_stages, new_pending=begin(marker, now)
    assert new_start==now and new_stages=={} and new_pending is None
assert not (repo/'data').exists(), 'No SAR acquisition may occur before dependency restart'
'''


def runtime_fixture(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();(repo/'.git').mkdir()
    (repo/'requirements-colab.txt').write_text('numpy==2.0\n')
    package=repo/'src/sar_water';package.mkdir(parents=True)
    (package/'__init__.py').write_text('')
    (package/'data.py').write_text('import numpy\nCHECKOUT_MARKER=numpy.use_core()\n')
    deps=tmp_path/'dependencies';(deps/'numpy').mkdir(parents=True)
    (deps/'numpy/__init__.py').write_text("__version__='1.0'\ndef use_core():\n    from ._core import legacy\n    return legacy\n")
    (deps/'numpy/_core.py').write_text("legacy='old core'\n")
    (deps/'numpy-1.0.dist-info').mkdir()
    (deps/'numpy-1.0.dist-info/METADATA').write_text('Name: numpy\nVersion: 1.0\n')
    return tmp_path


def run_phase(fixture, phase):
    root=Path(__file__).parents[1]
    result=subprocess.run([sys.executable,'-I','-S','-B','-c',HARNESS,str(root),str(fixture),phase],
                          capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr


@pytest.mark.parametrize('second_phase', ['resume','same-kernel','changed-source'])
def test_notebook_dependency_restart_preserves_clock_and_guards_resume(tmp_path, second_phase):
    fixture=runtime_fixture(tmp_path)
    run_phase(fixture,'install')
    run_phase(fixture,second_phase)
