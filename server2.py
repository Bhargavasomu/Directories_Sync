import socket
import os
import json
import time
import re
import hashlib
import stat

def parse(string):
    return string.split()

def md5(fname):
	hash = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash.update(chunk)
	return hash.hexdigest()

def TCPfilesend(socket,directory,file):
    path = directory + '/' + file
    if not os.path.isfile(path):
        print "File" , file , "was not found"
        print
        socket.send('-1')        # No file found
        socket.recv(1)
        return
    else:
        perm = int(oct(stat.S_IMODE(os.lstat(path).st_mode)),8)
        f = open(path,'r+')
        print
        print "Opened File: " , f.name
        size_file = os.path.getsize(path)
        socket.send(str(size_file))
        socket.recv(1)
        if size_file > 0:
            content = f.read(1024)
            while content != '':        # till EOF
                socket.send(content)
                content = f.read(1024)
        socket.recv(1)
        socket.send(str(perm))
        socket.recv(1)
        f.close()
        print "Sent File: " , f.name
        print
        dict = {'Name':file,'Size':size_file,'Timestamp':time.ctime(os.path.getmtime(path)), 'Hash':md5(path)}
        return dict
    socket.close()

def UDPfilesend(socket,clientaddr,directory,file):
    path = directory + '/' + file
    if not os.path.isfile(path):
        print "File" , file , "was not found"
        print
        socket.sendto('-1',clientaddr)        # No file found
        socket.recvfrom(1)
        return
    else:
        perm = int(oct(stat.S_IMODE(os.lstat(path).st_mode)),8)
        f = open(path,'r+')
        print
        print "Opened File: " , f.name
        size_file = os.path.getsize(path)
        socket.sendto(str(size_file),clientaddr)
        socket.recvfrom(1)
        if size_file > 0:
            content = f.read(1024)
            while content != '':        # till EOF
                socket.sendto(content,clientaddr)
                content = f.read(1024)
        socket.recvfrom(1)
        socket.sendto(str(perm),clientaddr)
        socket.recvfrom(1)
        f.close()
        print "Sent File: " , f.name
        print
        dict = {'Name':file,'Size':size_file,'Timestamp':time.ctime(os.path.getmtime(path)), 'Hash':md5(path)}
        return dict
    socket.close()

def Main():
    host = '127.0.0.1'                  # IP address of server 1
    directory = '/home/bhargava/Academics/2-2/Assignments/Computer Networks/Assignment1/shared2'   # shared directory in server 2
    port = 5002                        # port num of this process
    s = socket.socket()
    s.bind((host,port))
    s.listen(1)
    c,addr = s.accept()
    print "Connection From: " + str(addr)

    while True:
        message = c.recv(1024)
        if not message:
            break
        message = json.loads(message)   # deserializing mesage sent from client
        print "Got Message from Client: " + str(message[0])
        if message[0] == 'index_longlist':
            data = []
            files = os.listdir(directory)
            for f in files:
                temp = directory + '/' + f
                file_size = os.path.getsize(temp)
                seconds = os.path.getmtime(temp)
                timestamp = time.ctime(os.path.getmtime(temp))
                if os.path.isdir(temp) == True:
                    name_type = 'Directory'
                else:
                    name_type = 'File'
                dict = {'Name': f,'Size': file_size,'Seconds': seconds,'Timestamp': timestamp,'Type': name_type}
                data.append(dict)
            data = json.dumps(data, separators=(',',':'))  # converting tuple to string for sending
            c.send(data)
        elif message[0] == 'index_regex':
            reg = message[1]
            files = os.listdir(directory)
            act_files = []
            for f in files:
                if re.search(reg,f) != None:
                    act_files.append(f)
            data = []
            for f in act_files:
                temp = directory + '/' + f
                file_size = os.path.getsize(temp)
                seconds = os.path.getmtime(temp)
                timestamp = time.ctime(os.path.getmtime(temp))
                if os.path.isdir(temp) == True:
                    name_type = 'Directory'
                else:
                    name_type = 'File'
                dict = {'Name': f,'Size': file_size,'Seconds': seconds,'Timestamp': timestamp,'Type': name_type}
                data.append(dict)
            data = json.dumps(data, separators=(',',':'))  # converting tuple to string for sending
            c.send(data)
        elif message[0] == 'index_shortlist':
            data = []
            start_time = int(message[1]) # greater value
            end_time = int(message[2])   # lesser value since value is the time difference of modification
            files = os.listdir(directory)
            for f in files:
                temp = directory + '/' + f
                file_size = os.path.getsize(temp)
                seconds = os.path.getmtime(temp)
                timestamp = time.ctime(os.path.getmtime(temp))
                if os.path.isdir(temp) == True:
                    name_type = 'Directory'
                else:
                    name_type = 'File'
                if (end_time <= seconds) and (seconds <= start_time):
                    dict = {'Name': f,'Size': file_size,'Seconds': seconds,'Timestamp': timestamp,'Type': name_type}
                    data.append(dict)
            data = json.dumps(data, separators=(',',':'))  # converting tuple to string for sending
            c.send(data)
        elif message[0] == 'hash_verify':
            f = message[1]                  # the file name
            temp = directory + '/' + f
            data = []
            if os.path.exists(temp) and os.path.isfile(temp):
                timestamp = time.ctime(os.path.getmtime(temp))
                checksum = md5(temp)
                # hashlib.md5(open(temp,'rb').read()).hexdigest()
                error = 0
                dict = {'Timestamp': timestamp,'Checksum': checksum,'Error': 0}
                data.append(dict)
            else:
                data = [{'Data':'No such File exists in the Shared Directory','Error': 1}]
            data = json.dumps(data, separators=(',',':'))  # converting tuple to string for sending
            c.send(data)
        elif message[0] == 'hash_checkall':
            data = []
            files = os.listdir(directory)
            for f in files:
                temp = directory + '/' + f
                if os.path.isfile(temp):
                    timestamp = time.ctime(os.path.getmtime(temp))
                    checksum = md5(temp)
                    # hashlib.md5(open(temp,'rb').read()).hexdigest()
                    dict = {'Name': f,'Timestamp': timestamp,'Checksum': checksum}
                    data.append(dict)
            data = json.dumps(data, separators=(',',':'))  # converting tuple to string for sending
            c.send(data)
        elif message[0] == 'download_TCP':
            data = []
            for i in range(1,len(message)):
                obj = TCPfilesend(c,directory,message[i])
                if obj != None:
                    data.append(obj)
            data = json.dumps(data, separators=(',',':'))  # converting tuple to string for sending
            c.send(data)
        elif message[0] == 'download_UDP':
            transferport = 5135
            transfersock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            transfersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for reusing the same hostname
            transfersock.bind((host, transferport))
            client = ('127.0.0.1',5136)
            data = []
            for i in range(1,len(message)):
                obj = UDPfilesend(transfersock,client,directory,message[i])
                if obj != None:
                    data.append(obj)
            data = json.dumps(data, separators=(',',':'))  # converting tuple to string for sending
            c.send(data)
    c.close()

if __name__ == '__main__':
    Main()
