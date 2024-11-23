import socket
import subprocess
import time
import traceback
from tcp_by_size import send_with_size, recv_by_size
import sys

CHUNK = 1000000  # Global
TARGET = ''
RESULT = None
FINAL_CPU = 1


def handle_reply(request, sock):
    global TARGET
    global RESULT
    request = request.decode()
    request_code = request[:4]
    fields = request.split('~')
    if request_code == 'SEND':
        TARGET = fields[1]
        lst = []
        for i in fields[2:]:
            lst.append(i)
        start_time = time.time()

        process_s = []
        for i in range(len(lst)):
            process_s.append(subprocess.Popen(['python', 'subprocess_task.py', lst[i], TARGET], stdout=subprocess.PIPE))

        for process in process_s:
            output, error = process.communicate()
            if output:
                RESULT = output.decode().strip()  # Get the found result
                print(f'MD5 found! The number is: {RESULT}')
                break
            if error:
                print(f'Error in subprocess: {error.decode()}')

        print(f'It Took {time.time() - start_time} Seconds!')

        if RESULT is not None:
            to_send = f'FIND~{RESULT}'
            send_with_size(sock, to_send)
        else:
            to_send = 'FINS'
            send_with_size(sock, to_send)


def main(ip, num_cpus,percent):
    connected = False
    global FINAL_CPU
    FINAL_CPU = int(num_cpus) * int(percent) / 100
    sock = socket.socket()
    port = 1233
    try:
        sock.connect((ip, port))
        connected = True
    except:
        print(f'Error while trying to connect to {ip}:{port}')

    if connected:
        to_send = f'CPPE~{num_cpus}~{percent}'
        send_with_size(sock, to_send)

    #start_time = time.time()
    #interval = 2
    while connected:
        try:
            #elapsed_time = time.time() - start_time
            #if elapsed_time >= interval:
                #send_with_size(sock, b'LEVC')
                #start_time = time.time()
            byte_data = recv_by_size(sock)
            if byte_data == b'':
                print('Seems server disconnected abnormal')
                break
            if byte_data == b'LEVS':
                print('Seems server found what he wanted')
                break
            handle_reply(byte_data, sock)
        except socket.error as err:
            print(f'Got socket error: {err}')
            break
        except Exception as err:
            print(f'General error: {err}')
            print(traceback.format_exc())
            break

    print('Bye')
    sock.close()


if __name__ == '__main__':
    if len(sys.argv) > 3:
        main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    else:
        main('127.0.0.1', 12, 100)