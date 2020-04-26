import os
import numpy as np
import rasterio as rio
import rasterio.plot as rioplot
import rasterio.mask as mask
import rioxarray as riox
import shapely
import pyproj
import fiona
import geopandas as gpd
import matplotlib.pyplot as plt
import imageio
import shapefile
from PIL import Image

dst_crs = 'EPSG:32636'
CROP_SIZE = 244

def overlap_mask(shapes, profile, tiff_map,
	target_shape=(CROP_SIZE, CROP_SIZE)):

	transform, crs = tiff_map.profile['transform'], tiff_map.profile['crs']
	mask_arr = mask.raster_geometry_mask(tiff_map, 
		shapes)
	print(mask_arr)
	return

	mask = rio.features.rasterize(shapes, 
		(tiff_map.shape[0], tiff_map.shape[1]), 
		fill=0,
		#default_value=255,
		transform=transform)
	return mask

def save_divided_imgs(image, CROP_SIZE=CROP_SIZE):
	"""
	image should be an array of size
	(channels, height, width)
	"""
	i=0
	img_arr = []
	image = image.read()
	while i < image.shape[1]:
		img_arr = []
		for channel in range(image.shape[0]):
			img_arr.append(image[channel, i:i+CROP_SIZE, i:i+CROP_SIZE])
			#print(img_arr[channel].shape)
			print(np.array(img_arr[channel]))
			img = Image.fromarray(np.array(img_arr[channel]))
			img.save(os.path.join('tci', f'{i}_{channel}.png'))
		print(np.array(img_arr).shape)
		img_arr = np.array(img_arr)
		img_arr = Image.fromarray(np.ma.transpose(img_arr, [1, 2, 0]))
		img_arr.save(os.path.join('tci', f'{i}_{channel}.png'))
				#j += CROP_SIZE	
			#break
		i += CROP_SIZE

def get_geoms(shape_paths, crs=dst_crs):

	geoms = []
	for file in shape_paths:
		p = gpd.read_file(file).to_crs(crs)
		for shape in p.geometry:
			geoms.append(shape)
	print(geoms)


if __name__ == '__main__':

	full_map = rio.open('T36UYV_TCI_10m.tif')
	shape_paths = [os.path.join('regions', os.listdir('regions')[i]) 
		for i in range(len(os.listdir('regions')))]
	geoms = get_geoms(shape_paths, crs=full_map.profile['crs'])
	print(geoms)
	save_divided_imgs(full_map)
