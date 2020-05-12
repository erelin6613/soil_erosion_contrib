import os
import numpy as np
import rasterio as rio
import rasterio.plot as rioplot
import rasterio.mask as riomask
import geopandas as gpd
from PIL import Image
import earthpy.spatial as es
from tqdm import tqdm

BASE_DIR = os.getcwd()
DEFAULT_CRS = 'EPSG:32636'

DATES_DIRS = ['WV/20190427T083601',
				'WV/20190527T083601',
				'XA/20190427T083601',
				'XA/20190527T110449',
				'XV/20190427T083601',
				'XV/20190527T083601',
				'YA/20190427T083601',
				'YA/20190527T083601',
				'YV/20190427T083601',
				'YV/20190527T083601']

STACKING_INDEXES = {
	'swir': ['B12', 'B8A', 'B4'],
	'geology': ['B12', 'B11', 'B02'],
	'agriculture': ['B11', 'B8A', 'B02'],
	'false_color': ['B8A', 'B04', 'B03']
}

STACKING_INDEXES_10m = {
	'nrg': ['B08', 'B04', 'B03']
}


def stack_layer(directory, bands, name, 
	scale=False):
	print(directory)
	exit()
	files = []
	for d in os.listdir(directory):
		try:
			if d.split('_')[-2] in bands:
				files.append(os.path.join(directory, d))
		except Exception as e:
			print('Preparing layer', name, '...')
	try:
		array, raster_prof = es.stack(files)
	except Exception:
		print('Converting to common CRS')
	#print(array, raster_prof)
	raster_prof.update(driver='GTiff')
	raster_prof.update(dtype=rio.float32)
	f_name = directory.split('/')[-2]+'_'+directory.split('/')[-1]+'_'+name+'.tif'
	f_name = f_name.replace('B02_10m', 'b2')
	f_name = f_name.replace('B03_10m', 'b3')
	f_name = f_name.replace('B04_10m', 'b4')
	f_name = f_name.replace('B08_10m', 'b8')
	with rio.open(f_name, 'w', **raster_prof) as dst:
		dst.meta['nodata'] = -999
		dst.write(array.astype(rio.float32))
	if scale:
		scale_img(f_name)

def get_nvdi(red_file, nir_file, 
	save=True, outname='NDVI'):
	if red_file.endswith('.jp2') and nir_file.endswith('.jp2'):
		print('Converting to tif')
		# red = rio.open(red_file, driver='JP2OpenJPEG')
		# nir = rio.open(nir_file, driver='JP2OpenJPEG')
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
		try:
			scale_img(outname+'.tif', min_value=0, max_value=255, output_type='Byte')
		except Exception as e:
			print(e)


	return np.nan_to_num(ndvi, nan=-999)


def get_savi(red_file, nir_file, L=0.5,
	save=True, outname='SAVI'):

	if red_file.endswith('.jp2') and nir_file.endswith('.jp2'):
		print('Converting to tif')
		# red = rio.open(red_file, driver='JP2OpenJPEG')
		# nir = rio.open(nir_file, driver='JP2OpenJPEG')
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
		try:
			scale_img(outname+'.tif', min_value=0, max_value=255, output_type='Byte')
		except Exception as e:
			print(e)


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
		get_nvdi(red, nir, True, directory.split('/')[0]+'_'+directory.split('/')[1]+'_ndvi'+'.tif')
		get_savi(red, nir, 0.5, True, directory.split('/')[0]+'_'+directory.split('/')[1]+'_savi'+'.tif')

def merge(save_path, *images):
	os.system(f'gdal_merge.py -separate -o {save_path} {" ".join(images)}')

def scale_img(img_file, min_value=0, max_value=255, output_type='Byte'):
	with rio.open(img_file) as src:
		img = src.read(1)
		img = np.nan_to_num(img)
		mean_ = img.mean()
		std_ = img.std()
		min_ = max(img.min(), mean_ - 2 * std_)
		max_ = min(img.max(), mean_ + 2 * std_)
		os.system(
			f"gdal_translate -ot {output_type} \
			-scale {min_} {max_} {min_value} {max_value} \
			{img_file} {f'{os.path.splitext(img_file)[0]}_scaled.tif'}"
			)

def convert_to_tif(dates_dirs=DATES_DIRS):

	for each in dates_dirs:
		for file in os.listdir('../'+each+'/10m'):
			img_path = os.path.join('../'+each+'/10m', file)
			if img_path.endswith('.jp2'):
				geo_path = img_path.replace('.jp2', '.tif')
				print('Converting to tif')
				os.system(f'gdalwarp -of GTiff -overwrite -ot Byte -t_srs EPSG:4326 ' \
					f'-wm 4096 -multi -wo NUM_THREADS=ALL_CPUS ' \
					f'-co COMPRESS=DEFLATE -co PREDICTOR=2 {img_path} {geo_path}')
				os.system(f'rm {img_path}')

if __name__ == '__main__':
	for directory in tqdm(DATES_DIRS):
		for file in os.listdir(os.path.join('..', directory)):
			if '10m' in file and file.endswith('.tif'):
				#print(os.path.join('..', directory, file))
				if 'B04' in file.split('_'):
					red = os.path.join('..', directory, file)
				if 'B08' in file.split('_'):
					nir = os.path.join('..', directory, file)
				if 'B03' in file.split('_'):
					b03 = os.path.join('..', directory, file)
		#print(red, nir, b03)
		scale_img(b03)
		#print(directory)
		nvdi_name = directory.replace('/', '_')+'_ndvi'
		savi_name = directory.replace('/', '_')+'_savi'
		get_nvdi(red, nir, True, nvdi_name)
		get_savi(red, nir, savi_name)