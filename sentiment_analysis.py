# -*- coding: utf-8 -*-
"""Sentiment Analysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/175vULnl12pAHpZv52WopOmo1jtoHMLWB
"""

!pip install kaggle

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d kazanova/sentiment140

from zipfile import ZipFile
file_name = "/content/sentiment140.zip"

with ZipFile(file_name, 'r') as zip:
  zip.extractall()
  print('done')

import numpy as np
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import pickle

nltk.download('stopwords')

dataset_path = '/content/training.1600000.processed.noemoticon.csv'
df = pd.read_csv(dataset_path, encoding='latin-1', header=None)

dataset_path = '/content/training.1600000.processed.noemoticon.csv'
# Specify the delimiter, it's likely a comma or a tab
df = pd.read_csv(dataset_path, encoding='latin-1', header=None, delimiter=',') # Try delimiter='\t' if comma doesn't work

df.columns = ['target', 'id', 'date', 'flag', 'user', 'text']

df['label'] = df['target'].map({0: 0, 2: 1, 4: 2})

df.head()

df['label'].value_counts()

# Drop unnecessary columns
df = df[['text', 'label']]

def stemming (content):
  port_stem = PorterStemmer()
  stemmed_content = re.sub('[^a-zA-Z]', ' ', content)
  stemmed_content = stemmed_content.lower()
  stemmed_content = stemmed_content.split()
  stemmed_content = [port_stem.stem(word) for word in stemmed_content if word not in stopwords.words('english')]
  return ' '.join(stemmed_content)

df['text'] = df['text'].apply(stemming)

df.head()

X=df['text'].values
y=df['label'].values

X_train,X_test,Y_train,Y_test=train_test_split(X,y,test_size=0.2,stratify=y,random_state=2)

vectorizer = TfidfVectorizer()
vectorizer.fit_transform(X_train)
X_train = vectorizer.transform(X_train)
X_test = vectorizer.transform(X_test)

"""****Train Machine Learning Model1****"""

model=LogisticRegression(max_iter=10000)
model.fit(X_train,Y_train)

X_train_prediction=model.predict(X_train)
training_data_accuracy=accuracy_score(X_train_prediction,Y_train)

X_test_prediction=model.predict(X_test)
test_data_accuracy=accuracy_score(X_test_prediction,Y_test)

print('Accuracy score of the training data : ', training_data_accuracy)

print('Accuracy score of the test data : ', test_data_accuracy)

from sklearn.metrics import classification_report
print(classification_report(Y_test, X_test_prediction))

model2=MultinomialNB()
model2.fit(X_train,Y_train)

#Training Data
X_train_prediction=model2.predict(X_train)
training_data_accuracy=accuracy_score(X_train_prediction,Y_train)
print('Accuracy score of the training data : ', training_data_accuracy)

#Testing Data
X_test_prediction=model2.predict(X_test)
test_data_accuracy=accuracy_score(X_test_prediction,Y_test)
print('Accuracy score of the test data : ', test_data_accuracy)

import pickle
pickle.dump(model, open('model.pkl', 'wb'))
pickle.dump(vectorizer, open('vectorizer.sav', 'wb'))

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import numpy as np

Y_test_predictions = model.predict(X_test)

cm = confusion_matrix(Y_test, Y_test_predictions)

unique_classes = np.unique(np.concatenate((Y_test, Y_test_predictions)))

display_labels = ["Negative", "Neutral", "Positive"]

display_labels = [display_labels[i] for i in unique_classes]

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=display_labels)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix for Logistic Regression")
plt.show()

model = pickle.load(open('model.pkl', 'rb'))

vectorizer = pickle.load(open('vectorizer.sav', 'rb'))

def predict_sentiment(text):
    processed_text = stemming(text)
    vectorized_text = vectorizer.transform([processed_text])
    prediction = model.predict(vectorized_text)[0]
    return prediction

custom_text = "This is a movie!"
sentiment = predict_sentiment(custom_text)
if sentiment == 0:
    print("Negative sentiment")
elif sentiment == 1:
    print("Neutral sentiment")
else:
    print("Positive sentiment")