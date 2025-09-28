import time
from datetime import datetime


class Times:
    localtime = lambda:datetime.now()
    timestamp = lambda:int(time.time())
    timestr = lambda:datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]


class WebIP:
    HOST = "0.0.0.0"
    PORT = 5016

