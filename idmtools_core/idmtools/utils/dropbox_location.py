import os


def get_current_user():
    # Returns current logged in user for Windows filesystem
    import getpass
    return getpass.getuser()


def get_dropbox_location():
    user = get_current_user()
    dropbox_filepath = os.path.join("C:/Users/", "mfisher", "Dropbox (IDM)")
    # dropbox_filepath = os.path.join("C:/Users/", user, "Dropbox (IDM)/Malaria Team Folder/")
    return dropbox_filepath
