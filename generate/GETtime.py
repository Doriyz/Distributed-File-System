
import os
import time
 
filename = './file.txt'  # 当前路径
filemt = time.localtime(os.stat(filename).st_mtime)
print(time.strftime("%Y-%m-%d %H:%M:%S", filemt))



 
if __name__ == '__main__':
    f = './file.txt'
    mtime = time.ctime(os.path.getmtime(f)) # modified time
    print(mtime)