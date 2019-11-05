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

    if partname == 'Config__':
        print("*** Patching Config section! (remove uart_en=0).")
        asc_fn = f'{partname}_new.asc'
        with open(asc_fn, 'wt') as cfg_file_txt:
            cfg_start = startix + 4
            while True:
                cfg_end_rel = img[cfg_start:endix].find(0)
                if cfg_end_rel == 0:  # last entry
                    break

                cfg_end = cfg_start + cfg_end_rel
                cfg_line = img[cfg_start:cfg_end].decode('ascii')
                # remove uart_en=0 line
                cfg_start = cfg_end + 1

                if not cfg_line.startswith('uart_en='):
                    print(f'  {partname}: {cfg_line} <-- SKIPPING!')
                    print(cfg_line, file=cfg_file_txt)
                else:
                    print(f'  {partname}: {cfg_line}')

            print('uart_en=1', file=cfg_file_txt)

        print('Running mkenvimage...')
        subprocess.run(['mkenvimage',
                        f'-s{partlen}', f'-o{part_new_fn}', asc_fn])

    if partname == 'OS1':
        kern_fn = 'openwrt-ramips-mt7621-xiaomi_mir3g-squashfs-kernel1.bin'
        kern_data = open(kern_fn, 'rb').read()
        kern_len = len(kern_data)
        print(f'*** Read {kern_len} bytes from {kern_fn}.')

        img[startix:startix+kern_len] = kern_data

        skip_offs = (startix + kern_len + 0xffff) & ~0xffff
        print(f'*** Skipping to offset 0x{skip_offs:x}')

        rootfs_fn = 'openwrt-ramips-mt7621-xiaomi_mir3g-squashfs-rootfs0.bin'
        rootfs_data = open(rootfs_fn, 'rb').read()
        rootfs_len = len(rootfs_data)
        print(f'*** Read {rootfs_len} bytes from {rootfs_fn}.')

        img[skip_offs:skip_offs+rootfs_len] = rootfs_data

    if os.path.exists(part_new_fn):
        data_new = open(part_new_fn, 'rb').read()
        print(f'*** Read {len(data_new)} bytes from {part_new_fn}.')
        assert(len(data_new) <= partlen)
        img[startix:startix+len(data_new)] = data_new


open('mi_router_4a_new.img', 'wb').write(img)
