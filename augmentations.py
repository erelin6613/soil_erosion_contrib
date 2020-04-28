import os
import numpy as np
import torchvision.transforms as transforms
from PIL import Image
from cut_images import CROP_SIZE


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

img_path = 'T36UYV_TCI_10m_0_9272.png'
save_new_image('', img_path)