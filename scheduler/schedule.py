import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG)

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler

from glharvest import jobs

conn = StrictRedis(host='redis', port='6379')
q = Queue(connection=conn)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def queue_status_job():
    q.enqueue('glharvest.jobs.status')

@sched.scheduled_job('interval', hours=1)
def queue_update_job():
    q.enqueue('glharvest.jobs.update', timeout=600) # Timeout of 10min

@sched.scheduled_job('interval', hours=1)
def queue_export_job():
    q.enqueue('glharvest.jobs.export')

# Queue the status job syncrhonously so the test repo is created
# This is a workaround to a bug in Sesame that lets you create two repositories
# with the same ID which puts the database into an unusable state

time.sleep(10)
q.enqueue('glharvest.jobs.status')
q.enqueue('glharvest.jobs.update')

# Start the scheduler
sched.start()
