# Lock Server function：
# 1. record the file info and lock info (share or exclusive)
# 2. record the ACL (aceess control list) of each file
# 3. lock the file when client request
# 4. unlock the file when client release
# 5. communicate with tracker server to get the file list


import socket
import time
from datetime import datetime
from concurrent import futures
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import APIs.setting as setting

import grpc
import APIs.LockServer_pb2 as LS_pb2
import APIs.LockServer_pb2_grpc as LS_pb2_grpc
# from TrackerServer import TrackerServer_pb2 as TS_pb2
# from TrackerServer import TrackerServer_pb2_grpc as TS_pb2_grpc

import APIs.TrackerServer_pb2 as TS_pb2
import APIs.TrackerServer_pb2_grpc as TS_pb2_grpc

TrackerServer_PORT = setting.TrackerServer_PORT
TrackerServer_IP = setting.TrackerServer_IP
LockServer_PORT = setting.LockServer_PORT
LockServer_IP = setting.LockServer_IP




class ACL():
    # if a file is not in acl, then it is a global file for each user
    def __init__(self, user_id, read, write, delete):
        # read, write, delete is a boolean value
        self.user_id = user_id # if 0 then it is a group ACL
        self.read = read
        self.write = write
        self.delete = delete

class Lock():
    def __init__(self, lock_id, user_id, lock_type, lock_time):
        # lock_type: 0 for exclusive, 1 for share
        self.lock_id = lock_id
        self.user_id = user_id
        self.lock_type = lock_type
        self.lock_time = lock_time

class File():
    def __init__(self, file_name, file_path, group_id):
        self.file_name = file_name
        self.file_path = file_path
        self.group_id = group_id
        self.lock_info = []
        self.acl_info = []


class Group():
    def __init__(self, group_id):
        self.group_id = group_id
        self.file_info = []

    def add_file(self, file_name, file_path):
        self.file_info.append(File(file_name, file_path, self.group_id))

class Service(LS_pb2_grpc.LockServerServicer):
    def __init__(self):
        self.Group_INFO = []
        self.ROOT_PATH = './DATA/'
        self.FILE_NAME = 'file_info.txt'
        self.LOCK_NAME = 'lock_info.txt'
        self.ACL_NAME = 'acl_info.txt'
        if not os.path.exists(self.ROOT_PATH):
            os.mkdir(self.ROOT_PATH)
        print("[INIT] Lock Server is ready to serve.")

        # load the existing group and file from tracker server
        tracker_channel = grpc.insecure_channel(TrackerServer_IP + ':' + str(TrackerServer_PORT))
        self.tracker_stub = TS_pb2_grpc.TrackerServerStub(tracker_channel)
        # now we can call the function offered by tracker server in the storage server by stub
        print(f'[INIT] Connecting to Tracker Server successfully.')
        try:
            self.load_file_info_from_tracker()
        except Exception as e:
            print(f'[ERROR] Loading file info from Tracker Server failed.')
            print(e)
            exit(1)

       
    def load_file_info_from_tracker(self):   
        request = TS_pb2.GetFileListRequest()
        request.operation = "get"
        # response = self.tracker_stub.GetFileList(TS_pb2.GetFileListRequest(operation=""))
        response = self.tracker_stub.GetFileList(request)
        for group in response.groups:
            group_id = group.group_id
            newGroup = Group(group.group_id)
            for file in group.files:
                newGroup.add_file(file.file_name, file.file_path)
            self.Group_INFO.append(newGroup)
        print(f'[INIT] Loading group and file info from Tracker Server successfully.')
        self.update_group_info_file()
    

    def update_group_info_file(self):
        with open(self.ROOT_PATH + self.FILE_NAME, 'w') as f:
            f.write('GROUP_ID --- FILE_PATH --- FILE_NAME --- UPDATE_TIME\n')
            for i in range(len(self.Group_INFO)):
                for j in range(len(self.Group_INFO[i].file_info)):
                    f.write(f'{self.Group_INFO[i].group_id} - {self.Group_INFO[i].file_info[j].file_path} - {self.Group_INFO[i].file_info[j].file_name} \n')
        print(f'[INFO] Updating group info file successfully.')

    def update_lock_info_file(self):
        with open(self.ROOT_PATH + self.LOCK_NAME, 'w') as f:
            f.write('LOCK_ID --- USER_ID --- LOCK_TYPE --- LOCK_TIME --- FILE_PATH --- FILE_NAME\n')
            for i in range(len(self.Group_INFO)):
                for j in range(len(self.Group_INFO[i].file_info)):
                    for k in range(len(self.Group_INFO[i].file_info[j].lock_info)):
                        f.write(f'{self.Group_INFO[i].file_info[j].lock_info[k].lock_id} - {self.Group_INFO[i].file_info[j].lock_info[k].user_id} - {self.Group_INFO[i].file_info[j].lock_info[k].lock_type} - {self.Group_INFO[i].file_info[j].lock_info[k].lock_time} - {self.Group_INFO[i].file_info[j].file_path} - {self.Group_INFO[i].file_info[j].file_name}\n')
        print(f'[INFO] Updating lock info file successfully.')
    
    def update_acl_info_file(self):
        with open(self.ROOT_PATH + self.ACL_NAME, 'w') as f:
            f.write('USER_ID --- FILE_PATH --- FILE_NAME --- READ --- WRITE --- DELETE\n')
            for i in range(len(self.Group_INFO)):
                for j in range(len(self.Group_INFO[i].file_info)):
                    for k in range(len(self.Group_INFO[i].file_info[j].acl_info)):
                        f.write(f'{self.Group_INFO[i].file_info[j].acl_info[k].user_id} - {self.Group_INFO[i].file_info[j].file_path} - {self.Group_INFO[i].file_info[j].file_name} - {self.Group_INFO[i].file_info[j].acl_info[k].read} - {self.Group_INFO[i].file_info[j].acl_info[k].write} - {self.Group_INFO[i].file_info[j].acl_info[k].delete}\n')
        print(f'[INFO] Updating acl info file successfully.')

    


    ##### proto service #####
    def AddGroup(self, request, context):
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == request.group_id:
                print(f'[ERROR] Group {request.group_id} already exist.')
                return LS_pb2.AddGroupRequest(status=0)
        self.Group_INFO.append(Group(request.group_id))
        print(f'[INFO] Group {request.group_id} is added.')
        self.update_group_info_file()
        return LS_pb2.AddGroupRequest(status=1)
    
    def AddFile(self, request, context):
        group_id = request.group_id
        file_name = request.filename
        file_path = request.path
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == group_id:
                for j in range(len(self.Group_INFO[i].file_info)):
                    if(self.Group_INFO[i].file_info[j].file_name == file_name and self.Group_INFO[i].file_info[j].file_path == file_path):
                        print(f'[ERROR] File {file_name} already exist.')
                        return LS_pb2.AddFileResponse(status=0)
                        
                self.Group_INFO[i].file_info.append(File(file_name, file_path, group_id))
                print(f'[INFO] File {file_name} is added.')
                self.update_group_info_file()
                return LS_pb2.AddFileResponse(status=1)
        print(f'[INFO] Group {group_id} does not exist.')
        # add group
        self.Group_INFO.append(Group(group_id))
        print(f'[INFO] Group {group_id} is added.')
        # add file in group
        self.Group_INFO[len(self.Group_INFO)-1].file_info.append(File(file_name, file_path, group_id))
        print(f'[INFO] File {file_name} is added.')
        return LS_pb2.AddFileResponse(status=0)

    def AddACL(self, request, context):
        group_id = request.group_id
        file_name = request.file_name
        file_path = request.path
        user_id = request.user_id
        read = request.is_read
        write = request.is_write
        delete = request.is_delete
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == group_id:
                for j in range(len(self.Group_INFO[i].file_info)):
                    if self.Group_INFO[i].file_info[j].file_name == file_name and self.Group_INFO[i].file_info[j].file_path == file_path:
                        for k in range(len(self.Group_INFO[i].file_info[j].acl_info)):
                            if self.Group_INFO[i].file_info[j].acl_info[k].user_id == user_id:
                                print(f'[INFO] ACL of user {user_id} already exist.]')
                                self.Group_INFO[i].file_info[j].acl_info[k].read = read
                                self.Group_INFO[i].file_info[j].acl_info[k].write = write
                                self.Group_INFO[i].file_info[j].acl_info[k].delete = delete
                                return LS_pb2.AddACLResponse(status=1)
                        self.Group_INFO[i].file_info[j].acl_info.append(ACL(user_id, read, write, delete))
                        print(f'[INFO] ACL of user {user_id} is added.')
                        self.update_acl_info_file()
                        return LS_pb2.AddACLResponse(status=1)
                print(f'[ERROR] File {file_name} does not exist when add ACL')
                return LS_pb2.AddACLResponse(status=0)
        print(f'[ERROR] Group {group_id} does not exist when add ACL')
        return LS_pb2.AddACLResponse(status=0)

    # temp
    def checkACLbeforeLock(self, request, context):
        # check if user has permission to lock file
        group_id = request.group_id
        file_name = request.filename
        file_path = request.path
        user_id = request.user_id
        lock_type = request.lock_type
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == group_id:
                for j in range(len(self.Group_INFO[i].file_info)):
                    if self.Group_INFO[i].file_info[j].file_name == file_name and self.Group_INFO[i].file_info[j].file_path == file_path:
                        for k in range(len(self.Group_INFO[i].file_info[j].acl_info)):
                            if self.Group_INFO[i].file_info[j].acl_info[k].user_id == user_id:
                                if lock_type == 0 and self.Group_INFO[i].file_info[j].acl_info[k].read == 1:
                                    return True
                                elif lock_type == 1 and self.Group_INFO[i].file_info[j].acl_info[k].write == 1:
                                    return True
                                else:
                                    return False
                        return False
                return False
        return False

        


    def Lock(self, request, context):
        # lock type 0: read   lock type 1: write
        group_id = request.group_id
        file_name = request.filename
        file_path = request.path
        user_id = request.user_id
        lock_type = request.lock_type
        lock_time = time.time()

        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == group_id:
                for j in range(len(self.Group_INFO[i].file_info)):
                    if self.Group_INFO[i].file_info[j].file_name == file_name and self.Group_INFO[i].file_info[j].file_path == file_path:
                        if len(self.Group_INFO[i].file_info[j].lock_info) == 0:
                            self.Group_INFO[i].file_info[j].lock_info.append(Lock(0, user_id, lock_type, lock_time))
                            print(f'[INFO] Lock {lock_type} of user {user_id} is added.')
                            self.update_lock_info_file()
                            return LS_pb2.LockResponse(status=1)
                        else:
                            if lock_type == 0:
                                for k in range(len(self.Group_INFO[i].file_info[j].lock_info)):
                                    if self.Group_INFO[i].file_info[j].lock_info[k].lock_type == 1:
                                        print(f'[ERROR] Exclusive Lock of file {file_name} in path {file_path} already exist.')
                                        return LS_pb2.LockResponse(status=0)
                                self.Group_INFO[i].file_info[j].lock_info.append(Lock(0, user_id, lock_type, lock_time))
                                print(f'[INFO] Lock {lock_type} of user {user_id} is added.')
                                self.update_lock_info_file()
                                return LS_pb2.LockResponse(status=1)
                            else:
                                print(f'[ERROR] Lock of file {file_name} in path {file_path} already exist.')
                                return LS_pb2.LockResponse(status=0)
                print(f'[ERROR] File {file_name} does not exist when add Lock')
                return LS_pb2.LockResponse(status=0)
        print(f'[ERROR] Group {group_id} does not exist when add Lock')
        return LS_pb2.LockResponse(status=0)

    def Unlock(self, request, context):
        group_id = request.group_id
        file_name = request.filename
        file_path = request.path
        user_id = request.user_id
        lock_type = request.lock_type
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == group_id:
                for j in range(len(self.Group_INFO[i].file_info)):
                    if self.Group_INFO[i].file_info[j].file_name == file_name and self.Group_INFO[i].file_info[j].file_path == file_path:
                        for k in range(len(self.Group_INFO[i].file_info[j].lock_info)):
                            if self.Group_INFO[i].file_info[j].lock_info[k].user_id == user_id:
                                self.Group_INFO[i].file_info[j].lock_info.pop(k)
                                print(f'[INFO] Lock of user {user_id} is removed.')
                                self.update_lock_info_file()
                                return LS_pb2.UnlockResponse(status=1)
                        print(f'[ERROR] Lock of user {user_id} does not exist.')
                        return LS_pb2.UnLockResponse(status=0)
                print(f'[ERROR] File {file_name} does not exist when remove Lock')
                return LS_pb2.UnLockResponse(status=0)
        print(f'[ERROR] Group {group_id} does not exist when remove Lock')
        return LS_pb2.UnLockResponse(status=0)
    

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    LS_pb2_grpc.add_LockServerServicer_to_server(Service(), server)
    server.add_insecure_port('[::]:' + str(LockServer_PORT))
    server.start()
    print(f'[START] Lock Server is running on port {LockServer_PORT}')
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    run()