# postprocessing.py - Contains functions useful for postprocessing outputs
import json


def hybridize(first, second, duplicate_handling='ask', write_to_file=False, filename=None, verbose=False, ignore_source=False):
    '''
    Function to hybridize two jsons scraped that has GPTs. Carefully checks for duplicate GPTs and merges them into one
    via the openAI ID which we take to be objectively true.

    :return:
    '''

    total_errors = {'minor': 0, 'major': 0}
    total_uniqueness = 0

    MINOR_KEYS = ["vanity_metrics", "display", 'author', 'display', 'updated_at', 'short_url', 'share_recipient']
    total_gizmos = []

    # Deep copy
    for gizmo in second:
        total_gizmos.append(gizmo)

    # verify structure of them
    if verbose:
        print('Hybridizing GPTs...')

        # determine if the structures are valid
        if type(first) is list and type(second) is list:
            print("First and Second Arguments are both valid lists")

            for first_gizmo in first:

                id_of_gizmo = first_gizmo["gizmo"]["id"]
                id_already_exists, second_gizmo = check_if_id_already_exists_in_list(id_of_gizmo, second)

                if id_already_exists:

                    scoped_in_first_gizmo = first_gizmo["gizmo"]
                    scoped_in_second_gizmo = second_gizmo["gizmo"]
                    # print(scoped_in_first_gizmo["display"])
                    # print(scoped_in_second_gizmo["display"])
                    if id_already_exists:
                        errors = []
                        # check if every field other than "source" is the same
                        for key in scoped_in_first_gizmo:
                            if key == "id" or key == "source":
                                continue
                            else:
                                if scoped_in_first_gizmo[key] == scoped_in_second_gizmo[key]:
                                    continue
                                else:
                                    if verbose:
                                        print("Error in hybridizing GPTs, conflict between {} & {} on key {}".format(scoped_in_first_gizmo[key], scoped_in_second_gizmo[key], key))
                                    errors.append(key)

                        if len(errors) == 0:
                            pass
                        elif is_subset(MINOR_KEYS, errors):
                            if verbose:
                                print("All errors are only considered minor")
                            total_errors['minor'] += 1
                        else:
                            total_errors['major'] += 1

                            major_errors = errors
                            # remove all errors that are in MINOR_KEYS
                            for minor_error in MINOR_KEYS:
                                if minor_error in major_errors:
                                    major_errors.remove(minor_error)

                            if duplicate_handling == 'stop':
                                print(major_errors)
                                for error_key in errors:
                                    print(scoped_in_first_gizmo[error_key])
                                    print(scoped_in_second_gizmo[error_key])
                                raise ValueError("Serious errors found while hybridizing GPTs")
                else:
                    total_uniqueness += 1
                    total_gizmos.append(first_gizmo)

        else:
            raise ValueError("Type mismatch. First is {} and second is {}".format(type(first), type(second)))

    print("New Plugins Added: {}\nErrors found: {}\nLength of first: {}\nLength of second: {}\nLength of total: {}".format(total_uniqueness, total_errors, len(first), len(second), len(total_gizmos)))
    return total_gizmos, total_uniqueness, total_errors

def check_if_id_already_exists_in_list(id, reference_array):

    for gizmo in reference_array:
        if gizmo['gizmo']['id'] == id:
            return True, gizmo

    return False, None

def is_subset(reference_array, test_array):
    # Convert lists to sets
    reference_set = set(reference_array)
    test_set = set(test_array)

    # Check if test_set is a subset of reference_set
    return test_set.issubset(reference_set)

def main():
    print('Loading GPTs...')
    # GPT manifest s
    manifest_1 = json.load(open('data/manifest1.json'))
    manifest_2 = json.load(open('data/manifest2.json'))

    hybridize(manifest_1['gizmos'], manifest_2, duplicate_handling='second', write_to_file=False, filename=None, verbose=True)



if __name__ == "__main__":
    main()







