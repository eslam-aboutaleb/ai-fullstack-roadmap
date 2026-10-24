"""Test the optional API against a new disposable PostgreSQL cluster, never a user DSN."""
from pathlib import Path
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent


def binary(name):
    found=shutil.which(name)
    if found:return found
    candidates=sorted(Path('/usr/lib/postgresql').glob('*/bin/'+name),reverse=True)
    if candidates:return str(candidates[0])
    raise RuntimeError('Install local PostgreSQL 16+ to run the integration pilot')


def check():
    with tempfile.TemporaryDirectory(prefix='roadmap-pg-',dir='/tmp' if os.name!='nt' else None) as folder:
        directory=Path(folder);data=directory/'data';log=directory/'server.log'
        with socket.socket() as connection:
            connection.bind(('127.0.0.1',0));port=connection.getsockname()[1]
        subprocess.run([binary('initdb'),'-D',str(data),'-A','trust','-U','roadmap','--no-locale','-E','UTF8'],check=True,capture_output=True)
        options=f'-h 127.0.0.1 -p {port}' + (f' -k {folder}' if os.name!='nt' else '')
        subprocess.run([binary('pg_ctl'),'-D',str(data),'-l',str(log),'-o',options,'-w','start'],check=True,capture_output=True)
        try:
            env={**os.environ,'DATABASE_URL':f'postgresql://roadmap@127.0.0.1:{port}/postgres',
                 'DEMO_TOKEN_A':secrets.token_urlsafe(24),'DEMO_TOKEN_B':secrets.token_urlsafe(24)}
            subprocess.run([sys.executable,'-B',str(ROOT/'labs/transaction_api.py')],env=env,check=True,timeout=40)
            subprocess.run([sys.executable,'-B','-m','labs.fullstack_demo'],cwd=ROOT,env=env,check=True,timeout=40)
        finally:
            subprocess.run([binary('pg_ctl'),'-D',str(data),'-m','immediate','-w','stop'],check=True,capture_output=True)


if __name__=='__main__':check()
