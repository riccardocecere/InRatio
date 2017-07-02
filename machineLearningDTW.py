import numpy 
import scipy
import os
import pickle
from matplotlib import pyplot as plt
from scipy.sparse import csr_matrix

from sklearn import linear_model
from sklearn import model_selection
from sklearn import metrics

import errno
import re
import DTW


def compare(image1,image2):
  return DTW.compare(image1,image2)

def training(directory):
  X, y= get_instances_from_directory(directory)
  # Split the data and the targets into training/testing sets
  X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size = 0.1, random_state = 0)
  regr = linear_model.LogisticRegression(class_weight='balanced')
  #X_train = numpy.array(X_train,dtype=numpy.float64)
  regr.fit(X_train,y_train)
  y_predicted = regr.predict(X_test)

  cm = metrics.confusion_matrix(y_test, y_predicted)

  cwd = os.getcwd()
  directory_save=cwd+'\saves'
  filename = 'finalized_model.sav'
  if not os.path.exists(os.path.dirname(directory_save+'\\finalized_model.sav')):
      try:
          os.makedirs(os.path.dirname(directory))
          open(directory_save+'\\'+filename, 'wb')
      except OSError as exc: # Guard against race condition
          if exc.errno != errno.EEXIST:
              raise

  pickle.dump(regr, open(filename, 'wb'))

  print(metrics.classification_report(y_test, y_predicted, target_names = ['n','y']))
    
  
def get_instances_from_directory(directory):
  #inizializeResultsTxt(directory)
  os.chdir(directory)
  X = []
  y = []
  with open("listOfResults.txt","r") as results:
    lines = results.readlines()
    for line in lines:
      if line!="":
        fields = line.split()
        directory1=os.path.join(directory+"\imagewords", fields[0])
        directory2=os.path.join(directory+"\imageWords", fields[1])
        X.append(compare(directory1, directory2))
        y.append(fields[2]) 
  with open("listOfGoodPairs.txt","r") as results:
    lines = results.readlines()
    for line in lines:
      if line!="":
        fields = line.split()
        directory1=os.path.join(directory+"\goodPairs", fields[0])
        directory2=os.path.join(directory+"\goodPairs", fields[1])
        X.append(compare(directory1, directory2))
        y.append(fields[2]) 
  #A = csr_matrix(X, shape=(len(X),len(X[0])),dtype=numpy.float64)
  return X, y

def predict_result(directory1, directory2):
  # directory1=os.path.dirname(directory1)
  # directory2=os.path.dirname(directory2)
  cwd = os.getcwd()
  # directory_save=cwd+'\saves'
  # os.chdir(directory_save)
  with open('finalized_model.sav', 'rb') as file:
    vector= []
    loaded_model = pickle.load(file)
    print loaded_model.coef_
    vector.append(compare(directory1, directory2))
    #vector.append(compare(directory2, directory1))
    result = loaded_model.predict(vector)
    return result, vector

if __name__=='__main__':
  cwd = os.getcwd()
  training(cwd+'\saves')