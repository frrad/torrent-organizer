#!/usr/bin/python

import bencode
import glob
import hashlib
import os
import shutil
import sys
import types


def decode(path):
    with open(path, 'r') as f:
        answer = bencode.bdecode(''.join(f.readlines()))
    return answer


def chunk_files(paths, size):
    if isinstance(paths, types.StringTypes):
        paths = [paths]

    chunk = ''

    for path in paths:
        with open(path, 'r') as f:
            while True:
                chunk += f.read(size - len(chunk))
                if len(chunk) == size:
                    yield chunk
                    chunk = ''
                else:
                    break

    if chunk != '':
        yield chunk


def file_hash_list(path, piece_length):
    hash_list = [hashlib.sha1(chunk).digest()
                 for chunk in chunk_files(path, piece_length)]
    return ''.join(hash_list)


def extract_descriptor(path):
    return path[path.rfind('/') + 1:path.rfind('.')]


def handle_multi_torrent(torrent_info, search_glob, destination_folder):

    piece_length = torrent_info['info']['piece length']
    series = []

    for file_info in torrent_info['info']['files']:
        possibles = find_potential_files(search_glob, file_info['length'])
        if len(possibles) == 0:
            print "Can't find any files matching", file_info['path'][0]
            return

        series.append(possibles)

    sequences = [[]]
    for spread in series:
        trashcan = []
        for part in spread:
            for lid in sequences:
                trashcan.append(lid + [part])
        sequences = trashcan

    for possibility in sequences:
        matches = file_hash_list(
            possibility, piece_length) == torrent_info['info']['pieces']
        print "Found files", possibility
        print 'Matches.' if matches else 'Doesn\'t match'
        if matches:
            print 'Creating directory', destination_folder
            os.makedirs(destination_folder)

            de, a = torrent_file_path, destination_folder
            print 'Copying from', de, 'to', a
            shutil.copy(de, a)

            destination_folder += '/' + torrent_info['info']['name']

            print 'Creating directory', destination_folder
            os.makedirs(destination_folder)

            for a, de in zip(torrent_info['info']['files'], possibility):
                a = a['path'][0]
                a = destination_folder + '/' + a
                print 'Copying from', de, 'to', a
                shutil.copyfile(de, a)

            return


def find_potential_files(path_glob, file_size, threshold=0):
    return [x for x in glob.glob(path_glob) if abs(os.path.getsize(x) - file_size) <= threshold]


torrent_file_path = os.path.abspath(sys.argv[1])
search_glob = '/mnt/disk-2/bib-backup/*.epub'
multi_glob = '/mnt/disk-2/bib-backup/*/*'
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
    handle_multi_torrent(torrent_dict, multi_glob, archive_path)
    sys.exit()


potential_files = find_potential_files(
    search_glob, torrent_dict['info']['length'], 99)


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
