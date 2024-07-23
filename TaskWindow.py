'''Task Window and friends.'''

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
#from time import sleep

class CountDown(QtGui.QWidget):
    '''Quick countdown and reminder window right before task starts.'''

    count_done = QtCore.Signal()

    def __init__(self: 'CountDown', info: dict) -> None:

        super(CountDown, self).__init__()

        self.viskey = info['visual']
        self.aukey = info['aural']
        self.n_size = info['n']
        self.this_block = info['block_number']
        self.all_blocks = info['all blocks']

        self.message = str('Press "' + chr(int(self.viskey)) +
                           '" for visual match.\nPress "' +
                           chr(int(self.aukey)) +
                           '" key for auditory match.\n\nFor this trial n = '
                           + str(self.n_size) + '.\nThis block will be ' + 
                           str(self.this_block) + ' of ' +
                           str(self.all_blocks) + '.')

        self.how_long = 10  # Time in seconds
        self.countdown_message = str('Get ready: ' + str(self.how_long))

        self.keylabel = QtGui.QLabel(self.message)
        self.timelabel = QtGui.QLabel(self.countdown_message)

        self.grid_layout = QtGui.QGridLayout(self)
        self.grid_layout.addWidget(self.keylabel, 1, 1)
        self.grid_layout.addWidget(self.timelabel, 2, 1)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.increment_time_left)

        self.setWindowTitle('Get ready!')

        self.raise_()
        self.show()

    def start_countdown(self: 'CountDown') -> None:
        '''Start the countdown in the countdown window.'''

        # Timeout is once per second, timer auto repeats.
        self.timer.start(1000)

    def test_if_end_of_countdown(self: 'CountDown') -> None:
        '''Test if count down is finished.'''

        if self.how_long < 0:

            self.count_done.emit()
            self.timer.stop()
            self.close()
            return

    def increment_time_left(self: 'CountDown') -> None:
        '''Increment count down and update countdown window.'''

        self.how_long = self.how_long - 1
        self.countdown_message = str('Get ready: ' + str(self.how_long))
        self.timelabel.setText(self.countdown_message)
        self.update()
        self.test_if_end_of_countdown()


class TaskWindow(QtGui.QLabel):
    '''Open a fullscreen task window and run a session with current
    settings.'''

    # Just using a label widget, that way no need to fuss with a border etc.

    # task_done signal emitted when full block completed, log_worthy when event
    # worth logging takes place.



    # TODO: First sound stim always late.



    task_done = QtCore.Signal()
    log_worthy = QtCore.Signal()

    def __init__(self: 'TaskWindow', parent: 'DualNBackMainWindow') -> None:

        super(TaskWindow, self).__init__()

        self.parent = parent  # Need to access parent's methods and attributes

        self.setFocusPolicy(QtCore.Qt.StrongFocus)  # According to the manual
        # I cannot use a reimplemented event handler without setting this.

        self.results = {}

        self.parent.stimulus_buffer._refresh_attributes()
        self.parent.stimulus_buffer.make_buffer()
        # Now can fetch.
        self.stim_buffer_local = self.parent.stimulus_buffer.get_buffers()
        # Local copy costs memory but saves io

        self.block_length = self.parent.session_settings.\
            get_total_block_length()
        self.block_n = self.parent.session_settings.get_n()
        self.stim_resp_index = -1  # To guarantee we actually start on index 0.
        self.keypresses = []
        self.block_finished = False

        self.show_stim_timer = QtCore.QTimer(self)
        self.show_blank_timer = QtCore.QTimer(self)
        self.stim_expose_time = self.parent.session_settings.\
            get_stim_exposure_time()
        self.interstim_time = self.parent.session_settings.get_interstim_time()
        self.neutral_screen = self.parent.neutral_screen
        self.visual_key = self.parent.visual_key
        self.aural_key = self.parent.aural_key
        self.block_number = self.parent.blocks_run_so_far + 1
        self.total_blocks_to_be_run = self.parent.session_settings.\
            get_total_session_blocks()

        self.log_report = ''

        self.__init_ui()

    def __init_ui(self: 'TaskWindow') -> None:
        '''Initializes the task window user interface details.'''

        self.setWindowState(QtCore.Qt.WindowFullScreen)
        # WindowFullScreen removes all borders and the like for us, so, done
        # configuring the window, it's already all a label anyway.

        for i in range(self.block_length):

            # Makes list such that each entry assumes no keypresses have taken
            # place.
            self.keypresses.append([False, False])

        self.setPixmap(self.neutral_screen)

        self.show_stim_timer.timeout.connect(self.stim_presentation_end)
        self.show_blank_timer.timeout.connect(self.present_all_stims)
        self.show_stim_timer.setInterval(self.stim_expose_time)
        self.show_blank_timer.setInterval(self.interstim_time)

        self.grabKeyboard()
        self.setCursor(QtCore.Qt.BlankCursor)  # While task runs no cursor is
        # visible.

        self._creation_string()   

    def _log_it(self: 'TaskWindow') -> None:
        '''Have parent application log and reset log string.'''

        self.log_worthy.emit()

        # Clear for next entry.
        self.log_report = ''

    def keyPressEvent(self: 'TaskWindow', event: QtGui.QKeyEvent) -> None:
        '''Reimplementation to catch and record key presses relevant to
        testing only.'''

        key = event.key()

        # Note: No way to abort test as it stands, need to consider how to
        # deal with aborted trial before implementing. (prob esc key)

        # Note: Seems ok with two keys at once.
        # We assign True to say only a keypress existed for this stimulus, we
        # make no judgement yet on if a keypress was appropriate.

        if ((key == self.visual_key) or (key == self.aural_key)):

            if key == self.visual_key:

                # Assumption, entry 0 is visual.
                # Note: already knows how to index this by stim_resp_index
                # refernce.
                self.keypresses[self.stim_resp_index][0] = True
                return

            self.keypresses[self.stim_resp_index][1] = True

    def _creation_string(self: 'TaskWindow') -> str:
        '''Log the creation time and settings for task window.'''

        # Logging function itself inserts time of entry, so assumed included.

        # Modular so if wish to change what is logged, much easier.
        block_length_string = ('\nThis block length: ' +
                               str(self.block_length) +
                               '.\n')
        block_n_string = ('\nThis block n: ' + str(self.block_n) + '.\n')
        block_stim_present = ('\nThis block stimulus presentation time '
                               '(Note: for visual stimulus only): ' +
                               str(self.stim_expose_time) + ' milliseconds.\n')
        block_interstim = ('\nThis block interstimulus screen: ' +
                           str(self.interstim_time) + ' milliseconds.\n')
        block_visual_key = ('\nThis block key to indicate visual match: ' +
                            chr(int(self.visual_key)) + '.\n')
        block_aural_key = ('\nThis block key to indicate aural match: ' +
                            chr(int(self.aural_key)) + '.\n')
        block_stim_set = ('\nThis block stimulus set:\n' +
                          str(self.stim_buffer_local) + '\n')

        self.log_report = ('\nTask window opened.\n' + block_length_string +
                           block_n_string + block_stim_present +
                           block_interstim + block_visual_key +
                           block_aural_key + block_stim_set)

        self._log_it()

    def _start_block(self: 'TaskWindow') -> None:
        '''Provided for a last interupt point before we get going.'''

        info = {'visual': self.visual_key, 'aural': self.aural_key,
                'n': self.block_n, 'block_number': self.block_number,
                'all blocks': self.total_blocks_to_be_run}

        self.show()
        # Showing self early since sleep wasn't giving the right effect.
        self.countdown_msg = CountDown(info)
        self.countdown_msg.count_done.connect(self.present_all_stims)
        
        self.countdown_msg.start_countdown()

    def present_all_stims(self: 'TaskWindow') -> None:
        '''Engine for presentation of testing block.'''

        self.show_blank_timer.stop()

        self.stim_resp_index = self.stim_resp_index + 1

        # Just check to see if we are done.
        if self.stim_resp_index >= self.block_length:

            self.task_end()
            return

        stim_to_present = self.stim_buffer_local[self.stim_resp_index]
        self.stim_buffer_local[self.stim_resp_index][1].play()
        self.setPixmap(self.stim_buffer_local[self.stim_resp_index][0])
        self.update()  # Keeping up visually so sound/sight approx in sync.
        
        self.show_stim_timer.start()

    def stim_presentation_end(self: 'TaskWindow') -> None:
        '''Display a neutral screen and finish waiting between stimulus.
        Continue to monitor for response whole time.'''

        self.show_stim_timer.stop()

        self.setPixmap(self.neutral_screen)
        self.update()

        self.show_blank_timer.start()

    def _score_block(self: 'TaskWindow', reference_dict: dict) -> list:
        '''Score results for block according to these rules:
        -If match detected (true positive) recorded as 0.
        -If mismatch ignored (true negative) recorded as 1.
        -If match ignored (false negative) recorded as 2.
        -If mismatch responded to (false positive) recorded as 3.
        and return as list of lists, with each sublist having stimulus scores
        for visual at 0 and aural at 1.'''

        # WARNING!: test this.  Lots.

        scoring_list = []

        for count in range(self.block_length):

            scoring_list.append([0, 0])

            # NOTE: since 0's added, can just adapt to that.

        for index in range(self.block_length):

            # So each modality also tested:

            for visual_or_aural in range(2):

                # Mismatch of false positive type detected first.  If respond
                # before n presentations, must also be included as a false
                # positive.

                if ((((index - self.block_n) < 0)
                    and (True ==
                         reference_dict['recorded'][index][visual_or_aural]))
                    or ((True ==
                         reference_dict['recorded'][index][visual_or_aural])
                        and
                        (reference_dict['presented'][index][visual_or_aural]
                         != reference_dict['presented'][(
                             index - self.block_n)][visual_or_aural]))):

                    scoring_list[index][visual_or_aural] = 3

                # False negative next.

                elif ((False ==
                       reference_dict['recorded'][index][visual_or_aural]) and
                      (reference_dict['presented'][index][visual_or_aural]
                       == reference_dict['presented'][(
                           index - self.block_n)][visual_or_aural])):

                    scoring_list[index][visual_or_aural] = 2

                # True negative next.

                elif ((False ==
                       reference_dict['recorded'][index][visual_or_aural]) and
                      (reference_dict['presented'][index][visual_or_aural]
                       != reference_dict['presented'][(
                           index - self.block_n)][visual_or_aural])):

                    scoring_list[index][visual_or_aural] = 1

                # All that remains must be true positives.

        return scoring_list

    def _score_summary(self: 'TaskWindow') -> None:
        '''Return a quick reference summary of user score on task block.'''

        # Visual at index 0, aural at index 1 in scoring to be analysed.

        score_sum_dict = {}
        sub_dict_names = ['visual', 'aural']  # names at logical index location
        key_code_list = ['true positive', 'true negative',
                         'false negative', 'false positive']
        # I admit I'm being a little too cleaver in positioning here, so if
        # you change the scoring method you really have to make sure indices 
        # align again in all functions.

        for sub_dict in sub_dict_names:

            score_sum_dict[sub_dict] = {}

        # Looping twice is a little clunky, but if revised later will be easier
        # to change.

        for sub_dict in sub_dict_names:

            for score_type in key_code_list:

                score_sum_dict[sub_dict][score_type] = 0

        for entry in self.results['scoring']:

            for visual_or_aural in range(2):

                key_index = key_code_list[entry[visual_or_aural]]

                score_sum_dict[sub_dict_names[visual_or_aural]][key_index] = (
                    score_sum_dict[sub_dict_names[visual_or_aural]][key_index]
                    + 1)

        return score_sum_dict

    def task_start(self: 'TaskWindow') -> None:
        '''Initial organization and logging at head of task.'''
        # This is really the best place to add any other interupts.

        self.log_report = '\nBlock started.\n'
        self._log_it()

        if not (self.parent.session_settings.get_total_block_length() >=
            self.parent.blocks_run_so_far):

            #ummmmmm, fix this by moving to main app.
            self.parent.status_bar.showMessage('This round complete.')

        self.present_all_stims()

    def task_end(self: 'TaskWindow') -> None:
        '''End of task block clean up and organization.'''

        self.show_blank_timer.stop()
        
        self.log_report = str('\nBlock ' +
                              str(self.parent.blocks_run_so_far + 1) +
                              ' completed.\n')
        self._log_it()

        self.results['recorded'] = self.keypresses
        self.results['presented'] = self.stim_buffer_local
        self.results['scoring'] = self._score_block(self.results)
        self.results['score summary'] = self._score_summary()

        self.log_report = ('\nResult dictionary:\n' + str(self.results))
        self._log_it()

        self.task_done.emit()