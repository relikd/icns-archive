# Compatibility of macOS icon files – Analysis results


## Part 1

- Icns files were first used in OS 8.5. Before that, icons were stored directly in Resource Fork fields.
- The `ICON`-key was never used in icns files (only in Resource Forks).
- All `it32` keys have a header of four zero-bytes, without exception.
- All RGB fields use compression, without exception.
   - Even if compressed data is larger than uncompressed data.
   - Even when compressed data has the same length as uncompressed data.
- The `name` key can hold three different values:
   - "icon", "template", "selected" (nested inside "template")
- A detailed analysis can be found at [extracted-report.md](./extracted-report.md) ¹

¹ The analysis-results-table includes both, actual icns files and Resource Fork icons.
You can query the database manually to see specifics (`fake=0`).

__Note:__ the key column stores binary keys.
If you want to query a specific key, use the proper notation (e.g., `x'69636c38'` for "icl8").


## Part 2

- Many icns types render fine in `.icns` __OR__ in `.app` bundles, but not both (`icsb`, `icp6`).
- The ARGB format for icns files was introduced in macOS 11.
- But apparently, Apple could render some ARGB fields back in 10.5 when placed in an `.app` bundle.
- Uncompressed RGB / ARGB was never supported.
- In macOS 10.14 and 10.15 the ARGB fields `ic04` and `ic05` can be "fixed" by including a transparency mask (`s8mk` and `l8mk` respectively).
  This is wrong on a technical level.
  For one, these transparency masks are reserved for the RGB fields `is32` and `il32`
  — and ARGB already contains its own transparency mask.
- There is no `ic06` key. Tested all sizes on 10.12 and 15 (both, app and icns).
- OS 9.2.2 (and earlier) has no support for `.icns` files.
  Neither is there a Preview app to view icns files, nor has is support for `.app` bundles.
  PowerPC apps *can* include icons (via Resource Forks) but I couldn't find a quick-fix to apply a custom icon to a given app.
- A detailed analysis can be found at [rendered-report.md](./rendered-report.md)

Curiously, on my local machine (macOS 15) I cannot render `jp2` images, only `jpf`.
But when tested in a macOS 15 VM, `jp2` icons rendered fine.
I do not know why this issue exists (or whether it may affect other machines).


### Edge cases

- RGB fields (`is32`, `il32`, `ih32`, `it32`) should always set an alpha mask (`s8mk`, `l8mk`, `h8mk`, `t8mk`).
  If no mask is set, the behavior is undefined.
  MacOS 10.9 – 26 show an opaque artwork for `.app` but a transparent artwork for `.icns` files.
  MacOS 10.8 and earlier displays no icon for either.
- If a field with alpha channel (jpf, png, argb) is combined with an alpha mask, the alpha channel of the image is used.
  The alpha mask fields are ignored for all other types except 24-bit RGB.
- RGB and ARGB compression has an issue where the very last value is ignored (`.app` only).
  Additionally, if the last value is a repeating value, up to 130 copies would be ignored.
  This test shows, that the issue is prevelent on macOS 12 – 26.
  However, in my initial test in 2018, I stumbled upon this issue on a macOS 11 machine.
  Given that my macOS 11 VM was emulated (Intel), I assume this is an ARM issue.
- The `compression-w-fix`-test shows that adding one `NULL` byte can fix the compression issue – and is displayed correctly in all supported OS versions.
- The `retina` test results are inconclusive because all VMs were used without Retina display support.
  - All icns `@2x` images (`qlmanage` with flag `-f 2`) show the proper icon since 10.7.
    But that is expected, since only `ic10`, `ic11`, `ic12`, `ic13`, `ic14` fields are used (which are supported).
  - Most icns `@1x` images show a red color (expected, non-retina test color).
  - Preview for `.app` icons could not be tested because of the non-Retina display (all icons are red).
  - Starting with macOS 15, the `@2x` icon is displayed if no `@1x` icon exists (with smearing colors).
- The `retina-other` test tries to resolve these uncertainties.
  - macOS 10.13 is the first version to support ARGB in `.app` and `.icns` combined.
    Isolated, the ARGB fields (`ic04`, `ic05`) can only be shown in `.app` but not in `.icns`.
    Equaly, the PNG fields (`ic11`, `ic12`) can only be shown in `.icns` but not in `.app`.
    When comined, the Finder preview will load the @2x version (PNG) and apps will fallback to the @1x version (ARGB) on non-retina displays.
  - This is not true for `icsb` (@1x ARGB).
    The @1x variant cannot be displayed in Finder for `.icns` files until macOS 15.
    Whereas `.app` icons can be displayed since macOS 10.7 for the same field.
    The @2x variant, `icsB` (PNG), will display fine for `.icns` files when used as the only key.
    But when combined with the @1x variant, the `.icns` preview will break on non-Retina screens.
  - See [retina-report.md](./retina-report.md) for further details.
