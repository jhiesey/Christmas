#include <stdbool.h>
#include <p24FJ64GB002.h>

//#define T1INTOFF 3
//
//#define BYTEBUFFER_SIZE 2000
//
//#define ESC_BYTE 0xee
//
//volatile unsigned char byteBuffer[BYTEBUFFER_SIZE];
//volatile unsigned int byteReadPtr;
//volatile unsigned int byteWritePtr;
//
//static bool startNext = true;
//
//bool handleByte(unsigned char b) {
//    if(b == ESC_BYTE) {
//        startNext = true;
//        return true;
//    }
//
//    if(startNext) {
//        if(!(b & 0x80)) {
//            // Clear buffer
//            SRbits.IPL = T1INTOFF;
//            byteWritePtr = byteReadPtr;
//            SRbits.IPL = 0;
//        }
//    }
//    startNext = false;
//
//    int filled = byteWritePtr - byteReadPtr;
//    if(filled < 0)
//        filled += BYTEBUFFER_SIZE;
//
//    if(filled == BYTEBUFFER_SIZE - 1)
//        return false;
//
//    byteBuffer[byteWritePtr] = b;
//    byteWritePtr++;
//    return false;
//}
//
//
//void readBuffer() {
//
//}