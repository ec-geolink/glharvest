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
    q.enqueue(jobs.status)

@sched.scheduled_job('interval', minutes=1)
def queue_update_job():
    q.enqueue(jobs.update, timeout=600) # Timeout of 10min

@sched.scheduled_job('interval', hours=1)
def queue_export_job():
    q.enqueue(jobs.export)

@sched.scheduled_job('interval', minutes=1)
def print_jobs_job():
    sched.print_jobs()

# Wait a bit for Sesame to start
time.sleep(10)

# Queue the status job first. This creates the repository before any other
# jobs are run.
q.enqueue(jobs.status)

# Start the scheduler
sched.start()
