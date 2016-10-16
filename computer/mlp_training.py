__author__ = 'zhengwang & paulyim'

import cv2
import numpy as np
import glob

print 'Loading training data...'
e0 = cv2.getTickCount()         # Returns the number of ticks after a certain event.

# load training data
image_array = np.zeros((1, 38400))
label_array = np.zeros((1, 4), 'float')
training_data = glob.glob('training_data/*.npz')        # Finds filenames matching specified path or pattern.
print "training_data (npz files that will be used): ", training_data

for single_npz in training_data:                        # single_npz == one npz file in the 'training_data' folder.
    with np.load(single_npz) as data:
        print data.files
        train_temp = data['train']                      # returns the training data array assigned to 'train' argument created during np.savez step in 'data_collection.py'
        train_labels_temp = data['train_labels']        # returns the training user input data array assigned to 'train_labels' argument created during np.savez step in 'data_collection.py'
        print train_temp.shape
        print train_labels_temp.shape
    image_array = np.vstack((image_array, train_temp))
    label_array = np.vstack((label_array, train_labels_temp))

train = image_array[1:, :]
train_labels = label_array[1:, :]

print ''
print 'Final shape of "train": ', train.shape
print 'Final shape of "train_labels": ', train_labels.shape

e00 = cv2.getTickCount()
time0 = (e00 - e0)/ cv2.getTickFrequency()      # Returns the number of ticks per second.
print 'Loading image duration:', time0

# set start time
e1 = cv2.getTickCount()

# create MLP
# layer_sizes = np.int32([38400, 32, 4])          # Input: 38400 nodes;  Hidden: 32 nodes;  Output: 4 nodes.
layer_sizes = np.array([38400, 32, 4], dtype=np.uint8)          # Input: 38400 nodes;  Hidden: 32 nodes;  Output: 4 nodes.


# DEPRECATED?
# model = cv2.ANN_MLP()
# model.create(layer_sizes)

## EXAMPLE
# ann = cv2.ml.ANN_MLP_create()
# ann.setLayerSizes(np.array([9, 5, 9], dtype=np.uint8))
# ann.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP)
#
# ann.train(np.array([[1.2, 1.3, 1.9, 2.2, 2.3, 2.9, 3.0, 3.2, 3.3]], dtype=np.float32),
#   cv2.ml.ROW_SAMPLE,
#   np.array([[0, 0, 0, 0, 0, 1, 0, 0, 0]], dtype=np.float32))
##


model = cv2.ml.ANN_MLP_create()
model.setLayerSizes(np.array([4, 32, 4], dtype=np.uint8) )
model.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP)

#
# criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 0.0001)       # Uses criteria count OR EPS ('Earnings per share'); either 500 iteration or move by atleast 0.0001 pt
# criteria2 = (cv2.TERM_CRITERIA_COUNT, 100, 0.001)                               # Uses criteria count ('Earnings per share'); either 100 iteration or move by atleast 0.001 pt
# params = dict(term_crit = criteria,
#                train_method = 'ANN_MLP_TRAIN_PARAMS_BACKPROP',                # Using BACKPROP (as opposed to RPROP, which is default).
#                bp_dw_scale = 0.001,                                             # alpha? Strength of the weight gradient term. The recommended value is about 0.1.
#                bp_moment_scale = 0.0 )                                          # Strength of the momentum term (the difference between weights on the 2 previous iterations). This parameter provides some inertia to smooth the random fluctuations of the weights. It can vary from 0 (the feature is disabled) to 1 and beyond. The value 0.1 or so is good enough
#

# train MLP
print 'Training MLP ...'
# num_iter = model.train(train, train_labels, params=params)              # 'None' param is for sampleIdx; Optional integer vector indicating the samples (rows of inputs and outputs) that are taken into account.
num_iter = model.train(train, cv2.ml.ROW_SAMPLE, train_labels)


# set end time
e2 = cv2.getTickCount()
time = (e2 - e1)/cv2.getTickFrequency()
print 'Training duration:', time

# save param
model.save('mlp_xml/mlp.xml')                       # Parameters of the trained model are saved as .xml

print 'Ran for %d iterations' % num_iter

ret, resp = model.predict(train)                    # 'ret' = The method returns a dummy value which should be ignored. 'resp' = The responses for input samples.

# Model evaluation on TRAINING set?
prediction = resp.argmax(-1)                        #''' # y_hats. Max likelihood response values (predictions). Should be an array? '''
print 'Prediction:', prediction
true_labels = train_labels.argmax(-1)               # y_actuals.
print 'True labels:', true_labels

print 'Evaluating model performance on training set...'
train_rate = np.mean(prediction == true_labels)
print 'Train rate: %f:' % (train_rate*100)
