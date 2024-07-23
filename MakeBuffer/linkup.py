def link_up(list_of_pairs: list) -> list:
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






if __name__ == '__main__':

    lst = [[4, 1], [2, 3], [5, 6], [1, 2], [3,4]]

    print(link_up(lst))