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
#include <libpic30.h>
#include "timestep.h"

#include "dp_usb/usb_stack_globals.h"
#include "descriptors.h"

_CONFIG1(FWDTEN_OFF & ICS_PGx1 & GWRP_OFF & GCP_OFF & JTAGEN_OFF);
_CONFIG2(POSCMOD_NONE & IOL1WAY_OFF & OSCIOFNC_ON & FCKSM_CSDCMD & FNOSC_FRCPLL & PLL96MHZ_ON & PLLDIV_NODIV & IESO_OFF);
_CONFIG3 (SOSCSEL_IO);

enum SerState {
    SSTATE_READY,
    SSTATE_READING
};

#define SBYTE_CLEAR 0x0 // Clear buffer
#define SBYTE_ATTIME 0x0 // Begin time message
#define SBYTE_SINGLE 0x0 // Single, immediate update

#define SBYTE_ERROR 0x0

extern BYTE usb_device_state;

/*
 * 
 */
int main() {
    AD1PCFG = 0xffff;
    TRISA = 0;

    LATBbits.LATB5 = 1;
    TRISB = 0;

    T2CON = 0;
    TMR2 = 0;
    PR2 = 160;
    IPC1bits.T2IP = 5;

    IFS0bits.T2IF = 0;
    T2CONbits.TON = 1;

    T1CON = 0;
    T1CONbits.TCKPS = 1;
    TMR1 = 0;
    PR1 = 20000;
    IPC0bits.T1IP = 1;

    IFS0bits.T1IF = 0;
    IEC0bits.T1IE = 1;
    T1CONbits.TON = 1;

    initCDC(); // setup the CDC state machine
    usb_init(cdc_device_descriptor, cdc_config_descriptor, cdc_str_descs, USB_NUM_STRINGS); // initialize USB. TODO: Remove magic with macro
    usb_start(); //start the USB peripheral

    EnableUsbPerifInterrupts(USB_TRN + USB_SOF + USB_UERR + USB_URST);
    EnableUsbGlobalInterrupt();

    while (usb_device_state < CONFIGURED_STATE);
    usb_register_sof_handler(CDCFlushOnTimeout);

    __delay_ms(100);

    startTiming();
    enumerateLights();

    enum SerState state = SSTATE_READY;
    int bytesTillNext = 0;
    while(1) {
//        BYTE b;
//        if (poll_getc_cdc(&b)) {
//            switch(state) {
//                case SSTATE_READY:
//                    if(b == SBYTE_CLEAR) {
//                        // Empty buffer
//                    } else if(b == SBYTE_ATTIME) {
//                        // Begin storing message
//                    } else if(b == SBYTE_SINGLE) {
//                        // Begin storing message
//                    } else {
//                        putc_cdc(SBYTE_ERROR);
//                    }
//                    break;
//                case SSTATE_READING:
//
//
//            }
//        }
    }
    
    return 0;
}

// USB suspend not yet enabled
void USBSuspend(void) {}

void __attribute__((interrupt, auto_psv)) _USB1Interrupt() {
    //USB interrupt
    //IRQ enable IEC5bits.USB1IE
    //IRQ flag	IFS5bits.USB1IF
    //IRQ priority IPC21<10:8>
    usb_handler();
    ClearGlobalUsbInterruptFlag();
}