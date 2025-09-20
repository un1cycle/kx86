
org 0x7E00

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov ax, 0x4F02
    mov bx, 0x11F | 0x4000
    int 0x10

    mov ax, 0x4F01
    mov cx, 0x11F
    mov di, mode_info
    int 0x10
    
    

    mov eax, [mode_info + 0x28]
    mov [lfb_addr], eax

    movzx eax, word [mode_info + 0x10]
    mov [lfb_pitch], eax 

    lgdt [gdt_desc]

    mov eax, cr0
    or  eax, 1
    mov cr0, eax

    jmp CODE_SEL:pm_start

bits 32
pm_start:
    mov ax, DATA_SEL
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000

    mov esi, [lfb_addr]





; KX86 STARTS HERE








idxVar:
dd 1

strVar:
db "hello", 0x0D, 0x0A, "", 0

rdtsc
xor eax, edx


mov eax, eax 
mov ecx, 0
sub ecx, 70

xor edx, edx
div ecx 
mov eax, edx 
add eax, 70
mov dword [idxVar], eax
    

    mov esi, [lfb_addr]  
    mov edx, [lfb_pitch]  

    mov eax, 50
    imul eax, edx         
    add esi, eax
    mov edi, esi

    mov eax, 55
    sub eax, 50          
    mov ebx, eax

row_loop6221:
    push ebx                  
    mov edi, esi
    mov eax, 50
    imul eax, 3              
    add edi, eax         

    mov eax, 55
    sub eax, 50        
    mov ecx, eax

pixel_loop6221:
    mov byte [edi], 0x00 
    mov byte [edi+1], 0x00 
    mov byte [edi+2], 0xFF 
    add edi, 3
    loop pixel_loop6221

    pop ebx
    add esi, edx        
    dec ebx
    jnz row_loop6221



while1922:

mov eax, [idxVar]
cmp eax, 1
je true1922
jne false1922

true1922:




jmp while1922

false1922:


hlt






; KX86 ENDS HERE







align 4
lfb_addr: dd 0
lfb_pitch: dd 0
zero: dd 0
NULL: dd 0
KEYS dd 128 dup(0)

mode_info: times 256 db 0

align 8
gdt:
    dq 0x0000000000000000
    dq 0x00CF9A000000FFFF
    dq 0x00CF92000000FFFF

gdt_desc:
    dw gdt_end - gdt - 1
    dd gdt
gdt_end:

CODE_SEL equ 0x08
DATA_SEL equ 0x10