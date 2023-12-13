#!/bin/bash

taskset -c $1 python3 /home/sashi/work/ransomware/ransomware-data-collection-intel/trace-collection/experiment.py $2 $3

# Command to run from VM: ssh jas4pi@icy "nohup /home/jas4pi/power-analysis/trace-collection/run.sh 3 4 aes &" &
# Command for copying trace data to VM: scp jas4pi@shannon:/home/jas4pi/power-analysis/trace-collection/data/1031/log.csv /home/sashi/work/ransomware/side-channel-analysis-toolbox/data/amd-rapl/1031/
