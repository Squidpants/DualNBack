import unittest
import MakeStimBuffer
import DualNBack
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import sys

class DummyApp(object):
    '''A minimal dummy object that has all and only needed attributes and
    methods for the tests to run.'''

    def __init__(self: 'DummyApp') -> None:

        self.session_settings = DualNBack.SettingsObject()
        self.session_settings.set_settings_base_dict({})


class Test_stims(unittest.TestCase):

    def _helper_test_buffers(self: 'Test_stims',
                             stims_test: 'StimList') -> bool:
        '''Prints a message if buffers don't have enough matches.'''

        counts = {'visual': 0, 'aural': 0, 'both': 0}
        block_n = stims_test.get_n()
        block_length = stims_test.get_length() + block_n
        increment_both = 0

        for i in range(block_length):

            if (i + block_n) < block_length:

                if stims_test.buffers['visual'][i] == stims_test.buffers[
                    'visual'][(i + block_n)]:

                    counts['visual'] = counts['visual'] + 1
                    increment_both = increment_both + 1

                if stims_test.buffers['aural'][i] == stims_test.buffers[
                    'aural'][(i + block_n)]:

                    counts['aural'] = counts['aural'] + 1

                    if increment_both == 1:

                        counts['both'] = counts['both'] + 1

            increment_both = 0

        all_target_counts = stims_test.get_buffers()

        for modality in counts:

            if modality != 'both':

                all_target_counts[modality] = (all_target_counts[modality] +
                                               all_target_counts['both'])

            if counts[modality] != all_target_counts[modality]:

                print(modality + ' is wrong count: ' + str(counts[modality]) +
                      ' made but ' + str(all_target_counts[modality]) +
                      ' expected.\n')

                return False

        return True

    def test_buffers(self: 'Test_stims') -> None:
        app = QtGui.QApplication(sys.argv)
        dnba = DualNBack.DualNBackMainWindow(app)

        for i in range(1000):

            stims_test = MakeStimBuffer.StimList(dnba)
            stims_test.make_buffer()

            assert self._helper_test_buffers(stims_test)

if __name__ == '__main__':

    unittest.main(exit=False)
