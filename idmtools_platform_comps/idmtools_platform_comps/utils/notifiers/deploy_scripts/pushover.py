import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Notify Pushover of an event')
    parser.add_argument('--token', help='Main script to execute')
    parser.add_argument('--user-key', help='User Key')
    parser.add_argument('--message', help="Message to alert")
    parser.add_argument('--title', default=None, help="Message Title")
    args = parser.parse_args()
    from pushover import init, Client
    init(args.token)
    title = args.title if args.title else "COMPS"
    print("Sending notification to Pushover")
    Client(args.user_key).send_message(args.message, title=title)
