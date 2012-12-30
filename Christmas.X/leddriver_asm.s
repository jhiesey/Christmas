    .include "p24fJ64GB002.inc"

    .equiv ARRAY_SIZE, 20
    .equiv OUT_LATCH, LATB
    .equiv OUT_PIN, 5
    .equiv WAIT_BITS, 4

    .global __T2Interrupt
    .extern _lightOutBuf
    .extern _outReadPtr
    .extern _outWritePtr

    .data
nextOut:    .word 1
outState:   .word 0
bitNum:     .word 0
delayCount: .word 0

    .text
; Every bit time (10us)
__T2Interrupt:
    push.s
    cp0 nextOut
    mov OUT_LATCH, W0
    mov #OUT_PIN, W1
    bsw.z W0, W1
    mov W0, OUT_LATCH

    bclr IFS0, #T2IF

    mov outState, W0
    bra W0
    bra StateStart
    bra StateBit1
    bra StateBit2
    bra StateBit3
    bra StateWait

StateStart:
    clr bitNum
    mov #WAIT_BITS, W0
    mov W0, delayCount

    mov _outReadPtr, W0
    cp _outWritePtr
    bra z, NotReady

    clr nextOut
    inc outState
    bra StateDone

NotReady:
    bclr IEC0, #T2IE
    clr outState
    bra StateDone

StateBit1:
    mov #1, W0
    mov W0, nextOut
    inc outState
    bra StateDone

StateBit2:
    mov _outReadPtr, W0
    sl W0, #2, W0
    btss bitNum, #4
    add #2, W0
    mov #_lightOutBuf, W1
    add W1, W0, W0
    mov [W0], W1

    mov #0xf, W0
    and bitNum, WREG
    sl W1, W0, W0
    asr W0, #0xf, W0
    mov W0, nextOut

    inc outState
    bra StateDone

StateBit3:
    clr nextOut
    inc outState

    inc bitNum
    mov bitNum, W0
    mov #26, W1
    mov #1, W2
    cpseq W0, W1
    mov W2, outState

    bra StateDone

StateWait:
    mov #1, W0
    mov W0, nextOut
    dec delayCount
    bra nz, StateDone

    inc _outReadPtr, WREG
    mov #ARRAY_SIZE, W1
    cpslt W0, W1
    mov #0, W0
    mov W0, _outReadPtr

    clr outState

StateDone:
    pop.s
    retfie

    .end
