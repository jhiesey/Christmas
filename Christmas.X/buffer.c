#include "buffer.h"

#define BUFFER_SIZE 3000

static unsigned char buf[BUFFER_SIZE];
static int readIndex = 0;
static int readLimitIndex = 0; // One after last valid read position

static int writeIndex = 0;
static int writeBase = 0; // Beginning of current message
static bool writeFull = false;

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

bool bufferInsert(int byte) {
    if(writeFull)
        return false;

    int nextWrite = writeIndex + 1;
    if(nextWrite == BUFFER_SIZE)
        nextWrite = 0;
    
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
    if(++readIndex >= BUFFER_SIZE)
        readIndex = 0;
    
    return result;
}
