
#include <p24FJ64GB002.h>
#include <stdlib.h>
#include <stdbool.h>
#include "timestep.h"
#include "serhandler.h"
#include "buffer.h"
#include "leddriver.h"

static unsigned int timestep;
static bool timingStarted = false;

static unsigned char tempBuffer[6];
static bool tempBufferFull;

void startTiming(void) {
    timingStarted = true;
}

static void handleTempBuffer() {
    if(tempBuffer[2] & SMASK_SINGLE) {
        unsigned long val = ((unsigned long) tempBuffer[2]) << 30;
        val |= ((unsigned long) tempBuffer[3]) << 22;
        val |= ((unsigned long) tempBuffer[4]) << 14;
        val |= ((unsigned long) tempBuffer[5]) << 6;

        if(putOutputData(val)) {
            tempBufferFull = false;
        }
    } else {
        timestep = 0;
        tempBufferFull = false;
    }
}

void handleSerialUpdates() {
    while(true) {
        if(tempBufferFull) {
            unsigned int nextTime = (((unsigned int) tempBuffer[0]) << 8) | ((unsigned int) tempBuffer[1]);
            if(nextTime <= timestep) {
                handleTempBuffer();
            } else {
                Nop();
            }
            if(tempBufferFull)
                return;
        } else {
            int firstByte = bufferExtract();
            if(firstByte < 0)
                return;
            tempBuffer[0] = firstByte;
            tempBuffer[1] = bufferExtract();
            tempBuffer[2] = bufferExtract();
            if(tempBuffer[2] & SMASK_SINGLE) {
                tempBuffer[3] = bufferExtract();
                tempBuffer[4] = bufferExtract();
                tempBuffer[5] = bufferExtract();
            }
            tempBufferFull = true;
        }
    }
}

// Every timestep (10ms)
void __attribute__((__interrupt__,__auto_psv__)) _T1Interrupt(void) {
    IFS0bits.T1IF = 0;
    // Handle time steps
    if(timingStarted) {
        handleSerialUpdates();
        if(timestep != 0xffff) {
            timestep++;
        }
    }
}
