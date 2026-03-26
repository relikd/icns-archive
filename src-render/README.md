# Analysis Part II

## Quickstart

1. Run `make export` to generate a zip bundle with the `render` executable and all test files.
2. Copy the `variants.zip` to your test-machine, unzip it, and run `./render-icons` from the extracted directory.
3. Copy `results.zip` back to your machine.
4. Start post-processing.


## Detailed procedure

1) `gen-raw-files.py` generates raw image files (argb¹, rgb¹, png, jpf) with a 2px interleaved RGB-pattern.
=> Pre-computed results are archived in `assets/raw-files.zip`.  
*Note:* Due to lack of support, jp2 cannot be generated.

2) `gen-variants.py` converts raw images to `.icns` and `.app` bundle files (raw images are read directly from the zip file without unzipping).  
*Note:* You can generate these on the fly or copy the result to the target machine manually.

3) `render-icons` (10.6+) converts these `.icns` and `.app` thumbnails into `.png`.
This must be done on the target machine / macOS version because the rendering is the important part.
Make sure no UI (or cursor) is blocking the thumbnail preview and deactivate any screen savers.

4) `postprocess-crop.py` crops all `app` screenshots to only include the window content.  
*Note:* Images are scaled, so expect blur and slightly off color values.

5) `postprocess-collage.py` arranges all cropped `app` images in a single file.

6) `analyze.py` evaluates all rendered `.png` files for a pixel-perfect match and print out a format-support matrix table.  


¹ The script tests both, compressed and uncompressed, RGB data.
