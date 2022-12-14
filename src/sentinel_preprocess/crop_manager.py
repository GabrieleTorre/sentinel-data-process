from shapely.geometry import Polygon
from rasterio.windows import Window
from rasterio.io import MemoryFile
from tiff_utils import extrapolate
from pyproj import Transformer
from pathlib import Path
from glob import glob
import pandas as pd
import numpy as np
import itertools
import geopandas
import rasterio
import os


class crop_manager():
    def __init__(self):
        self.bands = ["B02", "B03", "B04", "B05", "B06", "B07", "B08",
                      "B8A", "B11", "B12"]
        self.resolutions = ["R10m", "R10m", "R10m", "R20m", "R20m", "R20m",
                            "R10m", "R20m", "R20m", "R20m"]

        self.masks = ['MSK_CLDPRB', 'MSK_SNWPRB']
        self.masks_resolution = ['20m', '20m']

        self.bands_and_resolutions = list(zip(self.bands, self.resolutions))
        self.masks_and_resolutions = list(zip(self.masks, self.masks_resolution))

        self.target_dim = (10980, 10980)
        self.id_format = 'lat{}long{}'


    @staticmethod
    def get_bands_dirs(src_dir):
        src_data_dirs = []
        # per ogni giorno a disposizione individua il path in cui recuperare i dati
        for x in glob(os.path.join(src_dir, '*')):
            name = x.split('/')[-1].split(".")[0]
            src_data_dir = glob(os.path.join(x, "GRANULE/*/IMG_DATA"))[0]
            src_data_dirs.append((name, src_data_dir))

        return sorted(src_data_dirs, key=lambda x: x[0])

    def read_all_bands(self, src_data_dir):
        tiff_f = None
        for i, (band, resolution) in enumerate(self.bands_and_resolutions, start=1):
            band_file = glob(os.path.join(src_data_dir, resolution, "*_" + band + "_*.jp2"))[0]

            band_f = rasterio.open(band_file, driver="JP2OpenJPEG")
            band_data = band_f.read(1)

            if band_data.shape[0] < self.target_dim[0] and band_data.shape[1] < self.target_dim[1]:
                # print("Extrapolating", band_data.shape, "to", self.target_dim)
                band_data = extrapolate(band_data, self.target_dim).astype(band_f.dtypes[0])

            if tiff_f is None:
                profile = band_f.profile
                profile['width'] = self.target_dim[0]
                profile['height'] = self.target_dim[1]
                profile.update(driver="Gtiff", count=len(self.bands_and_resolutions))
                tiff_f = MemoryFile().open(**profile)

            # print("Writing band {} for date {}".format(band, date))
            tiff_f.write(band_data, i)
            band_f.close()

        return tiff_f

    def read_cloud_masks(self, src_mask_dir):
        tiff_f = None
        for i, (mask, resolution) in enumerate(self.masks_and_resolutions, start=1):
            mask_file = os.path.join(src_mask_dir, '{}_'.format(mask) + resolution + ".jp2")

            mask_f = rasterio.open(mask_file, driver="JP2OpenJPEG")
            mask_data = mask_f.read(1)

            if mask_data.shape[0] < self.target_dim[0] and mask_data.shape[1] < self.target_dim[1]:
                mask_data = extrapolate(mask_data, self.target_dim)
                mask_data = mask_data.astype(mask_f.dtypes[0])

            if tiff_f is None:
                profile = mask_f.profile
                profile['width'] = self.target_dim[0]
                profile['height'] = self.target_dim[1]
                profile.update(driver="Gtiff", count=len(self.masks_and_resolutions))
                tiff_f = MemoryFile().open(**profile)

            # print("Writing band {} for date {}".format(band, date))
            tiff_f.write(mask_data, i)
            mask_f.close()

        return tiff_f

    @staticmethod
    def extract_tile_name(x): return x.split('/')[-2].split('_')[1]

    def create_crops_data(self, safe_data_path, numpy_root_data_dir):
        _name = safe_data_path.split('/')[-1].split(".")[0]

        curr_data_dir = glob(os.path.join(safe_data_path, "GRANULE/*/IMG_DATA"))[0]
        curr_mask_dir = ['/'] + curr_data_dir.split('/')[:-1] + ["QI_DATA"]
        curr_mask_dir = os.path.join(*curr_mask_dir)

        tile = self.extract_tile_name(curr_data_dir)

        npname = _name.split('/')[-1].split('_')[2].split('T')[0]

        dataset = self.read_all_bands(curr_data_dir)
        cldmask = self.read_cloud_masks(curr_mask_dir)

        df_meta = geopandas.GeoDataFrame.from_file(os.path.join(numpy_root_data_dir, tile, 'metadata.json'))
        for _, sel in df_meta.iterrows():
            _path = os.path.join(numpy_root_data_dir, tile, sel.id)
            Path(_path).mkdir(parents=True, exist_ok=True)

            # crop 128x128 partendo da coordinate top-left
            _frame = dataset.read(window=Window(sel.start_col, sel.start_row, 128, 128))
            np.save(os.path.join(_path, npname + '.npy'), _frame)

            _mask = cldmask.read(window=Window(sel.start_col, sel.start_row, 128, 128))
            cloudP_dir = os.path.join(_path, 'cloudProb')

            if os.path.isdir(cloudP_dir) == False: os.mkdir(cloudP_dir)
            np.save(os.path.join(cloudP_dir, npname+'.npy'), _mask)

    def create_metada(self, safe_path):
        curr_data_dir = glob(os.path.join(safe_path, "GRANULE/*/IMG_DATA"))[0]
        tile = self.extract_tile_name(curr_data_dir)
        dataset = self.read_all_bands(curr_data_dir)

        # si esclude una striscia (inferiore a 128)
        row_list = col_list = [i * 128 for i in range(10980 // 128 - 1)]
        transformer = Transformer.from_crs(dataset.crs, "epsg:4326", always_xy=True)
        meta_list = []
        for pixel_row, pixel_col in itertools.product(row_list, row_list):
            first_coord = transformer.transform(*dataset.xy(pixel_row, pixel_col, offset='ul'))
            _id = self.id_format.format(int(first_coord[1] * 1000), int(first_coord[0] * 1000))
            geometry = Polygon([first_coord,
                                transformer.transform(*dataset.xy(pixel_row, pixel_col + 127, offset='ur')),
                                transformer.transform(*dataset.xy(pixel_row + 127, pixel_col + 127, offset='lr')),
                                transformer.transform(*dataset.xy(pixel_row + 127, pixel_col, offset='ll'))
                                ])
            meta_list.append({'id': _id, 'tile': tile,
                              'start_row': pixel_row, 'start_col': pixel_col,
                              'geometry': geometry})
        df_meta = geopandas.GeoDataFrame(pd.DataFrame.from_dict(meta_list), crs="epsg:4326")
        return df_meta
