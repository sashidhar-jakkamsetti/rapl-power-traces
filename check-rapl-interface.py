import numpy as np
import os
import scipy.signal
from scipy.spatial import distance
import matplotlib.pyplot as plt

trace1 = []
trace2 = []

file = open('/home/jas4pi/power-analysis/trace-collection/data/1030/log-msr.csv', 'r')
        
while True:
    line = file.readline()
    if line == '':
        break
    if "[sudo] password for jas4pi: " in line:
        line = line.replace("[sudo] password for jas4pi: ", "")
    trace = []

    words = line.strip().strip(' ;,').split(';')
    # trace = [float(word) for word in words if float(word) != float(0)]
    trace = [float(word)/10000 for word in words]
    trace1.append(trace)
    line = file.readline()
    line = file.readline()

file.close()


file = open('/home/jas4pi/power-analysis/trace-collection/data/1030/log-pc.csv', 'r')
        
while True:
    line = file.readline()
    if line == '':
        break
    if "[sudo] password for jas4pi: " in line:
        line = line.replace("[sudo] password for jas4pi: ", "")
    trace = []

    words = line.strip().strip(' ;,').split(';')
    # trace = [float(word) for word in words if float(word) != float(0)]
    trace = [float(word) for word in words]
    trace2.append(trace)
    line = file.readline()
    line = file.readline()

file.close()

l = len(trace1)

filtered1 = []
filtered2 = []

for i in range(l):
    if len(trace1[i]) == len(trace2[i]):
        filtered1.append(trace1[i])
        filtered2.append(trace2[i])
        if len(filtered1) > 3:
            break

test_arr1 = [i for i in range(len(filtered1[0]))]     
test_rand = np.random.choice(np.arange(max(filtered2[0]), dtype=np.float32), size=(len(filtered2[0])), replace=True)
filtered1.append(test_arr1)

test_arr2 = [i for i in range(len(filtered1[0]))]
filtered2.append(test_arr2)

# filtered1 = np.array(filtered1)
# filtered2 = np.array(filtered2)

fig = 0
for i in range(int(len(filtered1))):

    alignment = scipy.signal.correlate(filtered1[i], filtered2[i])
    euclid_distance_a_to_b = distance.euclidean(filtered1[i], filtered2[i])
    print("euclidean distance ", euclid_distance_a_to_b)
    print(np.argmax(alignment))
    offset = np.argmax(alignment) - len(filtered1[0])
    pad_value = float(0)
    new_alignment = np.array([pad_value]*len(filtered1[i]))
    for j in range(len(filtered1[i])):
        if not (j + offset < 0 or j + offset >= len(filtered1[i])):
            new_alignment[j] = filtered2[i][j + offset]

    a = filtered1[i]
    b = new_alignment
    plt.figure(fig, figsize=(12, 4))
    # _, axes = plt.subplots(1, 1, figsize=(12, 4))
    plt.plot(a, alpha=0.7, label="msr", marker="o")
    plt.plot(b, alpha=0.7, label="powercap", marker="D")

    # axes.vlines(np.arange(0, len(a), 1), a, b, alpha = 0.7)
    plt.legend()
    # plt.set_title("Raw signals | Euclidean distance from 'a' to 'b' = {:0.1f}".format(euclid_distance_a_to_b))
    plt.savefig('plot{0}-traces.png'.format(fig))
    fig += 1
    plt.figure(fig, figsize=(8, 4))
    plt.plot(alignment, color='blue')
    plt.xlabel('time') 
    plt.ylabel('alignment') 
    plt.grid()
    plt.show() 
    plt.savefig('plot{0}-align.png'.format(fig))
    fig += 1