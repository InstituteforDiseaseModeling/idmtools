import sys
import time

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sleep_time = int(sys.argv[1])
    else:
        sleep_time = 100
    time.sleep(sleep_time)