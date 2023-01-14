# Tracker Server function:
# 1. record the info of storage servers and file info according to group
# 2. communicate with storage server to replicate file (from other storage server)
# 3. communicate with client to send or receive file info, and assign storage server
# 4. communicate with the lock server to pass the file list



import socket
import time as tm
from datetime import datetime
from concurrent import futures
import os
import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import APIs.setting as setting

TrackerServer_PORT = setting.TrackerServer_PORT
TrackerServer_IP = setting.TrackerServer_IP
LockServer_PORT = setting.LockServer_PORT
LockServer_IP = setting.LockServer_IP

import grpc
import APIs.TrackerServer_pb2 as TS_pb2
import APIs.TrackerServer_pb2_grpc as TS_pb2_grpc
import APIs.LockServer_pb2 as LS_pb2
import APIs.LockServer_pb2_grpc as LS_pb2_grpc


# TrackerServer_PORT = 5000
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


class file_info:
    def __init__(self, file_name, file_path, group_id):
        self.file_name = file_name
        self.file_path = file_path
        self.group_id = group_id
        self.update_time = tm.time()

class group_info:
    def __init__(self, group_id):
        self.group_id = group_id
        self.file_info = []

class storage_server_info:
    def __init__(self, storage_server_id, ip, port, group_id):
        self.storage_server_id = storage_server_id
        self.ip = ip
        self.port = port
        self.group_id = group_id
        self.init = 0

def timeTransfer(t):
    # input:time.time()
    # output: string
    t_obj = datetime.fromtimestamp(t)
    return t_obj.strftime('%Y-%m-%d %H:%M:%S')

class Servicer(TS_pb2_grpc.TrackerServerServicer):
    def __init__(self):
        self.GROUP_INFO = []
        self.FILE_INFO = []
        self.STORAGE_SERVER_INFO = []
        # build the directory to store server data
        self.ROOT_PATH = './DATA/'
        self.SERVER_FILE_NAME = 'server_info.txt'
        self.GROUP_FILE_NAME = 'group_info.txt'
        if not os.path.exists('./DATA/'):
            os.mkdir('./DATA/')
            print(f'[INIT] Successfully build the tracker server data directory.')
        print("[INIT] Tracker Server is ready to serve.")

    # check if group exist by g_id
    def check_group_ip(self, g_id):
        for group in self.GROUP_INFO:
            if(group.group_id == g_id):
                return True
        return False

    # update server info into file
    def update_server_info_file(self):
        with open(self.ROOT_PATH + self.SERVER_FILE_NAME, 'w') as f:
            f.write('IP --- PORT --- GROUP_ID' + '\n')
            for server in self.STORAGE_SERVER_INFO:
                f.write(str(server.ip) + ' ' + str(server.port) + ' ' + str(server.group_id) + '\n')
        print(f'[UPDATE SERVER INFO FILE] SUCCESS')

    # update group info into file
    def update_group_info_file(self):
        with open(self.ROOT_PATH + self.GROUP_FILE_NAME, 'w') as f:
            f.write('GROUP_ID --- FILE_PATH --- FILE_NAME --- UPDATE_TIME\n')
            for group in self.GROUP_INFO:
                for file in group.file_info:
                    update_time = timeTransfer(file.update_time)
                    f.write(str(file.group_id) + ' ' + file.file_path + ' ' + str(file.file_name) + ' ' + update_time + '\n')
        print(f'[UPDATE GROUP INFO FILE] Successful update group info file.')


    ##### proto service #####

    # 1. add storage server info to tracker server
    def AddStorageServer(self, request, context):
        newStServer = storage_server_info(request.storage_server_id, request.ip, request.port, request.group_id)
        self.STORAGE_SERVER_INFO.append(newStServer)
        self.update_server_info_file()

        if(not self.check_group_ip(request.group_id)):
            newGroup = group_info(request.group_id)
            self.GROUP_INFO.append(newGroup)
            self.update_group_info_file()
            print(f"[ADD GROUP] GROUP_IP: {request.group_id}")
        print(f"[ADD STORAGE SERVER] IP: {request.ip} PORT: {request.port} GROUP_ID: {request.group_id}")
        return TS_pb2.AddStorageServerResponse(status = 1)

    # 2. replicate the file to storage server in same group
    def Replicate(self, request, context):
        group_id = -1
        index = -1
        # get group ip from storage server info
        for i in self.STORAGE_SERVER_INFO:
            index += 1
            if(i.ip == request.ip and i.port == request.port):
                group_id == i.group_id
                break
        if(group_id != -1):
            for i in self.STORAGE_SERVER_INFO:
                if(i.group_id == group_id and i.init == 1):
                    # mark the requesting storage server initialed 
                    self.STORAGE_SERVER_INFO[index].init = 1
                    print(f'[REPLICATE] IP: {i.ip} PORT: {i.port} to IP: {request.ip} PORT: {request.port}')
                    return TS_pb2.ReplicateResponse(status = 1, ip = str(i.ip), port = i.port)
            print(f'[REPLICATE] NULL to IP: {request.ip} PORT: {request.port}')
            return TS_pb2.ReplicateResponse(status = 0, ip = '-1', port = -1)
        print(f'[REPLICATE] IP: {request.ip} PORT: {request.port} is the only storage server in the group')
        self.STORAGE_SERVER_INFO[index].init = 1
        return TS_pb2.ReplicateResponse(status = 0, ip = '-2', port = -2)

    # 3. answer to the client file operation ask
    def AskFileOperation(self, request, context):
        op = request.operation
        file_name = request.filename
        request_group = request.group_id
        file_path = request.path
        # check if the file exist
        for group in self.GROUP_INFO:
            if(group.group_id == request_group):
                if(not op == 'create'):
                    for file in group.file_info:
                        if(file.file_name == file_name and file.file_path == file_path):
                            print(f'[ASK FILE OPERATION] FILE EXIST IN GROUP: {request_group}')
                            # transfer the time to string
                            update_time = timeTransfer(file.update_time)

                            # find the storage server
                            for server in self.STORAGE_SERVER_INFO:
                                if(server.group_id == request_group and server.init == 1):
                                    ##### may ask to check if the server is alive #####
                                    print(f'[ASK FILE OPERATION] IP: {server.ip} PORT: {server.port}')
                                    return TS_pb2.AskFileOperationResponse(status = 1, ip = str(server.ip), port = server.port ,time = update_time)
                            print(f'[ASK FILE OPERATION] ! NO STORAGE SERVER IN GROUP: {request_group}')
                            return TS_pb2.AskFileOperationResponse(status = 0, ip = '-1', port = -1, time = "")
                else:
                    # set update_time as current local time
                    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # find the storage server
                    for server in self.STORAGE_SERVER_INFO:
                        if(server.group_id == request_group and server.init == 1):
                            ##### may ask to check if the server is alive #####
                            print(f'[ASK FILE OPERATION] IP: {server.ip} PORT: {server.port}')
                            return TS_pb2.AskFileOperationResponse(status = 1, ip = str(server.ip), port = server.port ,time = update_time)
                    print(f'[ASK FILE OPERATION] ! NO STORAGE SERVER IN GROUP: {request_group}')
                    return TS_pb2.AskFileOperationResponse(status = 0, ip = '-1', port = -1, time = "")
        print(f'[ASK FILE OPERATION] ! FILE NOT EXIST IN GROUP: {request_group}')
        return TS_pb2.AskFileOperationResponse(status = 0, ip = '-2', port = -2, time = "")

    # 4. get the file list of all groups from tracker server
    def GetFileList(self, request, context):
        groups = []
        for group in self.GROUP_INFO:
            files = []
            for file in group.file_info:
                files.append(TS_pb2.File(file_name = file.file_name, file_path = file.file_path))
            groups.append(TS_pb2.Group(group_id = group.group_id, files = files))
        print(f'[GET FILE LIST] Success.')
        return TS_pb2.GetFileListResponse(groups = groups)



    # 5. update the file info in tracker server
    def UpdateFileInfo(self, request, context):
        # update the file info
        file_name = request.filename
        file_path = request.filepath
        new_group_ip = request.group_id
        for i in range(len(self.GROUP_INFO)):
            if(self.GROUP_INFO[i].group_id == new_group_ip):
                for j in range(len(self.GROUP_INFO[i].file_info)):
                    if(self.GROUP_INFO[i].file_info[j].file_name == file_name and self.GROUP_INFO[i].file_info[j].file_path == file_path):
                        newTime = tm.time()
                        self.GROUP_INFO[i].file_info[j].update_time = newTime
                        newTime = timeTransfer(newTime)
                        print(f'[UPDATE FILE] GROUP: {new_group_ip} FILE: {file_name} TIME: {newTime}')
                        self.update_group_info_file()
                        # convert the time to string
                        return TS_pb2.UpdateFileInfoResponse(status = 1, time = newTime)
                newFile = file_info(file_name, file_path, new_group_ip)
                self.GROUP_INFO[i].file_info.append(newFile)
                print(f'[ADD FILE] GROUP: {new_group_ip} FILE: {file_name} TIME: {timeTransfer(newFile.update_time)}')
                self.update_group_info_file()

                # add file in lock server
                with grpc.insecure_channel(LockServer_IP + ':' + str(LockServer_PORT)) as channel:
                    lock_stub = LS_pb2_grpc.LockServerStub(channel)
                    response = lock_stub.AddFile(LS_pb2.AddFileRequest(filename=file_name, path = file_path, group_id=new_group_ip))
                    if(response.status == 0):
                        print("[ERROR] Fail to add the file in lock server.")
                        return TS_pb2.UpdateFileInfoResponse(status = 0, time = timeTransfer(tm.time()))
                    print("[INFO] Success to add the file in lock server.")


                return TS_pb2.UpdateFileInfoResponse(status = 1, time = timeTransfer(newFile.update_time))
        
        newGroup = group_info(new_group_ip)
        newFile = file_info(file_name, file_path, new_group_ip)
        newGroup.file_info.append(newFile)
        newTime = timeTransfer(newFile.update_time)
        self.GROUP_INFO.append(newGroup)
        print(f'[ADD GROUP] GROUP: {new_group_ip}')
        print(f'[ADD FILE] GROUP: {new_group_ip} FILE: {file_name} TIME: {newTime}')
        self.update_group_info_file()
        return TS_pb2.UpdateFileInfoResponse(status = 1, time = newTime)

    # 6. `delete` the file info
    def DeleteFile(self, request, context):
        file_name = request.filename
        file_path = request.filepath
        group = request.group_id
        for i in range(len(self.GROUP_INFO)):
            if(self.GROUP_INFO[i].group_id == group):
                for j in range(len(self.GROUP_INFO[i].file_info)):
                    if(self.GROUP_INFO[i].file_info[j].file_name == file_name and self.GROUP_INFO[i].file_info[j].file_path == file_path):
                        self.GROUP_INFO[i].file_info.pop(j)
                        print(f'[DELETE FILE] GROUP: {group} PATH: {file_path} FILE: {file_name}')
                        self.update_group_info_file()
                        return TS_pb2.DeleteFileResponse(status = 1)
        print(f'[DELETE FILE] ! GROUP: {group} FILE: {file_name} DO NOT EXIST')
        return TS_pb2.DeleteFileResponse(status = -1)

    
                

def run():
    servicer = Servicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    TS_pb2_grpc.add_TrackerServerServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:' + str(setting.TrackerServer_PORT))
    server.start()
    print(f'[START] Tracker server is running on port: ' + str(setting.TrackerServer_PORT))
    try:
        while True:
            tm.sleep(86400) # one day
    except KeyboardInterrupt:
        server.stop(0)
        print(f'[TRACKER SERVER] STOPPED')


if __name__ == '__main__':
    run()