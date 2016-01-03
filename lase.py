import sys

import config
import src.scanner as scanner

def main():

    reload(sys)
    sys.setdefaultencoding("utf-8")

    scanner.scan(config.ranges)

if __name__ == '__main__':
    main()
