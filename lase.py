import sys
import time
import multiprocessing

import config
import src.producer.producer as producer


def main():

    reload(sys)
    sys.setdefaultencoding("utf-8")

    start = time.time()
    print(time.time() - start)

    producer.scan(config.ranges)

    print(time.time() - start)

if __name__ == '__main__':
    main()
