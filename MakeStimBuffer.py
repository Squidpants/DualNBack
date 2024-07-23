from random import randrange
import os
import os.path
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

class StimList(object):

    def __init__(self: 'StimList', parent: 'DualNBackMainWindow') -> None:

        self.parent = parent

        self.n = None
        self.length = None
        self.placement = None
        self.valid_index = None
        self.targets = None
        self.buffers = None
        self.how_many_stims = None
        self.lists_to_be_built = None
        self.all_image_targets = []
        self.all_sound_targets = []

        # This connection probably redundant since refrech at buffer build.
        self.parent.session_settings.settings_changed_signal.connect(
            self._refresh_attributes)
        self._refresh_attributes()

    def _refresh_attributes(self: 'StimList') -> None:

        self.n = self.parent.session_settings.get_n()
        self.length = self.parent.session_settings.get_block_before_n()
        self.placement = []
        self.valid_index = []
        self.targets = {'aural': self.parent.match_in_aural,
                        'visual': self.parent.match_in_visual,
                        'both': self.parent.match_in_both}
        self.buffers = {'aural': [], 'visual': []}
        self.how_many_stims = {
            'aural': self.parent.session_settings.get_number_targets(),
            'visual': self.parent.session_settings.get_number_targets()}
        self.lists_to_be_built = [self.buffers['aural'],
                                  self.buffers['visual'], self.placement]
        self._make_stimulus_objects()

    def get_n(self: 'StimList') -> int:
        '''Return present n.'''

        return self.n

    def get_length(self: 'StimList') -> int:
        '''Return present list length.'''

        return self.length

    def get_working_total_stims(self: 'StimList', modality: str) -> int:
        '''Return how many different stim are available for the given
        modality.'''

        return self.how_many_stims[modality]

    def _make_stimulus_objects(self: 'StimList') -> None:

        #self.all_image_targets = []
        #self.all_sound_targets = []
        all_possible_image_targets = os.listdir('images/')
        all_possible_sound_targets = os.listdir('sounds/')
        
        for sound_file_index in range(len(all_possible_sound_targets)):

            # This reappending to a new list is to keep memory addresses 
            # uniform, this way points to single instance of each sound, if
            # only one list then each entry is a fresh reference.
            self.all_sound_targets.append(QtGui.QSound(str('sounds/' + all_possible_sound_targets[sound_file_index])))

        for path in all_possible_image_targets:

            if os.path.isfile(('images/' + path)):

                if str(
                    (self.parent.session_settings.get_number_targets() //
                     2)) not in path:

                    self.all_image_targets.append(
                        QtGui.QPixmap(('images/' + path)))

        # All targets are organized, and their index in the list is a unique
        # identifier for our purposes here.  Invoke the helper function that
        # returns a list for each modality that has the index for the stim
        # we want where the position in these lists are the position for the
        #  occurance of that stim.

    def make_index_list(self: 'StimList') -> None:
        '''Create and set stim target and available indicies lists.'''

        for i in range((self.get_length() + self.get_n())):

            for list_to_appended_to in self.lists_to_be_built:

                list_to_appended_to.append(-1)

            self.valid_index.append(i)

        # But the first n indexes are not valid for placement, so:

        self.valid_index = self.valid_index[self.get_n():]

    def place_targets(self: 'StimList') -> None:
        '''Place stim targets in valid positions.'''

        # For each modality type
        for mod in self.targets:

            for i in range(self.targets[mod]):

                # pick an index out of the list of available ones at random
                place_here = self.valid_index.pop(
                    randrange(0, len(self.valid_index)))
                # the string representing the modality is in the placement list
                # at the drawn index now.
                self.placement[place_here] = mod

    def place_stims(self: 'StimList', all_placed: bool=False) -> None:
        '''Place cue and target along with non match stims.'''

        n_value = self.get_n()
        block_length_total = n_value + self.get_length()
        visual_pairs = []
        aural_pairs = []

        for i in range(block_length_total):

            index_value = self.placement[i]

            if type(index_value) == str:

                if ((index_value == 'aural') or (index_value == 'both')):

                    aural_pairs.append([(i - n_value), i])

                if ((index_value == 'visual') or (index_value == 'both')):

                    visual_pairs.append([(i - n_value), i])

        aural_chains = self.link_up_chains(aural_pairs)
        visual_chains = self.link_up_chains(visual_pairs)

        for chain in [[aural_chains, 'aural'], [visual_chains, 'visual']]:

            self.pair_cue_targets(chain[0], chain[1])

        self._fill_non_matches()

    def pair_cue_targets(self: 'StimList', chain_list: list,
                         targets_modality: str) -> list:
        '''Updates object's list of matched targets and cues along with
        unmatched intermediate stimulus.'''

        last_stim_used = -1
        stim_number = -1

        for chain in chain_list:

            while stim_number == last_stim_used:

                stim_number = randrange(
                    0, self.get_working_total_stims(targets_modality))

            for index in chain:

                self.buffers[targets_modality][index] = stim_number

            last_stim_used = stim_number

    def _fill_non_matches(self: 'StimList') -> None:
        '''Fills in all positions that are not cues nor targets.'''

        block_n = self.get_n()
        stim_list_length = len(self.buffers['visual'])


        for modality in self.buffers:

            for i in range(stim_list_length):

                if self.buffers[modality][i] == -1:

                    write_value = False
                    candidate_value = randrange(
                        0, self.get_working_total_stims(modality))

                    while not write_value:

                        # Do 3 cases, nothing before to compare, nothing after
                        # to compare, midlist.  Check mislist first
                        if (((((i - block_n) >= 0) and
                              (self.buffers[modality][(i - block_n)] !=
                               candidate_value)) and
                             (((i + block_n) < stim_list_length) and
                              (self.buffers[modality][(i + block_n)] !=
                               candidate_value))) or
                            ((((i - block_n) >= 0) and
                              (self.buffers[modality][(i - block_n)] !=
                               candidate_value)) and
                             ((i + block_n) >= stim_list_length)) or
                            ((((i + block_n) < stim_list_length) and
                              (self.buffers[modality][(i + block_n)] !=
                               candidate_value)) and ((i - block_n) < 0))):

                            write_value = True

                        else:

                            candidate_value = randrange(
                                0, self.get_working_total_stims(modality))

                    self.buffers[modality][i] = candidate_value

    def link_up_chains(self: 'StimList', list_of_pairs: list) -> list:
        '''Attempt to make nice cue target fun times.'''

        list_of_matching_entries = []

        # first sort list, this sorts by first entry of each sublist.
        list_of_pairs.sort()

        # Next note all targets unique, all cues unique.  So, only one instance
        # of an index as a cue can exist, same for target.  However, a target
        # can be a cue.  Apply this fact.

        while len(list_of_pairs) > 0:

            working_entry = list_of_pairs.pop(0)

            # Have smallest [cue, target] pair isolated now.  See if target is also
            # a cue.  If so, meld together and check next, if not, pop out next
            # smallest and test that until no more to check.

            check_again = True

            while check_again:

                check_again = False

                entries_to_pop = []

                for entry in list_of_pairs:
                
                    if entry[0] == working_entry[-1]:

                        working_entry.append(entry[1])
                        entries_to_pop.append(entry)

                        # Well, before we move on, see if now some other pair
                        # links in to this chain.
                        check_again = True

                if len(entries_to_pop) > 0:
                
                    # Only pop out a pair if we bound it to a chain.
                    for pair in entries_to_pop:
                    
                        list_of_pairs.pop(list_of_pairs.index(pair))
                    
            list_of_matching_entries.append(working_entry)
            # Chain or pair, this is now to be outputted

        return list_of_matching_entries

    def _place_stimulus_objects(self: 'StimList') ->  None:
        '''Place image and sound objects into the respective buffers as a list
        whose elements are a list with the image object at index 0 and the
        sound object at index 1.'''

        buffer_object_keys = list(self.buffers.keys())
        final_buffer = []

        for i in range(self.parent.session_settings.get_total_block_length()):

            stims_at_point = [self.all_image_targets[
                self.buffers[buffer_object_keys[
                    buffer_object_keys.index('visual')]][i]],
                              self.all_sound_targets[
                                  self.buffers[buffer_object_keys[
                                      buffer_object_keys.index('aural')]][i]]]

            final_buffer.append(stims_at_point)

        return final_buffer

    def get_buffers(self: 'StimList') -> list:
        '''Return a list of sound and image objects blah blah blah.'''

        return self._place_stimulus_objects()
        #return list(zip(self.buffers['visual'], self.buffers['aural']))

    def make_buffer(self: 'StimList') -> None:
        '''Main procedural engine.'''

        self._refresh_attributes()
        self.make_index_list()
        self.place_targets()
        self.place_stims()