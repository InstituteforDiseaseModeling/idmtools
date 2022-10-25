"""
utilities for pathing of dropbox folders.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os


def get_current_user():
    """
    Get current user name.

    Returns:
        Current username
    """
    # Returns current logged in user for Windows filesystem
    import getpass
    return getpass.getuser()


def get_dropbox_location():
    """
    Get user dropbox location.

    Returns:
        User dropbox location
    """
    user = get_current_user()
    dropbox_filepath = os.path.join("C:/Users/", user, "Dropbox (IDM)")
    return dropbox_filepath
