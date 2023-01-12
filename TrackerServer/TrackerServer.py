# Tracker Server function:
# 1. record the info of storage servers and file info according to group
# 2. communicate with storage server to replicate file (from other storage server)
# 3. communicate with client to send or receive file info, and assign storage server

import socket
import time
from datetime import datetime
from setting import *

import grpc
import TrackerServer.TrackerServer_pb2 as TS_pb2
import TrackerServer.TrackerServer_pb2_grpc as TS_pb2_grpc



# TrackerServer_PORT = 5000
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


class file_info:
    def __init__(self, file_name, group_id):
        self.file_name = file_name
        self.group_id = group_id
        self.update_time = time.time()

class group_info:
    def __init__(self, group_id):
        self.group_id = group_id
        self.file_info = {}

class storage_server_info:
    def __init__(self, storage_server_id, ip, port, group_id):
        self.storage_server_id = storage_server_id
        self.ip = ip
        self.port = port
        self.group_id = group_id
        self.init = 0


class Service(TS_pb2_grpc.TrackerServerServiceServicer):
    def __init__(self):
        self.GROUP_INFO = {}
        self.FILE_INFO = {}
        self.STORAGE_SERVER_INFO = {}
        print("[INIT] Tracker Server is ready to serve.")

    # check if group exist by g_id
    def check_group_ip(self, g_id):
        for group in self.GROUP_INFO:
            if(group.group_id == g_id):
        return True
        return False

    ##### proto service #####

    # 1. add storage server info to tracker server
    def AddStorageServer(self, request, context):
        newStServer = storage_server_info(request.storage_server_id, request.ip, request.port, request.group_id)
        self.STORAGE_SERVER_INFO.push_back(newStServer)
        
        if(self.check_group_ip(request.group_id)):
            newGroup = group_info(request.group_id)
            self.GROUP_INFO.push_back(newGroup)
            print(f"[ADD GROUP] GROUP_IP: {request.group_id}")
        print(f"[ADD STORAGE SERVER] IP: {request.ip} PORT: {request.port} GROUP_ID: {request.group_id}")
        return TS_pb2.AddStorageServerResponse(status = 1)

    def Replicate(self, request, context):
        group = -1
        index = -1
        # get group ip from storage server info
        for i in self.STORAGE_SERVER_INFO:
            index += 1
            if(i.ip == request.ip and i.port == request.port):
                group == i.group_id
                break
        if(group != -1):
            for i in self.STORAGE_SERVER_INFO:
                if(i.group_id == group and i.init == 1):
                    # mark the requesting storage server initialed 
                    self.STORAGE_SERVER_INFO[index].init = 1
                    print('[REPLICATE] IP: {i.ip} PORT: {i.port} to IP: {request.ip} PORT: {request.port}')
                    return TS_pb2.ReplicateResponse(i.port, i.ip)
            print('[REPLICATE] NULL to IP: {request.ip} PORT: {request.port}')
            return TS_pb2.ReplicateResponse(-1, -1)
        print('[REPLICATE] ! IP: {request.ip} PORT: {request.port} DO NOT EXIST')
        return TS_pb2.ReplicateResponse(-2, -2)

    def 