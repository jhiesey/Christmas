#include <stdbool.h>
#include <p24FJ64GB002.h>
#include <stdbool.h>
#include <assert.h>

#include "serhandler.h"
#include "timestep.h"
#include "buffer.h"

#include "dp_usb/usb_stack_globals.h"

static unsigned int nextTime = 0;

static void setLightFromBuffer(bool hasDeriv, bool forceBright, int addr, unsigned char *buf) {
    if(addr >= NUM_LIGHTS && addr != 63)
        return;
    if(addr == 63)
        addr = NUM_LIGHTS;

    int brightVal = buf[0];
    int colorVal[3];
    colorVal[0] = buf[2] & 0xf;
    colorVal[1] = (buf[2] >> 4) & 0xf;
    colorVal[2] = buf[1];
    if(!brightValid(brightVal) || !colorValid(colorVal))
        return;

    states[addr].brightVal = brightVal;
    if(forceBright)
        states[addr].origBright = states[addr].brightVal;
    states[addr].colorVal = (colorVal[0]) | (colorVal[1] << 4) | (colorVal[2] << 8);

    if(hasDeriv) {
        states[addr].grads[0] = buf[7]; // r
        states[addr].grads[1] = buf[6]; // g
        states[addr].grads[2] = buf[5]; // b
        states[addr].grads[3] = buf[4]; // bright delay
        states[addr].grads[4] = buf[3]; // bright rate

        if(buf[4] != 0) {
            if(addr == NUM_LIGHTS) { // Only one type of brightness gradient is valid at a time
                int i;
                for(i = 0; i < NUM_LIGHTS; i++) {
                    states[i].grads[3] = 0;
                }
            } else {
                states[NUM_LIGHTS].grads[3] = 0;
            }
        }
    } else {
        memset(states[addr].grads, 0, sizeof(states[addr].grads));
    }
    int i;
    for(i = 0; i < 4; i++) {
        states[addr].counts[i] = 0;
    }
    states[addr].readyState = true;
}

static void readData(bool hasDeriv, unsigned char *buf) {
    int remainingBytes = hasDeriv ? 8 : 3;
    int i;
    for(i = 0; i < remainingBytes; i++) {
        buf[i] = bufferExtract();
    }
}

static void setSingleLight(int b, int addr) {
    bool hasDeriv = (b & SMASK_HASDERIV) == SBYTE_HASDERIV;
    bool forceBright = (b & SMASK_FORCEBRIGHT) == SBYTE_FORCEBRIGHT;

    unsigned char buf[7];
    readData(hasDeriv, buf);
    setLightFromBuffer(hasDeriv, forceBright, addr, buf);
}

static void setLightList(int b, int numLights, unsigned char *addrList) {
    bool hasDeriv = (b & SMASK_HASDERIV) == SBYTE_HASDERIV;
    bool forceBright = (b & SMASK_FORCEBRIGHT) == SBYTE_FORCEBRIGHT;

    unsigned char buf[6];
    readData(hasDeriv, buf);
    int i;
    for(i = 0; i < numLights; i++) {
        setLightFromBuffer(hasDeriv, forceBright, addrList[i], buf);
    }
}

static void setLightMask(int b, unsigned char *masks) {
    bool hasDeriv = (b & SMASK_HASDERIV) == SBYTE_HASDERIV;
    bool forceBright = (b & SMASK_FORCEBRIGHT) == SBYTE_FORCEBRIGHT;

    unsigned char buf[6];
    readData(hasDeriv, buf);
    int byteNum;
    int bitNum;
    for(byteNum = 0;; byteNum++) {
        for(bitNum = 0; bitNum < 8; bitNum++) {
            int addr = byteNum * 8 + bitNum;
            if(addr >= NUM_LIGHTS)
                return;
            if((masks[byteNum] >> bitNum) & 1) {
                setLightFromBuffer(hasDeriv, forceBright, addr, buf);
            }
        }
    }
}

int dbg;

static void timeReady() {
    while(true) {
        int b = bufferExtract();
        if(b < 0) // In case the buffer was cleared
            return;
        dbg = b;
        if((b & SMASK_SINGLE) == SBYTE_SINGLE) { // Single light
            int addr = bufferExtract();
            setSingleLight(b, addr);
        } else if((b & SMASK_LIST) == SBYTE_LIST) { // List of lights
            int numAddrs = bufferExtract() & 0xf;
            unsigned char addrList[15];
            int i;
            for(i = 0; i < numAddrs; i++)
                addrList[i] = bufferExtract();
            setLightList(b, numAddrs, addrList);
        } else if((b & SMASK_MASK) == SBYTE_MASK) { // Mask of lights
            unsigned char masks[7];
            int i;
            for(i = 0; i < 7; i++)
                masks[i] = bufferExtract();
            setLightMask(b, masks);
        } else if((b & SMASK_SETTIME) == SBYTE_SETTIME) { // Set time
            int timeHigh = bufferExtract();
            int timeLow = bufferExtract();
            timestep = (((unsigned int) timeHigh) << 8) | ((unsigned int) timeLow);
        } else if((b & SMASK_END) == SBYTE_END) { // End of message
            if((b & SMASK_ENDRESET) == SBYTE_ENDRESET) {
                timestep = 0;
            }
            return;
        } else {
            while(1);
//            assert(0);
        }
    }
}

void handleSerialUpdates() {
    while(true) {
        if(nextTime == 0) {
            int timeHigh = bufferExtract();
            if(timeHigh < 0)
                return;
            int timeLow = bufferExtract();
            nextTime = (((unsigned int) timeHigh) << 8) | ((unsigned int) timeLow);
        }
        if(nextTime > timestep)
            return;

        timeReady();
        nextTime = 0;
    }
}
