import os
import numpy as np
import pandas as pd
import torchvision.transforms as transforms
from PIL import Image
import albumentations as alb
from random import shuffle
from tqdm import tqdm

DIR = 'nrg'
MASK_DIR = 'mask'
OUT_DIR = 'data/input'
TRAIN_SIZE = 0.7
TEST_SIZE = 0.2
VAL_SIZE = 0.1

def albumentations_transform(image):

	augment = alb.Compose[Compose([
            RandomRotate90(),
            Flip(),
            OneOf([
                RandomSizedCrop(
                    min_max_height=(int(self.image_size * 0.7), self.image_size),
                    height=self.image_size, width=self.image_size)
            ], p=0.4),
            CLAHE(clip_limit=2),
            ToTensor()
        ])]

	return augment(image)


def generate_transforms(image):

	transform = transforms.Compose([
		transforms.ToPILImage(),
		transforms.Resize((CROP_SIZE, CROP_SIZE)),
		transforms.RandomHorizontalFlip(p=0.5),
		transforms.RandomRotation(degrees=(-180, 180)),
		transforms.RandomVerticalFlip(p=0.5)])

	return transform(image)

def save_new_image(folder, filename):
	path = os.path.join(folder, filename)
	image = generate_transforms(np.array(Image.open(img_path)))
	image.save(os.path.join(folder, 'transformed_'+filename))

def annotate(paths, DIR=DIR, MASK_DIR=MASK_DIR):

	df = pd.DataFrame(columns=['dataset_folder',
		'name','position', 'mask_pxl'])

	for file in tqdm(paths):

		d = dict()

		original_img = Image.open(os.path.join(DIR, file))
		mask_img = Image.open(os.path.join(MASK_DIR, file))
		original_array = np.asarray(original_img)
		mask_array = np.asarray(mask_img)
		new_dir = file.split('_')[0]+'_'+file.split('_')[1]+f'_{DIR}'
		d['dataset_folder'] = new_dir
		fn = file.split('.')[0]
		d['name'] = new_dir
		os.system(f'mkdir -p {OUT_DIR}/{new_dir}')
		os.system(f'mkdir -p {OUT_DIR}/{new_dir}/images')
		os.system(f'mkdir -p {OUT_DIR}/{new_dir}/masks')
		d['position'] = fn.split('_')[-2]+'_'+fn.split('_')[-1]
		d['mask_pxl'] = np.count_nonzero(mask_array)
		df = df.append(d, ignore_index=True)
		#original_img.save(os.path.join(OUT_DIR, new_dir,
		#	'images', fn+'.png'))
		#mask_img.save(os.path.join(OUT_DIR, new_dir,
		#	'masks', fn+'.png'))
		os.system('mv {} {}'.format(os.path.join(DIR, file), 
			OUT_DIR, new_dir, 'images', fn+'.png'))
		os.system('mv {} {}'.format(os.path.join(DIR, file), 
			OUT_DIR, new_dir, 'masks', fn+'.png'))

	return df

def make sets():
	all_paths = list(os.listdir(DIR))
	shuffle(all_paths)
	train_ind= int(len(all_paths)*TRAIN_SIZE)
	test_ind = int(len(all_paths)*TEST_SIZE)
	val_ind = len(all_paths) - train_ind - test_ind
	train_set = all_paths[:train_ind]
	test_set = all_paths[train_ind:(len(all_paths)-val_ind)]
	val_set = all_paths[-val_ind:]

	print('Getting data together...')
	annotate(train_set).to_csv('train_df.csv')
	print('Train set has been written')
	annotate(test_set).to_csv('test_df.csv')
	print('Test set has been written')
	annotate(val_set).to_csv(os.path.join('val_df.csv')
	print('Validation set has been written')