#include <stdio.h>

int main() {
    unsigned int eax, ebx, ecx, edx;

    // Execute CPUID with EAX=7, ECX=0
    asm volatile (
        "cpuid"
        : "=a" (eax), "=b" (ebx), "=c" (ecx), "=d" (edx)
        : "a" (7), "c" (0)
    );

    // Check bit 29 in the EDX register
    if (edx & (1 << 29)) {
        printf("Bit 29 is set (enumerated as 1).\n");
    } else {
        printf("Bit 29 is not set.\n");
    }

    return 0;
}
