#!/usr/bin/python

import bencode
import os
import glob
import hashlib


def file_hash_list(path, piece_length):
    hash_list = []

    with open(path, 'r') as f:
        chunk = f.read(piece_length)
        while chunk != '':
            hash_list.append(hashlib.sha1(chunk).digest())
            chunk = f.read(piece_length)

    return ''.join(hash_list)


file_path = '/home/frederick/104566.torrent'
search_path = '/mnt/disk-2/bib-backup/*.epub'


with open(file_path, 'r') as f:
    torrent_dict = bencode.bdecode(''.join(f.readlines()))


print 'Name:', torrent_dict['info']['name']
piece_length = torrent_dict['info']['piece length']
pieces = torrent_dict['info']['pieces']


potential_files = [x for x in glob.glob(search_path) if os.path.getsize(
    x) == torrent_dict['info']['length']]

num_matches = len(potential_files)
print 'Found %d potential file%s.' % (num_matches, 's' if num_matches > 1 else '')


print '===================='

for file in potential_files:
    print 'Considering "%s"...' % file
    if file_hash_list(file, piece_length) == pieces:
        print 'Matches.'
    else:
        print 'Doesn\'t match'
