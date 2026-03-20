# Analysis Part I

## Extract icons

__Warning:__ the disk image will be deleted in the process. Make a copy!

1) Run `main` on an macOS install image (iso or dmg or pkg) which combines the following two steps:

    a) `iso-deep-unpack` extracts all package-like formats and repeats the process for all nested packages.

    b) `rsrc-to-icns.py` will find all `.icns` files inside Resource Forks and extract them inplace. See Resource Fork disclaimer in [icon-archive/README.md](../icon-archive/README.md).


## Analyze

`analyze.py` will create (or update) the `analysis.db` database and then run an automated evaluation on it.
Both, results and db, are stored in [icon-archive](../icon-archive).
