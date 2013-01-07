
#include <p24FJ64GB002.h>
#include <stdlib.h>
#include "timestep.h"
#include "leddriver.h"
#include "serhandler.h"

#define MAX_BRIGHT 0xcc
#define MAX_COLOR (0xc * 3);

/*
struct lightState {
    unsigned char origBright;
    unsigned char brightVal;
    unsigned int colorVal;
    unsigned char readyState;

    unsigned int grads[4];
    unsigned int counts[4];
};
*/

struct lightState states[NUM_LIGHTS + 1]; // These two are global
unsigned int timestep;


static bool timingStarted = false;

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

bool brightValid(int newBright) {
    return newBright >= 0 && newBright <= MAX_BRIGHT;
}

bool colorValid(int *colorVals) {
    int total = 0;
    int i;
    for(i = 0; i < 3; i++) {
        if(colorVals[i] < 0 || colorVals[i] > 0xf)
            return false;
        total += colorVals[i];
    }
    return total <= MAX_COLOR;
}

static void adjustByGradient(int light, int channel, int gradient) {
    int change = (gradient > 0) ? 1 : -1;
    if(channel == 0)
        change *= gradient & 0xf;
    int newVal;
    int colorVals[3];
    switch(channel) {
        case 0:
            newVal = states[light].brightVal + change;
            if(newVal >= 0 && newVal <= MAX_BRIGHT)
                states[light].brightVal = newVal;
            break;
        case 1:
        case 2:
        case 3:
            colorVals[0] = states[light].colorVal & 0xf;
            colorVals[1] = (states[light].colorVal >> 4) & 0xf;
            colorVals[2] = (states[light].colorVal >> 8) & 0xf;
            colorVals[channel - 1] += change;
            if(colorValid(colorVals)) {
                states[light].colorVal &= ~(0xf << ((channel - 1) * 4));
                states[light].colorVal |= colorVals[channel - 1] << ((channel - 1) * 4);
            }
            break;
        default:
            break;
    }
}

static void stepTime(void) {
//    if(timestep % 100 == 0) {
//        int sec = timestep / 100;
//
//        int i;
//        for(i = 0; i < NUM_LIGHTS; i++) {
//            int c = (i + sec) % 3;
//            states[i].colorVal = 0xf << (4 * c);
//            states[i].readyState = 1;
//        }
//
//        if(sec == 9)
//            timestep = 0;
//    }

    handleSerialUpdates(timestep);

    int i;
    for(i = 0; i < NUM_LIGHTS; i++) {
        if(states[i].readyState) { // Only update non-changed lights
            int j;
            for(j = 0; j < 4; j++)
                states[i].counts[j] = 0;
        } else {
            int j;
            for(j = 0; j < 4; j++) {
                if(states[i].grads[j]) { // If non-zero gradient
                    unsigned int interval = abs(states[i].grads[j]);
                    if(j == 0)
                        interval >>= 4;
                    if(++states[i].counts[j] >= interval) {
                        states[i].counts[j] = 0;

                        adjustByGradient(i, j, states[i].grads[j]);
                    }
                }
            }
        }
    }

    if(timestep != 0xffff)
        timestep++;
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
