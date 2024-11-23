__author__ = 'Matan'

# 2.6  client server October 2021
import socket, random, traceback
import sys
import time, threading, os, datetime
from datetime import datetime
import math
from turtledemo.penrose import start

from tcp_by_size import send_with_size, recv_by_size

all_to_die = False  # global
FOUND = False
client_sock = 0  # global
ACTIVE = []
WAITING = []
CURRENT = 1
CHUNK = 1000000
CLIENTS = {}
TARGET = ''
start_time = 0
def send_parts(number_of_parts,sock):
    global CURRENT
    global WAITING
    global ACTIVE
    global CLIENTS
    global TARGET
    reply = f'SEND~{TARGET}~'
    lst = []
    for i in range(1, number_of_parts+1):
        WAITING.remove(CURRENT)
        ACTIVE.append(CURRENT)
        reply += f'{CURRENT}~'
        lst.append(CURRENT)
        CURRENT = WAITING[0]
    reply = reply[:-1]
    CLIENTS[sock] = lst
    sock.settimeout(80)
    return reply.encode()

def protocol_build_reply(request, sock):
    global CURRENT
    global WAITING
    global ACTIVE
    global CLIENTS
    global FOUND
    request = request.decode()
    request_code = request[:4]
    fields = request.split('~')
    reply = ''
    if request_code == 'CPPE':
        percent = int(fields[2])/100
        number_of_parts = percent*int(fields[1])
        number_of_parts = math.floor(number_of_parts)
        return send_parts(number_of_parts,sock)
    if request_code == 'FINS':
        lst = CLIENTS[sock]
        number_of_parts = len(lst)
        for i in lst:
            ACTIVE.remove(i)
        if not FOUND:
            return send_parts(number_of_parts,sock)
        print(f'It Took {time.time() - start_time} Seconds!')
        print(f'FOUND THE TARGET!!!: {str(fields[1]).zfill(10)} {datetime.now()}')
        return b'EXIT'
    if request_code == 'FIND':
        print(f'It Took {time.time() - start_time} Seconds!')
        FOUND = True
        print(f'FOUND THE TARGET!!!: {str(fields[1]).zfill(10)} {datetime.now()}')
        return b'EXIT'
    if request_code == 'LEVC':
        if FOUND:
            return b'LEVS'
    return reply.encode()


def handle_request(request, sock):
    try:
        request_code = request[:4]
        to_send = protocol_build_reply(request, sock)
        if request_code == b'EXIT' or to_send == b'EXIT':
            return to_send, True
    except Exception as err:
        print(traceback.format_exc())
        to_send = b'ERRR~001~General error'
    return to_send, False


def handle_client(sock, tid, addr):
    global all_to_die
    finish = False
    print(f'New Client number {tid} from {addr}')
    while not finish:
        if all_to_die:
            print('will close due to main server issue')
            break
        try:
            byte_data = recv_by_size(sock)
            to_send, finish = handle_request(byte_data, sock)
            if to_send != b'':
                send_with_size(sock, to_send)
            if finish:
                time.sleep(1)
                break
        except socket.timeout:
            print("No response from the client within 10 seconds. Stopping communication.")
            break
        except socket.error as err:
            print(f'Socket Error exit client loop: err:  {err}')
            break
        except Exception as err:
            print(f'General Error %s exit client loop: {err}')
            print(traceback.format_exc())
            break
    if finish:
        lst = CLIENTS[sock]
        for i in lst:
            ACTIVE.remove(i)
        del CLIENTS[sock]
    else:
        if sock in CLIENTS:
            lst = CLIENTS[sock]
            for i in lst:
                WAITING.append(i)
                ACTIVE.remove(i)
            del CLIENTS[sock]
    print(f'Client {tid} Exit')
    sock.close()


def active_waiting():
    global CHUNK
    global WAITING
    num = 10000000000//CHUNK
    for i in range(1,num+1):
        WAITING.append(i)


def main(target):
    global all_to_die
    global TARGET
    global start_time
    active_waiting()
    target = target.lower()
    TARGET = target
    threads = []

    srv_sock = socket.socket()

    srv_sock.bind(('0.0.0.0', 1233))

    srv_sock.listen(30)

    # next line release the port
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    i = 1
    while True:
        print('\nMain thread: before accepting ...')
        cli_sock, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
        if i == 1:
            start_time = time.time()
        t.start()
        i += 1
        print(i)
        threads.append(t)
        if i > 100000000:  # for tests change it to 4
            print('\nMain thread: going down for maintenance')
            break

    all_to_die = True
    print('Main thread: waiting to all clints to die')
    for t in threads:
        t.join()
    srv_sock.close()
    print('Bye ..')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('EC9C0F7EDCC18A98B1F31853B1813301')
