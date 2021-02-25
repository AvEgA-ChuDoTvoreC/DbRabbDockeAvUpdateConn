import argparse
import sys
from socket import *
from threading import *
from tqdm import tqdm


class ScanIP():

    screenLock = Semaphore(value=1)
    open_ports = []

    def __init__(self, args):
        self.ip = args.ip
        self.ports = str(args.ports).split(',')
        self.port_list = []
        for port in self.ports:
            try:
                if '-' in port:
                    l2 = port.split('-')
                    for x in range(int(l2[0]), int(l2[1]) + 1):
                        self.port_list.append(x)
                else:
                    self.port_list.append(int(port))
            except ValueError as ve:
                print(str(ve) + '\nНеверно указан порт (диапазон портов)')
                sys.exit()
        self.portScan(self.ip, self.port_list)

    def portScan(self, ip, port_list):
        setdefaulttimeout(1)
        threads = []
        port_list_split = []
        size = 256
        while len(port_list) > size:
            piece = port_list[:size]
            port_list_split.append(piece)
            port_list = port_list[size:]
        port_list_split.append(port_list)
        for port_list in tqdm(port_list_split):
            for port in port_list:
                t = Thread(target=self.connScan, args=(ip, port))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
        for item in self.open_ports:
            print(item)

    def connScan(self, ip, port):
        try:
            connSkt = socket(AF_INET, SOCK_STREAM)
            connSkt.connect((ip, port))
            connSkt.send('fffffffffffffffffffffff\r\n'.encode())
            results = connSkt.recv(100)
            self.screenLock.acquire()
            self.open_ports.append('[+]{0} open'.format(port))
        except Exception as ex:
            self.screenLock.acquire()
        finally:
            self.screenLock.release()
            connSkt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='''%(prog)s [опции]\nДля вызова помощи: %(prog)s -h''')
    parser.add_argument('ip', action='store', type=str, help='spec target host')
    parser.add_argument('ports', action='store', type=str, help='spec target port')
    args = parser.parse_args()
    scan = ScanIP(args)