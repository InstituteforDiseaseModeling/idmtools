import sys
import time

if __name__ == "__main__":
    sleep_time = 10 if sys.argv[1] is None else int(sys.argv[1])
    time.sleep(sleep_time)