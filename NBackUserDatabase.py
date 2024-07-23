'''Database object for Dual-n Back.'''

import datetime
import pickle
import os

class NoSuchUserError(Exception):
    pass

#dbcon = sqlite3.connect('resources/nbackusers.db')
#cur = dbcon.cursor()
#cur.execute('select name from sqlite_master where type=\'table\'')
#<sqlite3.Cursor object at 0x000000000313DAB0>
#for t in cur:
  #print(t[0])

import sqlite3

class NBackUserDatabase(object):
    '''Object that does our standard SQLite operations.'''

    def __init__(self: 'NBackUserDatabase') -> None:
        '''Object initialization.'''

        self.db_connection = sqlite3.connect('resources/nbackusers.db')
        # DB contains table "users (user_number integer primary key 
        # autoincrement, user_name text, hashed_password text, pw_salt text,
        # user_trivia blob, last_session_stats blob, full_history blob)"
        # since user_number is auto incremented, do not assign directly,
        # and must always use colum names.
        self.user_accnt = {}

    def get_user(self: 'NBackUserDatabase', user_name: int) -> dict:
        '''Return dictionary pickle of user.  If no such user exists, raises a
        NoSuchUserError exception.'''
        
        cur = self.db_connection.cursor()
        if user_name in cur:
            user_data
            #return it
        raise NoSuchUserError
    
    def add_user(self: 'NBackUserDatabase', new_name: str) -> None:
        
        #cur.execute('''insert into users (user_display_name, session_details) values ('hitler', 12)''')
        
        #DB OBJECT not cursor commits

        user_details ={}
        # If active_account is False, no new sessions or other updating allowed
        user_details['active_account'] = True
        user_details['account_created'] = str(datetime.datetime.today())

        user_salt = os.urandom(64)
        pass



