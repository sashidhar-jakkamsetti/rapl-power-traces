#include "measure.h"

#include <stdio.h>
#include <sys/select.h>
#include <unistd.h>
#include <pthread.h>
#include <cstring>
#include <time.h>
#include <signal.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <fcntl.h>

using namespace std;

#define MAX 100000

timer_t gTimerid;
uint64_t writer = 0;
uint64_t sample_interval_ns = 1*100*1000llu;
double sample_interval_s = 0.0001;
char shmfilename[] = "/home/sashi/workspace/trace-collection/bin/shmem.txt";

char *shmem;
int shmfd;

Measurement buffer[MAX];

void measurement_callback(int sig) {
  // buffer[writer++] = measure_only_rapl();
  buffer[writer++] = measure();
}

void start_timer(void) {
  struct itimerspec value;

  uint64_t ns = sample_interval_ns;

  value.it_value.tv_sec = 0;
  value.it_value.tv_nsec = ns;

  value.it_interval.tv_sec = 0;
  value.it_interval.tv_nsec = ns;

  timer_settime(gTimerid, 0, &value, NULL);
}

void stop_timer(void) {
  struct itimerspec value;

  value.it_value.tv_sec = 0;
  value.it_value.tv_nsec = 0;

  value.it_interval.tv_sec = 0;
  value.it_interval.tv_nsec = 0;

  timer_settime(gTimerid, 0, &value, NULL);
}

int setup_shm() {
  shmfd = -1;
  if ((shmfd = open(shmfilename, O_RDWR, 0)) == -1)
  {
    printf("unable to open shmem file\n");
    return -1;
  }
  shmem = (char*) mmap(NULL, 2, PROT_READ | PROT_WRITE, MAP_SHARED, shmfd, 0);
  return 0;
}

void destroy_shm() {
  close(shmfd);
}


int main(int argc, char** argv) {
  init();
  (void) signal(SIGALRM, measurement_callback);
  timer_create(CLOCK_REALTIME, NULL, &gTimerid);

  setup_shm();
  Sample samples[MAX];

  while(true) {
    memset(samples, 0, sizeof(Sample)*MAX);
    writer = 0;

    while(shmem[0] != '1'){
      sleep(0);
    }
    start_timer();
    memset(shmem, '0', 1);
    // shmem[0] = '0';

    while(shmem[0] != '2'){
      sleep(0);
    }
    stop_timer();

    for (uint64_t i = 0; i < writer-1; ++i) {
      // samples[i] = convert(buffer[i], buffer[i+1], sample_interval_s);
      samples[i] = convert(buffer[i], buffer[i+1]);
      fprintf(stderr, "%10.10f;", samples[i].power);
    }
    fprintf(stderr, "\n");
    memset(shmem, '0', 1);
    // shmem[0] = '0';

    while(shmem[0] != '3' && shmem[0] != '4'){
      sleep(0);
    }

    if (shmem[0] == '4'){
      break;
    }
  }
  
  destroy_shm();
}