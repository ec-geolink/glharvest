import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG)

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('/glharvest')
from glharvest import jobs

conn = StrictRedis(host='redis', port='6379')
q = Queue(connection=conn)

sched = BlockingScheduler()

# @sched.scheduled_job('interval', hours=1)
@sched.scheduled_job('interval', seconds=15)
def main_job():
    jobs.main_job()

@sched.scheduled_job('interval', seconds=10)
def status_job():
    jobs.status_job()

@sched.scheduled_job('interval', seconds=10)
def export_job():
    jobs.export_job()

# Wait for GraphDB
time.sleep(10)

# Run the status job syncrhonously so the test repo is created
# This is a workaround to a bug in Sesame that lets you create two repositories
# with the same ID which puts the database into an unusable state
jobs.status_job()
time.sleep(10)

sched.start()
