import time
from datetime import datetime



class TCP:
    HOST = "rpc_super.local"
    PORT = 4242
    

class Times:
    localtime = lambda:datetime.now()
    timestamp = lambda:int(time.time())
    timestr = lambda:datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
