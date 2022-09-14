#!/bin/bash

# out_dir='./tiff-files/'

out_dir='/Volumes/SSD1/Sentinel-2/test-italia-numpy/';
start_date='2021-08-01';
end_date='2021-11-01';

# for f in /Volumes/SSD1/Sentinel-2/2022/*.SAFE;do
for f in /Volumes/SSD1/Sentinel-2/test-italia/*.SAFE;do
      python crop_sentinel2.py $f --directory_out $out_dir --start_date $start_date --end_date $end_date;
done
