/* 
 * File:   serhandler.h
 * Author: jhiesey
 *
 * Created on January 7, 2013, 1:07 AM
 */

#ifndef SERHANDLER_H
#define	SERHANDLER_H

// Input
#define SBYTE_CLEAR 0x0 // Clear buffer
#define SBYTE_RESETTIME 0x1 // Reset time
#define SMASK_SINGLE 0xfc
#define SBYTE_SINGLE 0x80 // Single, immediate update

// Output
#define SBYTE_ERROR 0xff
#define SBYTE_FULL 0x80
#define SBYTE_AVAIL 0x81
#define SBYTE_SUCCESS 0x0

#endif	/* SERHANDLER_H */

