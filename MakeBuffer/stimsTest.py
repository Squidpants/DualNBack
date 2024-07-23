import unittest
import stims

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
                        #counts['visual'] = counts['visual'] - 1
                        #counts['aural'] = counts['aural'] - 1


            increment_both = 0

        all_target_counts = stims_test.get_targets()

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

        for i in range(30000):

            stims_test = stims.StimList()
            stims_test.make_buffer()

            #try:
            assert self._helper_test_buffers(stims_test)

            #except:
            #    print('I ran ' + str(i) + ' times.\n' +
            #          str(stims_test.buffers))


if __name__ == '__main__':

    unittest.main(exit=False)
