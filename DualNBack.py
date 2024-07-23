'''Dual n-task application.'''

#import os
#import os.path
import sys
import datetime
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import random
import MakeImages
#import sqlite3
import pickle
import TaskWindow as TW
import NBackUserDatabase
import UserLogin
import DNBWizard as DNBW
import MakeStimBuffer

class PythonVersionError(Exception):
    '''Raise if environment version of Python is less than 3.4.'''
    # I'm using the latest pickle protocol, that means 3.4 and up only.
    
    def __init__(self, user_version_info):

        print('\n\nPython must be at least version 3.4 as the latest pickle '
              'protocol is implemented here.\nYour version is ' + str(
                  user_version_info[0]) + '.' + str(
                      user_version_info[1]) + '.', flush = True)

class SettingsObject(QtCore.QObject):
    '''Qt Object whose instance holds present working settings.  When working
    settings are changed, emits signal that application can accept to update
    working environment.'''

    # Signal is emited on change in setting, agnostic as to nature of change.
    settings_changed_signal = QtCore.Signal()

    def __init__(self: 'SettingsObject') -> None:
        '''Initializes instance, adding generic methods of a Qt Object,
        including signal and slot capabilities.'''

        super(SettingsObject, self).__init__()

        # Object is simply a container and signal emitter, so simple dictionary
        # is all that is needed upon initialization.
        self.session_settings = {}

    def set_settings_base_dict(self, setting_dict) -> None:
        '''Replace existing settings dictionary as a whole with new provided
        dictionary then emit a "settings_changed_signal" signal.  Dictionary
        must be a fully valid settings dictionary as no attempt to check
        contents is made.'''

        self.session_settings = setting_dict
        self.settings_changed_signal.emit()

    def set_n(self: 'SettingsObject', new_n: int) -> None:
        '''Set present n for stimulus block creation and then emit a
        "settings_changed_signal" signal. n must be an integer or easily
        convered to an interger or TypeError will be thrown.'''

        self._change_specific_setting('current_n', new_n)

    def set_number_targets(self: 'SettingsObject', new_numb_tar: int) -> None:
        '''Set present number of targets (will be used for all modalities)
        for stimulus block creation and then emit a "settings_changed_signal"
        signal. This number must be an integer or easily convered to an
        interger or TypeError will be thrown.'''

        self._change_specific_setting('number_of_targets', new_numb_tar)

    def set_block_before_n(self: 'SettingsObject',
                           new_block_length: int) -> None:
        '''Set present block length before n and then emit a 
        "settings_changed_signal" signal. This number must be an integer or
        easily convered to an interger or TypeError will be thrown.'''

        self._change_specific_setting('session_length_before_n',
                                      new_block_length)

    def set_total_session_blocks(self: 'SettingsObject',
                                 new_total_blocks: int) -> int:
        '''Set the total blocks to be run for this entire session and then
        emit a "settings_changed_signal" signal. This number must be an
        integer or easily convered to an interger or TypeError will be
        thrown.'''

        self._change_specific_setting('session_blocks', new_total_blocks)

    def set_interstim_time(self: 'SettingsObject',
                           new_interstim_time: int) -> None:
        '''Set the present time between stimulus exposures and then emit a 
        "settings_changed_signal" signal. This number must be an integer or
        easily convered to an interger or TypeError will be thrown.'''

        self._change_specific_setting('interstim_time', new_interstim_time)

    def set_stim_exposure_time(self: 'SettingsObject',
                               new_stim_time: int) -> None:
        '''Set the present time of stimulus exposure and then emit a 
        "settings_changed_signal" signal. This number must be an integer or
        easily convered to an interger or TypeError will be thrown.'''

        self._change_specific_setting('stim_time', new_stim_time)

    def set_bg_colour(self: 'SettingsObject',
                      new_bg_colour: tuple) -> None:
        '''Set the background colour for the task window and then emit a 
        "settings_changed_signal" signal. This must be a tuple of positive 
        integers TypeError will be thrown.'''

        self._change_specific_setting('background_colour', new_bg_colour)

    def set_tg_colour(self: 'SettingsObject',
                      new_tg_colour: tuple) -> None:
        '''Set the target colour for the task window and then emit a 
        "settings_changed_signal" signal. This must be a tuple of positive 
        integers TypeError will be thrown.'''

        self._change_specific_setting('target_colour', new_tg_colour)

    def set_fx_colour(self: 'SettingsObject',
                      new_fx_colour: tuple) -> None:
        '''Set the fixator colour for the task window and then emit a 
        "settings_changed_signal" signal. This must be a tuple of positive 
        integers TypeError will be thrown.'''

        self._change_specific_setting('fixator_colour', new_fx_colour)

    def set_fx_size(self: 'SettingsObject', new_size: int=0) :
        '''Set the fixator colour for the task window and then emit a 
        "settings_changed_signal" signal.  Does nothing yet.'''

        self._change_specific_setting('fixator_size', new_size)

    def _change_specific_setting(self: 'SettingsObject', description: str,
                                 value: int) -> None:
        '''Helper function to change a specific setting in the general setting
        dictionary.  Description is the dictionary key and value is the new
        value to set.'''

        if type(value) == tuple:

            if len(value) != 3:

                raise ValueError

            for coord in value:

                if ((type(coord) != int) or (coord < 0)):

                    raise ValueError

        else:

            try:
                value = int(value)

                # Note: n = 0 is valid since used for training.  n < 0 becomes
                # possible however.  That said it'll still kinda work, but, not
                # really.

                # Why is this even here?
                #if ((new_block_length < 1) and (description != 'current_n')):

                #    raise ValueError

            except:
                raise TypeError

        self.session_settings[description] = value
        self.settings_changed_signal.emit()

    # The get methods that follow are copy/pastey, but all are trivial and a
    # helper method does not in fact increase readability at this point.
    # Could possibly use decorators instead?

    def get_settings_base_dict(self: 'SettingsObject') -> int:
        '''Get and return a copy of the entire base settings dictionary.'''

        return self.session_settings

    def get_number_targets(self: 'SettingsObject') -> int:
        '''Return the present number of targets to be used in calculating the
        upcoming block.'''

        return self.session_settings['number_of_targets']

    def get_n(self: 'SettingsObject') -> int:
        '''Return the present n to be used in calculating the upcoming
        block.'''

        return self.session_settings['current_n']

    def get_block_before_n(self: 'SettingsObject') -> int:
        '''Return the present block length before n added on to be used in
        calculating the upcoming block.'''

        return self.session_settings['session_length_before_n']

    def get_total_block_length(self: 'SettingsObject') -> int:
        '''Return the present total block length to be used in calculating
        the upcoming block.'''

        return (self.get_n() + self.get_block_before_n())

    def get_total_session_blocks(self: 'SettingsObject') -> int:
        '''Return total blocks to be run in this entire session.'''

        return self.session_settings['session_blocks']

    def get_stim_exposure_time(self: 'SettingsObject') -> int:
        '''Return the present stimulus exposure time to be used in
        calculating the upcoming block.'''

        return self.session_settings['stim_time']

    def get_interstim_time(self: 'SettingsObject') -> int:
        '''Return the present time between stimulus exposures to be used in
        calculating the upcoming block.'''

        return self.session_settings['interstim_time']

    def get_bg_colour(self: 'SettingsObject') -> tuple:
        '''Return the present background colour to be used in the upcoming
        block.'''

        return self.session_settings['background_colour']

    def get_tg_colour(self: 'SettingsObject') -> tuple:
        '''Return the present target colour to be used in the upcoming
        block.'''

        return self.session_settings['target_colour']

    def get_fx_colour(self: 'SettingsObject') -> tuple:
        '''Return the present fixator colour to be used in the upcoming
        block.'''

        return self.session_settings['fixator_colour']

    def get_fx_size(self: 'SettingsObject') -> tuple:
        '''Return the present fixator size to be used in the upcoming
        block.'''

        return self.session_settings['fixator_size']

    #def get_aural_key(self: 'SettingsObject') -> int:
    #    '''Return the present respond to aural stimulus exposure key to be
    #    used in performing the upcoming block.'''

    #    return int(self.session_settings['aural_key'])

    #def get_visual_key(self: 'SettingsObject') -> int:
    #    '''Return the present respond to visual stimulus exposure key to be
    #    used in performing the upcoming block.'''

    #    return int(self.session_settings['visual_key'])


class LogWindow(QtGui.QWidget):
    '''Makes the wacky log deally.'''

    log_saved = QtCore.Signal()

    def __init__(self: 'LogWindow') -> None:

        super(LogWindow, self).__init__()

        self.log_string = ('--------begin session--------' + '\n' +
                           str(datetime.datetime.today()) + ':\n')

        self.__config_log_window()

    def __config_log_window(self: 'LogWindow') -> None:
        '''All the fiddly stuff.'''

        self.setWindowTitle('Dual n-back log')

        self.g_l = QtGui.QGridLayout(self)

        self.text_display = QtGui.QTextEdit(self.log_string)
        self.text_display.setWordWrapMode(QtGui.QTextOption.WordWrap)
        self.text_display.setReadOnly(True)

        self.g_l.addWidget(self.text_display, 1, 1)

        self.lower()
        self.show()

    def log_event(self: 'LogWindow', event_log: str) -> None:
        '''Add to log file and update log window.'''

        string_to_insert = ('\n' + str(datetime.datetime.today()) + ':\n' +
                            event_log + '\n')
        self.log_string = (self.log_string + string_to_insert)

        self.text_display.append(string_to_insert)
        self.update()
        
    def closeEvent(self: 'LogWindow', event):
        '''Reimplemented close event handler.  Save log on application
        close.'''

        self.log_event('---------end session---------\n')

        save_file = open('resources/dualnback.log', 'a')
        save_file.writelines(self.log_string)
        save_file.close()

        # Is there an actual reason to emit this signal?  How about for a loop
        # in main app to wait until detected to finish closing?  (so far seems
        # not needed)
        self.log_saved.emit()

        # Any other clean up?  Don't forget to add it below.
        event.accept()


class DualNBackMainWindow(QtGui.QMainWindow):
    '''Main window of dual-n back application.'''

    # Signals, if any, go here.
    change_wanted_signal = QtCore.Signal()

    def __init__(
        self: 'DualNBackMainWindow',
        parent: QtGui.QMainWindow) -> None:
        '''Initialized an instance of the main application window.'''

        super(DualNBackMainWindow, self).__init__()


        # First,open log and then make sure the minimum python version is used.
        self.log_widget = LogWindow()
        self.check_py_ver()

        # Do I ever use this?
        #self.parent = parent
        # I don't really seem to need any of the QMainWindow methods after
        # initialization so commented out for now.

        # Central variable and widget initialization.
        self.central_widget = QtGui.QWidget(self)
        self.db_connection = UserLogin.UserSession()
        self.user_logged_in = False
        #self.user_name = ''
        self.results = None
        self.user_history = {'name': '', 'psswrd': '', 'svunpw': False}

        self.status_bar = QtGui.QStatusBar()
        self.main_menu = self.menuBar()

        ## Helper function to lay out the main application window.
        #self.__central_window()
        
        # self.list_of_settings_names is a convenience variable for listing and 
        # changing global settings.
        self.list_of_settings_names = []
        self.screen_dimensions = None
        self.all_session_settings = None
        # Dimensions and session settings are all set on next line.
        # Dimensions set by desktop the application is running on.
        self.__init_all_sessions()

        # Reference created here to ease code review if it's been a while
        # since last examined and details of working forgotten.
        self.settings_window = None

        # Only refer to active settings in this object, do not make extra
        # copies in app object.
        self.session_settings = SettingsObject()
        self.session_settings.settings_changed_signal.connect(
            self._refresh_settings_window)
        self.session_settings_name = 'default'
        # These settings are from a pickled dictionary of dictionaries.  See
        # following helper function.
        self._load_session_settings()


        
        # Some more helper function organization, see these functions for 
        # details but nothing too exciting.
        self.set_images()
        self.idle_messages = self.__load_idle_mssgs()
        self.idle_messages_index = 0

        self.stimulus_buffer = None    # Initialized fully with main window.
        self.training = False
        self.blocks_run_so_far = 0

        # The following block are variables only reachable through the sooper
        # sekrit settings.
        self.match_in_visual = 4
        self.match_in_aural = 4
        self.match_in_both = 2
        self.visual_key = QtCore.Qt.Key_A
        self.aural_key = QtCore.Qt.Key_L
        self.next_block_change_n = {'increase_n': {'mistakes_less_than': 3,
                                                   'increase_n_by': 1},
                                    'decrease_n': {'mistakes_greater_than': 5,
                                                   'decrease_n_by': 1}}
        # End of best not changed vars block.

        self.bad_idea = None  # This getting used is not a good idea, but who
        # am I to stop you.  See self._sooper_sekrit_settings() for info.

        self.neutral_screen = QtGui.QPixmap(
            ('images\screen' +
             str((self.session_settings.session_settings[
                 'number_of_targets'] // 2)) + '.png'))

        # Helper function to lay out the main application window.
        self.__central_window()

        self.__menu_and_status_bar()
        self.status_bar.showMessage('Please sign in first.', 5000)

        # Although used elsewhere, these lists initialized here to keep the
        # functions that use them a little less busy to read.
        self.settings_txt_list = [
            ['bg_colour_label', 'Background colour'],
            ['trgt_colour_label', 'Target colour'],
            ['fxtr_colour_label', 'Fixator colour'],
            ['fxtr_size_label', 'Fixator size'],
            ['number_of_targets_label',
             'Number of targets (not yet variable)'],
            ['init_n_label', 'Initial n'],
            ['number_of_trials_label', 'Number of trials'],
            ['stm_tm_label', 'Stimulus presentation time (msecs)'],
            ['interstm_tm_label',
             'Interstimulus neutral screen time (msecs)'],
            ['session_blcks_label', 'Number of blocks in this session']]


        # Do I need the method reference still?  See _refresh_settings_window
        # for possible new approach.
        self.settings_value_list = [
            ['bg_colour_value', 'background_colour',
             self.session_settings.get_bg_colour()],
            ['trgt_colour_value', 'target_colour',
             self.session_settings.get_tg_colour()],
            ['fxtr_colour_value', 'fixator_colour',
             self.session_settings.get_fx_colour()],
            ['init_n_value', 'current_n',
             self.session_settings.get_n()],
            ['number_of_trials_value', 'session_length_before_n',
             self.session_settings.get_block_before_n()],
            ['stm_tm_value', 'stim_time',
             self.session_settings.get_stim_exposure_time()],
            ['interstm_tm_value', 'interstim_time',
             self.session_settings.get_interstim_time()],
            ['session_blcks_value', 'session_blocks',
             self.session_settings.get_total_session_blocks()],
            ['fxtr_size_value', 'fixator_size',
             self.session_settings.get_fx_size()], 
            ['number_of_targets_value', 'number_of_targets',
             self.session_settings.get_number_targets()]]

        self.colour_sample_list = [
            ['bg_colour_smpl_lbl', 'bg_colour_smpl_img',
             'bg_colour_smpl_img_fillclr',
             self.session_settings.get_bg_colour()],
             ['tg_colour_smpl_lbl', 'tg_colour_smpl_img',
              'tg_colour_smpl_img_fillclr',
              self.session_settings.get_tg_colour()],
              ['fx_colour_smpl_lbl', 'fx_colour_smpl_img',
               'fx_colour_smpl_img_fillclr',
               self.session_settings.get_fx_colour()]]

        # I'm keeping this here for reference.  To fiddle with the default
        # set you will need to unpickle resources/session_config.sav and change
        # the 'default' subdictionary. (then repickle etc.)
        #self.session_settings = {
            #'background_colour': (0, 0, 0), 'fixator_colour': (255, 255, 255),
            #'target_colour': (75, 75, 255),
            #'number_of_targets': 8, 'current_n': 1,
            #'session_length_before_n': 20, 'stim_time' = 500, 
            # 'interstim_time' = 2500, 'session_blocks' = 20, 'fixator_size':
            # 'Working on it'}

        self.feel_love = True  # This program can feel love.

# Helpers for interface

    def check_py_ver(self):
        '''Raise PythonVersionError if Python environment is of a version
        less than 3.4.'''

        py_ver = sys.version_info
        if not ((py_ver[0] >= 3) and (py_ver[1] >= 4)):

            self.log_widget.log_event('Python version test failed.')
            self.log_widget.close()
            raise PythonVersionError(py_ver)

        del(py_ver)  # Not used again so just nuke it.
        self.log_widget.log_event('Python version test passed.')

    def __load_idle_mssgs(self: 'DualNBackMainWindow') -> list:
        '''Loads nonsense messages.'''

        idl_mssgs = open('resources/trufcts.inf', 'rb')

        mssg_list = pickle.load(idl_mssgs)

        idl_mssgs.close()

        random.shuffle(mssg_list)

        return mssg_list

    def __cycle_mssgs(self: 'DualNBackMainWindow') -> None:
        '''Cycles through silly messages.'''

        self.idle_thrd = QtCore.QThread()
        self.idle_thrd.start()

        # Note: application close signals triggering thread close first.

        self.idle_thrd.setPriority(QtCore.QThread.LowestPriority)
        self.idle_thrd.idl_mssg_timer = QtCore.QTimer(self.idle_thrd)

        self.idle_thrd.idl_mssg_timer.setInterval(60000)
        self.idle_thrd.idl_mssg_timer.timeout.connect(self.__set_idl_mssg)
        self.idle_thrd.idl_mssg_timer.start()

    def __set_idl_mssg(self: 'DualNBackMainWindow') -> None:
        '''Display a given silly message.'''

        idle_mess = self.idle_messages[
            self.idle_messages_index % len(self.idle_messages)]

        self.idle_messages_index = self.idle_messages_index + 1

        self.central_widget.idl_mss_label.setText(idle_mess)
        self.central_widget.update()

    def __init_all_sessions(self: 'DualNBackMainWindow') -> dict:
        '''Initializes dictionary of all saved session settings.'''

        # Call helper to initialize and set all session settings sets.
        self._get_all_session_settings()
        
        # Extracts the current desktop resolution being used on computer
        # running application so that images created are a perfrect fit.
        desktop_info = QtGui.QDesktopWidget()
        scrn_dims = desktop_info.screenGeometry().size()
        self.screen_dimensions = (
            int(scrn_dims.width()), int(scrn_dims.height()))

        # Never referenced again, so, nuke 'em.
        del(desktop_info)
        del(scrn_dims) 

    def closeEvent(self, event):
        '''Reimplemented close event handler.  If threads are running, closes
        them at application close.'''

        # Open thread cleanup first.
        if hasattr(self, 'idle_thrd'):

            self.idle_thrd.idl_mssg_timer.stop()
            self.idle_thrd.exit()

        if hasattr(self, 'session_thread'):

            self.session_thread.exit()

        # Any other clean up?

        if self.user_logged_in:

            self.logout_user()

        self.log_widget.close()
        # I think accept flag is already true.
        #event.accept()

# Menus and windows

    def __menu_and_status_bar(self: 'DualNBackMainWindow') -> int:
        '''Create main menu and the status bar.'''

        menu_structure = {'_file_menu': ['&File',
                                         [['new_user_action',
                                           '&Make new user'],
                                          ['logout_user_action',
                                           '&Log out user'],
                                          ['close_action', '&Close']]],
                          '_settings_menu': ['&Settings',
                                             [['setting_window_action',
                                               'Settings &dialog'],
                                              ['soper_sekrit_window_action',
                                               'Sooper Se&krit Settings!']]],
                          '_windows_menu': ['&Windows', [['log_window_action',
                                                         'Show &log window']]],
                          '_about_and_help_menu': ['&About and Help',
                                                   [['instructions_action',
                                                     '&Instructions'],
                                                    ['about_action',
                                                     '&About']]]}

        for top_menu in menu_structure:

            setattr(self, top_menu, QtGui.QMenu(menu_structure[top_menu][0],
                                                self))
            
            for menu_action in menu_structure[top_menu][1]:

                if menu_action[0] == 'close_action':

                    self._file_menu.addSeparator()
                    # Doesn't work
                
                setattr(self, menu_action[0], QtGui.QAction(menu_action[1],
                                                             self))

        for connection in [[self._file_menu, [[self.new_user_action,
                                              self._add_user],
                           [self.logout_user_action, self.logout_user],
                           [self.close_action, self.close]]], 
                           [self._settings_menu, [[self.setting_window_action,
                                                  self.__settings_window],
                            [self.soper_sekrit_window_action,
                             self._sooper_sekrit_settings]]],
                             [self._windows_menu, [[self.log_window_action,
                                                   self.toggle_log_window]]],
                             [self._about_and_help_menu,
                              [[self.instructions_action,
                                self._instructions_message],
                               [self.about_action, self._about_message]]]]:

            which_menu = connection[0]
            action_list = connection[1]

            for action_to_set in action_list:

                action_to_set[0].triggered.connect(action_to_set[1])
                which_menu.addAction(action_to_set[0])

        for menu_to_add in [self._file_menu, self._settings_menu,
                            self._windows_menu, self._about_and_help_menu]:

            self.main_menu.addMenu(menu_to_add)

        special_state_menus = {'enabled': [self.logout_user_action,
                                           self.soper_sekrit_window_action],
                               'checked': [[self.log_window_action,
                                            self.toggle_log_window]]}

        for special_state in special_state_menus:

            if special_state == 'enabled':

                for enabled_toggled_menu in special_state_menus[special_state]:

                    enabled_toggled_menu.setEnabled(False)

            elif special_state == 'checked':

                for checkable_menu in special_state_menus[special_state]:

                    checkable_menu[0].setCheckable(True)
                    checkable_menu[0].setChecked(True)
                    checkable_menu[0].triggered.disconnect(checkable_menu[1])
                    checkable_menu[0].toggled.connect(checkable_menu[1])

        # Status bar
        self.setStatusBar(self.status_bar)
        self.status_bar.label = QtGui.QLabel('Dual n-back task ready.',
                                             self.status_bar)
        self.status_bar.addPermanentWidget(self.status_bar.label)

    def __central_window(self: 'DualNBackMainWindow') -> None:
        '''Initialize and populate the central window.'''

        # A minimum size keeps this window from lookng terrible.
        self.central_widget.setMinimumSize(320, 240)
        self.central_widget.grid = QtGui.QGridLayout(self.central_widget)

        self.central_widget.label = QtGui.QLabel('User and session info')
        self.central_widget.label.setAlignment(QtCore.Qt.AlignTop)

        # Kinda useless and silly, will drop it eventually.
        self.central_widget.movie = QtGui.QMovie('resources/forFun.gif')
        self.central_widget.movie_display_label = QtGui.QLabel()
        self.central_widget.movie_display_label.setMovie(
            self.central_widget.movie)

        self.central_widget.nm_ps_widget = QtGui.QGroupBox('User login', self)
        self.central_widget.nm_ps_widget.g_l = QtGui.QGridLayout(
            self.central_widget.nm_ps_widget)

        self.central_widget.user_name_lbl = QtGui.QLabel()
        self.central_widget.user_name_lbl.setTextFormat(QtCore.Qt.PlainText)

        # Will this condition ever actually be needed?
        if self.user_history['name'] != '':

            self.central_widget.user_name_lbl.setText(
                self.user_history['name'])

        else:

            self.central_widget.user_name_lbl.setText('Enter user name')

        self.central_widget.user_name_entry = QtGui.QLineEdit()
        self.central_widget.user_name_entry.setPlaceholderText('Username')

        self.central_widget.user_name_pswd_lbl = QtGui.QLabel('Enter password')
        self.central_widget.user_name_pswd_bx = QtGui.QLineEdit()
        self.central_widget.user_name_pswd_bx.setEchoMode(
            QtGui.QLineEdit.PasswordEchoOnEdit)
        self.central_widget.user_name_pswd_bx.setPlaceholderText('Password')
        self.central_widget.user_name_pswd_bx.returnPressed.connect(
            self.get_user_info)

        self.central_widget.usr_sv_chck_bx = QtGui.QCheckBox('Save login')
        self.central_widget.lgn_sbmt = QtGui.QPushButton('Login')
        self.central_widget.lgn_sbmt.clicked.connect(self.get_user_info)

        self.central_widget.nm_ps_widget.g_l.addWidget(
            self.central_widget.user_name_lbl, 1, 1)
        self.central_widget.nm_ps_widget.g_l.addWidget(
            self.central_widget.user_name_entry, 1, 2)
        self.central_widget.nm_ps_widget.g_l.addWidget(
            self.central_widget.user_name_pswd_lbl, 2, 1)
        self.central_widget.nm_ps_widget.g_l.addWidget(
            self.central_widget.user_name_pswd_bx, 2, 2)
        self.central_widget.nm_ps_widget.g_l.addWidget(
            self.central_widget.usr_sv_chck_bx, 3, 1)
        self.central_widget.nm_ps_widget.g_l.addWidget(
            self.central_widget.lgn_sbmt, 3, 2)

        # CONNECT TO GET USER
        self.central_widget.lanch_button = QtGui.QPushButton(
            'Begin n-back task')
        self.central_widget.lanch_button.clicked.connect(self.run_session)
        self.central_widget.training_button = QtGui.QPushButton(
            'Training')
        self.central_widget.training_button.clicked.connect(
            self.run_training_session)

        self.central_widget.grid.addWidget(self.central_widget.label, 1, 1)

        self.central_widget.grid.addWidget(
            self.central_widget.movie_display_label, 2, 1, 1, 2)

        self.central_widget.grid.addWidget(
            self.central_widget.nm_ps_widget, 3, 1, 2, 2)
        self.central_widget.grid.addWidget(
            self.central_widget.lanch_button, 5, 2)
        self.central_widget.grid.addWidget(
            self.central_widget.training_button, 5, 1)

        self._local_user_persistence()

        self.setCentralWidget(self.central_widget)
        self.central_widget.lanch_button.setEnabled(False)

        #stim_buffer_dict = self.session_settings.get_settings_base_dict()
        #stim_buffer_dict['how_many_targets'] = {'aural': self.match_in_aural,
        #                                        'visual': self.match_in_visual,
        #                                        'both': self.match_in_both}

        #self.stimulus_buffer = MakeStimBuffer.StimList(stim_buffer_dict)
        self.stimulus_buffer = MakeStimBuffer.StimList(self)

        self.central_widget.movie.start()

    def __session_window(self: 'DualNBackMainWindow') -> None:
        '''Open a fullscreen session window and run a session with current
        settings.'''

        # Button now disabled when not logged in.
        #if not self.user_logged_in:
        #    self.status_bar.showMessage('Please sign in first.', 10000)
        #    return

        if not hasattr(self, 'session_thread'):

            # New call to this each block, so only create thread once.
            self._session_thread_creator()

        if hasattr(self, 'idle_thrd'):

            self.idle_thrd.idl_mssg_timer.stop()

        if not self.session_thread.isRunning():

            self.session_thread.start()

        # As hardware varies, safest just to tell the session thread that it's
        # to run as close to real time as possible.
        self.session_thread.setPriority(QtCore.QThread.TimeCriticalPriority)

        # See taskwindow module for details, connect signals from window.
        self.session_thread.session_window = TW.TaskWindow(self)
        self.session_thread.session_window.log_worthy.connect(
            self._session_log)
        self.session_thread.session_window.task_done.connect(self._end_block)
        self.session_thread.session_window._start_block()


        ##TODO CONTINUE

        #self.session_intro_screen_string = (
        #    'Your job is to watch the screen\nand indicate if the sound you\n'
        #    'hear was also heard ' + str(
        #        self.session_settings.session_settings['current_n']) +\
        #    'times back with the key "s"\nand if the image seen was also seen'\
        #    + str(self.session_settings.session_settings[
        #        'current_n']) + 'times ago with the "l" \
        #    key.\nThe first' + str(self.session_settings.session_settings[
        #        'current_n']) + 'Rounds need no response.\nTotal rounds will \
        #        be ' + str(
        #            self.session_settings.session_settings['current_n'] +
        #            self.session_settings.session_settings[
        #                'session_length_before_n']) + ' rounds.')

    def _session_thread_creator(self: 'DualNBackMainWindow') -> None:
        '''Creates a thread for task session to run within and starts
        thread.'''

        self.session_thread = QtCore.QThread()
        self.session_thread.start()

    def _session_log(self: 'DualNBackMainWindow') -> None:
        '''Logging helper function when interacting with task window.'''

        self.log_widget.log_event(
            self.session_thread.session_window.log_report)

    def _end_block(self: 'DualNBackMainWindow') -> None:
        '''End of task block administration function.  Responsibilities
        include dealing with changes to n and logging out user when all task
        blocks completed.'''

        if hasattr(self, 'idle_thrd'):

            self.idle_thrd.idl_mssg_timer.start()

        self.session_thread.setPriority(QtCore.QThread.LowestPriority)

        self.blocks_run_so_far = self.blocks_run_so_far + 1

        block_results = self.session_thread.session_window.results
        self.session_thread.session_window.close()

        self.log_widget.log_event(str(self.blocks_run_so_far) +
                                  ' blocks have been completed.')

        if (self.blocks_run_so_far >=
            self.session_settings.get_total_session_blocks()):

            self.status_bar.showMessage('Session complete, logging you out.',
                                        10000)
            self.log_widget.log_event(
                str('User ' + self.user_history['name'] +
                    ' has finished all session blocks.\n'))

            # SOME FINAL DATABASE WRITING HERE!

            self.logout_user()

        self._change_n(block_results['score summary'])

        # OK, NEW BUFFER HERE I GUESS

        self.stimulus_buffer._refresh_attributes()
        self.stimulus_buffer.make_buffer()

    def _change_n(self: 'DualNBackMainWindow', score_data: dict) -> None:
        '''If needed, change n.'''

        incorrect = 0
        present_n = self.session_settings.get_n()

        for modality in score_data:

            for result in score_data[modality]:

                if 'false' in result:

                    incorrect = incorrect + score_data[modality][result]

        if incorrect < self.next_block_change_n['increase_n'][
            'mistakes_less_than']:

            self.session_settings.set_n((
                present_n +
                self.next_block_change_n['increase_n']['increase_n_by']))

        if ((present_n > 1) and (incorrect > self.next_block_change_n['decrease_n'][
            'mistakes_greater_than'])):

            self.session_settings.set_n((
                present_n -
                self.next_block_change_n['decrease_n']['decrease_n_by']))

        # AS OF NOW n >= 1 ONLY!!!
        self.log_widget.log_event('n is now ' +
                                  str(self.session_settings.get_n()))
           
    def __settings_window(self: 'DualNBackMainWindow') -> None:
        '''Initialize and display a window the reports the common initial
        settings for the application.  No manipulation of settings can be
        done directly here, instead one must open the change settings window 
        via the "Add/delete saved..." button.'''

        # Basic initialization here.
        self.settings_window = QtGui.QWidget()
        self.settings_window.setWindowTitle('Dual n-back settings')

        self.settings_window.grid_layout = QtGui.QGridLayout(
            self.settings_window)

        self.settings_window.group_box = QtGui.QGroupBox(
            'Session settings', self)
        self.settings_window.group_box.grid_layout = QtGui.QGridLayout(
            self.settings_window.group_box)

        self.settings_window.load_label = QtGui.QLabel(
            'Load existing')

        self.settings_window.combo_box = QtGui.QComboBox()
        self.settings_window.combo_box.insertItems(
            len(self.list_of_settings_names), self.list_of_settings_names)
        # If you select a different set of settings, update with new values.
        self.settings_window.combo_box.currentIndexChanged.connect(
            self._refresh_settings_window)

        # Helper functions
        # Text labels
        self._settings_txt_helper(self.settings_window.group_box)
        # Feedback text display of the variable's value.
        self._settings_vlu_helper(self.settings_window.group_box)
        # Small image of the set colour at end
        self._settings_clrsmpl_helper(self.settings_window.group_box)

        # Helper function called to add all these to grid layout.
        self._setting_labelgrid(self.settings_window.group_box.grid_layout,
            [self.settings_window.group_box.bg_colour_label,
             self.settings_window.group_box.trgt_colour_label,
             self.settings_window.group_box.fxtr_colour_label,
             self.settings_window.group_box.fxtr_size_label,
             self.settings_window.group_box.number_of_targets_label,
             self.settings_window.group_box.init_n_label,
             self.settings_window.group_box.number_of_trials_label,
             self.settings_window.group_box.stm_tm_label,
             self.settings_window.group_box.interstm_tm_label,
             self.settings_window.group_box.session_blcks_label])

        # Helper function called to add all these to grid layout.
        # Note first entry is a sublist.
        self._setting_valuegrid(self.settings_window.group_box.grid_layout,
            [[self.settings_window.group_box.bg_colour_smpl_lbl,
              self.settings_window.group_box.tg_colour_smpl_lbl,
              self.settings_window.group_box.fx_colour_smpl_lbl],
             self.settings_window.group_box.bg_colour_value,
             self.settings_window.group_box.trgt_colour_value,
             self.settings_window.group_box.fxtr_colour_value,
             self.settings_window.group_box.fxtr_size_value,
             self.settings_window.group_box.number_of_targets_value,
             self.settings_window.group_box.init_n_value,
             self.settings_window.group_box.number_of_trials_value,
             self.settings_window.group_box.stm_tm_value,
             self.settings_window.group_box.interstm_tm_value,
             self.settings_window.group_box.session_blcks_value])
        
        self.settings_window.button_group = QtGui.QWidget()
        self.settings_window.button_grid_layout = QtGui.QGridLayout(
            self.settings_window.button_group)

        self.settings_window.button_group.ok_button = QtGui.QPushButton(
            'Ok')
        self.settings_window.button_group.save_new_button = \
            QtGui.QPushButton('Add/delete saved...')
        self.settings_window.button_group.cancel_button = \
            QtGui.QPushButton('Cancel')
        self.settings_window.button_group.cancel_button.clicked.connect(
            self.settings_window.close)
        self.settings_window.button_group.save_new_button.clicked.connect(
            self.__change_settings_dialogue)
        self.settings_window.button_group.ok_button.clicked.connect(
            self._load_session_settings)

        self.settings_window.button_grid_layout.addWidget(
            self.settings_window.button_group.ok_button, 1, 1)
        self.settings_window.button_grid_layout.addWidget(
            self.settings_window.button_group.save_new_button, 1, 2)
        self.settings_window.button_grid_layout.addWidget(
            self.settings_window.button_group.cancel_button, 1, 3)

        self.settings_window.grid_layout.addWidget(
            self.settings_window.load_label, 1, 1)
        self.settings_window.grid_layout.addWidget(
            self.settings_window.combo_box, 1, 2)
        self.settings_window.grid_layout.addWidget(
            self.settings_window.group_box, 2, 1, 1, 2)
        self.settings_window.grid_layout.addWidget(
            self.settings_window.button_group, 3, 1, 1, 2)

        self.settings_window.show()

    def __change_settings_dialogue(self: 'DualNBackMainWindow') -> None:
        '''Sub-dialogue for adding, updating or deleting non-default sets.'''

        # Hint strings.
        self.sv_str = 'Pick an existing set from the list or enter a new name.'
        self.del_str = 'Select which set you wish to delete.'

        

        # the list of all the different settings is copied so we can set in a
        # preferred order.
        lcl_settings_list = self.list_of_settings_names
        lcl_settings_list.pop(lcl_settings_list.index('default'))
        lcl_settings_list.insert(0, 'Save under a new name')

        # Initialize organizational widgets.
        self.settings_window.change_window = QtGui.QWidget()
        self.settings_window.change_window.setWindowTitle(
            'Save, update or delete')
        self.settings_window.change_window.g_l = QtGui.QGridLayout(
            self.settings_window.change_window)

        self.settings_window.change_window.setting_holder = {
            'background_colour': self.session_settings.get_bg_colour(),
            'target_colour': self.session_settings.get_tg_colour(),
            'fixator_colour': self.session_settings.get_fx_colour(),
            'fixator_size': self.session_settings.get_fx_size(),
            'number_of_targets': self.session_settings.get_number_targets(),
            'current_n': self.session_settings.get_n(),
            'session_length_before_n': self.session_settings.\
                get_block_before_n(),
            'stim_time': self.session_settings.get_stim_exposure_time(),
            'interstim_time': self.session_settings.get_interstim_time(),
            'session_blocks': self.session_settings.get_total_session_blocks()}

        # More organizational widget fun
        self.settings_window.change_window.sv_del = QtGui.QGroupBox(
            'Choose save/update or delete', self)
        self.settings_window.change_window.sv_del.g_l = QtGui.QGridLayout(
            self.settings_window.change_window.sv_del)

        self.settings_window.change_window.sttngs = QtGui.QGroupBox(
            'Adjust settings', self)
        self.settings_window.change_window.sttngs.g_l = QtGui.QGridLayout(
            self.settings_window.change_window.sttngs)

        self.settings_window.change_window.bttn_bx = QtGui.QWidget()
        self.settings_window.change_window.bttn_bx.g_l = QtGui.QGridLayout(
            self.settings_window.change_window.bttn_bx)

        self.settings_window.change_window.sv_del.sv_del_chk = QtGui.QCheckBox(
            'Delete')
        self.settings_window.change_window.sv_del.sv_del_chk.setCheckState(
            QtCore.Qt.Unchecked)
        #  Checked will mean inactivationg all of sttngs.
        self.settings_window.change_window.sv_del.sv_del_chk.stateChanged.\
            connect(self._change_settings_toggle)
        self.settings_window.change_window.sv_del.hint_lbl = QtGui.QLabel(
            self.sv_str)

        self.settings_window.change_window.sv_del.cmbbx = QtGui.QComboBox()
        self.settings_window.change_window.sv_del.cmbbx.insertItems(
            len(lcl_settings_list), lcl_settings_list)

        self.settings_window.change_window.sv_del.txt_entry = QtGui.QLineEdit()
        self.settings_window.change_window.sv_del.txt_entry.setPlaceholderText(
            'New save name')

        # Initialize functiona buttons.
        self.settings_window.change_window.bttn_bx.ok_b = QtGui.QPushButton(
            'Ok')
        self.settings_window.change_window.bttn_bx.cncl_b = QtGui.QPushButton(
            'Cancel')
        self.settings_window.change_window.bttn_bx.ok_b.clicked.connect(
            self._add_session_settings)
        self.settings_window.change_window.bttn_bx.cncl_b.clicked.connect(
            self.settings_window.change_window.close)

        # Organizational helper functions for common grid layout between all
        # settings windows.
        self._settings_txt_helper(self.settings_window.change_window.sttngs)
        self._settings_vlu_helper(self.settings_window.change_window.sttngs)

        # As the interface is a bit deeper than the window that merely
        # displays the settings, a bit more organization needed in sub
        # widgets.  As such helper function called here to keep readability.
        
        self._colour_buttons_helper()
        # Next line exqamine this function to see if bugginess introduced here.
        self._settings_clrsmpl_helper(
            self.settings_window.change_window.sttngs)

        # This should just over write the auto setup.
        # FIX since this is really a waste of time.
        self.settings_window.change_window.sttngs.init_n_value = QtGui.\
            QSpinBox()
        self.settings_window.change_window.sttngs.init_n_value.setAlignment(
            QtCore.Qt.AlignRight)
        self.settings_window.change_window.sttngs.init_n_value.valueChanged.\
            connect(self._set_min_trials_relative_to_n)

        # This should just over write the auto setup as well.
        self.settings_window.change_window.sttngs.\
            number_of_trials_value = QtGui.QSpinBox()
        self.settings_window.change_window.sttngs.number_of_trials_value.\
            setAlignment(QtCore.Qt.AlignRight)
        self._set_min_trials_relative_to_n()

        # A little more organization here because why be consistent in where
        # and how you do a given job

        self.settings_window.change_window.sv_del.g_l.addWidget(
            self.settings_window.change_window.sv_del.sv_del_chk, 1, 1)
        self.settings_window.change_window.sv_del.g_l.addWidget(
            self.settings_window.change_window.sv_del.cmbbx, 1, 2)
        self.settings_window.change_window.sv_del.g_l.addWidget(
            self.settings_window.change_window.sv_del.hint_lbl, 2, 1)
        self.settings_window.change_window.sv_del.g_l.addWidget(
            self.settings_window.change_window.sv_del.txt_entry, 2, 2)

        # Oh look, suddenly back to helper functions.  Why?  Reasons.
        self._setting_labelgrid(self.settings_window.change_window.sttngs.g_l,
            [self.settings_window.change_window.sttngs.bg_colour_label,
             self.settings_window.change_window.sttngs.trgt_colour_label,
             self.settings_window.change_window.sttngs.fxtr_colour_label,
             self.settings_window.change_window.sttngs.fxtr_size_label,
             self.settings_window.change_window.sttngs.number_of_targets_label,
             self.settings_window.change_window.sttngs.init_n_label,
             self.settings_window.change_window.sttngs.number_of_trials_label,
             self.settings_window.change_window.sttngs.stm_tm_label,
             self.settings_window.change_window.sttngs.interstm_tm_label,
             self.settings_window.change_window.sttngs.session_blcks_label])

        self._setting_valuegrid(self.settings_window.change_window.sttngs.g_l,
            [[self.settings_window.change_window.sttngs.bg_colour_smpl_lbl,
              self.settings_window.change_window.sttngs.tg_colour_smpl_lbl,
              self.settings_window.change_window.sttngs.fx_colour_smpl_lbl],
             self.settings_window.change_window.sttngs.bg_hldr,
             self.settings_window.change_window.sttngs.tg_hldr,
             self.settings_window.change_window.sttngs.fx_hldr,
             self.settings_window.change_window.sttngs.fxtr_size_value,
             self.settings_window.change_window.sttngs.number_of_targets_value,
             self.settings_window.change_window.sttngs.init_n_value,
             self.settings_window.change_window.sttngs.number_of_trials_value,
             self.settings_window.change_window.sttngs.stm_tm_value,
             self.settings_window.change_window.sttngs.interstm_tm_value,
             self.settings_window.change_window.sttngs.session_blcks_value])

        # Connect change signals
        
        #self.settings_window.change_window.sttngs.bg_colour_smpl_img_fillclr.\
        #    change_wanted_signal.connect(self._setting_holder_helper)
        #self.settings_window.change_window.sttngs.tg_colour_smpl_img_fillclr.\
        #    change_wanted_signal.connect(self._setting_holder_helper)
        self.change_wanted_signal.connect(self._setting_holder_helper)
        self.settings_window.change_window.sttngs.fxtr_size_value.\
            textEdited.connect(self._setting_holder_helper)
        self.settings_window.change_window.sttngs.number_of_targets_value.\
            textEdited.connect(self._setting_holder_helper)
        self.settings_window.change_window.sttngs.session_blcks_value.\
            textEdited.connect(self._setting_holder_helper)
        self.settings_window.change_window.sttngs.interstm_tm_value.\
            textEdited.connect(self._setting_holder_helper)
        self.settings_window.change_window.sttngs.stm_tm_value.\
            textEdited.connect(self._setting_holder_helper)
        self.settings_window.change_window.sttngs.init_n_value.\
            valueChanged.connect(self._setting_holder_helper)
        self.settings_window.change_window.sttngs.number_of_trials_value.\
            valueChanged.connect(self._setting_holder_helper)

        # Last bit of fussing and claim it all works!
        self.settings_window.change_window.bttn_bx.g_l.addWidget(
            self.settings_window.change_window.bttn_bx.ok_b, 1, 1)
        self.settings_window.change_window.bttn_bx.g_l.addWidget(
            self.settings_window.change_window.bttn_bx.cncl_b, 1, 2)

        self.settings_window.change_window.g_l.addWidget(
            self.settings_window.change_window.sv_del, 1, 1)
        self.settings_window.change_window.g_l.addWidget(
            self.settings_window.change_window.sttngs, 2, 1)
        self.settings_window.change_window.g_l.addWidget(
            self.settings_window.change_window.bttn_bx, 3, 1)

        
        self.settings_window.change_window.show()
    
        
        
        
        
    def _setting_holder_helper(self: 'DualNBackMainWindow') -> None:
        '''Update the holder dictionary for change settings window.'''

        setting_list = [
            ['background_colour',
             self.settings_window.change_window.sttngs.\
                 bg_colour_smpl_img_fillclr],
            ['target_colour',
             self.settings_window.change_window.sttngs.\
                 tg_colour_smpl_img_fillclr],
            ['fixator_colour',
             self.settings_window.change_window.sttngs.\
                 fx_colour_smpl_img_fillclr],
            ['fixator_size',
             self.settings_window.change_window.sttngs.fxtr_size_value],
            ['number_of_targets',
             self.settings_window.change_window.sttngs.\
                 number_of_targets_value],
            ['current_n',
             self.settings_window.change_window.sttngs.init_n_value],
            ['session_length_before_n',
             self.settings_window.change_window.sttngs.number_of_trials_value],
            ['stim_time',
             self.settings_window.change_window.sttngs.stm_tm_value],
            ['interstim_time',
             self.settings_window.change_window.sttngs.interstm_tm_value],
            ['session_blocks',
             self.settings_window.change_window.sttngs.session_blcks_value]]
        
        for setting in setting_list:

            self.settings_window.change_window.\
                setting_holder[setting[0]] = setting[1]

        self.session_settings.set_settings_base_dict(
            self.settings_window.change_window.setting_holder)

    def _settings_txt_helper(self: 'DualNBackMainWindow', root_object):

        for txt_attrb in self.settings_txt_list:

            setattr(root_object, txt_attrb[0], QtGui.QLabel(txt_attrb[1]))

    def _settings_vlu_helper(self: 'DualNBackMainWindow', root_object):
        
            
        for vl_attrb in self.settings_value_list:

            #TODO Use the session settings methods instead.
            setattr(root_object, vl_attrb[0], QtGui.QLineEdit(
                str(self.session_settings.session_settings[vl_attrb[1]])))

        for dsply_frmttng in [
            root_object.bg_colour_value, root_object.trgt_colour_value,
            root_object.fxtr_colour_value, root_object.fxtr_size_value,
            root_object.number_of_targets_value, root_object.init_n_value,
            root_object.number_of_trials_value, root_object.stm_tm_value,
            root_object.interstm_tm_value, root_object.session_blcks_value]:

            dsply_frmttng.setAlignment(QtCore.Qt.AlignRight)
            dsply_frmttng.setReadOnly(True)
            dsply_frmttng.setFrame(False)

    def _settings_clrsmpl_helper(self: 'DualNBackMainWindow', root_object):

        for clr_smpl in self.colour_sample_list:

            setattr(root_object, clr_smpl[0], QtGui.QLabel())
            setattr(root_object, clr_smpl[1], QtGui.QPixmap(20, 20))
            setattr(root_object, clr_smpl[2], QtGui.QColor(clr_smpl[3][0],
                                                           clr_smpl[3][1],
                                                           clr_smpl[3][2]))

        for fnlz_smpl in [[root_object.bg_colour_smpl_img,
                           root_object.bg_colour_smpl_img_fillclr,
                           root_object.bg_colour_smpl_lbl],
                          [root_object.tg_colour_smpl_img,
                           root_object.tg_colour_smpl_img_fillclr, 
                           root_object.tg_colour_smpl_lbl],
                          [root_object.fx_colour_smpl_img,
                           root_object.fx_colour_smpl_img_fillclr, 
                           root_object.fx_colour_smpl_lbl]]:

            fnlz_smpl[0].fill(fnlz_smpl[1])
            fnlz_smpl[2].setFixedSize(20, 20)
            fnlz_smpl[2].setPixmap(fnlz_smpl[0])
            fnlz_smpl[2].setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)

    def _setting_labelgrid(self: 'DualNBackMainWindow', root_object,
                           object_list) -> None:

        count = 1
        for widget_name in object_list:

            root_object.addWidget(widget_name, count, 1)
            count = count + 1

    def _setting_valuegrid(self: 'DualNBackMainWindow', root_object,
                           object_list) -> None:

        count = 1
        clr_smpls = object_list.pop(0)

        for widgets in object_list:

            if count <= 3:

                root_object.addWidget(clr_smpls.pop(0), count, 3)

            root_object.addWidget(widgets, count, 2)

            count = count + 1

    def toggle_log_window(self: 'DualNBackMainWindow') -> None:
        '''Adjust GUI to visibility state of log window.'''

        # If there is a checkmark next to the log visible option in the 
        # Windows menu, log window is visible.  Else, not.
        if self.log_window_action.isChecked():

            self.log_widget.log_event('Log Window made visible.')
            self.log_widget.show()
            return

        self.log_widget.log_event('Log Window hidden.')
        self.log_widget.hide()

    def _colour_buttons_helper(self: 'DualNBackMainWindow') -> None:

        for holder_object in ['bg_hldr', 'tg_hldr', 'fx_hldr']:

            setattr(self.settings_window.change_window.sttngs, holder_object,
                    QtGui.QWidget())

        for object_base in [self.settings_window.change_window.sttngs.bg_hldr,
                            self.settings_window.change_window.sttngs.tg_hldr,
                            self.settings_window.change_window.sttngs.fx_hldr]:

            setattr(object_base, 'g_l', QtGui.QGridLayout(object_base))
            setattr(object_base, 'bt', QtGui.QPushButton('Change'))

        for button_targets in [
            [self.settings_window.change_window.sttngs.bg_hldr.bt,
             self._set_bg_colour],
            [self.settings_window.change_window.sttngs.tg_hldr.bt,
             self._set_tg_colour],
            [self.settings_window.change_window.sttngs.fx_hldr.bt,
             self._set_fx_colour]]:

            button_targets[0].clicked.connect(button_targets[1])

        for widgets_to_add in [
            [self.settings_window.change_window.sttngs.bg_hldr.g_l,
             [self.settings_window.change_window.sttngs.bg_colour_value,
              self.settings_window.change_window.sttngs.bg_hldr.bt]], 
            [self.settings_window.change_window.sttngs.tg_hldr.g_l,
             [self.settings_window.change_window.sttngs.trgt_colour_value,
              self.settings_window.change_window.sttngs.tg_hldr.bt]],
            [self.settings_window.change_window.sttngs.fx_hldr.g_l,
             [self.settings_window.change_window.sttngs.fxtr_colour_value,
              self.settings_window.change_window.sttngs.fx_hldr.bt]]]:

            widgets_to_add[0].addWidget(widgets_to_add[1][0], 1, 1)
            widgets_to_add[0].addWidget(widgets_to_add[1][1], 1, 2)

    def _sooper_sekrit_settings(self: 'DualNBackMainWindow') -> None:
        '''Window best not used.'''

        discourage = ('There is really no advantage to changing these.  '
                      'You\'ll basically increase or decrease task difficulty '
                      'or difficuly rate of change into the realm of useless.  '
                      'Changes to these are not kept upon application close.')
        self.bad_idea = QtGui.QWidget()
        self.bad_idea.setWindowTitle('Changing these is kinda dumb.')
        self.bad_idea.g_l = QtGui.QGridLayout(self.bad_idea)

        self.bad_idea.do_not_label = QtGui.QLabel()
        self.bad_idea.do_not_label.setWordWrap(True)
        self.bad_idea.do_not_label.setText(discourage)

        self.bad_idea.ok_button = QtGui.QPushButton('Ok')
        self.bad_idea.ok_button.clicked.connect(self.bad_idea.close)

        self.bad_idea.cancel_button = QtGui.QPushButton('Cancel')
        self.bad_idea.cancel_button.clicked.connect(self.bad_idea.close)

        #self.match_in_visual = 4
        #self.match_in_aural = 4
        #self.match_in_both = 2
        #self.visual_key = QtCore.Qt.Key_A
        #self.aural_key = QtCore.Qt.Key_L
        #self.next_block_change_n = {'increase_n': {'mistakes_less_than': 3,
        #                                           'increase_n_by': 1},
        #                            'decrease_n': {'mistakes_greater_than': 5,
        #                                           'decrease_n_by': 1}}

        self.bad_idea.g_l.addWidget(self.bad_idea.do_not_label, 1, 1, 1, 2)
        self.bad_idea.g_l.addWidget(self.bad_idea.ok_button, 2, 1)
        self.bad_idea.g_l.addWidget(self.bad_idea.cancel_button, 2, 2)

        self.soper_sekrit_window_action.setEnabled(False)
        self.bad_idea.show()

    def _about_message(self: 'DualNBackMainWindow') -> None:
        '''Popup message box with simple about information.'''

        about_text = ('Prototype n-back test software.\n'
                      'Engine built in Python 3.4 (Note: not backwards '
                      'compatible)\nGui built in PySide, '
                      'an LGPL implementation of Qt for Python.  '
                      '\nDatabase powered by SQLite 3.\nImage creation and '
                      'manipulation utilizes Pillow, the friendly PIL fork.')

        logos_labels_etc = [['python_logo',
                             QtGui.QPixmap(
                                 'resources/python-powered-w-200x80.png')],
                            ['pyside_logo',
                             QtGui.QPixmap('resources/pysidelogo.png')],
                             ['sqlite_logo',
                              QtGui.QPixmap('resources/SQLite_Logo_4.png')],
                              ['pillow_logo',
                               QtGui.QPixmap('resources/pillow-logo.png')],
                               ['python_logo_label', QtGui.QLabel()],
                               ['pyside_logo_label', QtGui.QLabel()],
                               ['sqlite_logo_label', QtGui.QLabel()],
                               ['pillow_logo_label', QtGui.QLabel()],
                               ['ok_button', QtGui.QPushButton('Ok', self)],
                               ['bad_idea_button',
                                QtGui.QPushButton(
                                    'Enable core settings change', self)]]

        self.about_popup = QtGui.QWidget()

        self.about_popup.setWindowTitle('About Dual-n Back')
        self.about_popup.grid_layout = QtGui.QGridLayout(self.about_popup)
        self.about_popup.text_area = QtGui.QTextEdit(about_text)

        for attrib_to_add in logos_labels_etc:

            setattr(self.about_popup, attrib_to_add[0], attrib_to_add[1])

        self.about_popup.text_area.setReadOnly(True)

        # loopable
        self.about_popup.python_logo_label.setPixmap(
            self.about_popup.python_logo)
        self.about_popup.pyside_logo_label.setPixmap(
            self.about_popup.pyside_logo)
        self.about_popup.sqlite_logo_label.setPixmap(
            self.about_popup.sqlite_logo)
        self.about_popup.pillow_logo_label.setPixmap(
            self.about_popup.pillow_logo)
        self.about_popup.ok_button.clicked.connect(self.about_popup.close)
        self.about_popup.bad_idea_button.clicked.connect(self._allow_sekrit)

        self.about_popup.grid_layout.addWidget(self.about_popup.text_area, 1,
                                               1, 1, 3)
        self.about_popup.grid_layout.addWidget(
            self.about_popup.python_logo_label, 2, 1)
        self.about_popup.grid_layout.addWidget(
            self.about_popup.pyside_logo_label, 2, 2)
        self.about_popup.grid_layout.addWidget(
            self.about_popup.sqlite_logo_label, 3, 1)
        self.about_popup.grid_layout.addWidget(
            self.about_popup.pillow_logo_label, 3, 2,)

        self.about_popup.grid_layout.addWidget(self.about_popup.ok_button, 4,
                                               1)
        self.about_popup.grid_layout.addWidget(
            self.about_popup.bad_idea_button, 4, 2)

        self.about_popup.show()

        self.log_widget.log_event('Viewed about information.')

    def _allow_sekrit(self: 'DualNBackMainWindow') -> None:

        self.soper_sekrit_window_action.setEnabled(True)

        self.log_widget.log_event('Enabled non-persistent settings.')

    def _instructions_message(self: 'DualNBackMainWindow') -> None:
        '''Popup message box with simple instructions on and about task.'''

        instrct_mssg_box = DNBW.TeachTaskWizard()

        #instrct_mssg_box = QtGui.QMessageBox()
        #instrct_mssg_box.setText('Do everything, but, you know, correctly.')
        #instrct_mssg_box.setIcon(QtGui.QMessageBox.Information)
        #instrct_mssg_box.exec_()

        del(instrct_mssg_box)

    # Window and menu helpers

    def _change_settings_toggle(self: 'DualNBackMainWindow') -> None:
        '''Set behaviour in change settings window based on state of
        save/delete checkbox.'''

        if (self.settings_window.change_window.sv_del.sv_del_chk.\
            checkState() == QtCore.Qt.Unchecked):
            
            self.settings_window.change_window.sv_del.hint_lbl.setText(
                self.sv_str)
            self.settings_window.change_window.sttngs.show()
            self.settings_window.change_window.sv_del.txt_entry.show()
            self.settings_window.change_window.bttn_bx.ok_b.clicked.connect(
                self._add_session_settings)

            return

        self.settings_window.change_window.sv_del.hint_lbl.setText(
            self.del_str)
        self.settings_window.change_window.sttngs.hide()
        self.settings_window.change_window.sv_del.txt_entry.hide()
        self.settings_window.change_window.bttn_bx.ok_b.clicked.connect(
            self._delete_session_settings)

    def _set_min_trials_relative_to_n(self: 'DualNBackMainWindow') -> None:
        '''Set number of trials minimum to one more than n.'''

        min_trials = (
            self.settings_window.change_window.sttngs.init_n_value.value() + 1)
        self.settings_window.change_window.sttngs.number_of_trials_value.\
            setMinimum(min_trials)

    def _set_bg_colour(self: 'DualNBackMainWindow') -> None:

        bg_colour = QtGui.QColorDialog.getColor()

        if not bg_colour.isValid():

            return

        self._process_q_colour(
            bg_colour,
            [self.settings_window.change_window.\
                sttngs.bg_colour_smpl_img_fillclr,
             self.settings_window.change_window.sttngs.bg_colour_value,
             self.settings_window.change_window.sttngs.bg_colour_smpl_img,
             self.settings_window.change_window.sttngs.bg_colour_smpl_lbl])

    def _set_tg_colour(self: 'DualNBackMainWindow') -> None:

        tg_colour = QtGui.QColorDialog.getColor()

        if not tg_colour.isValid():

            return

        self._process_q_colour(
            tg_colour,
            [self.settings_window.change_window.\
                sttngs.tg_colour_smpl_img_fillclr,
             self.settings_window.change_window.sttngs.tg_colour_value,
             self.settings_window.change_window.sttngs.tg_colour_smpl_img,
             self.settings_window.change_window.sttngs.tg_colour_smpl_lbl])

    def _set_fx_colour(self: 'DualNBackMainWindow') -> None:

        fx_colour = QtGui.QColorDialog.getColor()

        if not fx_colour.isValid():

            return

        self._process_q_colour(
            fx_colour,
            [self.settings_window.change_window.\
                sttngs.fx_colour_smpl_img_fillclr,
             self.settings_window.change_window.sttngs.fx_colour_value,
             self.settings_window.change_window.sttngs.fx_colour_smpl_img,
             self.settings_window.change_window.sttngs.fx_colour_smpl_lbl])

    def _process_q_colour(self: 'DualNBackMainWindow',
                          colour: QtGui.QColor, target_object_list) -> None:

        colour_text = colour.toRgb()
        colour_text = colour.toTuple()
        colour_text = (colour_text[0], colour_text[1], colour_text[2])
        target_object_list[0] = colour_text
        target_object_list[1].setText(str(colour_text))

        target_object_list[2].fill(colour)
        target_object_list[3].setPixmap(target_object_list[2])

        self.change_wanted_signal.emit()

    def _refresh_settings_window(self: 'DualNBackMainWindow',
                                 change_settings_window: bool=False) -> None:
        '''Refreshes the displayed values in the settings window when 
        a different set of settings is selected.'''
        
        display_or_change_index = 0

        # If the change settings window is being dealt with, change the
        # pointer for the sublists above to 1.
        if change_settings_window:

            display_or_change_index = 1

        # since this does run once before settings window initialized
        if self.settings_window == None:

            return

        # Ok, if this far objects exist and can reference them.
        settings_map_list = [
            ['background_colour',
             [self.settings_window.group_box.bg_colour_value,
              self.settings_window.change_window.sttngs.bg_colour_value],
             self.session_settings.get_bg_colour()],
            ['target_colour',
             [self.settings_window.group_box.trgt_colour_value,
              self.settings_window.change_window.sttngs.trgt_colour_value],
             self.session_settings.get_tg_colour()],
            ['fixator_colour',
             [self.settings_window.group_box.fxtr_colour_value,
              self.settings_window.change_window.sttngs.fxtr_colour_value],
             self.session_settings.get_fx_colour()],
            ['current_n',
             [self.settings_window.group_box.init_n_value,
              self.settings_window.change_window.sttngs.init_n_value],
             self.session_settings.get_n()],
            ['session_length_before_n',
             [self.settings_window.group_box.number_of_trials_value,
              self.settings_window.change_window.sttngs.\
                  number_of_trials_value],
             self.session_settings.get_block_before_n()],
            ['stim_time', 
             [self.settings_window.group_box.stm_tm_value,
              self.settings_window.change_window.sttngs.stm_tm_value],
             self.session_settings.get_stim_exposure_time()],
            ['interstim_time',
             [self.settings_window.group_box.interstm_tm_value,
              self.settings_window.change_window.sttngs.interstm_tm_value],
             self.session_settings.get_interstim_time()],
            ['session_blocks',
             [self.settings_window.group_box.session_blcks_value,
              self.settings_window.change_window.sttngs.session_blcks_value],
             self.session_settings.get_total_session_blocks()],
            ['fixator_size',
             [self.settings_window.group_box.fxtr_size_value,
              self.settings_window.change_window.sttngs.fxtr_size_value],
             self.session_settings.get_fx_size()], 
            ['number_of_targets',
             [self.settings_window.group_box.number_of_targets_value,
              self.settings_window.change_window.sttngs.\
                  number_of_targets_value],
             self.session_settings.get_number_targets()]]

        # test if sent here without loading, in case previewing settings only.
        set_name = self.session_settings_name

        if (self.session_settings_name != str(
            self.settings_window.combo_box.currentText())):

            self.session_settings_name = self.settings_window.combo_box.\
                currentText()

        for entry in settings_map_list:

            entry[1][display_or_change_index].setText(str(entry[2]))

            #self.settings_window.group_box.entry[0].setText(
            #    str(self.session_settings.entry[2]))

        self.settings_window.update()

    def _get_all_session_settings(self: 'DualNBackMainWindow') -> None:
        '''Load all session setting sets from disk and allow access.'''

        full_settings_dict_file = open('resources/session_config.sav', 'rb')

        dict_to_set = pickle.load(full_settings_dict_file)

        full_settings_dict_file.close()

        for set_name in dict_to_set:

            self.list_of_settings_names.append(set_name)

        # Yeah, other ways to do this, but, I pick this way.  Places 'default'
        # as the first item in the list of all named settings sets.
        dflt = self.list_of_settings_names.pop(
            self.list_of_settings_names.index('default'))
        self.list_of_settings_names.insert(0, dflt)

        self.all_session_settings = dict_to_set

    def _save_session_settings(self: 'DualNBackMainWindow') -> None:
        '''Save all presently alive session settings sets.'''

        save_file = open('resources/session_config.sav', 'wb')
        pickle.dump(self.all_session_settings, save_file, -1)
        save_file.close()

    def _add_session_settings(self: 'DualNBackMainWindow') -> None:
        '''Updates existing or adds new set of settings with provided name.'''

        # self.session_settings.change_settings  NEEDS IN HERE!!!!!

        cmb_nm_selected = self.settings_window.change_window.sv_del.cmbbx.\
            currentText()
        nw_st_name = self.settings_window.change_window.sv_del.txt_entry.text()

        if cmb_nm_selected == 'Save under a new name':

            nw_st_name = nw_st_name.strip()

            # Sure I'll allow a blank name, but I'm updating it to -PRIME and
            # then saving it.  Repeat names just primed too.

            while ((nw_st_name in self.list_of_settings_names) or
                   (nw_st_name == '')):

                nw_st_name = nw_st_name + '-PRIME'

        # So if we are making a new named set, the name is in theory unique.

        else:

            nw_st_name = cmb_nm_selected

        self.all_session_settings[nw_st_name] = {
            'background_colour': self.settings_window.change_window.sttngs.\
                bg_colour_smpl_img_fillclr,
            'target_colour': self.settings_window.change_window.sttngs.\
                tg_colour_smpl_img_fillclr,
            'fixator_colour': self.settings_window.change_window.sttngs.\
                fx_colour_smpl_img_fillclr,
            'fixator_size': self.settings_window.change_window.sttngs.\
                fxtr_size_value,
            'number_of_targets': self.settings_window.change_window.sttngs.\
                number_of_targets_value,
            'current_n': self.settings_window.change_window.sttngs.\
                init_n_value,
            'session_length_before_n': self.settings_window.change_window.\
                sttngs.number_of_trials_value,
            'stim_time': self.settings_window.change_window.sttngs.\
                stm_tm_value,
            'interstim_time': self.settings_window.change_window.sttngs.\
                interstm_tm_value,
            'session_blocks': self.settings_window.change_window.sttngs.\
                session_blcks_value}

        if nw_st_name not in self.list_of_settings_names:

            self.list_of_settings_names.append(nw_st_name)


        self.settings_window.combo_box.clear()
        self.settings_window.combo_box.addItems(self.list_of_settings_names)
        #self.settings_window.combo_box.setCurrentIndex(
        #    self.settings_window.combo_box.findText(nw_st_name))
        self._save_session_settings()
        #self._load_session_settings()
        self.settings_window.change_window.close()

    def _load_session_settings(self: 'DualNBackMainWindow') -> None:
        '''Load a saved session setting.

        Precondition: named set does exist.'''

        # What does this even do?

        if self.settings_window != None:

            if not self.settings_window.isHidden():

                self.session_settings_name = str(
                    self.settings_window.combo_box.currentText())
                self.settings_window.hide()

        self.session_settings.set_settings_base_dict(
            self.all_session_settings[self.session_settings_name])

    def _delete_session_settings(self: 'DualNBackMainWindow') -> None:
        '''Delete the set of settings selected.'''

        # self.session_settings.change_settings  IN HERE!!!!!

        name_to_purge = self.settings_window.change_window.sv_del.cmbbx.\
            currentText()

        if name_to_purge not in self.list_of_settings_names:

            return

        self.list_of_settings_names.pop(self.list_of_settings_names.index(
            name_to_purge))

        self.all_session_settings.pop(name_to_purge)
        self.settings_window.combo_box.clear()
        self.settings_window.combo_box.addItems(self.list_of_settings_names)
        self._save_session_settings()
        self.session_settings_name = 'default'
        self.settings_window.combo_box.setCurrentIndex(
            self.settings_window.combo_box.findText('default'))

        self._load_session_settings()

    def _local_user_persistence(self):

        hist_to_chck_file = open('resources/usr.stg', 'rb')

        usr_hist = pickle.load(hist_to_chck_file)

        hist_to_chck_file.close()

        if not usr_hist['svunpw']:

            del(usr_hist)

            return

        self.user_history = usr_hist

        self.central_widget.user_name_entry.setText(self.user_history['name'])

        self.central_widget.user_name_pswd_bx.setText(
            self.user_history['psswrd'])

        self.central_widget.usr_sv_chck_bx.setCheckState(QtCore.Qt.Checked)

    def _add_user(self: 'DualNBackMainWindow') -> None:

        pass

    def get_user_info(self: 'DualNBackMainWindow') -> None:
        '''Retrive user details, if they exist, from the database.'''

        usr_nm = self.central_widget.user_name_entry.text()
        psswr = self.central_widget.user_name_pswd_bx.text()

        self.status_bar.st_msg = ('Probably logged in now, but this isn\'t '
                                 'implemented.')

        if self.central_widget.usr_sv_chck_bx.isChecked():

            self.user_history['name'] = usr_nm
            self.user_history['psswrd'] = psswr
            self.user_history['svunpw'] = True

            new_usr_sv_file = open('resources/usr.stg', 'wb')
            pickle.dump(self.user_history, new_usr_sv_file, -1)
            new_usr_sv_file.close()
        
        self.status_bar.showMessage(self.status_bar.st_msg)

        if hasattr(self.central_widget, 'idl_mss_label'):

            self.central_widget.idl_mss_label.show()
            self.central_widget.idl_mss_label.setText('Ready to go!')

        else:

            self.central_widget.idl_mss_label = QtGui.QLabel('Ready to go!')
            self.central_widget.idl_mss_label.setWordWrap(True)

        self.central_widget.grid.removeWidget(
            self.central_widget.nm_ps_widget)
        self.central_widget.nm_ps_widget.hide()
        self.central_widget.grid.addWidget(
            self.central_widget.idl_mss_label, 2, 1, 2, 2)

        self._log_in_out_update()

        #self.user_name = usr_nm

        self.log_widget.log_event(str('User ' + self.user_history['name'] +
                                      ' has logged in.'))

        self.__cycle_mssgs()
        
        #self.db_connection

        #try:

        #    self.user_history = pickle.loads(NBackUserDatabase.get_user(
        #        self.user_unique_id))

        #except NoSuchUserError:

        #    pass  # call event to reask.

    def set_user_info(self: 'DualNBackMainWindow') -> None:
        '''Set user settings and any revised session info to database.'''

        #NBackUserDatabase.SOMETHING THAT CHECKS IF IT EXISTS OR NOT YET.

    def logout_user(self: 'DualNBackMainWindow') -> None:

        self.central_widget.grid.removeWidget(
            self.central_widget.idl_mss_label)
        self.central_widget.idl_mss_label.hide()

        self.central_widget.nm_ps_widget.show()
        self.central_widget.grid.addWidget(self.central_widget.nm_ps_widget,
                                           2, 1, 2, 2)

        self.idle_thrd.idl_mssg_timer.stop()
        self.idle_thrd.exit()

        self.log_widget.log_event(str('User ' + self.user_history['name'] +
                                      ' has logged out.'))
        
        self.user_history['name'] = ''
        self.user_history['psswrd'] = ''
        self.blocks_run_so_far = 0
        self._log_in_out_update()

        # And, you know, actually log out.

    def _log_in_out_update(self: 'DualNBackMainWindow') -> None:
        '''Adapt gui to user log state.'''

        set_state = True

        if self.user_logged_in:

            set_state = False

        self.logout_user_action.setEnabled(set_state)
        self.central_widget.lanch_button.setEnabled(set_state)
        self.user_logged_in = set_state

        self.central_widget.update()

# Stimulus stuff

    def set_images(self: 'DualNBackMainWindow') -> None:
        '''Create the image set for this entire session.'''

        # Really best to check documentation in this module if questions.
        image_object = MakeImages.ImageSet(self)

        image_object.create_set_of_images()
        del(image_object)

    def run_session(self: 'DualNBackMainWindow') -> None:
        '''Engine to run a test.'''

        # TODO Finish.

        if hasattr(self, 'idle_thrd'):

            self.idle_thrd.idl_mssg_timer.stop()

        #self.prepare_session()
        self.__session_window()

        if not self.training:
            # write to db since not a software training round.
            pass

        if hasattr(self, 'idle_thrd'):

            self.idle_thrd.idl_mssg_timer.start()

        

        

        # NEXT RECORD RESULTS!


    def run_training_session(self: 'DualNBackMainWindow') -> None:

        hold_non_training_n = self.session_settings.get_n()
        self.training = True
        self.session_settings.set_n(0)

        # Caution!  Craft run_session carefully to tell the difference between
        # training and real.
        self.run_session()

        self.session_settings.set_n(hold_non_training_n)
        self.training = False


def main():
    '''Pythonic application launcher function.'''

    dnbapp = QtGui.QApplication(sys.argv)  # Must be created first.

    splash_screen = QtGui.QSplashScreen()
    splash_screen.setPixmap('resources/loadsplash.png')
    splash_screen.show()
    dnbapp.setWindowIcon(QtGui.QIcon('resources/DNB.ico'))
    dnbmainwindow = DualNBackMainWindow(dnbapp)
    dnbmainwindow.setWindowTitle('Dual N Back A-Dack-Dack')
    dnbmainwindow.show()

    splash_screen.finish(dnbmainwindow)
    dnbapp.exec_()

if __name__ == '__main__':

    main()