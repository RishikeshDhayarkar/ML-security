# -*- coding: utf-8 -*-
"""final_code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1u85Sq7RjlfJCdSAiDxIE4hocjwV1xT34

Our approach is RAM intensive, so the input data should be less than 1000 images.
"""

import keras
import sys
import h5py
import numpy as np
from PIL import Image
import numpy as np
from collections import Counter
from statistics import mode,median
from sklearn.metrics import confusion_matrix

clean_data_filename = str(sys.argv[1])
model_filename = str(sys.argv[2])


def data_loader(filepath):
    data = h5py.File(filepath, 'r')
    x_data = np.array(data['data'])
    y_data = np.array(data['label'])
    x_data = x_data.transpose((0,2,3,1))
    return x_data, y_data

def data_preprocess(x_data):
    return x_data/255

bd_model = keras.models.load_model(model_filename)
# bd_model = keras.models.load_model(model_filename)

x, y_clean = data_loader(clean_data_filename)
# x, y_clean = data_loader(clean_data_filename)

bs = 100

all_x_cleans = []
for i in range((x.shape[0])//bs):
    all_x_cleans.append(data_preprocess(x[i*bs : i*bs + bs]))



all_x_cleans.append(x[(x.shape[0]//bs)*100:])    

X_clean = np.concatenate(all_x_cleans, axis=0)
X_clean.shape

"""<h2>First part</h2>"""

img_wt_1 = 0.50
img_wt_2 = 0.50
num_pert = 50
samples = 1000
samples_poisoned = 1000

"""Function for combining two images to generate perturbed images."""

import cv2
def combine(img1,img2):
    img1 = img1.astype('float32')
    img2 = img2.astype('float32')

    return cv2.addWeighted(img1, img_wt_1, img2, img_wt_2, 0)

def random_samples(X):
    return X[np.random.randint(0,len(X))]

data = X_clean[0:samples]

combined_five = []

for x in data:
    rand_idx = []
    for i in range(num_pert):
        rand_idx.append(np.random.randint(0, len(X_clean)))

    for idx in rand_idx:
        combined_five.append(combine(x, X_clean[idx]))

all_outs = []
bs = 100

for i in range(0,int(len(combined_five)/bs)):
    combined_five_np = np.array(combined_five[i*bs:i*bs + bs])
    all_outs.append(bd_model(combined_five_np))

res_max = np.concatenate(all_outs, axis=0 )
res_max_argmax = np.argmax(res_max, axis=1)

k = []
for i in range(samples):
    k.append(Counter(res_max_argmax[i*num_pert:(i+1)*num_pert]))


a = []
for i in k:
    max_res = 0
    for key in i:
        max_res = max(max_res, i[key])
    a.append(max_res)

p = np.percentile(a,96)

"""<h2>second part</h2>

"""

# To our program, we created a test dataset of size 2000 with 1000 clean and poisoned data each. Replace data with your own dataset

# data = np.concatenate((X_clean[:samples],X_poison[:samples_poisoned]))
data = cv2.imread(str(sys.argv[3]))

# labels = np.concatenate((np.ones(samples),np.zeros(samples_poisoned)))  # 1 if clean, 0 if poisoned

# Actual labels with N+1 class
# temp = 1283*np.ones(samples_poisoned)
# true_labels = np.concatenate((y_clean[:samples],temp))



combined_five = []

# for x in data:
#     rand_idx = []
#     for i in range(num_pert):
#         rand_idx.append(np.random.randint(0, len(X_clean)))    

#     for idx in rand_idx:
#         combined_five.append(combine(x, X_clean[idx]))


rand_idx = []
for i in range(num_pert):
    rand_idx.append(np.random.randint(0, len(X_clean)))    

for idx in rand_idx:
    combined_five.append(combine(data, X_clean[idx]))

all_outs = []
bs = 10

combined_five_np = np.array(combined_five)

all_outs = bd_model(combined_five_np)
# res_max = np.concatenate(all_outs, axis=0 )
res_max_argmax = np.argmax(bd_model(combined_five_np), axis=1)

k = []
for i in range(len(data)):
    k.append(Counter(res_max_argmax[i*num_pert:(i+1)*num_pert]))


a = []
for i in k:
    max_res = 0
    for key in i:
        max_res = max(max_res, i[key])
    a.append(max_res)  

# for i in range((len(data))):
if a[0] > p:
    y_pred = 0
else:
    y_pred = 1

# print(y_pred)
# print(a[0])
# print(p)    


data = np.expand_dims(data, axis=0)
y_pred_actual = np.argmax(bd_model(data), axis=1)
if y_pred == 0:
    y_pred_actual=1283

print("Image label - ")
print(y_pred_actual)    

# temp = 0
# for i in range(len(data)):
#     if labels[i] == y_pred[i]:
#             temp += 1

# print(temp/(len(data)))

# Accuracy for classifying inputs into poisoned and clean classes
# conf = confusion_matrix(labels,y_pred)
# print(conf)

# y_pred_actual = np.argmax(bd_model(data),axis=1)

# for i in range(len(data)):
#     if y_pred[i] == 0:
#         y_pred_actual[i] = 1283 

# temp = 0
# for i in range(len(data)):
#     if true_labels[i] == y_pred_actual[i]:
#             temp += 1

# # Accuracy for classifying inputs into all seperate clean classes(classes 0 to 1282) and poisoned inputs(class 1283)
# print("Accuracy = ")
# print(temp/(len(data)))

# """FAR - False acceptance rate

# FRR - False rejection rate

# As we vary percentile from 95 to 99, FRR increases and FAR decreases. 
# """

# FRR = conf[0][1]/(conf[0][0] + conf[0][1])
# FAR = conf[1][0]/(conf[1][1] + conf[1][0])
# print(f'FRR = {FRR*100}%, FAR = {FAR*100}%')

# # print(y_pred)
# print(y_pred_actual)

