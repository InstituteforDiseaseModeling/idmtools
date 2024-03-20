import argparse
import json


def run_model(a, b):
    with open("output.json", 'w') as out:
        json.dump(dict(a=a, b=b, c=a+b), out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", type=int)
    parser.add_argument("--b", type=int)

    args = parser.parse_args()
    run_model(args.a, args.b)
