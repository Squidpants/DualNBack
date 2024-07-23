'''Dual n-task application.'''

import sys
import datetime
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import random
import MakeImages
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
        parent: 'QtGui.QMainWindow') -> None:
        '''Initialized an instance of the main application window.'''

        super(DualNBackMainWindow, self).__init__()

        # First,open log and then make sure the minimum python version is used.
        self.log_widget = LogWindow()
        self.check_py_ver()

        # Central variable and widget initialization.
        self.central_widget = QtGui.QWidget(self)
        self.status_bar = QtGui.QStatusBar()
        self.main_menu = self.menuBar()

        # User Database stuff
        self.db_connection = UserLogin.UserSession()
        self.user_logged_in = False
        self.results = None
        self.user_history = {'name': '', 'psswrd': '', 'svunpw': False}

        # self.list_of_settings_names is a convenience variable for listing and 
        # changing global settings.
        self.list_of_settings_names = []
        self.screen_dimensions = None
        self.all_session_settings = None

        # CONCEPT: New setting Object in the change settings windows?
        self.settings_window = None

        # Dimensions and session settings are all set on next line.
        # Dimensions set by desktop the application is running on.
        self.__init_all_sessions()

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

        # Fiddly directly task related stuff.
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

        # Helper functions to lay out the main application window.
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