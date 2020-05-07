import os
import numpy as np
import pandas as pd
import torchvision.transforms as transforms
from PIL import Image
import albumentations as alb
from random import shuffle
# CLAHE, RandomRotate90, Flip, OneOf, Compose, RGBShift, RandomSizedCrop
from cut_images import CROP_SIZE
from tqdm import tqdm

DIR = 'nrg'
MASK_DIR = 'mask'
OUT_DIR = 'input'
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

def annotate_n_augment(paths, DIR=DIR, MASK_DIR=MASK_DIR):

	df = pd.DataFrame(columns=['dataset_folder',
		'name','position']) #,'mask_pxl'])

	for file in tqdm(paths):

		d = dict()
		# print(file)

		original_img = Image.open(os.path.join(DIR, file))
		mask_img = Image.open(os.path.join(MASK_DIR, file))
		original_array = np.asarray(original_img)
		mask_array = np.asarray(mask_img)
		new_dir = file.split('_nrg')[0]
		d['dataset_folder'] = new_dir
		fn = file.split('.')[0]
		d['name'] = fn.split('_nrg')[0]
		os.system(f'mkdir -p {OUT_DIR}/{new_dir}')
		os.system(f'mkdir -p {OUT_DIR}/{new_dir}/images')
		os.system(f'mkdir -p {OUT_DIR}/{new_dir}/masks')
		positions = np.asarray(np.column_stack(np.ma.where(mask_array != 0)))
		for pos in positions:
			d['position'] = str(pos[0])+'_'+str(pos[1])
			#print(d)
			df = df.append(d, ignore_index=True)
		original_img.save(os.path.join(OUT_DIR, new_dir,
			'images', fn+'.png'))
		mask_img.save(os.path.join(OUT_DIR, new_dir,
			'masks', fn+'.png'))		

		
	return df

# img_path = 'T36UYV_TCI_10m_0_9272.png'
# save_new_image('', img_path)

all_paths = list(os.listdir(DIR))
shuffle(all_paths)
train_ind= int(len(all_paths)*TRAIN_SIZE)
test_ind = int(len(all_paths)*TEST_SIZE)
val_ind = len(all_paths) - train_ind - test_ind
train_set = all_paths[:train_ind]
test_set = all_paths[train_ind:(len(all_paths)-val_ind)]
val_set = all_paths[-val_ind:]

annotate_n_augment(train_set).to_csv(os.path.join(OUT_DIR, 'train_df.csv'))
annotate_n_augment(test_set).to_csv(os.path.join(OUT_DIR, 'test_df.csv'))
annotate_n_augment(val_set).to_csv(os.path.join(OUT_DIR, 'val_df.csv'))