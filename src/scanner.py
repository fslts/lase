import nmap
import time
import math
import hashlib
import socket

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


class OnlineScanner:

    def __init__(self):
        self._nm = nmap.PortScanner()
        self.online = []

    def scan_range(self, range_):
        res = []
        nmap_res = self._nm.scan(hosts=range_, arguments='-Pn -p 445')
        for ip, data in nmap_res['scan'].items():

            #TODO to method
            ports = [ port for port, port_data in data['tcp'].items() if port_data['state'] == 'open' ]

            if ports:
                res.append(ScannedHost(ip, ports))
        return res

def traverse(ftp, depth=0):
    """
    return a recursive listing of an ftp server contents (starting
    from the current directory)

    listing is returned as a recursive dictionary, where each key
    contains a contents of the subdirectory or None if it corresponds
    to a file.

    @param ftp: ftplib.FTP object
    """
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
    #return level

def shares(conn):
    return ( share.name for share in conn.listShares() if not share.isSpecial )

def smbwalk_shares(conn, es):
    for share in shares(conn):
        print(share)
        smbwalk(conn, es, share, '/')

def smbwalk(conn, es, share, path):
    try:
        for item in conn.listPath(share, path):
            if item.filename in ['.', '..']:
                continue
            #print(path + item.filename)
            new_path = path + item.filename

            es.index(index='lase_alt', doc_type='file', id=hashlib.sha1(new_path.encode('utf-8')).hexdigest(), body={'filename':item.filename, 'path':new_path})
            if item.isDirectory:
                smbwalk(conn, es, share, path + item.filename + '/')
    except smb.smb_structs.OperationFailure as e:
        #TODO dorobit
        print(e)
        #print('error')




def main():
   # ftp = ftplib.FTP('147.175.187.131')
   # ftp.connect()
   # ftp.login()
   # ftp.set_pasv(True)
   # level = traverse(ftp)
   # print(level)

    osc = OnlineScanner()
    scanned = osc.scan_range('147.175.187.0/24')

    start = time.time()
    es = Elasticsearch()

    for host in scanned:
        print(host.host_name())
        conn = SMBConnection('', '', 'lase', host.host_name())
        conn.connect(host.ip, 445)
        smbwalk_shares(conn, es)

    print(time.time() - start)

if __name__ == '__main__':
    main()


