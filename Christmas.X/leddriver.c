#include <p24FJ64GB002.h>
#include <stdbool.h>

#define ARRAY_SIZE 20

volatile unsigned long lightOutBuf[ARRAY_SIZE] __attribute__ ((near));
volatile unsigned int outReadPtr __attribute__ ((near));
volatile unsigned int outWritePtr __attribute__ ((near));

bool putOutputData(unsigned long data) {
    int filled = outWritePtr - outReadPtr;
    if(filled < 0)
        filled += ARRAY_SIZE;

    if(filled == ARRAY_SIZE - 1)
        return false;

    lightOutBuf[outWritePtr] = data;
    int newPtr = outWritePtr + 1;
    if(newPtr >= ARRAY_SIZE)
        newPtr = 0;
    outWritePtr = newPtr;
    IEC0bits.T2IE = 1;
    return true;
}