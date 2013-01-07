/* 
 * File:   main.c
 * Author: jhiesey
 *
 * Created on December 15, 2012, 7:16 AM
 */

#include <stdio.h>
#include <stdlib.h>

#include <p24FJ64GB002.h>
#include <stdbool.h>
#define FCY 16000000
#define TICKS_PER_MSEC 250
#include <libpic30.h>
#include <time.h>
#include "timestep.h"
#include "buffer.h"
#include "serhandler.h"

#include "dp_usb/usb_stack_globals.h"
#include "descriptors.h"

_CONFIG1(FWDTEN_OFF & ICS_PGx1 & GWRP_OFF & GCP_OFF & JTAGEN_OFF);
_CONFIG2(POSCMOD_NONE & IOL1WAY_OFF & OSCIOFNC_ON & FCKSM_CSDCMD & FNOSC_FRCPLL & PLL96MHZ_ON & PLLDIV_NODIV & IESO_OFF);
_CONFIG3 (SOSCSEL_IO);

extern BYTE usb_device_state;

static int getByte(int delayMs) {
    int delayCycles = delayMs * TICKS_PER_MSEC;
    unsigned int beginTime = TMR4;

    do {
        BYTE b;
        if (poll_getc_cdc(&b))
            return b;
        checkTimeResponse(); // Checks for a response
    } while (TMR4 < beginTime + delayCycles);
    return -1;
}

static void setup(void) {
    AD1PCFG = 0xffff;
    TRISA = 0;

    LATBbits.LATB5 = 1;
    TRISB = 0;

    T2CON = 0; // Fast (bit-bang) interrupt
    TMR2 = 0;
    PR2 = 160;
    IPC1bits.T2IP = 5;
    IFS0bits.T2IF = 0;
    T2CONbits.TON = 1;

    T1CON = 0; // Slow (timestep) interrupt
    T1CONbits.TCKPS = 1;
    TMR1 = 0;
    PR1 = 20000;
    IPC0bits.T1IP = 1;
    IFS0bits.T1IF = 0;
    IEC0bits.T1IE = 1;
    T1CONbits.TON = 1;

    T4CON = 0; // Bit timer
    T4CONbits.TCKPS = 2;
    TMR4 = 0;
    PR4 = 0xFFFF;
    T4CONbits.TON = 1;

    initCDC(); // setup the CDC state machine
    usb_init(cdc_device_descriptor, cdc_config_descriptor, cdc_str_descs, USB_NUM_STRINGS); // initialize USB. TODO: Remove magic with macro
    usb_start(); //start the USB peripheral

//    IPC21bits.USB1IP = 4; // Should be default anyway
    EnableUsbPerifInterrupts(USB_TRN + USB_SOF + USB_UERR + USB_URST);
    EnableUsbGlobalInterrupt();

    while (usb_device_state < CONFIGURED_STATE);
    usb_register_sof_handler(CDCFlushOnTimeout);

    __delay_ms(100);

    startTiming();
    enumerateLights();
    bufferInit();
}

static bool handleBytes(int numBytes) {
    int b;
    while(numBytes > 0) {
        if((b = getByte(1000)) < 0 || !bufferInsert(b)) {
            return false;
        }
        numBytes--;
    }
    return true;
}

static bool handleSingleMessage(int b) {
    int numBytes = ((b & SMASK_HASDERIV) == SBYTE_HASDERIV) ? 6 : 3;
    if(!bufferInsert(b)) {
        return false;
    }

    return handleBytes(numBytes);
}

static bool handleAtTime() {
    if(!handleBytes(2)) // The time itself
        return false;

    while(true) {
        int b = getByte(1000);
        if(b < 0 || !bufferInsert(b))
            return false;

        if((b & SMASK_SINGLE) == SBYTE_SINGLE) { // Single light
            int b2; // Single address
            if((b2 = getByte(1000)) < 0 || !bufferInsert(b2)) {
                return false;
            }
            if(!handleSingleMessage(b))
                return false;
        } else if((b & SMASK_LIST) == SBYTE_LIST) { // List of lights
            int b2;
            if((b2 = getByte(1000)) < 0 || !bufferInsert(b2)) {
                return false;
            }
            int numAddrs = b2 & SMASK_NUMADDRS; // Limited to 15 by mask
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
            success = bufferInsert(0) && bufferInsert(0); // Time of 0
            if(success)
                success = handleSingleMessage(b);
            if(success)
                success = bufferInsert(SBYTE_END);

            if(success)
                bufferEnd();
        } else if((b & SMASK_ATTIME) == SBYTE_ATTIME) { // Timed message
            bufferBegin();
            success = handleAtTime();
            if(success)
                bufferEnd();
        } else {
            success = false;
        }

        if(success) {
            putc_cdc(SBYTE_SUCCESS);
        } else {
            bufferClearCurrent();
            putc_cdc(SBYTE_ERROR);
        }
    }
    
    return 0;
}

// USB suspend not yet enabled
void USBSuspend(void) {}

void __attribute__((interrupt, auto_psv)) _USB1Interrupt(void) {
    //USB interrupt
    //IRQ enable IEC5bits.USB1IE
    //IRQ flag	IFS5bits.USB1IF
    //IRQ priority IPC21<10:8>
    usb_handler();
    ClearGlobalUsbInterruptFlag();
}