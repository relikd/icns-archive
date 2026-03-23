# Analysis results


## Part 1

- Icns files were first used in OS 8.5. Before that, icons were stored directly in Resource Fork fields.
- The `ICON`-key was never used in icns files (only in Resource Forks).
- A detailed analysis of which key was used in which macOS version can be found at [extracted.db-results.md](./extracted.db-results.md) ¹

¹ The analysis-results-table includes both, actual icns files and Resource Fork icons.
You can query the database manually to see specifics (`fake=0`).


## Part 2

- Many icns types render fine in `.icns` __OR__ in `.app` bundles, but not both (`icsb`, `icp6`).
- The ARGB format for icns files was introduced in macOS 11.
- But apparently, Apple could render some ARGB fields back in 10.5 when placed in an `.app` bundle.
- Uncompressed RGB / ARGB was never supported.
- In macOS 10.14 and 10.15 the ARGB fields `ic04` and `ic05` can be "fixed" by including a transparency mask (`s8mk` and `l8mk` respectively).
  This is wrong on a technical level.
  For one, these transparency masks are reserved for the RGB fields `is32` and `il32`
  — and ARGB already contains its own transparency mask.
- A detailed analysis can be found at [rendered.db-results.md](./rendered.db-results.md)

Curiously, on my local machine (macOS 15) I cannot render `jp2` images, only `jpf`.
But when tested in a macOS 15 VM, `jp2` icons rendered fine.
I do not know why this issue exists (or whether it may affect other machines).
