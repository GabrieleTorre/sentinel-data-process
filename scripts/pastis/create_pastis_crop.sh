#!/bin/bash

metadata='/Users/beppe/Volumes/Storage2/hdd/PASTIS/metadata.geojson';
safe_dir='/Users/beppe/Projects/AgriTech/PASTIS_test';
output_dir='/Users/beppe/Projects/AgriTech/DATA_S2';

for tile in T30UXV
do
  python create_pastis_crop.py --metadata $metadata --safe_dir $safe_dir --output_dir $output_dir --tile $tile;
done
