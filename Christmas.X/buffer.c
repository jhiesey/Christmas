#include "buffer.h"

static volatile unsigned char buf[BUFFER_SIZE];
static volatile int readIndex = 0;
static volatile int readLimitIndex = 0; // One after last valid read position

static volatile int writeIndex = 0;
static volatile int writeBase = 0; // Beginning of current message
static volatile bool writeFull = false;

void bufferInit(void) {
    // Nothing needed
}

void bufferClearAll(void) {
    readIndex = 0;
    writeIndex = 0;
}

void bufferClearCurrent(void) {
    writeIndex = writeBase;
    writeFull = false;
}

void bufferBegin(void) {
    writeBase = writeIndex;
}

void bufferEnd(void) {
    if(writeFull)
        return;
    
    readLimitIndex = writeIndex;
}

int bufferSpaceFree() {
    int usedSpace = writeIndex - readIndex;
    if(usedSpace < 0)
        usedSpace += BUFFER_SIZE;
    return BUFFER_SIZE - usedSpace - 1;
}

bool bufferInsert(int byte) {
    if(writeFull)
        return false;

    int nextWrite = writeIndex + 1;
    if(nextWrite == BUFFER_SIZE) {
        nextWrite = 0;
    }
    
    if(nextWrite == readIndex) {
        writeFull = true;
        return false;
    }

    buf[writeIndex] = byte;
    writeIndex = nextWrite;
    return true;
}

bool bufferGotFull() {
    return writeFull;
}

int bufferExtract() {
    if(readIndex == readLimitIndex)
        return -1;

    int result = buf[readIndex];
    int nextRead = readIndex + 1;
    if(nextRead >= BUFFER_SIZE) {
        nextRead = 0;
    }
    readIndex = nextRead;
    
    return result;
}
