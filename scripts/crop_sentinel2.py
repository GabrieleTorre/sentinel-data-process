from sentinel_preprocess.crop_manager import crop_manager
from datetime import datetime
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="cuttingout .save data into npy (128x128)",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("directory_in", default="None", help="Data In location")
    parser.add_argument("--directory_out", default="None", help="Data Out location")

    parser.add_argument("--start_date", default="None", help="processing start date yyyy-mm-dd")
    parser.add_argument("--end_date", default="None", help="processing end date yyyy-mm-dd")

    args = parser.parse_args()

    data_date = datetime.strptime(args.directory_in.split('_')[-5], "%Y%m%dT%H%M%S")
    if args.start_date: start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:   end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    conditions = [
        start_date is None and end_date is None,
        start_date is not None and end_date is None and (data_date >= start_date),
        start_date is None and end_date is not None and (data_date <= end_date),
        start_date is not None and end_date is not None and (data_date >= start_date) and (data_date <= end_date)
    ]

    if any(conditions):
        print('Currently Processing: {}'.format(args.directory_in.split('/')[-1]))
        crop_manager().create_crops_data(args.directory_in, args.directory_out)
