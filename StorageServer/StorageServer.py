# Storage Server function:
# 1. Store the file in the local storage
# 2. Communicate with the client to send or receive the file
# 3. Communicate with the other storage servers to replicate the file

import socket
import os
import time
from datetime import datetime
from setting import *
from concurrent import futures

import grpc
import StorageServer.StorageServer_pb2 as SS_pb2
import StorageServer.StorageServer_pb2_grpc as SS_pb2_grpc
import TrackerServer.TrackerServer_pb2 as TS_pb2
import TrackerServer.TrackerServer_pb2_grpc as TS_pb2_grpc


class Servicer(SS_pb2_grpc.StorageServerServicer):
    def __init__(self, storage_server_id, ip, port, group_ip):
        self.storage_server_id = storage_server_id
        self.ip = ip
        self.port = port
        self.group_ip = group_ip
        # build the directory to store server data
        self.ROOT_PATH = '../DATA/StorageServer' + str(storage_server_id) +'/'        
        if not os.path.exists(self.ROOT_PATH):
            os.mkdir(self.ROOT_PATH)
        # connect to the tracker server
        tracker_channel = grpc.insecure_channel(TrackerServer_IP + ':' + str(TrackerServer_PORT))
        self.tracker_stub = TS_pb2_grpc.TrackerServerServiceStub(tracker_channel)
        # now we can call the function offered by tracker server in the storage server by stub
        print('[INIT] Connecting to Tracker Server...')
        response = self.tracker_stub.AddStorageServer(TS_pb2.AddStorageServerRequest(group_ip=group_ip,storage_server_id=storage_server_id, ip=ip, port=port))
        if(response.status == 1):
            print('[INIT] Connected to Tracker Server.')
        else:
            print('[INIT] Failed to connect to Tracker Server!!!')
        print("[INIT] Storage Server is ready to serve.")

        # replicate the file from other storage server
        self.replicate_file()
    
    def replicate_file(self):
        # get the other storage server info from tracker server
        response = self.tracker_stub.Replicate(TS_pb2.ReplicateRequest(port=self.port, ip=self.ip))
        if(response.status == 0):
            if(response.ip == -1):
                print("[REPLICATE] No other storage server to replicate from.")
            else:
                print("[REPLICATE] The group has no file yet.")
        else:
            # connect to the other storage server
            storage_channel = grpc.insecure_channel(response.ip + ':' + str(response.port))
            storage_stub = SS_pb2_grpc.StorageServerServiceStub(storage_channel)
            # get the file list from the other storage server
            response = storage_stub.GetFileList(SS_pb2.GetFileListRequest(""))
            file_list = response.file_list
            # replicate the file from the other storage server
            for file in file_list:
                response = storage_stub.Read(SS_pb2.ReadRequest(path=file.path, filename=file.filename))
                if(response.status == 1):
                    with open(self.ROOT_PATH + file.path + file.filename, 'w') as f:
                        f.write(response.content)
                    print("[REPLICATE] File {path}{file_name} replicated.")
                else:
                    print("[REPLICATE] File {path}{file_name} does not exist.")

    def PassUpdateInfo(self, filename, group_ip):
        # pass the update info to tracker server
        response = self.tracker_stub.UpdateFileInfo(TS_pb2.UpdateFileInfoRequest(filename=filename, group_ip=group_ip))
        if(response.status == 1):
            print(f'[PASS UPDATE INFO] File {filename} in tracker server updated.')
            update_time = datetime.strptime(response.time, '%Y-%m-%d %H:%M:%S.%f')
            update_time = time.mktime(update_time.timetuple())
            return update_time


    ##### proto service #####
    def Create(self, request, context):
        path = request.path
        file_name = request.filename
        content = request.content
        # check if the file exist
        if os.path.exists(self.ROOT_PATH + path + file_name):
            print("[CREATE] File {path}{file_name} already exist.")
            return SS_pb2.CreateResponse(status=0)
        # create the file
        with open(self.ROOT_PATH + path + file_name, 'w') as f:
            f.write(content)
        print("[CREATE] File {path}{file_name} created.")
        self.PassUpdateInfo(file_name, self.group_ip)
        return SS_pb2.CreateResponse(status=1)

    def Delete(self, request, context):
        path = request.path
        file_name = request.filename
        # check if the file exist
        if not os.path.exists(self.ROOT_PATH + path + file_name):
            print("[DELETE] File {path}{file_name} does not exist.")
            return SS_pb2.DeleteResponse(status=0)
        # delete the file
        os.remove(self.ROOT_PATH + path + file_name)
        print("[DELETE] File {path}{file_name} deleted.")
        request = self.tracker_stub.DeleteFile(self.tracker_stub.DeleteFileRequest(filename=file_name, group_ip=self.group_ip))
        return SS_pb2.DeleteResponse(status=1)


    def Read(self, request, context):
        path = request.path
        file_name = request.filename
        # check if the file exist
        if not os.path.exists(self.ROOT_PATH + path + file_name):
            print("[READ] File {path}{file_name} does not exist.")
            return SS_pb2.ReadResponse(0, "")
        # read the file
        with open(self.ROOT_PATH + path + file_name, 'r') as f:
            content = f.read()
        print("[READ] File {path}{file_name} read.")
        return SS_pb2.ReadResponse(status=1, content=content)


    def Write(self, request, context):
        path = request.path
        file_name = request.filename
        content = request.content
        mode = request.mode
        # check if the file exist
        if not os.path.exists(self.ROOT_PATH + path + file_name):
            print("[WRITE] File {path}{file_name} does not exist.")
            return SS_pb2.WriteResponse(status=0)
        # write the file
        if(mode == 1):
            with open(self.ROOT_PATH + path + file_name, 'a') as f:
                f.write(content)
        else:
            with open(self.ROOT_PATH + path + file_name, 'w') as f:
                f.write(content)
        print("[WRITE] File {path}{file_name} written.")
        self.PassUpdateInfo(file_name, self.group_ip)
        return SS_pb2.WriteResponse(status=1)

    def GetFileList(self, request, context):
        path = request.path
        # get the file list
        file_list = []
        for root, dirs, files in os.walk(self.ROOT_PATH + path):
            for file in files:
                file_list.append(SS_pb2.File(path=root, filename=file))
        print("[GETFILELIST] File list returned.")
        return SS_pb2.GetFileListResponse(file_list=file_list)


def run():
    STORAGE_SERVER_ID = int(input('[INPUT] Please input the Storage server id'))
    GROUP_IP = input('[INPUT] Please input the Group IP')
    STORAGE_SERVER_PORT = int(input('[INPUT] Please input the Storage server port'))
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    servicer = Servicer(STORAGE_SERVER_ID, ip_address, STORAGE_SERVER_PORT, GROUP_IP)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SS_pb2_grpc.add_StorageServerServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:' + str(STORAGE_SERVER_PORT))
    server.start()
    print(f"[RUN] Storage Server {str(STORAGE_SERVER_ID)} is running on port " + str(STORAGE_SERVER_PORT))
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    run() 