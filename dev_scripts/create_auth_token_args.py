#!/usr/bin/env python
"""Creates a Token to be used on the COMPS platform.

This script is mostly used by automation.
"""
import argparse
import os
import sys
from COMPS import Client  # noqa: I900
from COMPS.CredentialPrompt import CredentialPrompt  # noqa: I900

__comps_client_version = 10


class StaticCredentialPrompt(CredentialPrompt):
    """Allows us to statically define username/password for COMPS Prompt at RunTime."""
    def __init__(self, comps_url, username, password):
        """Creates our Credential Prompt.

        Args:
            comps_url: URL to login to
            username: Username to use
            password: Password
        """
        if (comps_url is None) or (username is None) or (password is None):
            print("Usage: python create_auth_token_args.py --comps_url url --username username --password pwd")
            print("\n")
            raise RuntimeError('Missing comps_url, or username or password')
        self._times_prompted = 0
        self.comps_url = comps_url
        self.username = username
        self.password = password

    def prompt(self):
        """Instead of prompting we instead just return our username and password.

        Returns:
            Username and Password dict
        """
        print("logging in with hardcoded user/pw")
        self._times_prompted = self._times_prompted + 1
        if self._times_prompted > 3:
            raise RuntimeError('Failure authenticating')
        print("Hit here")
        return {'Username': self.username, 'Password': self.password}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--comps_url', default='https://comps2.idmod.org', help='comps url')
    parser.add_argument('--username', help='entry username')
    parser.add_argument('--password', default=os.getenv("COMPS_PASS", None), help='entry password')

    args = parser.parse_args()
    if args.password is None:
        print("Password is required either through COMPS_PASS environment var or through --password")
        sys.exit(-1)

    compshost = args.comps_url

    Client.login(compshost, StaticCredentialPrompt(comps_url=args.comps_url, username=args.username,
                                                   password=args.password))
