import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from scipy.spatial import distance
import statistics as stats

traces = []
file = open('/home/jas4pi/power-analysis/trace-collection/data/1120/log0.csv', 'r')

while True:
    line = file.readline()
    if line == '':
        break
    if "[sudo] password for jas4pi: " in line:
        line = line.replace("[sudo] password for jas4pi: ", "")
    trace = []

    words = line.strip().strip(' ;,').split(';')
    # trace = [float(word) for word in words if float(word) != float(0)]
    trace = [float(word)/1 for word in words]
    traces.append(trace)
    line = file.readline()
    line = file.readline()

file.close()

initial_len = len(traces)
len_trace = [len(t) for t in traces]
pad = 'mean'

mean_len = stats.mean(len_trace)
std_len = stats.stdev(len_trace)
range_min = int(mean_len - std_len*2)
range_max = int(mean_len + std_len*2)
print("\nPurning traces with length below: {0}, and above: {1}".format(range_min, range_max))

i = 0
while i < len(traces):
    if len(traces[i]) <= range_min or len(traces[i]) >= range_max:
        if len(traces[i]) <= range_min:
            print("deleting trace# {0} due to length {1} < {2}".format(i, len(traces[i]), range_min))
        elif len(traces[i]) >= range_max:
            print("deleting trace# {0} due to length {1} > {2}".format(i, len(traces[i]), range_max))
        
        del traces[i]
        del len_trace[i]
    else:
        i += 1

max_len = int(max(len_trace))

print("\nPre padding with pad value to make all traces match max len")
for i in range(len(traces)):
    if len(traces[i]) < max_len:
        pad_len = max_len - len(traces[i])
        if pad == 'mean':
            traces[i] = np.pad(traces[i], (0, pad_len), mode='mean')
        else:
            traces[i] = np.pad(traces[i], (0, pad_len), mode='constant', constant_values=float(0))


traces = np.array(traces)
fig = 0
for i in range(int(len(traces[:int(len(len_trace)*0.5)]))):
    a = traces[i]
    b = traces[i + 1]
    # a = traces[i][100:1000]
    # b = traces[i + 1][100:1000]
    print(a)
    alignment = sig.correlate(a, b)
    euclid_distance_a_to_b = distance.euclidean(a, b)
    print("euclidean distance ", euclid_distance_a_to_b)
    print(np.argmax(alignment))
    offset = np.argmax(alignment) - len(a)
    pad_value = np.mean(a)
    new_alignment = np.array([pad_value]*len(a))
    for j in range(len(a)):
        if not (j + offset < 0 or j + offset >= len(a)):
            new_alignment[j] = b[j + offset]

    a = a
    b = new_alignment
    plt.figure(fig, figsize=(12, 4))
    # _, axes = plt.subplots(1, 1, figsize=(12, 4))
    plt.plot(a, alpha=0.7, label="trace1", marker=".")
    # plt.plot(b, alpha=0.7, label="trace2", marker="D")

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