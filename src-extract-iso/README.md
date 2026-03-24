# Analysis Part I

## Extract icons

__Warning:__ the disk image will be deleted in the process. Make a copy!

1) Run `main` on an macOS install image (iso or dmg or pkg) which combines the following two steps:

    a) `iso-deep-unpack` extracts all package-like formats and repeats the process for all nested packages.

    b) `rsrc-to-icns.py` will find all `.icns` files inside Resource Forks and extract them inplace. See Resource Fork disclaimer in [collection-extracted/README.md](../collection-extracted/README.md).


## Analyze

`analyze.py` will create (or update) the `extracted.db` database (see [results](../results)) and then run an automated evaluation on it.
