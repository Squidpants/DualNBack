from random import randrange

class StimList(object):

    def __init__(self: 'StimList') -> None:

        self.n = 1
        self.length = 20
        self.placement = []
        self.valid_index = []
        self.targets = {'aural': 4, 'visual': 4, 'both': 2}
        self.buffers = {'aural': [], 'visual': []}
        self.how_many_stims = {'aural': 8, 'visual': 8}
        self.lists_to_be_built = [self.buffers['aural'],
                                  self.buffers['visual'], self.placement]

    def get_n(self: 'StimList') -> int:
        '''Return present n.'''

        return self.n

    def get_length(self: 'StimList') -> int:
        '''Return present list length.'''

        return self.length

    def get_placement(self: 'StimList') -> list:
        '''Return present placement list.'''

        return self.placement

    def get_targets(self: 'StimList') -> dict:
        '''Return present dictionary of number of each type of target.'''

        return self.targets

    def get_valid_remaining_indexes(self: 'StimList') -> int:
        '''Return list of presently available target indicies.'''

        return self.valid_index

    def get_working_total_stims(self: 'StimList', modality: str) -> int:
        '''Return how many different stim are available for the given
        modality.'''

        return self.how_many_stims[modality]

    def get_visual_buffer(self: 'StimList') -> list:
        '''Return visual buffer list.'''

        return self.buffers['visual']

    def get_aural_buffer(self: 'StimList') -> list:
        '''Return aural buffer list.'''

        return self.buffers['aural']

    def set_working_total_stims(self: 'StimList', modality: str,
                                new_value: int) -> None:
        '''Set how many different stim are available for the given modality.'''

        self.how_many_stims[modality] = new_value

    def set_n(self: 'StimList', new_n: int) -> None:
        '''Set new n.'''

        self.n = new_n

    def set_length(self: 'StimList', new_length: int) -> None:
        '''Set new stimulus list length.'''

        self.length = new_length

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

 
    def _pair_cue_targets_helper(self: 'StimList', targets_modality: str,
                                 end_index: int, n_gap: int) -> list:
        '''Helper for cue placement.'''

        test_value = self.buffers[targets_modality][(end_index - n_gap)]

        if type(test_value) == str:

            self.buffers[targets_modality][(end_index - n_gap)] = self.\
                _pair_cue_targets_helper(targets_modality, (end_index - n_gap), n_gap)

        elif test_value == -1:

            self.buffers[targets_modality][(end_index - n_gap)] = randrange(
                0, self.get_working_total_stims())

        return self.buffers[targets_modality][(end_index - n_gap)]

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

    def make_buffer(self: 'StimList') -> None:
        '''Main procedural engine.'''

        self.make_index_list()
        self.place_targets()
        self.place_stims()

if __name__ == '__main__':

    p = StimList()
    p.make_buffer()