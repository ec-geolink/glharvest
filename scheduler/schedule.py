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
print sched
@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every minute.')

@sched.scheduled_job('interval', hours=1)
def main_job():
    print('main_job()')
    jobs.main_job()

@sched.scheduled_job('interval', seconds=30)
def status_job():
    print('status_job()')
    jobs.status_job()

time.sleep(10)
sched.start()
