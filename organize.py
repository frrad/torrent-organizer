#!/usr/bin/python

import shutil
import bencode
import glob
import hashlib
import os
import sys


def decode(path):
    with open(path, 'r') as f:
        answer = bencode.bdecode(''.join(f.readlines()))
    return answer


def file_hash_list(path, piece_length):
    hash_list = []

    with open(path, 'r') as f:
        chunk = f.read(piece_length)
        while chunk != '':
            hash_list.append(hashlib.sha1(chunk).digest())
            chunk = f.read(piece_length)

    return ''.join(hash_list)


def extract_descriptor(path):
    return path[path.rfind('/') + 1:path.rfind('.')]


torrent_file_path = os.path.abspath(sys.argv[1])
search_glob = '/mnt/disk-2/bib-backup/*.epub'
archive_root = '/mnt/disk-2/bib-archive/'


archive_path = archive_root + extract_descriptor(torrent_file_path)

print '********************'
print 'Considering', torrent_file_path


if os.path.isdir(archive_path):
    # todo: verify contents of folder
    print 'Destination path', archive_path, 'already exists.'
    sys.exit()


torrent_dict = decode(torrent_file_path)


print 'Name:', torrent_dict['info']['name']

if 'length' not in torrent_dict['info']:
    # todo: fix
    print 'Torrents with more than one file are not yet supported.'
    sys.exit()


potential_files = [x for x in glob.glob(search_glob) if abs(os.path.getsize(
    x) - torrent_dict['info']['length']) < 99]

num_matches = len(potential_files)
print 'Found %d potential file%s.' % (num_matches, 's' if num_matches != 1 else '')

print '===================='

true_file = ''

for file in potential_files:
    print 'Considering "%s"...' % file
    if (file_hash_list(file, torrent_dict['info']['piece length']) ==
            torrent_dict['info']['pieces']):
        print 'Matches.'
        true_file = file
    else:
        print 'Doesn\'t match'


print '===================='

if true_file == '':
    print 'No match found.'
    sys.exit()

print 'Creating directory', archive_path
os.makedirs(archive_path)

de, a = true_file, archive_path + '/' + torrent_dict['info']['name']
print 'Copying from', de, 'to', a
shutil.copyfile(de, a)

de, a = torrent_file_path, archive_path
print 'Copying from', de, 'to', a
shutil.copy(de, a)
