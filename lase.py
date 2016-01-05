import sys
import time
import multiprocessing

import config
import src.producer as producer
import src.api as api


def lase_producer():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    start = time.time()

    producer.scan(config.ranges)

    print(time.time() - start)


def main():
    api.run_api()
    #lase_producer()

if __name__ == '__main__':
    main()
