#!/usr/bin/env python

import mmap
import os
import time
import datetime
import subprocess
from Crypto.Cipher import AES
# import progressbar
import sys

HOME_FOLDER = "/home/sashi/workspace/trace-collection/"

measureapi = HOME_FOLDER + "bin/measureapi"
shmfd_name = HOME_FOLDER + "bin/shmem.txt"
DATA_FOLDER = HOME_FOLDER + "data/"
DEBUG_FOLDER = HOME_FOLDER + "debug/"
OUT_FILE_PREFIX = "log"
DEBUG_FILE_PREFIX = "debug"

AES_NI = True

measure_cpu_id = sys.argv[1]
if sys.argv[2] != 'aes-ni':
	AES_NI = False

if AES_NI:
	OUT_FILE_PREFIX += "-aes-ni"
else:
	OUT_FILE_PREFIX += "-aes"

block_len = 16
enc_iter = 16*1024
if AES_NI:
	enc_iter = 16*1024 * 16

# exp_iter = 1024*1024
exp_iter = 2
pt_multiplier = 1024

# key = bytes([0,0,0,255,0,0,0,0,0,0,0,0,0,0,0,0])
key = bytes([75,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
# key = bytes([75,14,238,255,100,129,64,201,187,192,39,177,4,243,248,16])
# key = os.urandom(block_len)

password = ""

def encryption_exp():
	pt_og = os.urandom(block_len)
	pt = pt_og*(pt_multiplier)

	cipher = AES.new(key, AES.MODE_ECB, use_aesni=AES_NI)

	start_time = time.time()

	shm.seek(0)
	shm.write('1'.encode())
	shm.flush()
	
	shm.seek(0)
	while shm.read(1).decode() != '0':
		shm.seek(0)

	for _ in range(enc_iter):
		ct = cipher.encrypt(pt)

	shm.seek(0)
	shm.write('2'.encode())
	shm.flush()

	shm.seek(0)
	while shm.read(1).decode() != '0':
		shm.seek(0)

	end_time = time.time()

	debugfd.write("------ {0} seconds ------\n".format(str(end_time - start_time)))
	debugfd.flush()

	return key, pt_og, ct[:block_len]


with open(shmfd_name, "w+b") as fd:
	fd.write("00".encode())
	fd.flush()

date = datetime.datetime.now()
directory_name = str(date.month) + str(date.day)
data_folder_path = os.path.join(DATA_FOLDER, directory_name)
if not os.path.exists(data_folder_path):
	os.makedirs(data_folder_path)

log_filename = os.path.join(data_folder_path, OUT_FILE_PREFIX + ".csv")
logfd = open(log_filename, "w+")

passcmd = subprocess.Popen(['echo', password], stdout=subprocess.PIPE)
cproc = subprocess.Popen(["sudo", "-S", "taskset", "-c", measure_cpu_id, measureapi], 
						 stdin=passcmd.stdout, \
						 stdout=subprocess.DEVNULL, 
						 stderr=logfd, shell=False)

shmfd = open(shmfd_name, "r+")
shm = mmap.mmap(shmfd.fileno(), 2, flags=mmap.MAP_SHARED, \
				prot=mmap.PROT_WRITE|mmap.PROT_READ, offset=0)

debug_filename = os.path.join(DEBUG_FOLDER, DEBUG_FILE_PREFIX + str(date))
debugfd = open(debug_filename, "w+")

# print("starting experiments\n")
debugfd.write("Debug log for instance at time: {0}\n\n".format(str(date)))
debugfd.flush()

# bar = progressbar.ProgressBar(maxval=exp_iter, widgets=['[', progressbar.Timer(), '] ', \
# 														    progressbar.Bar(), ' (',  \
# 															progressbar.ETA(), ')', ' (', \
# 															progressbar.Percentage(), ')'])


# bar.start()
for i in range(exp_iter):
	debugfd.write("experiment {0}:\t".format(i))
	debugfd.flush()
	
	key, pt, ct = encryption_exp()
	logfd.flush()
	# print("exp ", i)

	key_list = list(key)
	for item in key_list:
		logfd.write("{0};".format(item))
	logfd.write("\n")
	logfd.flush()

	pt_list = list(pt)
	for item in pt_list:
		logfd.write("{0};".format(item))
	logfd.write("\n")
	logfd.flush()

	ct_list = list(ct)
	for item in ct_list:
		logfd.write("{0};".format(item))
	logfd.write("\n")
	logfd.flush()

	shm.seek(0)
	shm.write('3'.encode())
	shm.flush()

	# bar.update(i + 1)

shm.seek(0)
shm.write('4'.encode())
shm.flush()
shm.close()
shmfd.close()

# bar.finish()
logfd.flush()
logfd.close()

debugfd.write("Finished!\n")
debugfd.flush()
debugfd.close()
# print("finished!\n")