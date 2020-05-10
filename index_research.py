import os
import numpy as np
import rasterio as rio
import rasterio.plot as rioplot
import rasterio.mask as riomask
import geopandas as gpd
from PIL import Image
import earthpy.spatial as es

BASE_DIR = os.getcwd()

DATES_DIRS = ['20190427T083601',
				'20190527T083601']

STACKING_INDEXES = {
	'swir': ['B12', 'B8A', 'B4'],
	'geology': ['B12', 'B11', 'B02'],
	'agriculture': ['B11', 'B8A', 'B02'],
	'false_color': ['B8A', 'B04', 'B03']
}

STACKING_INDEXES_10m = {
	'nrg': ['B08', 'B04', 'B03']
}


def stack_layer(directory, bands, name):
	files = []
	for d in os.listdir(directory):
		try:
			if d.split('_')[-2] in bands:
				files.append(os.path.join(directory, d))
		except Exception as e:
			print('Preparing layer', name, '...')

	array, raster_prof = es.stack(files)
	print(array, raster_prof)
	raster_prof.update(driver='GTiff')
	raster_prof.update(dtype=rio.float32)
	with rio.open(directory.split('/')[1]+'_'+name+'.tif', 'w', **raster_prof) as dst:
		dst.meta['nodata'] = -999
		dst.write(array.astype(rio.float32))
	print(directory.split('/')[1]+'_'+name+'.tif')

def get_nvdi(red_file, nir_file, 
	save=True, outname='NDVI'):
	if red_file.endswith('.jp2') and nir_file.endswith('.jp2'):

		red = rio.open(red_file, driver='JP2OpenJPEG')
		nir = rio.open(nir_file, driver='JP2OpenJPEG')
	elif (red_file.endswith('.tif') and nir_file.endswith('.tif')) or \
	(red_file.endswith('.tiff') and nir_file.endswith('.tiff')):
		red = rio.open(red_file, driver='GTiff')
		nir = rio.open(nir_file, driver='GTiff')
	else:
		raise Exception('Bands images must be of the same format')
	meta = red.meta
	red = red.read()
	nir = nir.read()
	ndvi = (nir.astype(float)-red.astype(float))/(nir+red)
	ndvi = ndvi.astype(rio.float32)

	if save:
		ndvi = ndvi
		meta.update(driver='GTiff')
		meta.update(dtype=rio.float32)
		with rio.open(outname+'.tif', 'w', **meta) as dst:
			dst.meta['nodata'] = -999
			dst.meta['max'] = 1
			dst.meta['min'] = 0
			dst.write(ndvi.astype(rio.float32))


	return np.nan_to_num(ndvi, nan=-999)


def get_savi(red_file, nir_file, L=0.5,
	save=True, outname='NDVI'):

	if red_file.endswith('.jp2') and nir_file.endswith('.jp2'):

		red = rio.open(red_file, driver='JP2OpenJPEG')
		nir = rio.open(nir_file, driver='JP2OpenJPEG')
	elif (red_file.endswith('.tif') and nir_file.endswith('.tif')) or \
	(red_file.endswith('.tiff') and nir_file.endswith('.tiff')):
		red = rio.open(red_file, driver='GTiff')
		nir = rio.open(nir_file, driver='GTiff')
	else:
		raise Exception('Bands images must be of the same format')
	meta = red.meta
	red = red.read()
	nir = nir.read()
	L = np.full(red.shape, L)
	savi = ((1+L)*(nir.astype(float)-red.astype(float)))/(nir+red+L)
	savi = savi.astype(rio.float32)

	if save:
		savi = savi
		meta.update(driver='GTiff')
		meta.update(dtype=rio.float32)
		with rio.open(outname+'.tif', 'w', **meta) as dst:
			dst.meta['nodata'] = -999
			dst.meta['max'] = 1
			dst.meta['min'] = 0
			dst.write(savi.astype(rio.float32))


	return np.nan_to_num(savi, nan=-999)


def get_mi(b8a_file, b11_file,
	save=True, outname='MI'):

	if b8a_file.endswith('.jp2') and b11_file.endswith('.jp2'):

		b8a = rio.open(b8a_file, driver='JP2OpenJPEG')
		b11 = rio.open(b11_file, driver='JP2OpenJPEG')
	elif (b8a_file.endswith('.tif') and b11_file.endswith('.tif')) or \
	(b8a_file.endswith('.tiff') and b11_file.endswith('.tiff')):
		b8a = rio.open(b8a_file, driver='GTiff')
		b11 = rio.open(b11_file, driver='GTiff')
	else:
		raise Exception('Bands images must be of the same format')
	meta = b8a.meta
	b8a = b8a.read()
	b11 = b11.read()
	mi = ((b8a.astype(float)-b11.astype(float)))/(b8a+b11)
	mi = mi.astype(rio.float32)

	if save:
		mi = mi
		meta.update(driver='GTiff')
		meta.update(dtype=rio.float32)
		with rio.open(outname+'.tif', 'w', **meta) as dst:
			dst.meta['nodata'] = -999
			dst.meta['max'] = 1
			dst.meta['min'] = 0
			dst.write(mi.astype(rio.float32))


	return np.nan_to_num(mi, nan=-999)

def get_metrics(DATES_DIRS=DATES_DIRS):

	for directory in DATES_DIRS:
		for ind in STACKING_INDEXES.keys():
			stack_layer('../'+directory, STACKING_INDEXES[ind], ind)
		for ind in STACKING_INDEXES_10m.keys():
			stack_layer('../'+directory+'/10m', STACKING_INDEXES_10m[ind], ind)
		for each in os.listdir('../'+directory+'/10m'):
			if 'B04' in each.split('_'):
				red = os.path.join('../'+directory+'/10m/'+each)
			if 'B08' in each.split('_'):
				nir = os.path.join('../'+directory+'/10m/'+each)
			if 'B03' in each.split('_'):
				b03 = each
			if 'B02' in each.split('_'):
				b02 = each
		get_nvdi(red, nir, True, directory+'_ndvi')
		get_savi(red, nir, 0.5, True, directory+'_savi')


if __name__ == '__main__':

	for directory in DATES_DIRS:
		stack_layer(directory,
			STACKING_INDEXES_10m['nrg'],
			'nrg')