import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from scipy.spatial import distance
import statistics as stats

traces = []
file = open('/home/jas4pi/workspace/rapl-power-traces/data/log-aes-test.csv', 'r')

count = 0
while count <12:
    line = file.readline()
    if line == '':
        break
    if "[sudo] password for sashi: " in line:
        line = line.replace("[sudo] password for sashi: ", "")
    trace = []

    words = line.strip().strip(' ;,').split(';')
    # trace = [float(word) for word in words if float(word) != float(0)]
    trace = [float(word) for word in words]
    traces.append(trace)
    line = file.readline()
    line = file.readline()
    line = file.readline()
    count += 1

file.close()

traces = traces[1:-1]
initial_len = len(traces)
len_trace = [len(t) for t in traces]
pad = 'mean'

mean_len = stats.mean(len_trace)
std_len = stats.stdev(len_trace)
print("\nMean len: {0}, std len: {1}".format(mean_len, std_len))
range_min = int(mean_len - std_len*4)
range_max = int(mean_len + std_len*4)
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

print("\nPre padding with pad value to make all traces match max len\n")

for i in range(len(traces)):
    if len(traces[i]) < max_len:
        pad_len = max_len - len(traces[i])
        if pad == 'mean':
            traces[i] = np.pad(traces[i], (0, pad_len), mode='mean')
        else:
            traces[i] = np.pad(traces[i], (0, pad_len), mode='constant', constant_values=float(0))
    print("mean and std of trace {0}:  {1}, {2}".format(i, np.mean(traces[i]), np.std(traces[i])))


print("\npreprocessing: filtering, alignment\n")
traces = np.array(traces)
fig = 0
N=2
for i in range(int(len(traces[:int(len(len_trace)*0.5)]))):
    a = traces[i]
    a = sig.lfilter(np.ones((N,))/N, 1, a)
    print("mean and std of trace {0}:  {1}, {2}".format(i, np.mean(a), np.std(a)))
    b = traces[i + 1]
    b = sig.lfilter(np.ones((N,))/N, 1, b)
    # print(a)
    alignment = sig.correlate(a, b)
    euclid_distance_a_to_b = distance.euclidean(a, b)
    print("euclidean distance: ", euclid_distance_a_to_b)
    print("argmax of alignment: ", np.argmax(alignment))
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
    plt.plot(a[100:1100], alpha=0.7, label="trace1", marker=".")
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