# .icns Archive

Download files from [archive.org](https://archive.org/details/macos-icns-archive) and place in this directory.


## A note on Resource Forks

Classic Macintosh store icon files in Resource Forks.
You can access this data by appending the following path suffix:

```sh
cat ./{file}/..namedfork/rsrc
```


## Resource Fork Icon Usage

Not all `.icns` files in this folder are actual icns files.
The `_src.txt` shows the full path from where the icon was extracted.
Paths which end on suffix `{file}.rsrc/*/*.icns`, were extracted from Resource Forks.

- If the path is `.rsrc/icns/`, then the file is a proper `.icns` file.  
  => The Resource Fork did include the full icns file.
- If the path is `.rsrc/{KEY}/` (where `KEY` is anything but "icns" – e.g., `File.rsrc/h8mk/0.icns`), then the data was artificially wrapped in an `.icns` container for display purposes.  
  => The icon keys were scattered loosely in the Resource Fork. The icns container was not part of the original structure.

Technically, the latter should not be considered for the icns file format because they were never part of an icns-file.

This affects mostly old macOS versions (OS 7 – 9) as newer versions seem to avoid Resource Forks.
