#include "measure.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <inttypes.h>


#define MSR_RAPL_POWER_UNIT       0x606

/* Package RAPL Domain */
#define MSR_PKG_RAPL_POWER_LIMIT	0x610
#define MSR_PKG_ENERGY_STATUS		0x611
#define MSR_PKG_PERF_STATUS		0x613
#define MSR_PKG_POWER_INFO		0x614

/* PP0 RAPL Domain */
#define MSR_PP0_POWER_LIMIT		0x638
#define MSR_PP0_ENERGY_STATUS		0x639
#define MSR_PP0_POLICY			0x63A
#define MSR_PP0_PERF_STATUS		0x63B

/* PP1 RAPL Domain, may reflect to uncore devices */
#define MSR_PP1_POWER_LIMIT		0x640
#define MSR_PP1_ENERGY_STATUS		0x641
#define MSR_PP1_POLICY			0x642

/* DRAM RAPL Domain */
#define MSR_DRAM_POWER_LIMIT		0x618
#define MSR_DRAM_ENERGY_STATUS		0x619
#define MSR_DRAM_PERF_STATUS		0x61B
#define MSR_DRAM_POWER_INFO		0x61C

/* Core Voltage */
#define MSR_PERF_STATUS         0x198

/* RAPL bitsmasks */

#define POWER_UNIT_OFFSET          0
#define POWER_UNIT_MASK         0x0f

#define ENERGY_UNIT_OFFSET      0x08
#define ENERGY_UNIT_MASK        0x1f

#define TIME_UNIT_OFFSET        0x10
#define TIME_UNIT_MASK          0x0f

/* RAPL POWER UNIT MASKS */
#define POWER_INFO_UNIT_MASK     0x7fff
#define THERMAL_SHIFT                 0
#define MINIMUM_POWER_SHIFT          16
#define MAXIMUM_POWER_SHIFT          32
#define MAXIMUM_TIME_WINDOW_SHIFT    48


#define USE_MSR 1
#define SUB_DRAM 0

static uint64_t rdtsc() {
  uint64_t a, d;
  asm volatile("mfence");
  asm volatile("rdtsc" : "=a"(a), "=d"(d));
  a = (d << 32) | a;
  asm volatile("mfence");
  return a;
}

static uint64_t calib() {
  uint64_t start = rdtsc();
  sleep(1);
  uint64_t end = rdtsc();
  return end - start;
}

static int fd;
static int fd_dram;
static uint64_t rdtsc_scale;
static unsigned int energy_unit;

void init() {
#if USE_MSR == 0
  fd = open("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj", O_RDONLY);
  fd_dram = open("/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj", O_RDONLY);
#else
  fd = open("/dev/cpu/3/msr", O_RDONLY);
  uint64_t data;
  int n = pread(fd, &data, sizeof data, MSR_RAPL_POWER_UNIT);
  assert(n == sizeof data);
  energy_unit = 1<<((data>>ENERGY_UNIT_OFFSET)&ENERGY_UNIT_MASK);

#endif
  assert(fd > 0);
  rdtsc_scale = calib();
  // fprintf(stderr, "%" PRId64 "\n", rdtsc_scale);
}

uint64_t read_rapl() {
#if USE_MSR == 0
  char buffer[17];
  pread(fd, buffer, 16, 0);
  buffer[16] = 0;
  return strtol(buffer, NULL, 10);
#else
  uint64_t value;
  ssize_t n = pread(fd, &value, 8, MSR_PP0_ENERGY_STATUS);
  assert(n == 8);
  return value;
#endif
}

uint64_t read_rapl_dram() {
#if USE_MSR == 0
  char buffer[17];
  pread(fd_dram, buffer, 16, 0);
  buffer[16] = 0;
  return strtol(buffer, NULL, 10);
#else
  uint64_t value;
  ssize_t n = pread(fd, &value, 8, MSR_DRAM_ENERGY_STATUS);
  assert(n == 8);
  return value;
#endif
}

Measurement measure() {
  Measurement m;
  m.time_stamp = rdtsc();
  m.rapl_readout = read_rapl();
  #if SUB_DRAM == 1
    m.rapl_dram_only = read_rapl_dram();
  #endif
  return m;
}

Measurement measure_only_rapl() {
  Measurement m;
  m.rapl_readout = read_rapl();
  #if SUB_DRAM == 1
    m.rapl_dram_only = read_rapl_dram();
  #endif
  return m;
}

Sample convert(Measurement const &start, Measurement const &stop) {
  Sample s;
#if USE_MSR == 0
  s.energy = (stop.rapl_readout - start.rapl_readout) / 1000000.0;
  #if SUB_DRAM == 1
    s.energy = s.energy - ((stop.rapl_dram_only - start.rapl_dram_only) / 1000000.0);
  #endif
#else
  s.energy = (((double)(stop.rapl_readout - start.rapl_readout)/energy_unit));
  #if SUB_DRAM == 1
    s.energy = s.energy - (stop.rapl_dram_only - start.rapl_dram_only);
  #endif
#endif
  s.time   = (stop.time_stamp - start.time_stamp) / (double)rdtsc_scale;
  s.power  = s.energy / s.time;
  s.count  = 0;
  return s;
}

Sample convert(Measurement const &start, Measurement const &stop, double time_interval) {
  Sample s;
#if USE_MSR == 0
  s.energy = (stop.rapl_readout - start.rapl_readout) / 1000000.0;
  #if SUB_DRAM == 1
    s.energy = s.energy - ((stop.rapl_dram_only - start.rapl_dram_only) / 1000000.0);
  #endif
#else
  s.energy = (((double)(stop.rapl_readout - start.rapl_readout)/energy_unit));
  #if SUB_DRAM == 1
    s.energy = s.energy - (stop.rapl_dram_only - start.rapl_dram_only);
  #endif
#endif
  s.time   = time_interval;
  s.power  = s.energy / s.time;
  s.count  = 0;
  return s;
}

void add(Sample &dst, Sample const &src) {
  dst.energy += src.energy;
  dst.time += src.time;
  dst.power = dst.energy / dst.time;
  dst.count++;
}

void print(const Sample& sample) {
  printf("energy %5.5f J\n", sample.energy);
  printf("power  %5.5f W\n", sample.power);
  printf("time   %5.5f s\n", sample.time);
}

uint64_t get_timestamp() {
  return rdtsc();
}

uint64_t seconds_2_timeticks(double seconds) {
  return rdtsc_scale * seconds;
}