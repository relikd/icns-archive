# Compatibility of macOS icon files

Files and scripts to test compatibility of `.icns` files.  
=> Results see [results/README.md](./results/README.md).

Jump to [Wiki](#wiki).


## About this project

I wrote a Python library ([relikd/icnsutil](https://github.com/relikd/icnsutil/)) for parsing `.icns` files.
Back then, I did a lot of research into the file format and identified some limitations and undocumented keys.
Consequently, I wrote a lot of the information you can find on Wikipedia ([Apple Icon Image format](https://en.wikipedia.org/wiki/Apple_Icon_Image_format)).

Now, I am revisiting the Wikipedia article and it still bothers me that the compatibility column is not filled for all icon types.
It also misses info on whether/when a type was discontinued.
Or recommendations on which `OSType` to use if you target a specific macOS version.

So here it is, a full-fledged compatibility analysis.


## Hypothesis

How to test compatibility?

### Part 1

Download macOS installer images and extract all of its contents.
Find all `.icns` files and check which `OSTypes` are used.
The idea is that we can do this for __all__ macOS versions to see which types are used in which OS.
Theoretically, we can deduce whether icon types have been discontinued.
But more importantly, we can also see the first macOS version which introduced a new icon type (or data type inside an icon field).

Assumptions:
- New types are introduced only on major OS versions.
- Support for a new type and usage of a new type happen in the same OS version.
- We focus on Apple provided software and not third parties because Apple knows best how to create/use icns files. Other developers may add types which weren't supposed to be used (or misuse them).

=> source code in [src-extract-iso](./src-extract-iso/), results in [collection-extracted](./collection-extracted/)


### Part 2

Boot into each macOS version and analyze which types are supported, namely displayed properly.
We can test this with known input data and check whether the representation matches the expectation.
And while we are on it, we can try all possible combinations between icon types (`OSType`) and data types (`argb`, `jp2`, `jpf`, `png`, `rgb`).

Assumptions:
- No error were made during test-icon creation (*fingers crossed*)
- Since we try this on the latest update version (per OS), we may falsely declare support for a new type (e.g., no support in 10.5.1 but added in 10.5.3). Arguably, users will likely update to the latest patch version even if they stick to a specific major release.

=> source code in [src-render](./src-render/), results in [collection-rendered](./collection-rendered/)


# Wiki

... because Wikipedia doesnt want my research.


## File structure

The file format consists of an 8 byte header, followed by any number of icons.

### Header

Offset | Size | Purpose
-------|------|---------
0      | 4    | Magic literal, must be "icns" (0x69, 0x63, 0x6e, 0x73)
4      | 4    | Length of file, in bytes, msb first

### Icon data

Offset | Size     | Purpose
-------|----------|---------
0      | 4        | Icon type, see OSType below.
4      | 4        | Length of data, in bytes (including type and length), msb first
8      | Variable | Icon data


## Known types

### Classic icons

These icons were mostly used in Mac OS 9 and earlier, and have a fixed data length (width * height * bits).

OSType | Bytes | Size  | Supported OS | Description
-------|-------|-------|--------------|---------------
`ICON` | 128   | 32×32 | 1.0 – 9.2.2  | 1-bit mono icon
`ICN#` | 256   | 32×32 | 6.0          | 1-bit mono icon with 1-bit mask
`icm#` | 48    | 16×12 | 6.0 – 10.6   | 1 bit mono icon with 1-bit mask
`icm4` | 96    | 16×12 | 7.0 – 10.6   | 4 bit icon
`icm8` | 192   | 16×12 | 7.0 – 10.6   | 8 bit icon
`ics#` | 64    | 16×16 | 6.0          | 1-bit mono icon with 1-bit mask
`ics4` | 128   | 16×16 | 7.0          | 4-bit icon
`ics8` | 256   | 16×16 | 7.0          | 8 bit icon
`icl4` | 512   | 32×32 | 7.0          | 4-bit icon
`icl8` | 1024  | 32×32 | 7.0          | 8-bit icon
`ich#` | 576   | 48×48 | 8.5          | 1-bit mono icon with 1-bit mask
`ich4` | 1152  | 48×48 | 8.5          | 4-bit icon
`ich8` | 2304  | 48×48 | 8.5          | 8-bit icon


### Modern icons

These are the preferred icons since Mac OS X 10.0.
The some icons can display more than one data type but the values below are what Apple has used over the years.
The data type column shows the designated type for each icon (see [Compatibility](#compatibility)).

OSType | Size      | Data Type  | Supported OS | Notes
-------|-----------|------------|--------------|---------------
`is32` | 16×16     | 24-bit RGB | 8.5          | 
`s8mk` | 16×16     | 8-bit mask | 8.5          | fixed length: 256 bytes
`il32` | 32×32     | 24-bit RGB | 8.5          | 
`l8mk` | 32×32     | 8-bit mask | 8.5          | fixed length: 1024 bytes
`ih32` | 48×48     | 24-bit RGB | 9.0          | 
`h8mk` | 48×48     | 8-bit mask | 9.0          | fixed length: 2304 bytes
`it32` | 128×128   | 24-bit RGB | 9.0          | + 4-byte header¹
`t8mk` | 128×128   | 8-bit mask | 9.0          | fixed length: 16384 bytes
`icp4` | 16×16     | 24-bit RGB | 10.7         | 
`icp5` | 32×32     | 24-bit RGB | 10.7         | 
`icp6` | 48×48     |            | 10.7         | see [Compatibility](#compatibility)
`ic07` | 128×128   | PNG        | 10.7         | 
`ic08` | 256×256   | JPF, PNG   | 10.5         | no PNG support in 10.5
`ic09` | 512×512   | JPF, PNG   | 10.5         | no PNG support in 10.5
`ic10` | 1024×1024 | PNG        | 10.7         | 512x512@2x "retina"
`ic11` | 32×32     | PNG        | 10.7         | 16x16@2x "retina"
`ic12` | 64×64     | PNG        | 10.7         | 32x32@2x "retina"
`ic13` | 256×256   | PNG        | 10.7         | 128x128@2x "retina"
`ic14` | 512×512   | PNG        | 10.7         | 256x256@2x "retina"
`ic04` | 16×16     | ARGB       | 10.13        | 
`ic05` | 32×32     | ARGB       | 10.13        | 16x16@2x "retina"
`icsb` | 18×18     | ARGB       | 10.7         | 
`icsB` | 36×36     | PNG        | 10.7         | 18x18@2x "retina"
`sb24` | 24×24     | PNG        | 10.15        | 
`SB24` | 48×48     | PNG        | 10.15        | 24x24@2x "retina"

¹ it32 data always starts with a header of four zero-bytes (see [Image data formats](#image-data-formats)).


### Nested icns

Each field contain a full icns file with multiple formats.
The icns file header (magic number + length) is omitted from the data.
So, if you want to save the data to a file you have to re-create and prepend the [icns header](#header).

OSType        | Supported OS  | Description
--------------|---------------|-------------
`tile`        | 10.0 – 10.7   | 
`over`        | 10.3 – 10.6   | 
`open`        | 10.3 – 10.6   | 
`odrp`        | 10.3 – 10.6   | 
`sbpp`        | 10.7 – 10.10  | 
`slct`        | 10.9          | "selected" icns file. Usage unknown.
`sbtp`        | 10.10         | "template" icns file. Usage unknown.
`FF DA 3A 5D` | 10.10 – 10.10 | 
`FD D9 2F A8` | 10.14         | "dark" icns file. Allows automatic icon switching in Dark mode.


### Other types

OSType | Supported OS | Description
-------|--------------|-------------
`TOC ` | 10.7         | "Table of Contents" a list of all image types in the file, and their sizes. A TOC is written out as OSType (4 bytes) and size (4 bytes) for each icon field in the file.
`icnV` | 10.5         | 4-byte big endian float - equal to the bundle version number of Icon Composer app that created the icon
`name` | 10.11        | Usage unknown. Known values are: "icon", "template", and "selected". The two latter have not been used since MacOS 10.15.
`info` | 10.12        | Info binary plist. Usage unknown (only name field seems to be used).


## Image data formats

### Mono
Mono icons with alpha mask can display three colors: white, black, and transparent.
The first half of the icon data is dedicated to the color (0-bit: white, 1-bit: black).
The second half is the alpha mask (0-bit: transparent, 1-bit: opaque).

### 4-bit an 8-bit icons
The 4-bit an 8-bit icons use a fixed color palette with 16 colors and 256 colors, respectively.

### 8-bit mask
Mask elements provide only the alpha channel data.
The data is not compressed and uses one byte per pixel.

### 24-bit RGB
The 24-bit RGB data is encoded by color channels and not by pixels (e.g., RRRGGGBBB instead of RGBRGBRGB).
The three channels are separately compressed and tightly packed (see [Compression](#compression)).

it32 data must start with a four-byte header.
By convention, the header has four zero-bytes, but it can be any value and is quietly ignored.
In all other cases, no header is needed.

### ARGB
All ARGB images start with an ascii 'ARGB' header.
The ARGB format is very similar to the 24-bit RGB format and uses the same Compression.
The image data is split into four channels (e.g., AAARRRGGGBBB) and separately compressed (see [Compression](#compression)).
The only difference is the added alpha channel.

### JP2, JPF, PNG
Unmodified image data of a JPEG 2000 or PNG image.


## Compatibility of other image formats

Icns files have support for multiple image formats (RGB, ARGB, PNG, JPEG200) but that does not mean all image formats are supported by all icon fields.
Though later macOS versions may add support for new formats for an existing OSType.
For example, when ic08 and ic09 were introduced in Mac OS 10.5, they could only display JPEG200 images.
Support for PNG was added in Mac OS 10.6. Furthermore, there is a distinction how the icon is used: in a standalone `.icns` file or bundled in a `.app` application.
E.g., even though Mac OS 10.5 could display JPEG2000 icons in icns files, the icons were not rendered as an app icon.

Therefore, usage of the icns format depends on your use case.
If your process includes composing icns files, you should stick to the designated data types in the table above.
If your process involves reading icns files, you should add support for all possible data formats.
Since Mac OS 10.7, all modern icon fields (even the 24-bit RGB) can display PNG and JPEG2000 in standalone icns files (but not in app bundles).

icp6 has no designated type because it was not used by Apple in any icns files since OS 7.
The rendering analysis shows that this field cannot hold any value which can be displayed in both styles (standalone or app).
Using a PNG will display standalone icns files fine, but won't show an app icon. Using ARGB will display an app icon but won't produce an icns thumbnail.
The field does not seem to be used in application icons and can safely be ignored.

Retina icons are used on a Retina display – the used hardware is irrelevant.
E.g., a Macbook with a Retina display will display the @2x icons but on a non-Retina display connected to the Macbook, the @1x version will be used.
Be careful when composing new icns files that all icon fields are supported.
This issue is especially tricky to detect if the @1x icon is broken but never used on the test machine. 


## Compression

lead value | tail bytes | result uncompressed
-----------|------------|--------------------
  0...127  | 1...128    | 1...128 bytes
128...255  | 1 byte     | 3...130 copies

The ARGB and 24-bit RGB pixel data is compressed (per channel) with a format similar to PackBits.
The image data is always compressed.
Even if the uncompressed data would be smaller than the compressed data and even if the compressed data has the same size as the uncompressed data.


## Known issues

There are certain issues / bugs with the file format:

1. Compressed ARGB data is not interpreted correctly on ARM-based hardware.
   The last value of the blue channel (aka. the very last value) is ignored and treated as if it were all zero-bytes (affects `.app` icon but not `.icns` preview).
   Usually this is no issue since most icons will have transparency at the bottom right corner anyway.
   However, it can become an issue if the last value is a repeating byte (see [Compression](#compression)).
   Potentially, up to 130 pixels can lack the blue channel value.
   A workaround is to append an additional NULL-byte at the end which is ignored.
   You can compare the difference with these two examples:
   - `69636E73 00000024 69633034 0000001C 41524742 FFFFFBFF FF00FB00 FF00FB00 FFFFFBFF`
   - `69636E73 00000025 69633034 0000001D 41524742 FFFFFBFF FF00FB00 FF00FB00 FFFFFBFF 00`
2. RGB fields (`is32`, `il32`, `ih32`, `it32`) should always set an alpha mask (`s8mk`, `l8mk`, `h8mk`, `t8mk`).
   If no mask is set, the behavior is undefined. MacOS 10.9 – 26 show an opaque artwork for `.app` bundles but a transparent artwork for `.icns` files.
   MacOS 10.8 and earlier displays no icon for either.
3. If a field with alpha channel (JPEG2000, PNG, ARGB) is combined with an alpha mask, the alpha channel of the image takes precedence.
   The alpha mask fields are ignored for all other types except 24-bit RGB.
