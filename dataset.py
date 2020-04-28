import os
import numpy as np
from PIL import Image
from cut_images import *

class Dataset:
	"""
	Currently bands we use: B04, B08
	"""
	def __init__(self, mask_folder='mask',
				b04_folder='B04', b08_folder='B08',
				batch_size=16):

		self.mask_folder = mask_folder
		self.b04_folder = b04_folder
		self.b08_folder = b08_folder
		self.batch_size = batch_size

	def get_item(self, filename):
		filename = filename.split('.')[:-1]
		item = dict()
		item['b04'] = np.array(Image.open(os.path.join(self.b04_folder), 
			self.b04_folder))
		item['b08'] = np.array(Image.open(os.path.join(self.b08_folder), 
			self.b08_folder))
		item['mask'] = np.array(Image.open(os.path.join(self.b08_folder), 
			self.mask_folder))
		item['ndvi'] = get_nvdi(item['b04'], item['b08'])
		item['savi'] = get_savi(item['b04'], item['b08'])
		return item