'''User login module.'''

# import os
import hashlib
import binascii
import NBackUserDatabase

class UserSession(object):
    '''Object that is only bridge to database allowed if database is on a
    server.'''

    def __init__(self: 'UserSession') -> None:
        
        self.user_name = ''
        self.user_password_hash = b''
        self.account_info = None
        self.dummy_info = {} # Make nonsense user entry here.
        self.db_connection = NBackUserDatabase.NBackUserDatabase()

    def login(self: 'UserSession', username: str, psswrd: str) -> None:

        try:

            self.db_connection.get_user(username)
            self.account_info = self.db_connection.user_accnt

        except:

            self.account_info = self.dummy_info

        psswrd = bytes((user_salt + psswrd), 'utf-8')
        hshd_pw = hashlib.pbkdf2_hmac('SHA512', psswrd, user_salt, 1000000)
        binascii.hexlify(hshd_pw)

        

if __name__ == '__main__':

    raise NotImplementedError