#!/bin/bash

# out_dir='./tiff-files/'

out_dir='/Volumes/Volume/test-italia-numpy/'

# for f in /Volumes/SSD1/Sentinel-2/2022/*.SAFE;do
for f in /Volumes/Volume/test-italia/*.SAFE;do
    echo $f;
    python crop_sentinel2.py $f --directory_out $out_dir;
done
