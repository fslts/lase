import nmap
import time
import math
import hashlib

import ftplib
import smb
from smb.SMBConnection import SMBConnection
from elasticsearch import Elasticsearch

class OnlineScanner:

    def __init__(self):
        self._nm = nmap.PortScanner()
        self.online = []

    def scan_range(self, range_):
        res = self._nm.scan(hosts=range_, arguments='-p 21')
        print(res)
        self.online = self._nm.all_hosts()
        return self.online

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

            es.index(index='files', doc_type='file', id=hashlib.sha1(new_path.encode('utf-8')).digest(), body={'filename':item.filename, 'path':new_path})
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

    start = time.time()
    es = Elasticsearch()

    conn = SMBConnection('', '', 'lase', 'sadista')
    conn.connect('sadista.ynet.sk')
    ans = smbwalk_shares(conn, es)
    print(ans)

    #print(verify_hosts(hosts_to_test()))
    #print(isOpen('192.168.1.13', 445))
   # osc = OnlineScanner()
   # print(osc.scan_range('147.175.187.0/24'))
    print(time.time() - start)

if __name__ == '__main__':
    main()


