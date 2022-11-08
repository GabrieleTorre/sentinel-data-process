from sentinelsat import SentinelAPI, geojson_to_wkt
from shapely.geometry import Point
from datetime import date


lat = 44.94
long = 9.52
start_date = date(2022, 1, 1)
end_date = date(2022, 11, 1)
out_dir = '/storage/hdd/0/vh/Sentinel/zip_file'

api = SentinelAPI('pipporusso', 'pipporusso89', 'https://scihub.copernicus.eu/dhus')

# search by polygon, time, and SciHub query keywords
mygeojson = Point(long, lat).__geo_interface__
footprint = geojson_to_wkt(mygeojson)
products = api.query(footprint, date=(start_date, end_date),
                     platformname='Sentinel-2', processinglevel='Level-2A',
                     cloudcoverpercentage=(0, 100))

api.download_all(products, directory_path=out_dir)
