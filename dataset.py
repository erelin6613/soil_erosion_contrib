import os
import numpy as np
from PIL import Image
from cut_images import *

class Dataset:
	"""
	Currently bands we use: nrg layer
	"""
	def __init__(self, mask_folder='mask',
				train_folder='nrg'):

		self.mask_folder = mask_folder
		self.train_folder = train_folder

	def get_item(self, filename):
		#filename = filename.split('.')[:-1]
		path_img = os.path.join(self.train_folder, 
			filename)
		path_mask = os.path.join(self.mask_folder, 
			filename)
		image = np.array(Image.open(path_img))/255
		mask = np.array(Image.open(path_mask))/255
		return (image, mask)

	def get_masks_paths(self):
		print(os.walk(self.mask_folder))
		return os.listdir(self.mask_folder)

	def get_images_paths(self):
		return os.listdir(self.train_folder)