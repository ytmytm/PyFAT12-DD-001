
# PyFAT12-DD-001

This is a fork of PyFAT12 Python library to support FAT12 in flavour supported by
DD-001 3.5" floppy drive interface firmware for C64.

If you want to know more about DD-001 visit [this blog entry](http://news.ide64.org/2018/11/floppy-drive-tib-plc-dd-001-drive-2001.html).

The main difference related to standard FAT12 is that DD-001 doesn't store Commodore files
in a standard format - with first two bytes of the file data stream interpreted as load address.
This information is instead stored at offsets `$10/$11` of the file entry with high-byte first.
It makes it impossible to just copy PRG files from any source on to a floppy, like you can do with
SD2IEC. (At least until firmware is updated.)

## Hardware notes

The blog entry above contains all information you need to build your own clone of the device.
Some comments that may help you initially. Your mileage may vary.

- Only the straight ribbon-cable connection worked for me, drive connected to the last connector (after the twist)
  was not accessible, even with its jumper set to DS0. With DS1 nothing worked, with DS0 setting the LED blinked
  like for access, but motor didn't turn. I think this is a design problem and there should be a full set of jumpers
  on the cartridge side
- I used standard PC FDD for HD floppies, with HD floppies. But the provided firmware can't format HD floppies. It
  returned 'DISK NOT RELIABLE' error until the HD hole is covered. Still - it's a HD FDD with HD floppy, the only
  thing to do was to cover the HD hole on the floppy. This was true also for formatting 720K (DD) floppies on an
  ancient PC, from Windows 2000. I could format HD floppy as DD, but DD-001 couldn't read it reliably. Only after
  covering the HD hole and formatting it again as DD it worked fine.
- If there is no floppy in the drive the firmware will try to read it for several seconds until displaying a message.
  That's the only time when you can hit RUN/STOP key to regain control and enter BASIC
- If there is a DD-formatted floppy in the drive, without BOOT.EXE file firmware will give up immediately
- Don't bother with v1.0 firmware, use only v1.1
- The cartridge should have a RESET button
- Ideally the cartridge should have at least 16K of ROM for proper support of FAT12 filesystem and CBM DOS-style commands
- Ideally the cartridge should also have at least 16K of RAM to read whole track (both sides) at once and keep FAT in memory at all times

## Software notes

- only root folder is supported
- long filenames are not supported (VFAT is quite complex)

## Final words

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
