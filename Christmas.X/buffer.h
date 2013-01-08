/* 
 * File:   buffer.h
 * Author: jhiesey
 *
 * Created on January 6, 2013, 11:10 PM
 */

#ifndef BUFFER_H
#define	BUFFER_H

#include <stdbool.h>

// Sender-side
void bufferInit(void);
void bufferClearAll(void);
void bufferClearCurrent(void);
void bufferBegin(void);
void bufferEnd(void);
bool bufferInsert(int byte);
bool bufferGotFull();
int bufferExtract();

#endif	/* BUFFER_H */

