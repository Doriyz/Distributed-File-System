import os
from os.path import isfile, join
# onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for file in os.listdir('./'):
    if(isfile(join('./', file))):
        print(file)