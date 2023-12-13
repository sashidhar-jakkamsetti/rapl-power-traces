import numpy as np
import os
import datetime
import scipy.signal
import progressbar

SBOX = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

data_subfolder = '1031'
DATA_FOLDER = "/home/jas4pi/power-analysis/trace-collection/data/"
OUT_FILE_PREFIX = "data"
IN_FILE_PREFIX = "log"

align_algo = 'corr'
pad = 'mean'

TRACES = []
PT = []
KEY = []


def read_raw_data(folder, prefix):
    failed_traces = []
    count = 0
    allfiles = [file for file in os.listdir(folder) if prefix in file]
    bar = progressbar.ProgressBar(maxval=len(allfiles)*37000, widgets=['[', progressbar.Timer(), '] ', \
														    progressbar.Bar(), ' (',  \
																progressbar.ETA(), ')', ' (', \
																	 progressbar.Percentage(), ')'])
    print("reading traces from log files in folder: \n", folder)
    bar.start()
    for i, filename in enumerate(allfiles):
        # print("reading traces from file: ", os.path.join(folder, filename))
        f = os.path.join(folder, filename)
        file = open(f, 'r')
        
        while True:
            line = file.readline()
            if line == '':
                break
            if "[sudo] password for jas4pi: " in line:
                line = line.replace("[sudo] password for jas4pi: ", "")
            trace = []
            key = []
            pt = []

            try:
                words = line.strip().strip(' ;,').split(';')
                # trace = [float(word) for word in words if float(word) != float(0)]
                trace = [float(word) for word in words]
                
                line = file.readline()
                words = line.strip().strip(' ;,').split(';')
                key = [int(word) for word in words]
                
                line = file.readline()
                words = line.strip().strip(' ;,').split(';')
                pt = [int(word) for word in words]
                
            except:
                print("Unable to parse line# {0}".format(count))
                failed_traces.append(count)
                continue
            
            count += 1
            TRACES.append(trace)
            KEY.append(key)
            PT.append(pt)
            bar.update(count)
                
        file.close()
            
        assert(len(TRACES) == len(KEY) == len(PT))
    bar.finish()


def align_traces(aligned: np.ndarray, unaligned: np.ndarray, algo='fft', pad='zero'):
    bar = progressbar.ProgressBar(maxval=len(unaligned), widgets=['[', progressbar.Timer(), '] ', \
														    progressbar.Bar(), ' (',  \
																progressbar.ETA(), ')', ' (', \
																	 progressbar.Percentage(), ')'])
    
    aligned2 = np.zeros(((len(aligned) + len(unaligned)), len(aligned[0])))
    for i in range(len(aligned)):
        aligned2[i] = aligned[i]

    align_func = None
    if algo == 'fft':
        print("\nAligning traces using fft convolution\n")
    else:
        print("\nAligning traces using time correlate\n")

    bar.start()
    for i in range(len(unaligned)):
        alignment = None
        if algo == 'fft':
            alignment = scipy.signal.fftconvolve(aligned[0], unaligned[i])
        else:
            alignment = scipy.signal.correlate(aligned[0], unaligned[i])

        offset = np.argmax(alignment) - len(aligned[0])
        pad_value = float(0)
        if pad == 'mean':
            pad_value = np.mean(unaligned[i])
        new_alignment = np.array([pad_value]*len(aligned[0]))
        for j in range(len(aligned[0])):
            if not (j + offset < 0 or j + offset >= len(aligned[0])):
                new_alignment[j] = unaligned[i][j + offset]

        aligned2[i + len(aligned)] = new_alignment
        bar.update(i + 1)
    bar.finish()
    return aligned2


def interp1d(array: np.ndarray, new_len: int) -> np.ndarray:
    la = len(array)
    return np.interp(np.linspace(0, la - 1, num=new_len), np.arange(la), array)


def convert_to_nparray(align_algo, pad='zero'):
    len_trace = np.array([len(t) for t in TRACES])
    mi = len_trace.min()
    ma = len_trace.max()
    print("\nMin length of trace: {0}, max: {1}".format(mi, ma))
    print("Number of traces before purning: {0}".format(len(TRACES)))

    mean_len = len_trace.mean()
    std_len = len_trace.std()
    range_min = int(mean_len - std_len*6)
    range_max = int(mean_len + std_len*6)
    print("\nPurning traces with length below: {0}, and above: {1}".format(range_min, range_max))

    i = 0
    mi = ma
    while i < len(TRACES):
        if len(TRACES[i]) <= range_min or len(TRACES[i]) >= range_max:
            if len(TRACES[i]) <= range_min:
                print("deleting trace# {0} due to length {1} < {2}".format(i, len(TRACES[i]), range_min))
            elif len(TRACES[i]) >= range_max:
                print("deleting trace# {0} due to length {1} > {2}".format(i, len(TRACES[i]), range_max))
            
            del TRACES[i]
            del KEY[i]
            del PT[i]
        else:
            if mi > len(TRACES[i]):
                mi = len(TRACES[i])
            i += 1
    
    assert(len(TRACES) == len(KEY) == len(PT))
    print("\nNumber of traces after purning: {0}".format(len(TRACES)))
    print("Number of traces purned: {0}".format(len(len_trace) - len(TRACES)))

    ref_ids = []
    trim_len = int(mean_len)
    pad_value = float(0) # default pad value is zero

    print("\nPading the traces with {}".format(pad))

    for i in range(len(TRACES)):
        if len(TRACES[i]) > trim_len:
            TRACES[i] = TRACES[i][:trim_len]
        elif len(TRACES[i]) < trim_len:
            if pad == 'mean':
                pad_value = np.mean(TRACES[i])
            TRACES[i].extend([pad_value]*(trim_len - len(TRACES[i])))
            # TRACES[i].extend([float(0)]*(trim_len - len(TRACES[i])))
        else:
            ref_ids.append(i)

    aligned_traces = []
    aligned_traces.append(TRACES[ref_ids[0]])
    aligned_traces = np.array([np.array(t) for t in aligned_traces])

    unaligned_traces = TRACES[:ref_ids[0]] + TRACES[ref_ids[0] + 1:]
    unaligned_traces = np.array([np.array(t) for t in unaligned_traces])
    all_aligned = align_traces(aligned_traces, unaligned_traces, algo=align_algo, pad=pad)
    # eq_trace = [interp1d(np.array(t), mi) for t in TRACES]

    assert(len(all_aligned) == len(KEY) == len(PT))
    
    print("Trace length after alignment: {0}".format(len(all_aligned[0])))

    np_trace = all_aligned
    np_key = np.array([np.array(ai) for ai in KEY])
    np_pt = np.array([np.array(ai) for ai in PT])
    return np_trace, np_key, np_pt


def gen_labels(pt, key):
    labels = []
    for i in range(len(pt)):
        label = []
        for j in range(16):
            label.append(SBOX[pt[i][j]^key[i][j]])
        labels.append(np.array(label))
    return np.array(labels)


def save_np_data(np_trace, np_key, np_pt, np_label, folder, prefix):
    assert(len(np_trace) == len(np_key) == len(np_pt) == len(np_label))
    fn_trace = prefix + "_traces.npy"
    fn_trace = os.path.join(folder, fn_trace)
    np.save(fn_trace, np_trace)
    fn_key = prefix + "_keys.npy"
    fn_key = os.path.join(folder, fn_key)
    np.save(fn_key, np_key)
    fn_pt = prefix + "_pts.npy"
    fn_pt = os.path.join(folder, fn_pt)
    np.save(fn_pt, np_pt)
    fn_label = prefix + "_labels.npy"
    fn_label = os.path.join(folder, fn_label)
    np.save(fn_label, np_label)


data_folder_path = os.path.join(DATA_FOLDER, data_subfolder)

log_prefix = IN_FILE_PREFIX
out_prefix = OUT_FILE_PREFIX + str('_') + align_algo + str('_') + pad

print("Initiating data cleaning and preprocessing\n")

read_raw_data(data_folder_path, log_prefix)
trace, key, pt = convert_to_nparray(align_algo, pad)
label = gen_labels(pt, key)

save_np_data(trace, key, pt, label, data_folder_path, out_prefix)

print("\nFinal number of traces: {0}, Trace length: {1}".format(len(key), len(trace[0])))

