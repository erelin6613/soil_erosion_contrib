import os
import numpy as np
import rasterio as rio
import rasterio.plot as rioplot
import rasterio.mask as riomask
from rasterio.windows import Window
import geopandas as gpd
from PIL import Image
from shapely.ops import cascaded_union
from threading import Thread

dst_crs = 'EPSG:32636'
CROP_SIZE = 224
MASK_FILE = 'all_masks.geojson'

def overlap_mask(shapes, filename, profile, tiff_map,
	target_shape=(CROP_SIZE, CROP_SIZE)):

	transform, crs = tiff_map.profile['transform'], tiff_map.profile['crs']
	mask_arr = riomask.raster_geometry_mask(tiff_map, 
		shapes, invert=True)
	mask_arr = mask_arr[0]*255
	i=0
	j=0
	while i < mask_arr.shape[0]:
		while j < mask_arr.shape[1]:
			img_arr = mask_arr[i:i+CROP_SIZE, j:j+CROP_SIZE]
			if np.argmax(img_arr.ravel()) == 0 or img_arr.shape != (CROP_SIZE, CROP_SIZE):
				j += CROP_SIZE
				continue
			img_arr = np.array(img_arr, dtype='uint8')
			img_arr = Image.fromarray(img_arr)
			img_arr.save(os.path.join('mask', f'{filename}_{i}_{j}.png'))
			j += CROP_SIZE
		i += CROP_SIZE
		j=0

def save_divided_imgs(image, filename, CROP_SIZE=CROP_SIZE):
	"""
	image should be an array of size
	(channels, height, width)
	"""
	i=0
	j=0
	#img_arr = []
	img = image.read()
	while i < img.shape[1]:
		while j < img.shape[2]:
			meta = image.profile
			meta.update(driver='GTiff')
			meta.update(dtype=rio.float32)
			with rio.open(f'{filename}_{i}_{j}.tif', 'w', **meta) as dst:
				dst.meta['nodata'] = -999
				dst.meta['max'] = 1
				dst.meta['min'] = 0
				dst.write(img.astype(rio.float32), 
					window=Window(i, j, i+CROP_SIZE, j+CROP_SIZE))
			j += CROP_SIZE
		i += CROP_SIZE
		j=0

def get_geoms(shape_paths, crs=dst_crs):

	geoms = []
	for file in shape_paths:
		p = gpd.read_file(file).to_crs(crs)
		for shape in p.geometry:
			geoms.append(shape)
	geoms = cascaded_union(geoms)
	return geoms


def get_masks_n_imgs(base_dir, band, shapes=[MASK_FILE], 
					CROP_SIZE=CROP_SIZE, geoms=None,
					no_cut=False):
	"""
	The data structure is expected to resemble with what it
	has been tested:

	BASE_DIR
		|
		|_WV
		| |
		| |_20190427T083601
		| |	|
		| | |_20190427T083601_agriculture.jp2
		| |	|_20190427T083601_false_color.jp2
		| |	...
		| |_20190427T083601
		| | |
		| | |_20190427T083601_geology.jp2
		| | ...
		|_XA
		| |
		| |_20190427T083601
		| | |
		....
	"""

	tiles = []
	os.system(f'mkdir -p {band}')
	os.system(f'mkdir -p mask')
	for d in os.walk(base_dir):
		if len(d[2]) > 0:
			l=[i for i in d[2] if '_'+str(band) in i]
			#print(l)
			if len(l) > 0:
				tiles.append(os.path.join(d[0], l[0]))
	
	for tile in tiles:
		i=j=0
		try:
			assert tile.split('.')[-1] == 'jp2'
			file = rio.open(tile, driver='JP2OpenJPEG')
			file_array = file.read()
			#print(file_array.shape)
			mask_arr, mask_transform, window = riomask.raster_geometry_mask(file, geoms, invert=True)
		except NotImplementedError:
			raise NotImplementedError('Tif files are written after masking\
				happens, provide .jp2 file first')
			return
		print('Getting shapes...')
		if geoms is None:
			geoms = get_geoms(shapes, crs=file.profile['crs'])
		transform, crs = file.profile['transform'], file.profile['crs']
		if no_cut:
			mask_arr.save(os.path.join('mask', filename))
			tag_arr = np.ma.transpose(file_array, [1, 2, 0])
			tag_img.save(os.path.join(band, filename))
			return

		
		while i < file_array.shape[1]:
			while j < file_array.shape[2]:
				img_arr = mask_arr[i:i+CROP_SIZE, j:j+CROP_SIZE]*255
				#print(img_arr)
				if np.argmax(img_arr.ravel()) == 0 or img_arr.shape != (CROP_SIZE, CROP_SIZE):	
					print('No overlaping masks found in tile {}'
						.format((i, i+CROP_SIZE, j, j+CROP_SIZE)))
					j += CROP_SIZE
					continue
				filename = '{}_{}_{}_{}.png'.format(tile.split('/')[-3], 
					tile.split('/')[-1].split('.')[0], i, j)
				print(filename, 'will be added to masks and images')
				#print(img_arr)
				img_arr = Image.fromarray(np.uint8(img_arr))
				img_arr.save(os.path.join('mask', filename))
				tag_arr = file_array[:, i:i+CROP_SIZE, j:j+CROP_SIZE]
				#print(tag_arr.shape)
				tag_arr = np.ma.transpose(tag_arr, [1, 2, 0])
				tag_img = Image.fromarray(tag_arr.astype(np.uint8))
				tag_img.save(os.path.join(band, filename))

				j += CROP_SIZE
			i += CROP_SIZE
			j = 0


if __name__ == '__main__':

	#base_dir = '../research_indexes/WV'
	#base_dir = '../research_indexes/XA'
	#base_dir = '../research_indexes/XV'
	#base_dir = '../research_indexes/YV'
	base_dir = '../research_indexes/'
	shape_paths = [os.path.join('regions', os.listdir('regions')[i]) 
		for i in range(len(os.listdir('regions')))]
	geoms = get_geoms(shape_paths, crs=dst_crs)

	get_masks_n_imgs(base_dir, 'nrg', shape_paths, CROP_SIZE, geoms)
