#include <stdbool.h>
#include <p24FJ64GB002.h>
#include <stdbool.h>
#include <assert.h>

#include "serhandler.h"
#include "timestep.h"
#include "buffer.h"


/*
#define SBYTE_CLEAR 0x0 // Clear buffer
#define SBYTE_ATTIME 0x0 // Begin time message
#define SMASK_ATTIME 0x0
#define SBYTE_SINGLE 0x0 // Single, immediate update
#define SMASK_SINGLE 0x0

#define SMASK_HASDERIV 0x0
#define SBYTE_HASDERIV 0x0
#define SMASK_NUMADDRS 0x0

#define SMASK_LIST 0x0
#define SBYTE_LIST 0x0
#define SMASK_MASK 0x0
#define SBYTE_MASK 0x0
#define SMASK_NOTIFY 0x0
#define SBYTE_NOTIFY 0x0
#define SMASK_SETTIME 0x0
#define SBYTE_SETTIME 0x0
#define SMASK_END 0x0
#define SBYTE_END 0x0

#define SBYTE_ERROR 0x0
 */

static unsigned int nextTime = 0;

static void setLightFromBuffer(bool hasDeriv, bool forceBright, int addr, unsigned char *buf) {
    if(addr >= NUM_LIGHTS && addr != 64)
        return;
    if(addr == 64)
        addr = NUM_LIGHTS;

    states[addr].brightVal = buf[0];
    if(forceBright)
        states[addr].origBright = states[addr].brightVal;
    states[addr].colorVal = (((unsigned int) buf[1]) << 8) | ((unsigned int) buf[2]);

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
    
}


static void timeReady() {
    int b = bufferExtract();

    while(true) {
        if((b & SMASK_SINGLE) == SBYTE_SINGLE) { // Single light
            int addr = bufferExtract();
            setSingleLight(b, addr);
        } else if((b & SMASK_LIST) == SBYTE_LIST) { // List of lights
            int numAddrs = bufferExtract();
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