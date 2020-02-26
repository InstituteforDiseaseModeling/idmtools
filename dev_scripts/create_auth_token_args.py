import argparse
from COMPS import Client
from COMPS.CredentialPrompt import CredentialPrompt

__comps_client_version = 10


class StaticCredentialPrompt(CredentialPrompt):
    def __init__(self, comps_url, username, password):
        self._times_prompted = 0
        self.comps_url = comps_url
        self.username = username
        self.password = password

    def prompt(self):
        print("logging in with hardcoded user/pw")
        self._times_prompted = self._times_prompted + 1
        if self._times_prompted > 3:
            raise RuntimeError('Failure authenticating')
        print("Hit here")
        return {'Username': self.username, 'Password': self.password}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--comps_url', default='https://comps2.idmod.org', help='comps url')
    parser.add_argument('--username', default='pycomps_bamboo', help='username')
    parser.add_argument('--password', default='Password123', help='password')

    args = parser.parse_args()

    compshost = args.comps_url

    Client.login(compshost, StaticCredentialPrompt(comps_url=args.comps_url, username=args.username,
                                                   password=args.password))
