"""
This script provides a hash-based approach to find duplicate files in given
directory and one can remove the duplicates if needed.

Limitation:
1. This script works perfectly on Windows because the method 'subprocess.Popen'
that locates file in explorer is only for Windows.
2. This program can only identify duplicates if files are exactly the same.
For cases where files are extremely similar (e.g. a PDF research paper
with/without annotation) but they don't have the same hash, one can refer to
Locality Sensitive Hashing for Similar Item Search for an answer.
"""

import os
import hashlib
import time
import pickle
import subprocess
from pathlib import Path


folder = Path('./example_remove_dup')  # folder to investigate
dup_file_name = 'duplicates.pickle'  # name of file to store duplicates results
dup_file_path = os.path.join(folder, dup_file_name)
buffer_size = 65536  # Read file in chunks (e.g. 32kb=32768 or 64kb=65536)
duplicates = {}  # a dictionary of (hash, file) pairs, a hash may have many
# corresponding files with different names


def file_hash(file_path, buff_size):
    """Compute md5 hash for a given file"""
    h = hashlib.md5()  # create a hash object
    with open(file_path, 'rb') as f:  # rb - binary mode
        while True:
            data = f.read(buff_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def find_duplicates(directory):
    """Find duplicate files in a directory"""
    for dir_path, dir_names, file_names in os.walk(directory):
        for file_name in file_names:
            full_path = os.path.join(dir_path, file_name)
            hash_key = file_hash(full_path, buffer_size)
            if hash_key in duplicates:
                duplicates[hash_key].append(full_path)
            else:
                duplicates[hash_key] = [full_path]
    # remove unique entries that each hash has only one corresponding file
    for hash_key, f in list(duplicates.items()):
        if len(f) == 1:
            del duplicates[hash_key]
    return duplicates


# identify duplicates if it's not done before
if not os.path.exists(dup_file_path):
    start_time = time.time()  # measure time used to finish the task
    duplicates = find_duplicates(folder)
    # save the duplicates dictionary to a pickle file
    with open(dup_file_path, 'wb') as pickle_out:
        pickle.dump(duplicates, pickle_out)
    end_time = time.time()
    runtime = end_time - start_time  # in seconds
    print('Time used to find the duplicates is {} seconds'.format(runtime))
# load the pickle file that saves the duplicates into a dictionary
else:
    with open(dup_file_path, 'rb') as pickle_in:
        duplicates = pickle.load(pickle_in)
num_dup_files = len(duplicates)
print('There are {} files have duplicates.'.format(num_dup_files))

# locate duplicates for a file in explorer and remove useless ones
idx = 0
for files in duplicates.values():
    idx += 1
    for file in files:
        if os.path.exists(file):
            subprocess.Popen(r'explorer /select,"{}"'.format(file))
            # manually remove useless ones
        else:
            print('No such file: {}'.format(file))
    print('Locate the duplicates for file {0}'.format(idx)
          + ' and please delete useless ones.')
    if idx != num_dup_files:
        input('Press Enter to proceed to the next file {0}/{1}'.format(
                idx+1, num_dup_files))
    else:
        print('No more duplicates!')
