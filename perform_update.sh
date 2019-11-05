#!/bin/sh

###
# read flash
###

if ! [ -f  mi_router_4a.img ] ; then
        sudo flashrom -p ch341a_spi -c GD25Q128C -r mi_router_4a.img
fi

if ! [ -f openwrt-ramips-mt7621-xiaomi_mir3g-v2-initramfs-kernel.bin ] ; then
	wget https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/openwrt-ramips-mt7621-xiaomi_mir3g-v2-initramfs-kernel.bin
fi

if ! [ -f openwrt-ramips-mt7621-xiaomi_mir3g-v2-squashfs-sysupgrade.bin ] ; then
	wget https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/openwrt-ramips-mt7621-xiaomi_mir3g-v2-squashfs-sysupgrade.bin
fi

./patch_image.py
sudo flashrom -p ch341a_spi -c GD25Q128C -w mi_router_4a_new.img

echo "Now copy sysupgrade to device, and mtd write sysupgrade /dev/mtd7!"

