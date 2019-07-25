import argparse
from COMPS import Client, AuthManager

__comps_client_version = 10


class TestAuthManager(AuthManager):
    _times_prompted = 0
    _username = None
    _password = None

    @classmethod
    def _prompt_user_for_creds(cls):
        cls._times_prompted = cls._times_prompted + 1
        if cls._times_prompted > 3:
            raise RuntimeError('Failure authenticating')
        print("Hit here")
        return {'Username': cls._username, 'Password': cls._password}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--comps_url', default='https://comps2.idmod.org', help='comps url')
    parser.add_argument('--username', default='pycomps_bamboo', help='username')
    parser.add_argument('--password', default='Password123', help='password')

    args = parser.parse_args()

    compshost = args.comps_url
    TestAuthManager._username = args.username
    TestAuthManager._password = args.password

    # Clear auth_token first in case we change to other user
    Client._Client__auth_manager = TestAuthManager(compshost)
    Client._Client__auth_manager.clear_auth_token()
    Client.login(compshost)
