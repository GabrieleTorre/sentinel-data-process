from sentinel_preprocess.crop_manager import crop_manager
from tiff_utils import reproject

from rasterio.mask import mask
import geopandas as gpd
from glob import glob
from tqdm import tqdm
import pandas as pd
import numpy as np
import os


class crop_pastis(crop_manager):
    """
    pastis_metadata: location of geojson containing pastis metadata
    safe_dir: data .SAFE location
    output_dir: data out location
    """
    def __init__(self, pastis_metadata, safe_dir, output_dir):
        super().__init__()
        self.pastis_metadata = pastis_metadata
        self.safe_dir = safe_dir
        self.output_dir = output_dir
        self.shape = (10, 128, 128)
        self.npy_template = 'S2_{}.npy'

    def crop_tiff_to_npy(self, mem_file, polygons, from_crs=2154, crop=True, invert=False, filled=False):
        polygons = reproject(polygons, "EPSG:{}".format(from_crs), mem_file.crs)  # "EPSG:4326"
        result_image, _ = mask(mem_file, polygons, crop=crop, invert=invert, filled=filled)
        return result_image.compressed().reshape(*self.shape)

    def retrieve_sentinel_path(self):
        sentinel_df = pd.DataFrame(glob(self.safe_dir + '/*'), columns=['path'])

        sentinel_df.loc[:, 'tile'] = sentinel_df.path.apply(lambda x: x.split('/')[-1].split('_')[5])
        sentinel_df.loc[:, 'ref_date'] = sentinel_df.path.apply(
            lambda x: int(x.split('/')[-1].split('_')[2].split('T')[0]))
        return sentinel_df

    def crop_tile_for_pastis(self, tile, ref_date):
        meta_df = gpd.read_file(self.pastis_metadata)
        meta_df.loc[:, 'TILE'] = meta_df.TILE.str.upper()
        if tile in meta_df.TILE.unique():
            sentinel_df = self.retrieve_sentinel_path()
            data = meta_df[meta_df.TILE == tile.upper()]

            _path = sentinel_df[(sentinel_df.tile == tile.upper()) &
                                (sentinel_df.ref_date == ref_date)].path.iloc[0]
            _name = _path.split('/')[-1].split(".")[0]
            curr_data_dir = glob(os.path.join(_path, "GRANULE/*/IMG_DATA"))[0]
            dataset = crop_manager().read_all_bands(curr_data_dir)
            for _, parcel in data.iterrows():
                X = self.crop_tiff_to_npy(dataset, parcel.geometry)[np.newaxis, :]
                file_path = os.path.join(self.output_dir, self.npy_template.format(parcel.id))
                if os.path.isfile(file_path):
                    tmp = np.load(file_path)
                    X = np.concatenate((tmp, X), axis=0)

                np.save(file_path, X)

        else:
            print('Unknown tile!')
