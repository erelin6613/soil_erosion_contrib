import os
import numpy as np
import rasterio as rio
import rasterio.plot as rioplot
import rasterio.mask as riomask
from rasterio.windows import Window
import geopandas as gpd
from PIL import Image
from shapely.ops import cascaded_union

dst_crs = 'EPSG:32636'
CROP_SIZE = 244
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
		#print(i, j)
		while j < mask_arr.shape[1]:
			img_arr = mask_arr[i:i+CROP_SIZE, j:j+CROP_SIZE]
			if np.argmax(img_arr.ravel()) == 0:
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


def get_masks_n_imgs(base_dir, band, 
					shapes=[MASK_FILE], CROP_SIZE=CROP_SIZE):
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
	for d in os.walk(base_dir):
		if len(d[2]) > 0:
			l=[i for i in d[2] if '_'+str(band) in i]
			if len(l) > 0:
				tiles.append(os.path.join(d[0], l[0]))
	
	for tile in tiles:
		i=j=0
		try:
			assert tile.split('.')[-1] == 'jp2'
			file = rio.open(tile, driver='JP2OpenJPEG')
		except NotImplementedError:
			raise NotImplementedError('Tif files are not appropriate for this task \
				since the dimationality might be scewed. Use .jp2 file instead')
			return
		print('Getting shapes...')
		geoms = get_geoms(shapes, crs=file.profile['crs'])
		transform, crs = file.profile['transform'], file.profile['crs']
		
		while i < file.read().shape[1]:
			while j < file.read().shape[2]:
				filename = '{}_{}_{}_{}.jp2'.format(tile.split('/')[-3], 
					tile.split('/')[-1], i, j)
				file_window = file.read(window=Window(0, 0, width=244, height=244))
				mask_arr, mask_transform, window = riomask.raster_geometry_mask(file, geoms, invert=True)
				img_arr = mask_arr[i:i+CROP_SIZE, j:j+CROP_SIZE]*1
				if np.argmax(img_arr.ravel()) == 0:
					j += CROP_SIZE
					print('No overlaping masks found in tile {}'
						.format((i, i+CROP_SIZE, j, j+CROP_SIZE)))
					continue
				print(filename, 'will be added to masks and images')
				with rio.open(os.path.join('true', filename), 'w', **file.profile) as f:
					f.write(file.read(window=Window(i, j, width=CROP_SIZE, height=CROP_SIZE))) #.astype(rio.float32)) #, window=Window(0, 0, 244, 244))
				
				with rio.open(os.path.join('mask', filename), 'w', **file.profile) as dst:
					dst.meta['max'] = 1
					dst.meta['min'] = 0
					dst.write(mask_arr)
				j += CROP_SIZE
			i += CROP_SIZE


if __name__ == '__main__':

	base_dir = '../research_indexes/'
	get_masks_n_imgs(base_dir, 'nrg')
