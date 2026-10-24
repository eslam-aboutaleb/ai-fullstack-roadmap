"""Start a disposable native Kafka broker from a verified, extracted distribution.

Use --download for the checksum-pinned official distribution, or --distribution
for an already verified extraction. This never modifies a shared cluster. Java 17+ required.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import hashlib
import tarfile
import urllib.request
import os
import socket
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent


def port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));return sock.getsockname()[1]


def check(distribution):
    binary=Path(distribution).resolve()/'bin'
    assert (binary/'kafka-storage.sh').is_file(), 'Pass an extracted Apache Kafka distribution'
    broker_port,controller_port=port(),port()
    while broker_port==controller_port:controller_port=port()
    with TemporaryDirectory(prefix='roadmap-kafka-') as folder:
        temp=Path(folder);config=temp/'server.properties'
        config.write_text('\n'.join([
            'process.roles=broker,controller','node.id=1',
            f'controller.quorum.bootstrap.servers=127.0.0.1:{controller_port}',
            f'listeners=PLAINTEXT://127.0.0.1:{broker_port},CONTROLLER://127.0.0.1:{controller_port}',
            f'advertised.listeners=PLAINTEXT://127.0.0.1:{broker_port}',
            'controller.listener.names=CONTROLLER','listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT',
            'inter.broker.listener.name=PLAINTEXT',f'log.dirs={temp/"data"}',
            'offsets.topic.replication.factor=1','transaction.state.log.replication.factor=1',
            'transaction.state.log.min.isr=1','group.initial.rebalance.delay.ms=0']))
        env={**os.environ,'KAFKA_HEAP_OPTS':'-Xmx256m -Xms128m'}
        cluster=subprocess.check_output([str(binary/'kafka-storage.sh'),'random-uuid'],env=env,text=True,timeout=20).strip()
        subprocess.run([str(binary/'kafka-storage.sh'),'format','--standalone','-t',cluster,'-c',str(config)],env=env,check=True,capture_output=True,timeout=30)
        with (temp/'broker.log').open('w+') as log:
            process=subprocess.Popen([str(binary/'kafka-server-start.sh'),str(config)],env=env,stdout=log,stderr=subprocess.STDOUT)
            try:
                result=subprocess.run([sys.executable,str(ROOT/'labs/kafka_recovery.py'),'--bootstrap',f'127.0.0.1:{broker_port}'],capture_output=True,text=True,timeout=150)
                if result.returncode:
                    log.seek(0);print(log.read()[-6000:],file=sys.stderr)
                    raise RuntimeError(result.stderr)
                print(result.stdout.strip())
            finally:
                process.terminate()
                try:process.wait(timeout=15)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    options=parser.add_mutually_exclusive_group(required=True)
    options.add_argument('--distribution');options.add_argument('--download',action='store_true')
    args=parser.parse_args()
    if args.download:
        with TemporaryDirectory(prefix='roadmap-kafka-distribution-') as folder:
            archive_path=Path(folder)/'kafka.tgz'
            url='https://downloads.apache.org/kafka/4.3.1/kafka_2.13-4.3.1.tgz'
            expected='c7d7b2318cb51aa0c61d3246a51c349210073c5c9b754947ef965a439f2f939e8600f204e134a75ac31faf3829c9370960ef7c6a9886c8a1dbf0339a21f4c54c'
            with urllib.request.urlopen(url,timeout=60) as response, archive_path.open('wb') as output:
                while chunk:=response.read(1024*1024):output.write(chunk)
            if hashlib.sha512(archive_path.read_bytes()).hexdigest()!=expected:
                raise ValueError('Kafka distribution SHA-512 mismatch')
            with tarfile.open(archive_path) as archive:archive.extractall(folder,filter='data')
            check(Path(folder)/'kafka_2.13-4.3.1')
    else:
        check(args.distribution)
