import time
from datetime import datetime

# Get current time in seconds since the epoch
epoch_time = time.time()

# Convert seconds to a datetime object
time_obj = datetime.fromtimestamp(epoch_time)

# Use strftime() to format the datetime object as a string
time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
print(time_str)



from datetime import datetime

time_str = "2022-01-11 13:45:00"
time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

# you can then convert the time_obj to seconds again
epoch_time = time.mktime(time_obj.timetuple())

