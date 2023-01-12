# Lock Server function：
# 1. record the file info and lock info (share or exclusive)
# 2. record the ACL (aceess control list) of each file
# 3. lock the file when client request
# 4. unlock the file when client release
# 5. communicate with tracker server to get the file list

import socket
import os
import time
from datetime import datetime
from setting import *
from concurrent import futures

import grpc
import TrackerServer.TrackerServer_pb2 as TS_pb2
import TrackerServer.TrackerServer_pb2_grpc as TS_pb2_grpc
import LockServer.LockServer_pb2 as LS_pb2
import LockServer.LockServer_pb2_grpc as LS_pb2_grpc


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
        self.lock_info = {}
        self.acl_info = {}


class Group():
    def __init__(self, group_id):
        self.group_id = group_id
        self.file_info = {}



class Service(LS_pb2_grpc.LockServerServicer):
    def __init__(self):
        self.Group_INFO = {}
        self.ROOT_PATH = '../DATA/LockServer/'
        self.FILE_NAME = 'file_info.txt'
        self.LOCK_NAME = 'lock_info.txt'
        self.ACL_NAME = 'acl_info.txt'
        if not os.path.exists(self.ROOT_PATH):
            os.mkdir(self.ROOT_PATH)
        print("[INIT] Lock Server is ready to serve.")

    
    ##### proto service #####
    def AddGroup(self, request, context):
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == request.group_id:
                print(f'[ERROR] Group {request.group_id} already exist.')
                return LS_pb2.AddGroupReply(status=0)
        self.Group_INFO.push_back(Group(request.group_id))
        print(f'[INFO] Group {request.group_id} is added.')
        return LS_pb2.AddGroupReply(status=1)
    
    def AddFile(self, request, context):
        group_id = request.group_id
        file_name = request.file_name
        file_path = request.path
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == group_id:
                for j in range(len(self.Group_INFO[i].file_info)):
                    if(self.Group_INFO[i].file_info[j].file_name == file_name and self.Group_INFO[i].file_info[j].file_path == file_path):
                        print(f'[ERROR] File {file_name} already exist.')
                        return LS_pb2.AddFileReply(status=0)
                self.Group_INFO[i].file_info.push_back(File(file_name, file_path, group_id))
                print(f'[INFO] File {file_name} is added.')
                return LS_pb2.AddFileReply(status=1)
        print(f'[ERROR] Group {group_id} does not exist.')
        return LS_pb2.AddFileReply(status=0)

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
                                return LS_pb2.AddACLReply(status=1)
                        self.Group_INFO[i].file_info[j].acl_info.push_back(ACL(user_id, read, write, delete))
                        print(f'[INFO] ACL of user {user_id} is added.')
                        return LS_pb2.AddACLReply(status=1)
                print(f'[ERROR] File {file_name} does not exist when add ACL')
                return LS_pb2.AddACLReply(status=0)
        print(f'[ERROR] Group {group_id} does not exist when add ACL')
        return LS_pb2.AddACLReply(status=0)

    def Lock(self, request, context):
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
                            self.Group_INFO[i].file_info[j].lock_info.push_back(Lock(0, user_id, lock_type, lock_time))
                            print(f'[INFO] Lock {lock_type} of user {user_id} is added.')
                            return LS_pb2.LockReply(status=1)
                        else:
                            if lock_type == 0:
                                for k in range(len(self.Group_INFO[i].file_info[j].lock_info)):
                                    if self.Group_INFO[i].file_info[j].lock_info[k].lock_type == 1:
                                        print(f'[ERROR] Exclusive Lock of file {file_name} in path {file_path} already exist.')
                                        return LS_pb2.LockReply(status=0)
                                self.Group_INFO[i].file_info[j].lock_info.push_back(Lock(0, user_id, lock_type, lock_time))
                                print(f'[INFO] Lock {lock_type} of user {user_id} is added.')
                                return LS_pb2.LockReply(status=1)
                            else:
                                print(f'[ERROR] Lock of file {file_name} in path {file_path} already exist.')
                                return LS_pb2.LockReply(status=0)
                print(f'[ERROR] File {file_name} does not exist when add Lock')
                return LS_pb2.LockReply(status=0)
        print(f'[ERROR] Group {group_id} does not exist when add Lock')
        return LS_pb2.LockReply(status=0)

    def Unlock(self, request, context):
        group_id = request.group_id
        file_name = request.filename
        file_path = request.path
        user_id = request.user_id
        for i in range(len(self.Group_INFO)):
            if self.Group_INFO[i].group_id == group_id:
                for j in range(len(self.Group_INFO[i].file_info)):
                    if self.Group_INFO[i].file_info[j].file_name == file_name and self.Group_INFO[i].file_info[j].file_path == file_path:
                        for k in range(len(self.Group_INFO[i].file_info[j].lock_info)):
                            if self.Group_INFO[i].file_info[j].lock_info[k].user_id == user_id:
                                self.Group_INFO[i].file_info[j].lock_info.erase(k)
                                print(f'[INFO] Lock of user {user_id} is removed.')
                                return LS_pb2.UnlockReply(status=1)
                        print(f'[ERROR] Lock of user {user_id} does not exist.')
                        return LS_pb2.UnlockReply(status=0)
                print(f'[ERROR] File {file_name} does not exist when remove Lock')
                return LS_pb2.UnlockReply(status=0)
        print(f'[ERROR] Group {group_id} does not exist when remove Lock')
        return LS_pb2.UnlockReply(status=0)
    
                        