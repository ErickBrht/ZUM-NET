#!/usr/bin/env python


#uiuiuiu

import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = "" 
target = ""
upload_destination = ""
port = 0


def usage():
    print "Ferramenta baseada no netcat"
    print "ZUM Net Tool"
    print 
    
    print "To use the tool: zum.py -t target_host -p port"

    print "-l --listen                   - listen on [host]:[port] for incoming connections"
    print "-e --execution                - execute the given file upon receiving a connections"
    print "-c --command                  - initialize a command shell"
    print "-u --upload=destination       - upon receiving connection upload a file and write to [destination]"
    
    print 
    print 
    
    print "Exemples: "
    print 
    print "zum.py -t 192.168.0.1 -p 5555 -l -c"
    print "zum.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "zum.py -t 192.168.0.1 -p 5555 -l -e=\'cat /etc/passwd'"
    print "echo 'ZUMMMMMMM' | ./zum.py -t 192.111.22.33 -p 135"
    sys.exit(0)

def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)
        while True:
            recv_len = 1 
            response = ""
            
            while recv_len:
                data      = client.recv(4096)
                recv_len  = len(data)
                response += data
                if recv_len < 4096:
                    break
            
            print response
            
            buffer = raw_input("")
            buffer += "\n"
            
            client.send(buffer)
    except:
        print "[*] Exception!!! Exiting."
        client.close()

def client_handler(client_socket):
    global upload
    global execute
    global command
    
    if len(upload_destination):
        file_buffer = ""
        
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            else:
                file_buffer += data
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor = write(file_buffer)
            file_descriptor = close()
            client_socket.send("Sucessfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)
    
    if command:
        while True:
            client_socket.send("<ZUM:#> ")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer)
            client_socket.send(response)
        
        
def run_command(command):
    command = command.rstrip()
    
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command. \r\n"
        
    return output


def main():
    global listen
    global port 
    global execute 
    global command 
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
        
    if not listen and len(target) and port > 0:
    #Caso queira enviar dados de forma interativa, sera necessario utilizar o CTRL+D#
    #If you want to send data interactively, you will need to use CTRL + D#
        buffer = sys.stdin.read()
        
        client_sender(buffer)
    if listen:
        server_loop()

main()

#uiuiui 2