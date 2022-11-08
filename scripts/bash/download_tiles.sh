#!/bin/bash

json_tile='/Users/beppe/Projects/AgriTech/Sentinel-2/PASTIS/tiff_polygon.json'
directory_out='/Users/beppe/Projects/AgriTech/Sentinel-2/PASTIS'
start_date='2022-09-01'
end_date='2022-10-01'

log_file='/Users/beppe/Projects/AgriTech/Sentinel-2/PASTIS/download_tiles.log'

python download_tiles.py --json_tile $json_tile --directory_out $directory_out \
--start_date $start_date --end_date $end_date > $log_file;