from sentinelsat import SentinelAPI
from collections import OrderedDict
from pathlib import Path
from glob import glob
import os


class download_manager():
    def __init__(self, output_dir, user='pipporusso', pwd='pipporusso89'):
        self.output_dir = output_dir
        self.api = SentinelAPI(user, pwd, 'https://scihub.copernicus.eu/dhus')

    def download(self, df_tile, start_date, end_date):
        for tile, footprint in df_tile.footprint.iteritems():
            filtered = OrderedDict()
            products = self.api.query(footprint,
                                      date=(start_date, end_date),
                                      platformname='Sentinel-2',
                                      processinglevel='Level-2A',
                                      cloudcoverpercentage=(0, 100)
                                      )
            tile_output_dir = os.path.join(self.output_dir, tile.upper())
            Path(tile_output_dir).mkdir(parents=True, exist_ok=True)
            for key, elm in products.items():
                if (tile.upper() in elm['title']) and (not glob(os.path.join(tile_output_dir, elm['title']) + '.*')):
                    filtered[key] = elm
            out = self.api.download_all(filtered, directory_path=tile_output_dir)
            with open(os.path.join(self.output_dir, 'download_tiles.log'), 'a+') as f:
                f.write(str(out))
