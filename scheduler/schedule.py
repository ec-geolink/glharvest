import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG)

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('/glharvest')
# from glharvest import jobs
import glharvest

conn = StrictRedis(host='redis', port='6379')
q = Queue(connection=conn)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    print('This job is run every 10 minutes.')

time.sleep(10)
sched.start()
