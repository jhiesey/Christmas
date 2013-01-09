/* 
 * File:   serhandler.h
 * Author: jhiesey
 *
 * Created on January 7, 2013, 1:07 AM
 */

#ifndef SERHANDLER_H
#define	SERHANDLER_H

#define SMASK_CLEAR 0xf0
#define SBYTE_CLEAR 0x0 // Clear buffer
#define SMASK_ATTIME 0xe0
#define SBYTE_ATTIME 0x20 // Begin time message
#define SMASK_SINGLE 0xf0
#define SBYTE_SINGLE 0x10 // Single, immediate update

#define SMASK_HASDERIV 0x8
#define SBYTE_HASDERIV 0x8
#define SMASK_FORCEBRIGHT 0x4
#define SBYTE_FORCEBRIGHT 0x4
#define SMASK_NUMADDRS 0xf

#define SMASK_LIST 0xf0
#define SBYTE_LIST 0x20
#define SMASK_MASK 0xf0
#define SBYTE_MASK 0x30
#define SMASK_SETTIME 0xf0
#define SBYTE_SETTIME 0x90
#define SMASK_END 0xf0
#define SBYTE_END 0x00
#define SMASK_ENDRESET 0x80
#define SBYTE_ENDRESET 0x80

#define SBYTE_ERROR 0xff
#define SBYTE_FULL 0x80
#define SBYTE_AVAIL 0x81
#define SBYTE_SUCCESS 0x0

void handleSerialUpdates();

#endif	/* SERHANDLER_H */

