#include "buffer.h"

#define BUFFER_SIZE 3000

static unsigned char buf[BUFFER_SIZE];
static int readIndex = 0;
static int readLimitIndex = 0; // One after last valid read position

static int writeIndex = 0;
static int writeBase = 0; // Beginning of current message

void bufferInit(void) {
    // Nothing needed
}

void bufferClearAll(void) {
    readIndex = 0;
    writeIndex = 0;
}

void bufferClearCurrent(void) {
    writeIndex = writeBase;
}

void bufferBegin(void) {
    writeBase = writeIndex;
}

void bufferEnd(void) {
    readLimitIndex = writeIndex;
}

bool bufferInsert(int byte) {
    int nextWrite = writeIndex + 1;
    if(nextWrite == BUFFER_SIZE)
        nextWrite = 0;
    
    if(nextWrite == readIndex)
        return false;

    buf[writeIndex] = byte;
    writeIndex = nextWrite;
    return true;
}

int bufferExtract() {
    if(readIndex == readLimitIndex)
        return -1;

    int result = buf[readIndex];
    if(++readIndex >= BUFFER_SIZE)
        readIndex = 0;
    
    return result;
}
