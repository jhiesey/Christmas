
#include <p24FJ64GB002.h>
#include <stdlib.h>
#include "timestep.h"
#include "leddriver.h"
#include "serhandler.h"

#define MAX_BRIGHT 0xcc
#define MAX_COLOR (0xc * 3);

struct lightState states[NUM_LIGHTS + 1]; // These two are global
bool masterValid = true;
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
    states[NUM_LIGHTS].origBright = MAX_BRIGHT;
    states[NUM_LIGHTS].brightVal = MAX_BRIGHT;
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

static void adjustByGradient(int light, int channel, int gradient, int factor) {
    int change = (gradient > 0) ? factor : -factor;
    int newVal;
    int colorVals[3];
    switch(channel) {
        case 0:
        case 1:
        case 2:
            colorVals[0] = states[light].colorVal & 0xf;
            colorVals[1] = (states[light].colorVal >> 4) & 0xf;
            colorVals[2] = (states[light].colorVal >> 8) & 0xf;
            colorVals[channel] += change;
            if(colorValid(colorVals)) {
                states[light].colorVal &= ~(0xf << (channel * 4));
                states[light].colorVal |= colorVals[channel] << (channel * 4);
            }
            break;
        case 3:
            newVal = states[light].brightVal + change;
            if(newVal < 0) {
                states[light].brightVal = 0;
            } else if(newVal > MAX_BRIGHT) {
                states[light].brightVal = MAX_BRIGHT;
            } else {
                states[light].brightVal = newVal;
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
    for(i = 0; i <= NUM_LIGHTS; i++) {
//        if(states[i].readyState) { // Only update non-changed lights
//            int j;
//            for(j = 0; j < 4; j++)
//                states[i].counts[j] = 0;
//        } else {
            int j;
            for(j = 0; j < 4; j++) {
                if(states[i].grads[j]) { // If non-zero gradient
                    int interval = abs(states[i].grads[j]);
                    if(++states[i].counts[j] >= interval) {
                        states[i].counts[j] = 0;

                        int factor = 1;
                        if(j == 3)
                            factor = states[i].grads[4];
                        adjustByGradient(i, j, states[i].grads[j], factor);
                        states[i].readyState = true;
                    }
                }
            }
//        }
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

    volatile struct lightState *br = states + NUM_LIGHTS;
    while(br->readyState) {
        unsigned char bright = br->origBright;
        if(br->brightVal == br->origBright || !masterValid) {
            bright = br->brightVal;
        } else if(br->brightVal > br->origBright) {
            bright = br->origBright + 1;
        } else {
            bright = br->origBright - 1;
        }
        unsigned long val = ((unsigned long) bright) << 18;
        val |= ((unsigned long) 63) << 26;

        if(!putOutputData(val))
            return;

        masterValid = true;
        int i;
        for(i = 0; i < NUM_LIGHTS; i++) {
            states[i].origBright = bright;
            states[i].brightVal = bright;
        }
        br->origBright = bright;
        if(br->brightVal == bright) {
            br->readyState = 0;
        }
    }

    static int statePos = 0;
    int pos = statePos;
    while(true) {
        volatile struct lightState *curr = states + pos;
        while(curr->readyState) {
            unsigned long val = ((unsigned long) curr->colorVal) << 6;
            unsigned char bright = curr->origBright;
            if(curr->brightVal == curr->origBright) {
                bright = curr->brightVal;
            } else if(curr->brightVal > curr->origBright) {
                bright = curr->origBright + 1;
            } else {
                bright = curr->origBright - 1;
            }
            val |= ((unsigned long) bright) << 18;
            val |= ((unsigned long) pos) << 26;

            if(!putOutputData(val)) {
                statePos = pos;
                return;
            }
            
            if(bright != states[NUM_LIGHTS].origBright)
                masterValid = false;
            curr->origBright = bright;
            if(curr->brightVal == bright) {
                curr->readyState = 0;
            }
        }

        pos = pos + 1;
        if(pos >= NUM_LIGHTS)
            pos = 0;
        if(pos == statePos) {
            statePos = 0;
            break;
        }
    }
}
