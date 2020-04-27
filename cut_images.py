import os
import numpy as np
import rasterio as rio
import rasterio.plot as rioplot
import rasterio.mask as riomask
import geopandas as gpd
from PIL import Image

dst_crs = 'EPSG:32636'
CROP_SIZE = 244

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
			#print(i, j)
			img_arr = np.array(img_arr, dtype='uint8')
			img_arr = Image.fromarray(img_arr)
			img_arr.save(os.path.join('mask', f'{filename}_{i}_{j}.png'))
			j += CROP_SIZE
		i += CROP_SIZE
		j=0
		#print(i, mask_arr.shape[0])

	#return mask

def save_divided_imgs(image, filename, CROP_SIZE=CROP_SIZE):
	"""
	image should be an array of size
	(channels, height, width)
	"""
	i=0
	j=0
	img_arr = []
	image = image.read()
	# TODO: actual grid
	while i < image.shape[1]:
		while j < image.shape[2]:
			img_arr = []
			"""
			for channel in range(image.shape[0]):
				img_arr.append(image[channel, i:i+CROP_SIZE, j:j+CROP_SIZE])
				print(np.array(img_arr[channel]))
				img = Image.fromarray(np.array(img_arr[channel]))
				img.save(os.path.join('true', f'{i}_{j}_{channel}.png'))
			"""
			print(np.array(img_arr).shape)
			img_arr = np.array(img_arr)
			img_arr = Image.fromarray(np.ma.transpose(img_arr, [1, 2, 0]))
			img_arr.save(os.path.join('true', f'{filename}_{i}_{j}.png'))
			j += CROP_SIZE
		i += CROP_SIZE
		j=0

def get_geoms(shape_paths, crs=dst_crs):

	geoms = []
	for file in shape_paths:
		p = gpd.read_file(file).to_crs(crs)
		for shape in p.geometry:
			geoms.append(shape)
	return geoms

def write_nvdi(red, nir, save=False, meta=None):

	red = red.read()
	nir = nir.read()
	print(red.shape, nir.shape)
	ndvi = (nir.astype(float)-red.astype(float))/(nir+red)
	ndvi = ndvi*255
	ndvi = np.nan_to_num(ndvi, nan=-999)
	ndvi = ndvi.astype(rio.float32)

	if save:
		meta.update(driver='GTiff')
		meta.update(dtype=rio.float32)
		with rio.open('NDVI.tif', 'w', **meta) as dst:
			dst.write(ndvi.astype(rio.float32))


	return ndvi


if __name__ == '__main__':

	full_map = rio.open('T36UYV_TCI_10m.jp2', driver='JP2OpenJPEG')
	red = rio.open('T36UXA_B04_10m.jp2', driver='JP2OpenJPEG')
	nir = rio.open('T36UXA_B08_10m.jp2', driver='JP2OpenJPEG')
	meta = red.meta
	print(write_nvdi(red, nir, True, meta))
	exit()
	shape_paths = [os.path.join('regions', os.listdir('regions')[i]) 
		for i in range(len(os.listdir('regions')))]
	geoms = get_geoms(shape_paths, crs=full_map.profile['crs'])
	print(geoms)
	overlap_mask(geoms, filename='T36UYV_TCI_10m.jp2'.split('.')[0],
		profile=full_map.profile, tiff_map=full_map)
	save_divided_imgs(full_map, filename='T36UYV_TCI_10m.jp2'.split('.')[0])
