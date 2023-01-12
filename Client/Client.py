# Client function
# 1. get command and pass it to tracker server
# 2. get the storage server info and file info from tracker server
# 3. pass command to lock server
# 4. get lock from lock server
# 5. get connection with storage server
# 5. operate file in local cashe
# 6. update file in storage server and other storage servers
# 7. if write, update file info in tracker server
# 7. release lock

import socket
import os
from os.path import isfile, join
import time
from datetime import datetime
from setting import *
from concurrent import futures

import grpc
import TrackerServer.TrackerServer_pb2 as TS_pb2
import TrackerServer.TrackerServer_pb2_grpc as TS_pb2_grpc
import LockServer.LockServer_pb2 as LS_pb2
import LockServer.LockServer_pb2_grpc as LS_pb2_grpc
import StorageServer.StorageServer_pb2 as SS_pb2
import StorageServer.StorageServer_pb2_grpc as SS_pb2_grpc



def run():
    # get the hostname and ip address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    client_id = input("[INPUT] Please input your client id: ")
    ROOT_PATH = '../DATA/Client/' + client_id + '/' # also the path for data
    CASHE_PATH = ROOT_PATH + 'cashe/' # actually should be hidden to user
    if not os.path.exists(ROOT_PATH):
        os.mkdir(ROOT_PATH)
        os.mkdir(CASHE_PATH)
        print('[INIT] Client data directory is created.')
    else:
        print('[INIT] Client data directory already exists.')

    # connect to tracker server
    with grpc.insecure_channel(TrackerServer_IP + ':' + str(TrackerServer_PORT)) as channel:
        stub = TS_pb2_grpc.TrackerServerServiceStub(channel)
        print('[INIT] Connecting to Tracker Server successfully.')

        print("[INFO] Client is ready to serve.")
        print('[INPUT] You can input "help" if you need help.')
        # get command from user
        while True:
            command = input("[INPUT] Please input your command: ")
            if(command == 'exit'):
                break
            if(command == 'help'):
                print('[HELP] <your command> --- <description>')
                print('[HELP] list local --- list all files in local directory')
                print('[HELP] list remote --- list all files in remote directory')
                print('[HELP] read <file_name> <group_id> --- read the file in certain group')
                print('[HELP] write <file_name> <group_id> --- write the file in certain group')
                print('[HELP] delete <file_name> <group_id> --- delete the file in certain group')
                print('[HELP] create <file_name> <group_id> --- create the file in certain group')
                print('[HELP] help --- show help message')
                print('[HELP] exit --- exit the client')
                continue
            # get the file name and operation from command
            command_list = command.split()
            if(len(command_list) == 2):
                target = command_list[1]
                operation = command_list[0]
                if(operation == 'list'):
                    if(target == 'local'):
                        print('[INFO] List all files in local directory:')
                        print('[INFO] ', end='')
                        for file in os.listdir(ROOT_PATH):
                            if(isfile(join(ROOT_PATH, file))):
                                print(file, end=' ')
                        print()
                        continue
                    if(target == 'remote'):
                        print('[INFO] List all files in remote directory:')
                        print('[INFO] ', end='')
                        response = stub.GetFileList(TS_pb2.GetFileListRequest(""))
                        for group in response.groups:
                            print('Group ' + str(group.group_id) + ': ', end='')
                            for file in group.files:
                                print(file.file_name, end=' ')
                            print()
                        continue
                
            if(len(command_list) == 3):
               

            file_name = command_list[1]
            operation = command_list[0]
            # get the storage server info from tracker server
            response = stub.GetStorageServerInfo(TS_pb2.GetStorageServerInfoRequest(file_name=file_name))
            if(response.status == 0):
                print("[ERROR] The file doesn't exist.")
                continue
            else:
                storage_server_id = response.storage_server_id
                storage_server_ip = response.ip
                storage_server_port = response.port
                print("[INFO] The file is stored in Storage Server " + str(storage_server_id) + ".")
            # get the lock from lock server
            with grpc.insecure_channel(LockServer_IP + ':' + str(LockServer_PORT)) as channel:
                lock_stub = LS_pb2_grpc.LockServerServiceStub(channel)
                response = lock_stub.GetLock(LS_pb2.GetLockRequest(file_name=file_name, operation=operation))
                if(response.status == 0):
                    print("[ERROR] The file is locked.")
                    continue
                else:
                    print("[INFO] The file is unlocked.")
            # connect to storage server
            with grpc.insecure_channel(storage_server_ip + ':' + str(storage_server_port)) as channel:
                storage_stub = SS_pb2_grpc.StorageServerServiceStub(channel)
                # get the file from storage server
                if(operation == 'read'):
                    response = storage_stub.GetFile(SS_pb2.GetFileRequest(file_name=file_name))
                    if(response.status == 0):
                        print("[ERROR] The file doesn't exist.")
                        continue
                    else:
                        # write the file to local cashe
                        with open(CASHE_PATH

    # connect to lock server
    with grpc.insecure_channel(LockServer_IP + ':' + str(LockServer_PORT)) as channel:
        lock_stub = LS_pb2_grpc.LockServerServiceStub(channel)

