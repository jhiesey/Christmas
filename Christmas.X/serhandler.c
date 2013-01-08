#include <stdbool.h>
#include <p24FJ64GB002.h>
#include <stdbool.h>
#include <assert.h>

#include "serhandler.h"
#include "timestep.h"
#include "buffer.h"

#include "dp_usb/usb_stack_globals.h"

static unsigned int nextTime = 0;
static bool timeResponseReady = false;
static int timeResponse;

static void setLightFromBuffer(bool hasDeriv, bool forceBright, int addr, unsigned char *buf) {
    if(addr >= NUM_LIGHTS && addr != 64)
        return;
    if(addr == 64)
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
        states[addr].grads[0] = buf[3];
        states[addr].grads[1] = buf[4] & 0xf;
        states[addr].grads[2] = (buf[4] >> 4) & 0xf;
        states[addr].grads[3] = buf[5] & 0xf;
    }
    states[addr].readyState = true;
}

static void readData(bool hasDeriv, unsigned char *buf) {
    int remainingBytes = hasDeriv ? 6 : 3;
    int i;
    for(i = 0; i < remainingBytes; i++) {
        buf[i] = bufferExtract();
    }
}

static void setSingleLight(int b, int addr) {
    bool hasDeriv = (b & SMASK_HASDERIV) == SBYTE_HASDERIV;
    bool forceBright = (b & SMASK_FORCEBRIGHT) == SBYTE_FORCEBRIGHT;

    unsigned char buf[6];
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
            if(addr >= NUM_LIGHTS + 1)
                return;
            if((masks[byteNum] >> bitNum) & 1) {
                setLightFromBuffer(hasDeriv, forceBright, addr, buf);
            }
        }
    }
}

static void notifyComputer(void) {
    if(timeResponseReady)
        return;

    timeResponse = timestep;
    timeResponseReady = true;
}

int dbg;

static void timeReady() {
    while(true) {
        int b = bufferExtract();
        dbg = b;
        if((b & SMASK_SINGLE) == SBYTE_SINGLE) { // Single light
            int addr = bufferExtract();
            setSingleLight(b, addr);
        } else if((b & SMASK_LIST) == SBYTE_LIST) { // List of lights
            int numAddrs = bufferExtract() & 0x15;
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
        } else if((b & SMASK_NOTIFY) == SBYTE_NOTIFY) { // Notification
            notifyComputer();
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

        nextTime = 0;
        timeReady();
    }
}

void checkTimeResponse () {
    if(!timeResponseReady)
        return;

    putc_cdc(SBYTE_TIMERESPONSE);

    putc_cdc(timeResponse >> 8);
    putc_cdc(timeResponse & 0xff);

    timeResponseReady = false;
}

/*

static bool handleSingleMessage(int b) {
    int numBytes = ((b & SMASK_HASDERIV) == SBYTE_HASDERIV) ? 7 : 4;
    if(!bufferInsert(b)) {
        return false;
    }

    return handleBytes(numBytes);
}

static bool handleAtTime() {
    int b = getByte(1000);
    if(b < 0 || !bufferInsert(b))
        return false;

    if(!handleBytes(2)) // The time itself
        return false;

    while(true) {
        if((b & SMASK_SINGLE) == SBYTE_SINGLE) { // Single light
            if(!handleSingleMessage(b))
                return false;
        } else if((b & SMASK_LIST) == SBYTE_LIST) { // List of lights
            int numAddrs = b & SMASK_NUMADDRS;
            if(!handleBytes(numAddrs))
                return false;
            if(!handleSingleMessage(b))
                return false;
        } else if((b & SMASK_MASK) == SBYTE_MASK) { // Mask of lights
            if(!handleBytes(7))
                return false;
            if(!handleSingleMessage(b))
                return false;
        } else if((b & SMASK_NOTIFY) == SBYTE_NOTIFY) { // Notification
            // Nothing to do
        } else if((b & SMASK_SETTIME) == SBYTE_SETTIME) { // Set time
            if(!handleBytes(2))
                return false;
        } else if((b & SMASK_END) == SBYTE_END) { // End of message
            return true;
        } else {
            return false;
        }
    }
}


int main(void) {
    setup();

    while(1) {
        int b;
        bool success = true;
        do { // Wait for the first byte
            b = getByte(10000);
        } while(b < 0);

        if(b == SBYTE_CLEAR) { // Empty buffer
            bufferClearAll();
        } else if((b & SMASK_SINGLE) == SBYTE_SINGLE) { // Single message
            bufferBegin();
            success = bufferInsert(SBYTE_ATTIME) && bufferInsert(0) && bufferInsert(0);
            if(success)
                success = handleSingleMessage(b);
            if(success)
                success = bufferInsert(SBYTE_END);

            if(success)
                bufferEnd();
        } else if((b & SMASK_ATTIME) == SBYTE_ATTIME) { // Timed message
            bufferBegin();
            if(!bufferInsert(b)) {
                success = false;
            }
            if(success)
                success = handleAtTime();
            if(success)
                bufferEnd();
        } else {
            putc_cdc(SBYTE_ERROR);
        }

        if(!success) {
            bufferClearCurrent();
            putc_cdc(SBYTE_ERROR);
        }
    }

    return 0;
}
*/