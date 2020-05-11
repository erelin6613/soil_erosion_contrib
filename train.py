# from model import SegNet, ModSegNet
from dataset import Dataset
from tqdm import tqdm
import numpy as np
from torch import Tensor, from_numpy
from torch.optim import Adam
import torch.nn.functional as F
from pytorch_unet_segnet.segnet import SegNet
from pytorch_unet_segnet.modsegnet import ModSegNet

LOSS = 'binary_crossentropy'
OPTIMIZER = 'Adam'
EPOCHS = 100
BATCH_SIZE = 4

def train(model, X, y, epochs=EPOCHS, lr=0.01, batch_size=BATCH_SIZE):

	optimizer = Adam(model.parameters(), lr=lr)
	model.train()
	for epoch in range(EPOCHS):
		loss = 0

	    for i in tqdm(range(0, len(X), batch_size)):
	        optimizer.zero_grad()


	        batch_x = np.array(X[i:i+batch_size])
	        batch_y = np.array(y[i:i+batch_size])
	        batch_x = from_numpy(batch_x).float()
	        batch_y = from_numpy(batch_y).float()

	        outputs = model.forward(batch_x)
	        loss += F.mse_loss(outputs, batch_y)
	        #print(loss)
	        loss.backward()
	        optimizer.step()
	    print('epoch:', epoch, 'loss:', loss)

	
def test(model):

	model.eval()
	for sample in test:
		X, y = sample[0], sample[1]
		output = model(X)

model = ModSegNet(num_classes=1)
model = model.float()

print('Loading images...')
dataset = Dataset()
X = []
y = []
for i in tqdm(dataset.get_images_paths()[:100]):
	X.append(np.ma.transpose(dataset.get_item(i)[0], [2, 0, 1]))
	y.append(dataset.get_item(i)[1].T)

#print(X[0])
train(model, X, y, 1)
