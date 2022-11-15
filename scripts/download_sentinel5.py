from sentinel5dl import search, download
from datetime import datetime
from pathlib import Path
import pandas as pd
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
    df_products = pd.DataFrame(result.get('products'))
    df_products.loc[:, 'dateref'] = df_products.summary.apply(lambda x: datetime.strptime(x[0].split(' : ')[1],
                                                                                          '%Y-%m-%dT%H:%M:%S.%fZ'))
    # select the first product for each week
    weekly_products = df_products.set_index('dateref').resample('W').first().dropna(subset=['id']).astype({'id': int})

    output_dir = os.path.join(sentinel5_dir, product)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    weekly_products.to_json(path_or_buf=os.path.join(output_dir, 'weekly_products.json'), orient='records')
    download(weekly_products.to_dict(orient='records'), output_dir=output_dir)


if __name__ == "__main__":
    for _prod in bands:
        main(_prod)
