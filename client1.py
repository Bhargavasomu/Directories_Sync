import socket
import os
import json
import re
import hashlib
import time
import stat

def parse(string):
    return string.split()

def md5(fname):
	hash = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash.update(chunk)
	return hash.hexdigest()

def longlist(socket):
    msg = ['index_longlist']
    msg = json.dumps(msg, separators=(',',':'))  # serializing the message that is to be sent to server
    socket.send(msg)
    data = socket.recv(40096)
    data = json.loads(data) # deserializing json data
    return data

def shortlist(socket,start,end):
    msg = ['index_shortlist',start,end] # start > end
    msg = json.dumps(msg, separators=(',',':'))
    socket.send(msg)
    data = socket.recv(40096)
    data = json.loads(data) # deserializing json data
    return data

def hashverify(socket,fname):
    msg = ['hash_verify',fname]
    msg = json.dumps(msg, separators=(',',':'))
    socket.send(msg)
    data = socket.recv(40096)
    data = json.loads(data) # deserializing json data
    return data

def TCPreq(socket,key_word,directory,display_flag):
    msg = ['download_TCP']
    for i in range(2,len(key_word)):
        msg.append(key_word[i])
    if display_flag == 1:
        print
    msg = json.dumps(msg, separators=(',',':'))
    socket.send(msg)                          # send message to parent socket but receive from file socket
    for i in range(2,len(key_word)):
        if display_flag == 1:
            print "Attempting to download",key_word[i]
            print "....."
        size = int(socket.recv(1024))
        socket.send('R')
        if size == -1:
            print "The File",key_word[i],"was not found in the other directory"
            print
        else:
            path = directory + '/' + key_word[i]
            f = open(path ,'wb+')     # creates a new file if not there
            if size > 0:
                size_read = 0
                while True:
                    content = socket.recv(1024)
                    f.write(content)
                    size_read = size_read + len(content)
                    if (not content) or (size_read >= size):
                        break
            socket.send('O')
            perm = socket.recv(1024)
            perm = int(perm)
            os.chmod(path,perm)
            socket.send('O')
            f.close()
            if display_flag == 1:
                print "Download Complete"
                print
    data = socket.recv(40096)         #for displaying the file's data
    data = json.loads(data)          # deserializing json data
    return data

# def sync_dir(socket,serv_dir):
#     for root, dirs, files in os.walk(serv_dir):
#         break
#     for f in files:
#         temp = serv_dir + "/" + f
#         if os.path.exists(temp) == False:
#             waste = TCPreq(socket,['download','TCP',f['Name']],directory,0)
#         else:       # file exists but now we have to check for modification
#             current_checksum = md5(temp)
#             TCPreq(socket,['download','TCP',f['Name']],directory,0)

def sync(socket,directory):
    files = longlist(socket)
    serv_dir = '/home/bhargava/Academics/2-2/Assignments/Computer Networks/Assignment1/shared2'
    for f in files:
        temp = directory + "/" + f['Name']
        if str(f['Type']) == 'File':
            if os.path.exists(temp) == False:
                waste = TCPreq(socket,['download','TCP',f['Name']],directory,0)
            else:       # file exists but now we have to check for modification
                current_checksum = md5(temp)
                obj = hashverify(socket,f['Name'])
                verify_checksum = obj[0]['Checksum']
                if str(current_checksum) != str(verify_checksum):
                    TCPreq(socket,['download','TCP',f['Name']],directory,0)
        # else:
        #     path = serv_dir + f
        #     sync_dir(socket,path)
    print "Synced"

def Main():
    host = '127.0.0.1'                  # IP address of server 1
    directory = '/home/bhargava/Academics/2-2/Assignments/Computer Networks/Assignment1/shared1'   # shared directory in server 1
    port = 5002                         # port num of this process
    s = socket.socket()
    s.connect((host,port))

    command = raw_input("-> ")
    key_word = parse(command)
    while key_word[0] != 'q':
        if key_word[0] == 'index':
            if key_word[1] == 'longlist':
                data = longlist(s)
                print "Received the following data from Server"
                print
                column_width = 25
                print "\t"+str('NAME').ljust(column_width),str('SIZE').ljust(column_width),str('SECONDS').ljust(column_width),str('TIMESTAMP').ljust(column_width),str('TYPE').ljust(column_width)
                print
                for d in data:
                    print "\t"+str(d['Name']).ljust(column_width),str(d['Size']).ljust(column_width),str(d['Seconds']).ljust(column_width),str(d['Timestamp']).ljust(column_width),str(d['Type']).ljust(column_width)
                print
            elif key_word[1] == 'regex':
                msg = ['index_regex',key_word[2]]
                msg = json.dumps(msg, separators=(',',':'))
                s.send(msg)
                data = s.recv(40096)
                data = json.loads(data) # deserializing json data
                print "Received the following data from Server"
                print
                column_width = 25
                print "\t"+str('NAME').ljust(column_width),str('SIZE').ljust(column_width),str('SECONDS').ljust(column_width),str('TIMESTAMP').ljust(column_width),str('TYPE').ljust(column_width)
                print
                for d in data:
                    print "\t"+str(d['Name']).ljust(column_width),str(d['Size']).ljust(column_width),str(d['Seconds']).ljust(column_width),str(d['Timestamp']).ljust(column_width),str(d['Type']).ljust(column_width)
                print
            elif key_word[1] == 'shortlist':
                data = shortlist(s,key_word[2],key_word[3])
                print "Received the following data from Server"
                print
                column_width = 25
                print "\t"+str('NAME').ljust(column_width),str('SIZE').ljust(column_width),str('SECONDS').ljust(column_width),str('TIMESTAMP').ljust(column_width),str('TYPE').ljust(column_width)
                print
                for d in data:
                    print "\t"+str(d['Name']).ljust(column_width),str(d['Size']).ljust(column_width),str(d['Seconds']).ljust(column_width),str(d['Timestamp']).ljust(column_width),str(d['Type']).ljust(column_width)
                print
            else:
                print
                print "Unknown Flags under index command: Please use longlist, shortlist or regex as one of the flags"
                print

        elif key_word[0] == 'hash':
            if key_word[1] == 'verify':
                data = hashverify(s,key_word[2])
                print "Received the following data from Server"
                print
                if int(data[0]['Error']) == 1:
                    print data[0]['Data']
                    print
                else:
                    column_width = 40
                    print "\t"+str('CHECKSUM').ljust(column_width),str('TIMESTAMP').ljust(column_width)
                    print
                    for d in data:
                        print "\t"+str(d['Checksum']).ljust(column_width),str(d['Timestamp']).ljust(column_width)
                    print
            elif key_word[1] == 'checkall':
                msg = ['hash_checkall']
                msg = json.dumps(msg, separators=(',',':'))
                s.send(msg)
                data = s.recv(1024)
                data = json.loads(data) # deserializing json data
                print "Received the following data from Server"
                print
                column_width = 40
                print "\t"+str('NAME').ljust(column_width),str('CHECKSUM').ljust(column_width),str('TIMESTAMP').ljust(column_width)
                print
                for d in data:
                    print "\t"+str(d['Name']).ljust(column_width),str(d['Checksum']).ljust(column_width),str(d['Timestamp']).ljust(column_width)
                print
            else:
                print
                print "Unknown Flags under hash command: Please use verify or checkall as one of the flags"
                print

        elif key_word[0] == 'download':
            if key_word[1] == 'TCP':
                data = TCPreq(s,key_word,directory,1)
                print "Received the following data from Server"
                print
                column_width = 30
                print "\t"+str('NAME').ljust(column_width),str('SIZE').ljust(column_width),str('TIMESTAMP').ljust(column_width),str('HASH').ljust(column_width)
                print
                for d in data:
                    print "\t"+str(d['Name']).ljust(column_width),str(d['Size']).ljust(column_width),str(d['Timestamp']).ljust(column_width),str(d['Hash']).ljust(column_width)
                print
            elif key_word[1] == 'UDP':
                transferport = 5136                 # UDP transfer socket
                transfersock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                transfersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for reusing the same hostname
                transfersock.bind((host, transferport))
                msg = ['download_UDP']
                for i in range(2,len(key_word)):
                    msg.append(key_word[i])
                print
                msg = json.dumps(msg, separators=(',',':'))
                s.send(msg)                          # send message to parent socket but receive from file socket
                for i in range(2,len(key_word)):
                    print "Attempting to download",key_word[i]
                    print "....."
                    size,addr = transfersock.recvfrom(1024)
                    size = int(size)
                    transfersock.sendto('R',addr)
                    if size == -1:
                        print "The File",key_word[i],"was not found in the other directory"
                        print
                    else:
                        path = directory + '/' + key_word[i]
                        f = open(path ,'wb+')     # creates a new file if not there
                        if size > 0:
                            size_read = 0
                            while True:
                                content,addr = transfersock.recvfrom(1024)
                                f.write(content)
                                size_read = size_read + len(content)
                                if (not content) or (size_read >= size):
                                    break
                        f.close()
                        transfersock.sendto('O',addr)
                        perm,addr = transfersock.recvfrom(1024)
                        perm = int(perm)
                        transfersock.sendto('O',addr)
                        os.chmod(path,perm)
                        print "Download Complete"
                        print
                data = s.recv(40096)         #for displaying the file's data
                data = json.loads(data) # deserializing json data
                print "Received the following data from Server"
                print
                column_width = 35
                print "\t"+str('NAME').ljust(15),str('SIZE').ljust(10),str('TIMESTAMP').ljust(25),str('ORIGINAL HASH').ljust(column_width),str('HASH AFTER TRANSFER').ljust(column_width)
                print
                for d in data:
                    temp = directory + '/' + str(d['Name'])
                    checksum = md5(temp)
                    # hashlib.md5(open(temp,'rb').read()).hexdigest()
                    print "\t"+str(d['Name']).ljust(15),str(d['Size']).ljust(10),str(d['Timestamp']).ljust(25),str(d['Hash']).ljust(column_width),str(checksum).ljust(column_width)
                    if str(checksum) == str(d['Hash']):
                        print "\tSuccessfully Received The File",d['Name'],"without contents changed"
                    else:
                        print "\tEncountered and Error in receiving Please download again as the contents may have changed"
                    print
                print
            else:
                print
                print "Unknown Flags under download command: Please use TCP or UDP as one of the flags"
                print

        else:
            print
            print "Unidentified Command: Please use commands starting with index or hash or download"
            print
        sync(s,directory)
        command = raw_input("-> ")
        key_word = parse(command)
    s.close()

if __name__ == '__main__':
    Main()
