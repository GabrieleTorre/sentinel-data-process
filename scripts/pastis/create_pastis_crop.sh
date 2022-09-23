#!/bin/bash

metadata='/Users/beppe/Projects/AgriTech/DATA_S2/dataframe.geojson';
safe_dir='/Users/beppe/Projects/AgriTech/PASTIS_test';
output_dir='/Users/beppe/Projects/AgriTech/DATA_S2';
dates='/Users/beppe/Projects/AgriTech/DATA_S2/dates_test.json';

tile='T30UXV';

jq -c '.[]' $dates | while read i; do
  python create_pastis_crop.py --metadata $metadata --safe_dir $safe_dir --output_dir $output_dir --tile $tile --ref_date $i;
done
