import nmap
import time
import math
import hashlib
import socket
import ipaddress

import ftplib
import smb
from smb.SMBConnection import SMBConnection
from elasticsearch import Elasticsearch

class ScannedHost:
    def __init__(self, ip, ports):
        self.ip = ip
        self.ports = ports
        self._host_name = None

    def host_name(self):
        if not self._host_name:
            (self._host_name, _, _) = socket.gethostbyaddr(self.ip)
        return self._host_name

    def remote_name(self):
        return self.host_name().split('.')[0]


class OnlineScanner:

    def __init__(self):
        self._nm = nmap.PortScanner()
        self.online = []

    def scan_range(self, range_):
        res = []
        nmap_res = self._nm.scan(hosts=range_, ports='445', arguments='-Pn')
        for ip, data in nmap_res['scan'].items():
            print(ip)

            #TODO to method
            ports = [ port for port, port_data in data['tcp'].items() if port_data['state'] == 'open' ]

            if ports:
                res.append(ScannedHost(ip, ports))
        return res

def traverse(ftp, depth=0):

    if depth > 10:
        return ['depth > 10']
    level = {}
    for entry in (path for path in ftp.nlst() if path not in ('.', '..')):
        try:
            print(entry)
            ftp.cwd(entry)
            traverse(ftp, depth+1)
            ftp.cwd('..')
        except ftplib.error_perm:
            pass

def shares(conn):
    return ( share.name for share in conn.listShares() if not share.isSpecial )

def smbwalk_shares(conn, es):

    for share in shares(conn):
        print(share)
        smbwalk(conn, es, share, '/')


def smbwalk(conn, es, share, path):
    try:
        for item in conn.listPath(share, path):
            if item.filename in ['.', '..', '']:
                continue
            #print(path + item.filename)
            full_path = path + item.filename

            #TODO visitor
            es.index(index='lase_alt', doc_type='file', id=hashlib.sha1(newpath.encode('utf-8')).hexdigest(), body={'filename':item.filename, 'path':path})

            if item.isDirectory:
                smbwalk(conn, es, share, path + item.filename + '/')
    except smb.smb_structs.OperationFailure as e:
        #TODO logger
        print(e)

def main():
   # ftp = ftplib.FTP('147.175.187.131')
   # ftp.connect()
   # ftp.login()
   # ftp.set_pasv(True)
   # level = traverse(ftp)
   # print(level)

    osc = OnlineScanner()
    #TODO to config
    scanned = osc.scan_range('147.175.187.2-254')

    start = time.time()
    es = Elasticsearch()

    for host in scanned:
        print(host.host_name())
        try:
            conn = SMBConnection('', '', 'lase', host.remote_name())
            conn.connect(host.ip)

            smbwalk_shares(conn, es)
        except socket.timeout:
            #TODO logger
            print('timeout')
        except smb.base.NotReadyError as e:
            #TODO logger
            print(e)

    print(time.time() - start)


if __name__ == '__main__':
    main()
