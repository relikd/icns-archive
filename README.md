# Compatibility of macOS icon files

Files and scripts to test compatibility of `.icns` files.  
=> Results see [results/README.md](./results/README.md).


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

=> source code in [extract-from-iso](./extract-from-iso/), results in [icon-archive](./icon-archive/)


### Part 2

Boot into each macOS version and analyze which types are supported, namely displayed properly.
We can test this with known input data and check whether the representation matches the expectation.
And while we are on it, we can try all possible combinations between icon types (`OSType`) and data types (`argb`, `jp2`, `jpf`, `png`, `rgb`).

Assumptions:
- No error were made during test-icon creation (*fingers crossed*)
- Since we try this on the latest update version (per OS), we may falsely declare support for a new type (e.g., no support in 10.5.1 but added in 10.5.3). Arguably, users will likely update to the latest patch version even if they stick to a specific major release.

=> source code in [check-display-support](./check-display-support/), results in [rendered-archive](./rendered-archive/)
