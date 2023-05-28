
# PyFAT12-DD-001

This is a fork of PyFAT12 Python library to support FAT12 in flavour supported by
DD-001 3.5" floppy drive interface firmware for C64.

I have added support for reading/saving PRG load address as needed by DD-001 firmware and changed the library just enough to make it work on 720K DD images.

If you want to know more about DD-001 visit [this blog entry](http://news.ide64.org/2018/11/floppy-drive-tib-plc-dd-001-drive-2001.html).

## DD-001 disk boot image

The main purpose of this fork was to read the contents of original DD-001 boot disk image.

All data files are in `dd-001-boot` folder:

- `files_data/` contains raw data streams, without load addresses
- `files_with_loadaddr/` contains files with load addresses included, as you would expect for PRG files; except text file MULT.ASC
- `files_with_loadaddr_runnable/` has all the runnable files compressed with [Exomizer](https://bitbucket.org/magli143/exomizer/wiki/Home) 

The contents of the last folder were also copied to a D81 disk image in `dd-001-boot/dd-001-boot.d81`.

This work was done using `dd-001-boot-convert-to-d81.py` script. Read it and comments there for details.

### Boot sector

Important information about FAT filesystem is contained in the boot sector (first 512) bytes. There is a data structure stored there
that describes FAT filesytem (number of FATs, number of entries in root directory, number of sectors per cluster, etc.).
This information is missing from the original dump of dd-001 boot disk image, hence it was not recognized as a FAT12 disk image by any tool.

I have added a standard (copied from an empty, freshly formatted 720k image) boot sector and saved result as `dd001boot-with-bootsector.img`.

### Load addresses

Original firmware doesn't follow Commodore DOS convention and doesn't keep load address as the first two bytes (low byte first) of the file
data stream.

Instead, the load address is stored (high byte first) at offsets `$10/$11` of each file entry, where FAT expects to find creation date.

### Start addresses

Almost all executable files stored on the original boot disk are stored as binaries without BASIC header (a SYS line). The only information
about how to actually run the loaded files was kept within BOOT.EXE menu program.

Fortunately there is a source code for that program, which lists both file names and their start addresses.

I listed this information in `dd-001-boot-convert-to-d81.py` script so that [Exomizer](https://bitbucket.org/magli143/exomizer/wiki/Home) can
start the program after decompression.

## Hardware notes

The blog entry above contains all information you need to build your own clone of the device. For convenience and preservation I copied the archive into this repository.

There is another project with KiCad design for the PCB: [sjgray/TIB-001-Cart](https://github.com/sjgray/TIB-001-Cart)

Here are some comments that may help you initially. Your mileage may vary.

- Only the straight ribbon-cable connection worked for me, drive connected to the last connector (after the twist)
  was not accessible, even with its jumper set to DS0. With DS1 nothing worked, with DS0 setting the LED blinked
  like for access, but motor didn't turn. I think this is a design problem and there should be a full set of jumpers
  on the cartridge side
- I used standard PC HD FDD, with HD floppies. The provided firmware can't format HD floppies. It only returned 'DISK NOT RELIABLE' error for me. 
  I had to cover HD hole on all the floppies even though they were in fact HD, not DD.
  HD floppies (with open hole) formatted as 720K DD on a PC were not read reliably by DD-001. Only after
  covering the HD hole and formatting it again on PC with exactly the same settings (720K DD) it worked fine.
- If there is no floppy in the drive the firmware will try to read it for several seconds until displaying a message.
  That's the only time when you can hit RUN/STOP key to regain control and enter BASIC
- If there is a DD-formatted floppy in the drive, without BOOT.EXE file firmware will give up immediately
- If there is a BOOT.EXE file on the floppy, firmware will load it and then execute by jumping to `$1000`.
- Don't bother with v1.0 firmware, use only v1.1
- The cartridge should have a RESET button
- Ideally the cartridge should have at least 16K of ROM for proper support of FAT12 filesystem and CBM DOS-style commands
- Ideally the cartridge should also have at least 16K of RAM to read whole track (both sides) at once and keep FAT in memory at all times

## Firmware flaws

The whole product is both awesome (yay! cheap 3.5" FDD for a C64 and it's super fast too) and disappointing. The source of
disappointment is deeply flawed firmware which seems rushed and unfinished with important features missing.

- only root folder is supported, up to 112 entries (altough the first one is occupied by volume label)
- keeping load address as creation date makes it impossible to exchange data via PC
- in CBM DOS there is distinction between SEQ files and PRG files. Both are just data streams but for CBM Kernal first two bytes of a PRG
  file have special meaning; there is no such distinction here - but it *could be* easily added via one of the attributes
- disk directory is printed directly, it's not really LOADed
- file-level access is not supported, you can only LOAD and SAVE
- command channel is not supported, CBM DOS commands: N (format), S (scratch, delete), R (rename) commands are not supported (V (validate) command makes no sense for FAT, but could do some
  integrity checking for FAT data)

Long filenames are not supported, but it's not a flaw - VFAT was not invented yet when DD-001 was released.

# 

Original notes for PyFAT12 author follow

# PyFAT12

PyFAT12 is a Python 3 library that allows handling FAT12 file systems. FAT12,
or original FAT, is a file system designed by Microsoft that was used primarily
on 5.25-inch and 3.5-inch floppy disks.

Currently PyFAT12 supports 3.5-inch high density (1.44 MB) floppy disk images
and handling any FAT12 file systems on them. It is also possible to format
a new FAT12 volume. Files can be opened, overwritten, created, renamed, deleted
and so on; subdirectory and volume label support is also present.

This library has not been tested extensively, but basic functionality appears
to work. There might still be bugs.

## Installation

PyFAT12 has been tested on recent Python 3 versions and does not require
any libraries beyond the standard library Python comes with.

```
pip install pyfat12
```

## Documentation

The library comes with docstrings which can be viewed with `help`. Currently
no documentation exists other than this README and the docstrings, but there
are plans to improve the situation.

## Examples

The following example creates a new 3.5-inch high density (1.44 MB) floppy
image called `DISK1.IMG` in the current directory. The image contains a blank,
formatted FAT12 file system:

```python3
from pyfat12 import FloppyImage, FAT12
floppy = FloppyImage()
fs = FAT12.format(floppy, "Disk label")
floppy.save("DISK1.IMG")
```

Opening up an existing image and lists all files from its root directory:

```python3
from pyfat12 import FloppyImage, FAT12
floppy = FloppyImage.open("DISK1.IMG")
fs = FAT12(floppy)
fileCount = 0

for file in fs.listfiles("/"):
    fileCount += 1
    print(file.name, file.size)

print(fileCount, "files in total")
```

Opening up an existing image, adding a new file (or overwriting an existing
one) and saving:

```python3
from pyfat12 import FloppyImage, FAT12
floppy = FloppyImage.open("DISK1.IMG")
fs = FAT12(floppy)
fs.write_file("/HELLO.TXT", b"Hello World!\r\n")
floppy.save("DISK1.IMG")
```

## License

MIT License. See `LICENSE`.
