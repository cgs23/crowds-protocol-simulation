import csv
from random import randrange
import argparse

# Create parser
parser = argparse.ArgumentParser()

# Add arguments to the parser
parser.add_argument('corrupted_users_file', type=argparse.FileType('r'))

# Parse the arguments
args = parser.parse_args()

# Get the corrupted users from the given file
with open(args.corrupted_users_file.name) as corrupted_users_file:
    corrupted_users = [int(corrupted_user) for corrupted_user in corrupted_users_file]

# Parse the arguments
args = parser.parse_args()
with open('genUsersFile.csv', 'w', newline='') as csvfile:
    i = 0
    file_writer = csv.writer(csvfile, delimiter='\n')
    while i < 10000:
        randomUser = randrange(100)
        if randomUser not in corrupted_users:
            i = i + 1
            file_writer.writerow([randomUser])
