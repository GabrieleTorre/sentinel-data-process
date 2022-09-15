from scipy.interpolate import RectBivariateSpline, interp2d
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry import Polygon
from rasterio.io import MemoryFile
from shapely.ops import transform
from rasterio.mask import mask
from skimage import exposure
import numpy as np
import rasterio
import pyproj


def rgb_from_tiff(path):
    img = rasterio.open(path)
    # https://gis.stackexchange.com/questions/341809/merging-sentinel-2-rgb-bands-with-rasterio#355077
    # 'matplotlib' can only plot 8-bit images between the values of 0 - 255 or floating point values between 0 - 1.
    # Try dividing the Sentinel 2 data by 10000 before plotting it or use min-max normalization
    image = np.array([img.read(3), img.read(2), img.read(1)])
    p2, p98 = np.percentile(image, (0, 98))
    image = exposure.rescale_intensity(image, in_range=(p2, p98))  # / 100000
    return image


def reproject(polygons, proj_from, proj_to):
    proj_from = pyproj.Proj(proj_from)
    proj_to = pyproj.Proj(proj_to)

    projection = pyproj.Transformer.from_proj(proj_from, proj_to)
    out = None
    if isinstance(polygons, MultiPolygon):
        out = [transform(projection.transform, p) for p in polygons.geoms]
    elif isinstance(polygons, Polygon):
        out = [transform(projection.transform, polygons)]
    return out


def extrapolate(arr, target_dim):
    x = np.array(range(arr.shape[0]))
    y = np.array(range(arr.shape[1]))
    z = arr
    xx = np.linspace(x.min(), x.max(), target_dim[0])
    yy = np.linspace(y.min(), y.max(), target_dim[1])

    # new_kernel = RectBivariateSpline(x, y, z, kx=1, ky=2)
    new_kernel = interp2d(x, y, z, kind='linear')

    result = new_kernel(xx, yy)
    return result


def crop_memory_tiff_file(mem_file, polygons, crop=True, invert=False):
    polygons = reproject(polygons, "EPSG:4326", mem_file.crs)  # "EPSG:4326"
    result_image, result_transform = mask(mem_file, polygons, crop=crop, invert=invert)

    profile = mem_file.profile
    profile.update(width=result_image.shape[1],
                   height=result_image.shape[2],
                   transform=result_transform)

    result_f = MemoryFile().open(**profile)
    result_f.write(result_image)

    return result_f


def get_test_polygon(points_list, swap_coordinates=False):
    # Copernicus hub likes polygons in lng/lat format
    return Polygon([(y, x) if swap_coordinates else (x, y) for x, y in points_list])
