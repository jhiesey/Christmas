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

static unsigned long long getFullTime(void) {
    unsigned long lsb = TMR4;
    unsigned long msb = TMR5HLD;
    return ((unsigned long long) msb) << 16 | lsb;
}

static int getByte(void) {
    unsigned long long delayCycles = 2000ULL * TICKS_PER_MSEC;
    unsigned long long beginTime = getFullTime();

    do {
        BYTE b;
        if (poll_getc_cdc(&b))
            return b;
    } while (getFullTime() < beginTime + delayCycles);
    return -1;
}

static void enumerateLights(void) {
    int i;
    bufferBegin();
    for(i = 0; i < NUM_LIGHTS; i++) {
        bufferInsert(0);
        bufferInsert(0);
        bufferInsert(0x80 | (i >> 4));
        bufferInsert((i << 4) | 0xf);
        bufferInsert(0xf0);
        bufferInsert(0);
    }
    bufferEnd();
    if(bufferGotFull()) {
        while(true);
    }
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
    T4CONbits.T32 = 1;
    TMR4 = 0;
    PR4 = 0xFFFF;
    PR5 = 0xFFFF;
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

    bufferInit();
    enumerateLights();
    startTiming();
}

static int handleBytes(int numBytes) {
    int b;
    while(numBytes > 0) {
        if((b = getByte()) < 0)
            return -1;
        bufferInsert(b);
        numBytes--;
    }
    return 0;
}

static int handleTimeReset(int b) {
    int status = handleBytes(2);
    if(status)
        return status;
    bufferInsert(b);
    return 0;
}

static int handleTimeMessage(int b) {
    int status = handleBytes(2);
    if(status)
        return status;
    bufferInsert(b);
    return handleBytes(3);
}

int main(void) {
    setup();

    while(1) {
        int b;
        int status = 0;
        do { // Wait for the first byte
            b = getByte();
        } while(b < 0);

        if(b == SBYTE_CLEAR) { // Empty buffer
            bufferClearAll();
        } else if(b == SBYTE_RESETTIME) { // Reset time
            bufferBegin();
            status = handleTimeReset(b);
            if(status == 0) {
                bufferEnd();
            }
        } else if((b & SMASK_SINGLE) == SBYTE_SINGLE) { // Timed message
            bufferBegin();
            status = handleTimeMessage(b);
            if(status == 0) {
                bufferEnd();
            }
        } else {
            status = -1;
        }

        bool gotFull = bufferGotFull();
        if(status == 0 && !gotFull) {
            putc_cdc(SBYTE_SUCCESS);
        } else {
            bufferClearCurrent();
            if(gotFull) {
                putc_cdc(SBYTE_FULL);
                CDC_Flush_In_Now();
                while(true) {
                    int bufferAvail = bufferSpaceFree();
                    if(bufferAvail >= BUFFER_SIZE / 2) {
                        putc_cdc(SBYTE_AVAIL);
                        break;
                    }
                    unsigned char dummy;
                    if(peek_getc_cdc(&dummy)) {
                        break; // If we get a byte, quit waiting
                    }
                }
            } else {
                putc_cdc(SBYTE_ERROR);
            }
        }
        CDC_Flush_In_Now();
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