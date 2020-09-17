import argparse
import sys

import requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Notify Microsoft Flow of an event')
    parser.add_argument('--url', help='Flow HTTP Url')
    parser.add_argument('--message', help="Message to alert")
    parser.add_argument('--title', default=None, help="Message Title")
    args = parser.parse_args()

    title = args.title if args.title else "COMPS"
    body = dict(message=args.message, url="TODO", title=title, status="TODO")
    r = requests.post(args.url, json=body)

    if r.status_code not in [202, 200]:
        print(r.content)
        print(r.status_code)
        sys.exit(-1)
