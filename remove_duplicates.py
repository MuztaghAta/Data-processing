"""
This script provides a hash-based approach to find duplicate files in given
directory and one can remove the duplicates if needed. Here I assume same name 
or same size based approach is not reliable.

Limitation:
1. This script works perfectly on Windows because the metheod subprocess.Popen 
that locates file in explorer is only for Windows.
2. this program can only identify duplicates if files are exactly the same. 
For a few cases, files are extremely similar (e.g. a PDF research paper 
with/without annotation) but they don't have the same hash. One can refer to 
Locality Sensitive Hashing for Similar Item Search for an answer.
"""

import os
import hashlib
from pathlib import Path
import time
import pickle
import subprocess


folder = Path('E:/MEGA/LitePrograms/example_remove_dup')  # folder to investigate
dup_file_name = 'duplicates.pickle'  # name of file to store buplicates results 
dup_file_path = os.path.join(folder, dup_file_name)
BUF_SIZE = 65536  # Read file in (e.g. 32kb=32768 or 64kb=65536) chunks
duplicates = {}  # a dictionary of (hash, file) pairs, a hash may have many
# corresponding files


def file_hash(file_path, buf_size):
    buf_size = BUF_SIZE
    h = hashlib.md5()  # create a hash object
    with open(file_path, 'rb') as f:  # rb - binary mode
        while True:
            data = f.read(buf_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


# find duplicate files in a directory
def find_duplicates(directory):
    for dir_path, dir_names, file_names in os.walk(directory):
        for file_name in file_names:
            full_path = os.path.join(dir_path, file_name)
            hash_key = file_hash(full_path, BUF_SIZE)
            if hash_key in duplicates:
                duplicates[hash_key].append(full_path)
            else:
                duplicates[hash_key] = [full_path]
    # remove unique entries that each hash has only one corresponding file
    for hash_key, files in list(duplicates.items()):
        if len(files) == 1:
            del duplicates[hash_key]
    return duplicates


# identify duplicates if it's not done before
if not os.path.exists(dup_file_path):
    start_time = time.time()  # measure time used to finish the task

    duplicates = find_duplicates(folder)

    # save the duplicates dictionary to a pickle file
    with open(dup_file_path,'wb') as pickle_out:
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
            # munually remove useless ones
        else:
            print('No such file: {}'.format(file))
    print('Locate the duplicates for file {0}'.format(idx) 
            + ' and please delete useless ones.')
    if idx != num_dup_files:
        input('Press Enter to proceed to the next file {0}/{1}'.format(
                idx+1, num_dup_files))
    else:
        print('No more duplicates!')
