"""Real broker → durable SQLite projection with a process crash before offset commit.

Run against a disposable local Kafka broker with requirements-advanced.txt.
A single topic/partition and one worker are intentional limits, not an EOS claim.
"""
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import argparse
import json
import os
import sqlite3
import subprocess
import sys
import uuid

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from data_contract_pipeline import create_database, event, ingest


def worker(bootstrap, topic, group, path, total, crash=False):
    consumer = Consumer({'bootstrap.servers':bootstrap,'group.id':group,'enable.auto.commit':False,
                         'enable.auto.offset.store':False,'auto.offset.reset':'earliest','session.timeout.ms':6000})
    replayed = 0; deadline = monotonic()+40
    try:
        consumer.subscribe([topic])
        with closing(sqlite3.connect(path)) as db:
            while monotonic() < deadline:
                message = consumer.poll(0.5)
                if message is None:
                    continue
                if message.error():
                    raise RuntimeError(str(message.error()))
                assert message.topic() == topic and message.partition() == 0
                outcome = ingest(db, message.offset()+1, json.loads(message.value()))
                replayed += outcome == 'already-checkpointed'
                if crash:
                    # Real process exit after SQLite commit but before Kafka acknowledgment.
                    os._exit(73)
                consumer.commit(message=message, asynchronous=False)
                if message.offset()+1 == total:
                    return replayed
        raise TimeoutError('Kafka recovery worker did not reach the fixture end')
    finally:
        consumer.close()


def verify(bootstrap):
    identity = uuid.uuid4().hex
    topic, group = 'roadmap-recovery-'+identity, 'roadmap-worker-'+identity
    admin = AdminClient({'bootstrap.servers':bootstrap,'socket.timeout.ms':5000})
    # Readiness has an explicit deadline and creates only this exercise's unique topic.
    deadline = monotonic()+60
    while True:
        try:
            admin.list_topics(timeout=2)
            break
        except Exception:
            if monotonic() >= deadline:
                raise TimeoutError('Disposable Kafka broker never became ready')
            sleep(0.5)
    for future in admin.create_topics([NewTopic(topic,num_partitions=1,replication_factor=1)]).values():
        future.result(timeout=10)
    try:
        values = [event('first',1), event('new',3,schema=2,title='Schema two'), event('late',2),
                  event('delete',4,operation='delete'), event('stale-after-delete',3), {'schema':99}]
        errors=[]
        producer=Producer({'bootstrap.servers':bootstrap,'enable.idempotence':True,'message.timeout.ms':10000})
        for value in values:
            producer.produce(topic,partition=0,key='A/policy',value=json.dumps(value).encode(),
                             on_delivery=lambda error,_:errors.append(str(error)) if error else None)
        assert producer.flush(15) == 0 and not errors, errors
        with TemporaryDirectory(prefix='roadmap-kafka-destination-') as folder:
            path=Path(folder)/'projection.db'
            with closing(create_database()) as template, closing(sqlite3.connect(path)) as destination:
                template.backup(destination)
            command=[sys.executable,str(Path(__file__).resolve()),'--worker','--bootstrap',bootstrap,
                     '--topic',topic,'--group',group,'--database',str(path),'--total',str(len(values))]
            first=subprocess.run([*command,'--crash'],capture_output=True,text=True,timeout=50)
            assert first.returncode == 73, first.stderr
            with closing(sqlite3.connect(path)) as db:
                assert db.execute('SELECT offset FROM checkpoint').fetchone() == (1,)
                assert db.execute('SELECT count(*) FROM receipts').fetchone() == (1,)
            second=subprocess.run(command,capture_output=True,text=True,timeout=50)
            assert second.returncode == 0, second.stderr
            replayed=json.loads(second.stdout)['replayed']
            assert replayed >= 1, replayed
            with closing(sqlite3.connect(path)) as db:
                assert db.execute('SELECT offset FROM checkpoint').fetchone() == (6,)
                assert db.execute('SELECT revision,title,deleted FROM documents').fetchone() == (4,'',1)
                assert db.execute('SELECT count(*) FROM receipts').fetchone() == (5,)
                assert db.execute('SELECT count(*) FROM quarantine').fetchone() == (1,)
            print(json.dumps({'kafka_recovery':'pass','topic_partitions':1,'worker_processes':1,
                'crash_exit':73,'unacknowledged_replays':replayed,'checkpoint':6,
                'final_revision':4,'tombstone_preserved':True,'quarantined':1}))
    finally:
        for future in admin.delete_topics([topic],operation_timeout=5).values():
            future.result(timeout=10)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--bootstrap',default='127.0.0.1:9092')
    parser.add_argument('--worker',action='store_true');parser.add_argument('--crash',action='store_true')
    parser.add_argument('--topic');parser.add_argument('--group');parser.add_argument('--database');parser.add_argument('--total',type=int)
    args=parser.parse_args()
    if args.worker:
        print(json.dumps({'replayed':worker(args.bootstrap,args.topic,args.group,args.database,args.total,args.crash)}))
    else:
        verify(args.bootstrap)
