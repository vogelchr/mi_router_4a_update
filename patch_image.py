#!/usr/bin/python
import re
import subprocess
import os

img = bytearray(open('mi_router_4a.img', 'rb').read())

# I'm parsing a bootlog for NOR flash partitions!
bootlog_re = re.compile('(0x[0-9a-f]{12})-(0x[0-9a-f]{12}) : "(.*)"')
bootlog = open('bootlog.txt', 'rt', encoding='ascii', errors='replace').read()

for match in bootlog_re.findall(bootlog):
    # parsing the regexp
    startix = int(match[0], 0)
    endix = int(match[1], 0)
    partname = match[2]
    partlen = endix - startix

    part_fn = partname+'.part'
    part_new_fn = partname+'_new.part'

#   dump partition
#    open(part_fn, 'wb').write(img[startix:endix])

    print(
        f'Partition name {partname} from 0x{startix:x}..0x{endix-1:x}, len is {partlen}')

    if partname == 'OS1':
        kern_fn = 'openwrt-ramips-mt7621-xiaomi_mir3g-v2-initramfs-kernel.bin'
        kern_data = open(kern_fn, 'rb').read()
        kern_len = len(kern_data)
        print(f'*** Read {kern_len} bytes from {kern_fn}.')

        img[startix:startix+kern_len] = kern_data

open('mi_router_4a_new.img', 'wb').write(img)
