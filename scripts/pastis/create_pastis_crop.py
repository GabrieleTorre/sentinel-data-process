from sentinel_preprocess.crop_pastis import crop_pastis
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="create crop for PASTIS model, from Sentinel-2 data",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--metadata",  default="None", help="location of geojson containing pastis metadata")
    parser.add_argument("--safe_dir", default="None", help="data .SAFE location")
    parser.add_argument("--output_dir", default="None", help="data out location")
    parser.add_argument("--tile", default="None", help="tile of interest")
    parser.add_argument("--ref_date", default="None", help="date of interest")
    args = parser.parse_args()

    crop_pastis(pastis_metadata=args.metadata,
                safe_dir=args.safe_dir,
                output_dir=args.output_dir).crop_tile_for_pastis(args.tile, int(args.ref_date))
