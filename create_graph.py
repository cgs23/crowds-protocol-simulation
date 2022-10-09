import sys
import random

num_users = int(sys.argv[1])
assert num_users > 0, 'Positive integer for num users'
adj_prob = float(sys.argv[2])
assert adj_prob >= 0 and adj_prob <= 1, 'Float within [0,1] for adjacency probability'

matrix = []

for i in range(num_users):
    tmp = []
    for j in range(num_users):
        tmp.append('0')
    matrix.append(tmp)

for i in range(num_users):
    for j in range(i+1, num_users):
        if random.random() <= adj_prob:
            matrix[i][j] = '1'
            matrix[j][i] = '1'

for i in matrix:
    print(' '.join(i))