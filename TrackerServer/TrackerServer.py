# Tracker Server function:
# 1. record the info of storage servers and file info according to group
# 2. communicate with storage server to replicate file (from other storage server)
# 3. communicate with client to send or receive file info, and assign storage server
# 4. communicate with the lock server to pass the file list

import socket
import os
import time
from datetime import datetime
from setting import *
from concurrent import futures

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


class Servicer(TS_pb2_grpc.TrackerServerServiceServicer):
    def __init__(self):
        self.GROUP_INFO = {}
        self.FILE_INFO = {}
        self.STORAGE_SERVER_INFO = {}
        # build the directory to store server data
        self.ROOT_PATH = '../DATA/TrackerServer/'
        self.SERVER_FILE_NAME = 'server_info.txt'
        self.GROUP_FILE_NAME = 'group_info.txt'
        if not os.path.exists(self.ROOT_PATH):
            os.mkdir(self.ROOT_PATH)
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
        self.update_server_info_file()

        if(self.check_group_ip(request.group_id)):
            newGroup = group_info(request.group_id)
            self.GROUP_INFO.push_back(newGroup)
            self.update_group_info_file()
            print(f"[ADD GROUP] GROUP_IP: {request.group_id}")
        print(f"[ADD STORAGE SERVER] IP: {request.ip} PORT: {request.port} GROUP_ID: {request.group_id}")
        return TS_pb2.AddStorageServerResponse(status = 1)

    # 2. replicate the file to storage server in same group
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
                    return TS_pb2.ReplicateResponse(1, i.port, i.ip)
            print('[REPLICATE] NULL to IP: {request.ip} PORT: {request.port}')
            return TS_pb2.ReplicateResponse(0, -1, -1)
        print('[REPLICATE] ! IP: {request.ip} PORT: {request.port} DO NOT EXIST')
        return TS_pb2.ReplicateResponse(0, -2, -2)

    # 3. answer to the client file operation ask
    def AskFileOperation(self, request, context):
        op = request.operation
        file_name = request.filename
        group = request.group_id
        # find the storage server
        for server in self.STORAGE_SERVER_INFO:
            if(server.group_id == group and server.init == 1):
                ##### may ask to check if the server is alive #####
                print('[ASK FILE OPERATION] IP: {server.ip} PORT: {server.port}')
                return TS_pb2.AskFbeileOperationResponse(status = 1, ip = server.ip, port = server.port)
        print('[ASK FILE OPERATION] ! NO STORAGE SERVER IN GROUP: {group}')
        return TS_pb2.AskFileOperationResponse(-2, -2, -2)

    # 4. get the file list of all groups
    def GetFileList(self, request, context):
        group_ids = []
        file_names = []
        for group in self.GROUP_INFO:
            file_name = ""
            for file in group.file_info:
                print(f'[GET FILE LIST] GROUP: {file.group_id} FILE: {file.file_name} ')
                file_name += file.file_name + " "
            group_ids.append(group.group_id)
            file_names.append(file_name)
        return TS_pb2.GetFileListResponse(group_ids, file_names)

    # 5. update the file info
    def UpdateFileInfo(self, request, context):
        # update the file info
        file_name = request.filename
        group = request.group_id
        for i in range(len(self.GROUP_INFO)):
            if(self.GROUP_INFO[i].group_id == group):
                for j in range(len(self.GROUP_INFO[i].file_info)):
                    if(self.GROUP_INFO[i].file_info[j].file_name == file_name):
                        newTime = time.time()
                        self.GROUP_INFO[i].file_info[j].update_time = newTime
                        print(f'[UPDATE FILE] GROUP: {group} FILE: {file_name} TIME: {newTime}')
                        self.update_group_info_file()
                        # convert the time to string
                        time_obj = datetime.fromtimestamp(newTime)
                        time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
                        return TS_pb2.UpdateFileInfoResponse(status = 1, time = time_str)
                newFile = file_info(file_name, group)
                self.GROUP_INFO[i].file_info.append(newFile)
                print(f'[ADD FILE] GROUP: {group} FILE: {file_name} TIME: {newFile.update_time}')
                self.update_group_info_file()
                
                time_obj = datetime.fromtimestamp(newFile.update_time)
                time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
                return TS_pb2.UpdateFileInfoResponse(status = 1, time = time_str)
        
        newGroup = group_info(group)
        newFile = file_info(file_name, group)
        newGroup.file_info.append(newFile)
        self.GROUP_INFO.append(newGroup)
        print(f'[ADD GROUP] GROUP: {group}')
        print(f'[ADD FILE] GROUP: {group} FILE: {file_name} TIME: {newFile.update_time}')
        self.update_group_info_file()
        time_obj = datetime.fromtimestamp(newFile.update_time)
        time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
        return TS_pb2.UpdateFileInfoResponse(status = 1, time = time_str)

    # 6. delete the file info
    def DeleteFile(self, request, context):
        file_name = request.filename
        group = request.group_id
        for i in range(len(self.GROUP_INFO)):
            if(self.GROUP_INFO[i].group_id == group):
                for j in range(len(self.GROUP_INFO[i].file_info)):
                    if(self.GROUP_INFO[i].file_info[j].file_name == file_name):
                        self.GROUP_INFO[i].file_info.pop(j)
                        print(f'[DELETE FILE] GROUP: {group} FILE: {file_name}')
                        self.update_group_info_file()
                        return TS_pb2.DeleteFileResponse(status = 1)
        print(f'[DELETE FILE] ! GROUP: {group} FILE: {file_name} DO NOT EXIST')
        return TS_pb2.DeleteFileResponse(status = -1)

    def update_server_info_file(self):
        with open(self.root_path + self.SERVER_FILE_NAME, 'w') as f:
            f.write('IP --- PORT --- GROUP_ID' + '\n')
            for server in self.STORAGE_SERVER_INFO:
                f.write(str(server.ip) + ' ' + str(server.port) + ' ' + str(server.group_id) + '\n')
        print('[UPDATE SERVER INFO FILE] SUCCESS')

    def update_group_info_file(self):
        with open(self.root_path + self.GROUP_FILE_NAME, 'w') as f:
            f.write('GROUP_ID --- FILE_NAME --- UPDATE_TIME\n')
            for group in self.GROUP_INFO:
                for file in group.file_info:
                    f.write(str(file.group_id) + ' ' + str(file.file_name) + ' ' + str(file.update_time) + '\n')
        print('[UPDATE GROUP INFO FILE] SUCCESS')
                

def run():
    servicer = Servicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    TS_pb2_grpc.add_TrackerServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:' + str(TrackerServer_PORT))
    server.start()
    print('[TRACKER SERVER] STARTED')
    try:
        while True:
            time.sleep(86400) # one day
    except KeyboardInterrupt:
        server.stop(0)
        print('[TRACKER SERVER] STOPPED')


if __name__ == '__main__':
    run()