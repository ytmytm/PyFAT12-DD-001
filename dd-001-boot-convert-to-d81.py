#!/usr/bin/python3

import subprocess
import pdb
from pyfat12 import FloppyImage, FAT12

# This script extracts files from dd001boot disk image
# - adds load addresses (via modified pyfat12)
# - adds start addresses (copied from MULT.ASC file) to runnable files
# - compresses runnable files with exomizer so that you can actually load & run them

# To make dd-001 boot disk image actually readable/mountable I had to replace the data
# in the boot sector (first 512 bytes).
# This is necessary because important FAT information that defines filesystem is stored there.
# Original DD-001 firmware doesn't use this information.

# Folders within BOOTFOLDER:
# - files_data/ - raw data stream, that's what you would get if copying files out in Windows/Linux
# - files_with_loadaddr - files prepended with load address, except MULT.ASC (this proves that original firmware is broken)
# - files_with_loadaddr_runnable - files that you can run compressed with exomizer and with start address set

# Tools you need in path:
# - exomizer from https://bitbucket.org/magli143/exomizer/wiki/Home
# - c1541 from VICE package

#
# Maciej 'YTM/Elysium' Witkowiak, 2023 <ytm@elysium.pl>
#

BOOTFOLDER = "dd-001-boot"

floppy = FloppyImage(size=3.5, capacity=720)
floppy.open(f"{BOOTFOLDER}/dd001boot-with-bootsector.img")
fs = FAT12(floppy)
fileCount = 0

# list of start addresses mapped from MULT.ASC file

startaddr = {
    "GUTZ.EXE" : 0x0800,
    "FIRE.PRG" : 0x1000,
    "MOUSE0.EXE" : 0xC000,
    "NINJA.EXE" : 0x0880,
    "PYJAMAS.PRG" : 0x0b09,
    "QUACK.PRG" : 0x445C,
    "FROSTY.PRG" : 0x0b09,

    "EQUINOX.PRG" : 0x0b09,
    "DISKMON.EXE" : 0x1000,
    "DISKASC.EXE" : 0x1000,
    "DISKHEX.EXE" : 0x1000,
    "DISKCOPY.EXE" : 0x0800,
    "FILECOPY.EXE" : 0x0800,
    "BROWSER.EXE" : 0x1000,
    "FORMAT.EXE" : 0x0800,
    # this one is fixed in firmware
    "BOOT.EXE" : 0x1000
}

diskimage = f"{BOOTFOLDER}/dd-001-boot.d81"
subprocess.run(f"c1541 -format DD-001,01 d81 {diskimage} 8", shell=True)

for file in fs.listfiles("/"):
    fileCount += 1
    print(f"{file.name}, {file.size} @ {file.load_address:04x}")
    with open(f"{BOOTFOLDER}/files_with_loadaddr/{file.name}", 'wb') as f:
        with_load_address = file.name != "MULT.ASC"
        f.write(fs.read_file(file.name, with_load_address))

    with open(f"{BOOTFOLDER}/files_data/{file.name}", 'wb') as f:
        f.write(fs.read_file(file.name, False))


    if file.name in startaddr.keys():
        print(f"exomize: {startaddr[file.name]:04x}")

        inputfile = f"{BOOTFOLDER}/files_with_loadaddr/{file.name}"
        outputfile = f"{BOOTFOLDER}/files_with_loadaddr_runnable/{file.name.lower()}"
        start_address = f"0x{startaddr[file.name]:04x}"
        command = f"exomizer sfx {start_address} -t64 \"{inputfile}\" -o \"{outputfile}\""
        subprocess.run(command, shell=True)
        subprocess.run(f"c1541 -attach {diskimage} 8 -write {outputfile}", shell=True)
    else:
        inputfile = f"{BOOTFOLDER}/files_with_loadaddr/{file.name}"
        subprocess.run(f"c1541 -attach {diskimage} 8 -write {inputfile} {file.name.lower()}", shell=True)

print(fileCount, "files in total")

