/* 
 * File:   buffer.h
 * Author: jhiesey
 *
 * Created on January 6, 2013, 11:10 PM
 */

#ifndef BUFFER_H
#define	BUFFER_H

#include <stdbool.h>

#define BUFFER_SIZE 3000

// Sender-side
void bufferInit(void);
void bufferClearAll(void);
void bufferClearCurrent(void);
void bufferBegin(void);
void bufferEnd(void);
int bufferSpaceFree();
bool bufferInsert(int byte);
bool bufferGotFull();

// Receiver-side
int bufferExtract();

#endif	/* BUFFER_H */

