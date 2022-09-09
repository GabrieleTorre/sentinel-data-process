from sentinel_preprocess.crop_manager import crop_manager
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="cuttingout .save data into npy (128x128)",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("directory_in",  default="None", help="Data In location")
    parser.add_argument("--directory_out", default="None", help="Data Out location")
    args = parser.parse_args()

    crop_manager().create_crops_data(args.directory_in, args.directory_out)

