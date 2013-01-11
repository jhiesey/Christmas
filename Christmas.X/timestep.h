/* 
 * File:   timestep.h
 * Author: jhiesey
 *
 * Created on December 21, 2012, 9:27 PM
 */

#ifndef TIMESTEP_H
#define	TIMESTEP_H

#include <stdbool.h>

#define NUM_LIGHTS 50

//struct lightState {
//    unsigned char origBright;
//    unsigned char brightVal;
//    unsigned int colorVal;
//    unsigned char readyState;
//
//    signed char grads[5];
//    unsigned char counts[4];
//};
//
//extern struct lightState states[NUM_LIGHTS + 1];
extern unsigned int timestep;

void startTiming(void);
//void enumerateLights(void);
//
//bool brightValid(int newBright);
//
//bool colorValid(int *colorVals);

#endif	/* TIMESTEP_H */

