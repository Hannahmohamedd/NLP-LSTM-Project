# -*- coding: utf-8 -*-
"""NLP LSTM Project

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-S3Bm8FgKIK6WCBChg0n8VPnKi-bM_i1
"""

pip install --upgrade tensorflow

# Machine Learning Library
import pandas as pd
import numpy as np
import pickle
import nltk
import re
from nltk.stem import PorterStemmer
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.preprocessing import LabelEncoder
plt.style.use('ggplot')

pip install --upgrade keras

pip install keras_preprocessing

from tensorflow.keras.preprocessing.text import Tokenizer

# Deep Learning Library
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.text import one_hot
from keras_preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

from tensorflow.keras.preprocessing.text import one_hot

df = pd.read_csv("train.txt", header = None, sep=";", names=["Comment", "Emotion"], encoding="utf-8")

df['length'] = [len(x) for x in df['Comment']]

df.head()

df.shape

df.isnull().sum()

df['Emotion'].value_counts()

df.duplicated().sum()

df = df.drop_duplicates()

df.duplicated().sum()

#EDA

sns.countplot(x=df['Emotion'])
plt.show()

df2 = df.copy()
df2['length'] = [len(x) for x in df['Comment']]
length_value = df2['length'].values
sns.histplot(data=df2, x='length',hue='Emotion',multiple = 'stack')
plt.show()

def words_cloud(wordcloud, df):
    plt.figure(figsize=(10,10))
    plt.title(df + ' Wordcloud', size = 15)
    plt.imshow(wordcloud)
    plt.axis("off")
emotions_list = df['Emotion'].unique()
for emotion in emotions_list:
    text = ' '.join([sentence for sentence in df.loc[df['Emotion'] == emotion,'Comment']])
    wordcloud = WordCloud(width = 600, height = 600).generate(text)
    words_cloud(wordcloud, emotion)

#data preprocessing

lb = LabelEncoder()
df['Emotion'] = lb.fit_transform(df['Emotion'])

df.head()

df.tail()

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

df_f = df.copy()

df_f.head()

#Text_PreProcessing(LVL1: Stemming)

from tqdm import tqdm
tqdm.pandas()
nltk.download('stopwords')
stopwords = set(nltk.corpus.stopwords.words('english'))

def clean_data(text):
    stemmer = PorterStemmer()
    text = re.sub("[^a-zA-Z]", " ",text)
    text = text.lower()
    text = text.split()
    text = [stemmer.stem(word) for word in text if word not in stopwords]
    return " ".join(text)


df_f['cleaned_comment']  = df_f['Comment'].progress_apply(clean_data)
#df['cleaned_comment']  = df['Comment'].apply(clean_data)

df_f.head()

#split data

X_train, X_test, y_train, y_test = train_test_split(df_f['cleaned_comment'], df_f['Emotion'], test_size = 0.2, random_state=42)

#Text_PreProcessing(LVL2 : TF-IDF )

tfidfvectorizer = TfidfVectorizer()
X_train_tfidf = tfidfvectorizer.fit_transform(X_train)
X_test_tfidf = tfidfvectorizer.transform(X_test)

X_train_tfidf.shape

#applying the models

classifier={
    'MultinomialNB':MultinomialNB(),
    'LogisticRegression':LogisticRegression(),
    'Random Forest':RandomForestClassifier(),
    'Support Vector Machine': SVC(),
    'xgboost':XGBClassifier()

}

for name,clf in classifier.items():
    print(f"\n============{name}============")
    clf.fit(X_train_tfidf, y_train)
    y_pred_tfidf = clf.predict(X_test_tfidf)
    accuracy_tfidf = accuracy_score(y_test, y_pred_tfidf)
    print(f"======={accuracy_tfidf}============")
    print("Classification Report")
    print(classification_report(y_test, y_pred_tfidf))

#xgb = XGBClassifier()
#xgb.fit(X_train_tfidf, y_train)
#xgb_y_pred = xgb.predict(X_test_tfidf)

rf = RandomForestClassifier(random_state=42)
rf.fit(X_train_tfidf, y_train)
rf_y_pred = rf.predict(X_test_tfidf)



def predict_emotion(input_text):
    cleaned_text = clean_data(input_text)
    input_vectorizer = tfidfvectorizer.transform([cleaned_text])

    predicted_label = rf.predict(input_vectorizer)[0]
    predicted_emotion = lb.inverse_transform([predicted_label])[0]
    label = np.max(rf.predict(input_vectorizer))

    return predicted_emotion, label

predict_emotion("She breakup with me")

predict_emotion("i am ever feeling nostalgic about the fireplace i will know that it is still on the property")

predict_emotion("i hate u")

predict_emotion("She is in love with me")

predict_emotion("She is hopeless about me")

predict_emotion("She feel happy")

predict_emotion("i am so excited")



import pickle
pickle.dump(rf, open("randomforest.pkl","wb"))
pickle.dump(lb, open("label_encoder.pkl","wb"))
pickle.dump(tfidfvectorizer, open("tfidfvectorizer.pkl","wb"))

# APPLYING DEEP LEARNING USING LSTM(LONG SHORT TERM MEMORY)

def text_cleaning(df, column, vocab_size, max_len):
    stemmer = PorterStemmer()
    corpus = []
    for text in df[column]:
        text = re.sub("[^a-zA-Z]", " ",text)
        text = text.lower()
        text = text.split()
        text = [stemmer.stem(word) for word in text if word not in stopwords]
        text = " ".join(text)
        corpus.append(text)
    one_hot_word = [one_hot(input_text=word, n=vocab_size) for word in corpus]
    pad = pad_sequences(sequences=one_hot_word, maxlen=max_len, padding="pre")
    return pad

x_train = text_cleaning(df, "Comment", vocab_size=11000, max_len=300)
y_train = to_categorical(df["Emotion"])

model = Sequential()
model.add(Embedding(input_dim = 11000, output_dim = 150, input_length = 300))
model.add(Dropout(0.2))
model.add(LSTM(128))
model.add(Dropout(0.2))
model.add(Dense(64, activation = 'sigmoid'))
model.add(Dropout(0.2))
model.add(Dense(6, activation = 'softmax'))
model.compile(optimizer='adam', loss = "categorical_crossentropy", metrics=['accuracy'])

callback = EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True)
model.fit(x_train, y_train, epochs = 10, batch_size = 64, verbose = 1, callbacks=[callback])

model.save("model.h5")

def predictive_system_dl(sentence):
    stemmer = PorterStemmer()
    corpus = []
    text = re.sub("[^a-zA-Z]", " ",sentence)
    text = text.lower()
    text = text.split()
    text = [stemmer.stem(word) for word in text if word not in stopwords]
    text = " ".join(text)
    corpus.append(text)
    one_hot_word = [one_hot(input_text=word, n=11000) for word in corpus]
    pad = pad_sequences(sequences=one_hot_word, maxlen=300, padding="pre")
    return pad

sentence = predictive_system_dl("Iam feeling love with you")
result = lb.inverse_transform(np.argmax(model.predict(sentence), axis = 1))[0]
prob = np.max(model.predict(sentence))
print(f"{result} with probability of {prob}")

