"""
This script provides a hash-based approach to find duplicate files in given
directory and one can remove the duplicates if needed.

Limitation: this program can only identify duplicates if files are exactly
the same. For a few cases, files are extremely similar (e.g. a PDF research
paper with/without annotation) but they don't have the same hash. One can
refer to Locality Sensitive Hashing for Similar Item Search for an answer.
"""

import os
import hashlib
from pathlib import Path
import time
import csv
import subprocess


BUF_SIZE = 65536  # Read file in (32kb=32768 or 64kb=65536) chunks
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


dup_file_name = 'duplicates.csv'
dup_file_path = os.path.join(os.getcwd(), dup_file_name)
# identify duplicates if it's not done before
if not os.path.exists(dup_file_path):
    start_time = time.time()  # measure time used to finish the task

    folder = Path('E:/MEGA/Literature/')
    duplicates = find_duplicates(folder)

    # save the duplicates dictionary to a csv file
    with open(dup_file_name, 'w', encoding='utf-8') as save_duplicates:
        w = csv.writer(save_duplicates)
        for key, val in duplicates.items():
            w.writerow([key, val])

    end_time = time.time()
    runtime = end_time - start_time  # in seconds
    print('Time used to find the duplicates is {} seconds'.format(runtime))
# load the csv file that saves the duplicates into a dictionary
else:
    with open(dup_file_name, 'r', encoding='utf-8') as extract:
        duplicates = dict(filter(None, csv.reader(extract)))

dup_list = list(duplicates.values())

# locate duplicates for a file in explorer and remove useless ones
num_dup_files = len(dup_list)
idx = 0
for files in dup_list:
    idx += 1
    for file in files:
        if os.path.exists(file):
            subprocess.Popen(r'explorer /select,"{}"'.format(file))
        else:
            print('No such file: {}'.format(file))
        # remove useless ones after all duplicates for a file are located
    input('Press Enter to proceed to next file {0}/{1}'.format(
        idx+1, num_dup_files))

# open the csv file that saves the duplicates dictionary (only for Windows)
# os.startfile(dup_file_path)  # open the file in explorer
# os.startfile(os.getcwd(), 'explore')  # open the containing folder
