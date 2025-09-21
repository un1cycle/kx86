import os
import subprocess
import sys
import random
import time
import platform

bootloader = """
org 0x7C00
bits 16

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00





    mov [dap_num_sectors], word 127 
    mov [dap_offset], word 0x7E00 
    mov [dap_segment], word 0x0000
    mov dword [dap_lba], 1          
    mov dword [dap_lba+4], 0     

    mov si, dap
    mov ah, 0x42
    mov dl, 0x80   
    int 0x13
    jc disk_error
idx_53479354:
    dw 4
loop_2054387:
    add dword [dap_lba], 127
    mov cx, 127
    advance_offset1:
        add word [dap_offset], 512
        loop advance_offset1
    mov word [dap_num_sectors], 127
    int 0x13
    jc disk_error
    sub word [idx_53479354], 1
    cmp word [idx_53479354], 0
    jne loop_2054387




    jmp 0x0000:0x7E00 


disk_error:
    hlt

dap:
dap_size:       db 0x10
dap_reserved:   db 0
dap_num_sectors: dw 0
dap_offset:     dw 0
dap_segment:    dw 0
dap_lba:        dq 0

times 510-($-$$) db 0
dw 0xAA55

"""

kernel = """
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

section .data





"""

def create_image(name="._kx86.img", show="bin"):
    global kernel
    kernel += """





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
DATA_SEL equ 0x10"""
    id_num = random.randint(1000,10000)
    attempts = 0
    while os.path.exists(f".boot{id_num}.asm") or os.path.exists(f".boot{id_num}.bin") or os.path.exists(f".kernel{id_num}.asm") or os.path.exists(f".kernel{id_num}.bin"):
        if attempts > 1000:
            print(f"please don't have lots of files with similar names to '.boot{id_num}.asm'/'.boot{id_num}.bin'/'.kernel{id_num}.asm'/'.boot{id_num}.bin'")
            sys.exit()
        id_num = random.randint(1000,10000)
        attempts += 1

    with open(f".boot{id_num}.asm", "w") as f:
        f.write(bootloader)

    with open(f".kernel{id_num}.asm", "w") as f:
        f.write(kernel)
    if show == "asm":
        with open(name, "w") as f:
            f.write(kernel)

    def run_nasm(src, out):
        subprocess.run(["nasm", "-f", "bin", src, "-o", out], check=True)

    def make_image(name, boot_bin, kernel_bin):
        size = 512 * 2000 
        image = bytearray(size)

        with open(boot_bin, "rb") as f:
            boot = f.read()
        image[0:len(boot)] = boot

        with open(kernel_bin, "rb") as f:
            kernel = f.read()
        start = 512  
        image[start:start+len(kernel)] = kernel

        with open(name, "wb") as f:
            f.write(image)

    boot_asm = f".boot{id_num}.asm"
    kernel_asm = f".kernel{id_num}.asm"
    boot_bin = f".boot{id_num}.bin"
    kernel_bin = f".kernel{id_num}.bin"

    try:
        if show == "bin" or show == "jit":
            run_nasm(boot_asm, boot_bin)
            run_nasm(kernel_asm, kernel_bin)
            make_image(name, boot_bin, kernel_bin)
    except Exception as e:
        print(e)

    try:
        os.remove(f".boot{id_num}.asm")
    except:
        pass
    try:
        os.remove(f".boot{id_num}.bin")
    except:
        pass
    try:
        os.remove(f".kernel{id_num}.asm")
    except:
        pass
    try:
        os.remove(f".kernel{id_num}.bin")
    except:
        pass
    if show == "jit":
        try:
            match platform.system():
                case "Windows":
                    os.system(f"qemu-system-i386 -drive format=raw,file={name} -vga std -cpu max -m 1G")
                case "Darwin":
                    os.system(f"qemu-system-i386 -drive format=raw,file={name} -vga std -accel hvf -cpu max -m 1G")
                case "Linux":
                    os.system(f"qemu-system-i386 -drive format=raw,file={name} -vga std -accel kvm -cpu max -m 1G")
        finally:
            os.remove("._kx86.img")