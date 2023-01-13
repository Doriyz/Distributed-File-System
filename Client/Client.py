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
import time as tm
import sys
from datetime import datetime
from APIs.setting import *
from concurrent import futures

import grpc
import APIs.TrackerServer_pb2 as TS_pb2
import APIs.TrackerServer_pb2_grpc as TS_pb2_grpc
import APIs.LockServer_pb2 as LS_pb2
import APIs.LockServer_pb2_grpc as LS_pb2_grpc
import APIs.StorageServer_pb2 as SS_pb2
import APIs.StorageServer_pb2_grpc as SS_pb2_grpc
import shutil

debug = True

ROOT_PATH = "./DATA" # to be defined in run()
CASHE_PATH = "" # to be defined in run()

if not os.path.exists(ROOT_PATH):
    os.mkdir(ROOT_PATH)


class FileInfo():
    def __init__(self, file_name, file_path, group_id, update_time):    
        self.file_name = file_name
        self.file_path = file_path
        self.group_id = group_id
        self.update_time = update_time

def is_cashe_hit(group_id, file_path, file_name, cashe_info):
    for file_info in cashe_info:
        if(file_info.group_id == group_id and file_info.file_path == file_path and file_info.file_name == file_name):
            return file_info.update_time
    return ""

def update_cashed_file(group_id, file_path, file_name, update_time,cashe_info, content = ""):
    for i in range(len(cashe_info)):
        if(cashe_info[i].group_id == group_id and cashe_info[i].file_path == file_path and cashe_info[i].file_name == file_name):
            cashe_info[i].update_time = update_time
            # update file content
            if(content != ""):
                global ROOT_PATH, CASHE_PATH
                file = open(ROOT_PATH + CASHE_PATH + file_path + file_name, 'w')
                file.write(content)
                file.close()
            print(f'[INFO] Successfully update cashed file')
            return
    print(f'[INFO] Fail to update cashed file')

def delete_cashed_file(group_id, file_path, file_name, cashe_info):
    for i in range(len(cashe_info)):
        if(cashe_info[i].group_id == group_id and cashe_info[i].file_path == file_path and cashe_info[i].file_name == file_name):
            cashe_info.pop(i)
            # delete in local cashe
            global ROOT_PATH, CASHE_PATH
            os.remove(ROOT_PATH + CASHE_PATH + file_path + file_name)
            print(f'[INFO] Successfully delete cashed file')
            return
    print(f'[INFO] Fail to delete cashed file')

def create_cashed_file(group_id, file_path, file_name, content, update_time, cashe_info):
    # create file in local cashe
    global ROOT_PATH, CASHE_PATH
    file = open(ROOT_PATH + CASHE_PATH + file_path + file_name, 'w')
    file.write(content)
    file.close()
    # update cashe info
    cashe_info.append(FileInfo(group_id=group_id, file_path=file_path, file_name=file_name, update_time=update_time))
    print(f'[INFO] Successfully create cashed file')

def run():
    global ROOT_PATH, CASHE_PATH
    # get the hostname and ip address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    if(debug):
        user_id = 1
    else:
        user_id = input("[INPUT] Please input your user id: ")
    ROOT_PATH = './DATA/Client' + str(user_id) + '/' # also the path for data
    CASHE_PATH = 'cashe/' # actually should be hidden to user
    if os.path.exists(ROOT_PATH):
        shutil.rmtree(ROOT_PATH + CASHE_PATH)
        print(f'[INIT] Remove the old client cashe directory.')
        os.mkdir(ROOT_PATH + CASHE_PATH)
    else:
        os.mkdir(ROOT_PATH)
        os.mkdir(ROOT_PATH + CASHE_PATH)
        print(f'[INIT] Client data directory is created.')
 

    Cashe_Info = [] # list of FileInfo

    # connect to tracker server
    try:
        with grpc.insecure_channel(TrackerServer_IP + ':' + str(TrackerServer_PORT)) as channel:
            stub = TS_pb2_grpc.TrackerServerStub(channel)
            print(f'[INIT] Connecting to Tracker Server successfully.')

            print("[INFO] Client is ready to serve.")
            print(f'[INPUT] You can input "help" if you need help.')
            # get command from user
            while True:
                command = input("[INPUT] Please input your command: ")
                if(command == 'exit'):
                    break
                if(command == 'help'):
                    # if file_path = "", just mark it as ' "" '
                    print(f'[HELP] <your command> --- <description>')
                    print(f'[HELP] list local --- list all files in local directory')
                    print(f'[HELP] list remote --- list all files in remote directory')
                    print(f'[HELP] read <file_path> <file_name> <group_id> --- read the file in certain group')
                    print(f'[HELP] write <file_path> <file_name> <group_id> --- write the file in certain group')
                    print(f'[HELP] delete <file_path> <file_name> <group_id> --- delete the file in certain group')
                    print(f'[HELP] create <file_name> <group_id> --- create the file in certain group')
                    print(f'[HELP] download <file_path> <file_name> <group_id> --- download the file to local directory')
                    print(f'[HELP] upload <file_path> <file_name> <group_id> --- upload the file to remote directory')
                    print(f'[HELP] help --- show help message')
                    print(f'[HELP] exit --- exit the client')
                    continue
                # get the file name and operation from command
                command_list = command.split()
                if(len(command_list) == 2):
                    target = command_list[1]
                    operation = command_list[0]
                    if(operation == 'list'):
                        if(target == 'local'):
                            if(len(os.listdir(ROOT_PATH)) == 0):
                                print(f'[INFO] ')
                            else:
                                print(f'[INFO] List all files in local directory:')
                                print(f'[INFO] ', end='')
                                for file in os.listdir(ROOT_PATH):
                                    if(isfile(join(ROOT_PATH, file))):
                                        print(file, end=' ')
                                print()
                            continue
                        if(target == 'remote'):
                            print(f'[INFO] List all files in remote directory:')
                            response = stub.GetFileList(TS_pb2.GetFileListRequest(operation = ""))
                            for group in response.groups:
                                print(f'[INFO] Group ' + str(group.group_id))
                                for file in group.files:
                                    print(f'[INFO] {file.file_path}: {file.file_name}')
                            if(len(response.groups) == 0):
                                print(f'[INFO]')
                            continue
                    
                if(len(command_list) == 4):
                    group_id = int(command_list[3])
                    file_name = command_list[2]
                    file_path = command_list[1]
                    operation = command_list[0]
                    if file_path == '""':
                        file_path = ''
                    if(operation == 'read' or operation == 'write' or operation == 'delete' or operation == 'create' or operation == 'download' or operation == 'upload'):
                        # get the storsage server info from tracker server
                        response = stub.AskFileOperation(TS_pb2.AskFileOperationRequest(filename=file_name, group_id=group_id, operation=operation, path = file_path))
                        if(response.status == 0):
                            print("[ERROR] Fail to get the storage server info.")
                            continue
                        ss_ip = response.ip
                        ss_port = response.port
                        update_time = response.time

                        lock_type = 1
                        if(operation == 'read'):
                            lock_type = 0

                        if(operation == 'create'):
                            # create the file
                            if os.path.exists(ROOT_PATH + file_name):
                                print(f'[ERROR] The file already exists in local.')
                                continue
                            with grpc.insecure_channel(ss_ip + ':' + str(ss_port)) as channel:  
                                storage_stub = SS_pb2_grpc.StorageServerStub(channel)
                                response = storage_stub.Create(SS_pb2.CreateRequest(filename=file_name, path = file_path, content = ""))
                                if(response.status == 1):
                                    print(f'[INFO] Successfully create the file in storage server.')
                                    response = stub.UpdateFileInfo(TS_pb2.UpdateFileInfoRequest(filename=file_name, filepath = file_path, group_id=group_id))
                                    if(response.status == 1):
                                        f = open(ROOT_PATH + file_name, 'w')
                                        f.close()
                                        update_time = response.time
                                        print(f'[INFO] Create file info in tracker server in {update_time}.')
                                        # create the cashe
                                        content = ""
                                        create_cashed_file(group_id, file_path, file_name, content,update_time, Cashe_Info)
                                        continue
                                    else:
                                        print(f'[ERROR] Fail to update file info in tracker server.')
                                else:
                                    print(f'[ERROR] Fail to create the file in storage server')
                                continue
                            

                    
                                    


                        # get the lock from lock server
                        with grpc.insecure_channel(LockServer_IP + ':' + str(LockServer_PORT)) as channel:
                            lock_stub = LS_pb2_grpc.LockServerStub(channel)
                            response = lock_stub.Lock(LS_pb2.LockRequest(filename=file_name, path = file_path, group_id=group_id, user_id = user_id, lock_type = lock_type))
                            if(response.status == 0):
                                print("[ERROR] The file is locked.")
                                print(f'[INFO] Retry to lock the file in 5 seconds...')
                                tm.sleep(5)
                                response = lock_stub.Lock(LS_pb2.LockRequest(filename=file_name, path = file_path, group_id=group_id, user_id = user_id, lock_type = lock_type))
                                if(response.status == 0):
                                    print("[ERROR] The file is locked.")
                                    print(f'[INFO] Please try to lock the file later.')
                                    continue
                            print("[INFO] The file is locked successfully.")

                        # if read, cashe hit and file is the latest, read from cashe 
                        if operation == 'read':
                            time = is_cashe_hit(group_id, file_path, file_name, update_time)
                            if time == update_time:
                                print(f'[INFO] Cashe hit.')
                                print(f'[INFO] Read the file from cashe.')
                                with open(join(ROOT_PATH + file_path, file_name), 'r') as f:
                                    print(f.read())
                                continue
                            elif time == "":
                                print(f'[INFO] Cashe miss.')
                            else:
                                print(f'[INFO] Cashe hit.')
                                print(f'[INFO] The file is out of date.')
                                print(f'[INFO] Update the cashe from storage server.')
                        # connect to storage server
                        with grpc.insecure_channel(ss_ip + ':' + str(ss_port)) as channel:  
                            storage_stub = SS_pb2_grpc.StorageServerStub(channel)
                            # read
                            if operation == 'read':
                                response = storage_stub.Read(SS_pb2.ReadRequest(filename=file_name, path = file_path))
                                if(response.status == 1):
                                    print(f'[INFO] Read the file {file_name} from storage server.')
                                    print(f'[READ] {response.content}')
                                    # update the cashe
                                    if time != "":
                                        with open(join(ROOT_PATH + file_path, file_name), 'w') as f:
                                            f.write(response.content)
                                            update_cashed_file(group_id, file_path, file_name, update_time, response.content)
                                else:
                                    print(f'[ERROR] Fail to read the file.')

                            elif operation == 'write':
                                content = input('[INFO] Please input the content you want to write:')
                                response = storage_stub.Write(SS_pb2.WriteRequest(filename=file_name, content=content, path = file_path, group_id=group_id))
                                if(response.status == 1):
                                    print(f'[INFO] Write the file to storage server.')
                                    # update in tracker server
                                    response = stub.UpdateFileInfo(TS_pb2.UpdateFileInfoRequest(filename=file_name, path = file_path, group_id=group_id))
                                    if(response.status == 1):
                                        print(f'[INFO] Successfully update file info in tracker server.')
                                        update_time = response.time
                                        # update the cashe
                                        with open(join(ROOT_PATH + file_path, file_name), 'w') as f:
                                            f.write(content)
                                            update_cashed_file(group_id, file_path, file_name, update_time, content)
                                    else:
                                        print(f'[ERROR] Fail to update file info in tracker server.')
                                else:
                                    print(f'[ERROR] Fail to write the file.')

                            elif operation == 'delete':
                                response = storage_stub.Delete(SS_pb2.DeleteRequest(filename=file_name, path = file_path, group_id=group_id))
                                if(response.status == 1):
                                    print(f'[INFO] Delete the file from storage server.')
                                    # delete the cashe
                                    delete_cashed_file(group_id, file_path, file_name)
                                    # delete in tracker server
                                    response = stub.DeleteFile(TS_pb2.DeleteFileRequest(filename=file_name, path = file_path, group_id=group_id))
                                    if(response.status == 1):
                                        print(f'[INFO] Successfully delete file info in tracker server.')
                                        continue
                                    else:
                                        print(f'[ERROR] Fail to delete file info in tracker server.')
                                else:
                                    print(f'[ERROR] Fail to delete the file.')
                                                      
                            else:
                                print(f'[ERROR] Invalid operation.')

                        # release the lock
                        with grpc.insecure_channel(LockServer_IP + ':' + str(LockServer_PORT)) as channel:
                            lock_stub = LS_pb2_grpc.LockServerStub(channel)
                            response = lock_stub.ReleaseLock(LS_pb2.ReleaseLockRequest(filename=file_name, operation=operation, path = file_path, group_id=group_id, user_id = user_id))
                            if(response.status == 1):
                                print("[INFO] Successfully release the lock.")
                            else:
                                print("[ERROR] Fail to release the lock.")
                        
                    else:
                        print("[ERROR] Invalid command.")
                else:
                    print(f'[ERROR] Invalid command.')
            
        print(f'[INFO] Exit the client.')

                
    except KeyboardInterrupt:
        print(f'[ERROR] Keyboard interrupt.')
        sys.exit(0)

if __name__ == '__main__':
    run()