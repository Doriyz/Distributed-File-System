
import datetime
import time as tm

def timeTransfer(t):
    # input:time.time()
    # output: string
    t_obj = datetime.datetime.fromtimestamp(t)
    return t_obj.strftime('%Y-%m-%d %H:%M:%S')

now = tm.time()
print(timeTransfer(now))