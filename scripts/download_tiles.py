from sentinel_preprocess.download_manager import download_manager
from datetime import datetime
import pandas as pd
import argparse
import json


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="download tile from Sentinel-2",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--json_tile",  default="None", help="location of Json containing tile coordinates")
    parser.add_argument("--directory_out", default="None", help="Data Out location")
    parser.add_argument("--start_date", default="None", help="first date (format %Y-%m-%d)")
    parser.add_argument("--end_date", default="None", help="last date (format %Y-%m-%d)")
    parser.add_argument("--user", default="pipporusso", help="Copernicus user")
    parser.add_argument("--pwd", default="pipporusso89", help="Copernicus pwd")
    args = parser.parse_args()

    with open(args.json_tile) as f:
        df_tile = pd.DataFrame(json.load(f))

    start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    download_manager(args.directory_out).download(df_tile, start_date, end_date)
