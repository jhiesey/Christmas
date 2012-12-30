
#include <stdbool.h>
#include <p24FJ64GB002.h>
#include "leddriver.h"

#define NUM_LIGHTS 50
#define MAX_BRIGHT 0xcc

struct lightState {
    unsigned char origBright;
    unsigned char brightVal;
    unsigned int colorVal;
    unsigned char readyState;
};

static volatile struct lightState states[NUM_LIGHTS + 1];
static volatile unsigned int timestep;
static volatile bool timingStarted = false;

void startTiming(void) {
    timingStarted = true;
}

void enumerateLights(void) {
    int i;
    for(i = 0; i < NUM_LIGHTS; i++) {
        states[i].origBright = MAX_BRIGHT;
        states[i].brightVal = MAX_BRIGHT;
        states[i].readyState = 1;
    }
}

void stepTime(void) {
    timestep++;
    if(timestep % 100 == 0) {
        int sec = timestep / 100;

        int i;
        for(i = 0; i < NUM_LIGHTS; i++) {
            int c = (i + sec) % 3;
            states[i].colorVal = 0xf << (4 * c);
            states[i].readyState = 1;
        }

        if(sec == 9)
            timestep = 0;
    }
}

// Every timestep (10ms)
void __attribute__((__interrupt__,__auto_psv__)) _T1Interrupt(void) {
    IFS0bits.T1IF = 0;
    // Handle time steps
    if(timingStarted) {
        stepTime();
    }

    static int statePos = 0;
    int pos = statePos;
    while(true) {
        volatile struct lightState *curr = states + pos;
        while(curr->readyState) {
            static unsigned long val;
            val = ((unsigned long) curr->colorVal) << 6;
            unsigned char bright = curr->origBright;
            if(curr->brightVal == curr->origBright) {
                bright = curr->brightVal;
            } else if(curr->brightVal > curr->origBright) {
                bright = curr->origBright + 1;
            } else {
                bright = curr->origBright - 1;
            }
            val |= ((unsigned long) bright) << 18;

            unsigned char addr = pos;
            if(pos == NUM_LIGHTS)
                addr = 63;
            val |= ((unsigned long) addr) << 26;

            if(!putOutputData(val)) {
                statePos = pos;
                return;
            }
            curr->origBright = bright;
            if(curr->brightVal == bright) {
                curr->readyState = 0;
            }
        }

        pos = pos + 1;
        if(pos >= NUM_LIGHTS + 1)
            pos = 0;
        if(pos == statePos) {
            statePos = 0;
            break;
        }
    }
}
