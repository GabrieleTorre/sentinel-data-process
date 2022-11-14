from sentinel5dl import search, download
from datetime import datetime
from pathlib import Path
import os


str_polygon = 'POLYGON ((9.078124246782346 44.48547000202995, ' \
              '9.078124246782346 44.66988462274853, 8.820027000588126 44.66988462274853, ' \
              '8.820027000588126 44.48547000202995, 9.078124246782346 44.48547000202995))'

bands = ['L2__CO____', 'L2__NO2___', 'L2__SO2___', 'L2__AER_LH']

sentinel5_dir = '/Volumes/Volume/Sentinel-5'


def main(product):
    result = search(
        polygon=str_polygon,
        begin_ts=datetime(2021, 1, 1),
        end_ts=datetime(2022, 1, 1),
        product=product,
        processing_level='L2',
        # processing_mode='Near real time'
        processing_mode='Offline'
    )

    output_dir = os.path.join(sentinel5_dir, product)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    download(result.get('products'), output_dir=output_dir)


if __name__ == "__main__":
    for _prod in bands:
        main(_prod)
