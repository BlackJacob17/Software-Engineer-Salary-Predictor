# -*- coding: utf-8 -*-
"""MLProject.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uIMzk8-dBrJS4IivlBkEIq84sum2R0XY
"""

import pandas as pd
import numpy as np
import datetime as dt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats
import seaborn as sns

pd.options.display.float_format = '{:.2f}'.format
sns.set_theme(color_codes=True)

def log(f):
    def wrapper(df, *args, **kwargs):
        start = dt.datetime.now()
        result = f(df, *args, **kwargs)
        stop = dt.datetime.now()
        print(f'{f.__name__}:\n  runtime={stop - start}, end shape={result.shape}')
        return result
    return wrapper

@log
def startPipeline(df):
    return df.copy()

@log
def clean(df):
    df = df[[
        'ConvertedCompYearly',
        # 'EdLevel', # will need to vectorize (worst = 0, best = 1, rest in between)
        'Employment',
        # 'Age1stCode',
        'YearsCode',
        'YearsCodePro',
        # 'OrgSize'
    ]]
    df = df[df["Employment"] == "Employed full-time"]
    df = df.drop("Employment", axis=1)
    df = df.dropna(subset=['ConvertedCompYearly'])
    # do this better. don't drop these. vectorize them.
    # drop rows in 'YearsCode', 'YearsCodePro' that are 'Less than 1 year'
    df = df[df['YearsCode'].str.contains('Less than 1 year')==False]
    df = df[df['YearsCodePro'].str.contains('Less than 1 year')==False]
    df = df[df['YearsCode'].str.contains('More than 50 years')==False]
    df = df[df['YearsCodePro'].str.contains('More than 50 years')==False]

    df[['YearsCode', 'YearsCodePro']] = df[['YearsCode', 'YearsCodePro']].apply(pd.to_numeric)

    df = df.round(2)

    return df

@log
def removeOutliers(df):
    # df = df[(np.abs(stats.zscore(df['ConvertedCompYearly'])) < .25)]
    df = df[df["ConvertedCompYearly"] <= 300000]
    df = df[df["ConvertedCompYearly"] >= 15000]
    return df

def get_df():
    df_raw = pd.read_csv('./survey_results_public.csv')
    return (df_raw
        .pipe(startPipeline)
        .pipe(clean)
        .pipe(removeOutliers)
)

df = get_df()
df.head()

df.info()

# df['Country'].value_counts()

df.describe()

reg = LinearRegression()
label = 'ConvertedCompYearly'
labels = df[label]
train = df.drop([label], axis=1)

x_train, x_test, y_train, y_test = train_test_split(train, labels, test_size=0.2, random_state=1776)

reg.fit(x_train, y_train)

from sklearn.metrics import mean_squared_error, r2_score

def performance(x, y, name, tolerance=0.1):
    y_predict = reg.predict(x)
    rmse = np.sqrt(mean_squared_error(y, y_predict))
    r2 = r2_score(y, y_predict)

    # Calculate accuracy based on tolerance
    accuracy_within_tolerance = np.mean(np.abs((y - y_predict) / y) < tolerance) * 100

    print(name)
    print(f'  RMSE={rmse}, R^2={r2}, Accuracy within {tolerance*100}% tolerance={accuracy_within_tolerance:.2f}%')

# Example usage
performance(x_train, y_train, 'train')
performance(x_test, y_test, 'test')

predicted = reg.predict(x_test)
expected = y_test
ax = sns.regplot(x=predicted, y=expected)

import tensorflow as tf
from tensorflow import keras

df = get_df()
print(df.shape)
train_dataset = df.sample(frac=0.8, random_state=0)
test_dataset = df.drop(train_dataset.index)

train_dataset.tail()

sns.pairplot(train_dataset, diag_kind="kde")

train_dataset.describe().transpose()

train_features = train_dataset.copy()
test_features = test_dataset.copy()

train_labels = train_features.pop('ConvertedCompYearly')
test_labels = test_features.pop('ConvertedCompYearly')

train_dataset.describe().transpose()[['mean', 'std']]

normalizer = tf.keras.layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))
print(normalizer.mean.numpy())

first = np.array(train_features[:1])

with np.printoptions(precision=2, suppress=True):
  print('First example:', first)
  print()
  print('Normalized:', normalizer(first).numpy())

def build_and_compile_model(norm):
  model = keras.Sequential([
      norm,
      keras.layers.Dense(64, activation='relu'),
      keras.layers.Dense(64, activation='relu'),
      keras.layers.Dense(1)
  ])

  model.compile(loss='mean_absolute_error',
                optimizer=tf.keras.optimizers.Adam(0.001))
  return model

dnn_model = build_and_compile_model(normalizer)
dnn_model.summary()

# Commented out IPython magic to ensure Python compatibility.
# %%time
# history = dnn_model.fit(
#     train_features,
#     train_labels,
#     validation_split=0.2,
#     verbose=0, epochs=50)

dnn_model.evaluate(test_features, test_labels, verbose=0)

# this has issues when trying to load/predict
tf.saved_model.save(dnn_model, './dnn_model')

# keras save seems to work better
tf.keras.models.save_model(dnn_model, './dnn_model_keras.h5')

# saved_dnn_model = tf.saved_model.load('./dnn_model')
saved_dnn_model_keras = tf.keras.models.load_model('./dnn_model_keras.h5')

# print(list(saved_dnn_model.signatures.keys()))
# infer = saved_dnn_model.signatures["serving_default"]
# saved_dnn_model.evaluate(test_features, test_labels, verbose=0)
saved_dnn_model_keras.evaluate(test_features, test_labels, verbose=0)

# predict salary for 30 years and 32 years
predictions = saved_dnn_model_keras.predict(np.array([[30, 32]]))
print(predictions)

import random # Import the random module
import pandas as pd
import numpy as np
import tensorflow as tf

# ... (Your existing code to load the model and define predict1YOE) ...

# First Training Iteration
new_inputs_count = 10_000
new_inputs_labels = pd.Series([random.randint(20_000, 30_000) # Now random is defined and can be used.
                    for x in range(new_inputs_count)])
# Reshape new_inputs_features to match the original input shape
new_inputs_features = pd.DataFrame([{"YearsCode": 1, "YearsCodePro": 1} for x in range(new_inputs_count)])
# Convert the DataFrame to a NumPy array with the correct shape.
new_inputs_features = new_inputs_features[['YearsCode', 'YearsCodePro']].values # Assuming your original model expected two numerical features

predict1YOE()

# **Important:** Compile the model again before fitting with new data
saved_dnn_model_keras.compile(optimizer='adam', loss='mse') # or your original optimizer and loss function

saved_dnn_model_keras.fit(
    new_inputs_features,  # Pass features as the first argument
    new_inputs_labels,  # Pass labels as the second argument
    validation_split=0.2,
    verbose=0, epochs=10)

predict1YOE()


# Second Training Iteration (similar changes)
new_inputs_count = 10_000
new_inputs_labels = pd.Series([random.randint(20_000, 30_000)
                    for x in range(new_inputs_count)])

new_inputs_features = pd.DataFrame([{"YearsCode": 1, "YearsCodePro": 1} for x in range(new_inputs_count)])
# Convert the DataFrame to a NumPy array with the correct shape.
new_inputs_features = new_inputs_features[['YearsCode', 'YearsCodePro']].values # Assuming your original model expected two numerical features

def predict1YOE():
    # Ensure the input shape matches the model's input shape
    return saved_dnn_model_keras.predict(np.array([[1, 1]]))[0][0]

predict1YOE()

# **Important:** Recompile the model if needed
saved_dnn_model_keras.compile(optimizer='adam', loss='mse')  # Or your original optimizer and loss

saved_dnn_model_keras.fit(
    new_inputs_features,  # Pass features as the first argument
    new_inputs_labels,  # Pass labels as the second argument
    validation_split=0.2,
    verbose=0, epochs=10)

predict1YOE()

import time
import pandas as pd
import sys
sys.path.append('/common.py')  # Replace with the actual path
from common import DataLoader
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MultiLabelBinarizer
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
import tensorflow as tf
from tensorflow import keras
# Install keras-tuner if not already installed
!pip install keras-tuner
import keras_tuner as kt # Now import keras_tuner
import seaborn as sns
import matplotlib.pyplot as plt

pd.options.display.float_format = '{:.2f}'.format
sns.set_theme(color_codes=True)
path = './survey_results_public.csv'
dl = DataLoader(path=path)
df = dl.df
df.head()

df.isna().sum()

from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MultiLabelBinarizer
dl.encodings = {}
dl.encodings["Country"] = OneHotEncoder()
dl.encodings["Country"].fit(df[["Country"]])

row = df.loc[df['Country'] == "United States of America"].iloc[0]
country_us = row["Country"]
country_us_encoded = dl.encodings["Country"].transform(pd.DataFrame(data={"Country": [country_us]}))
country_us_encoded

X = df[['YearsCode', 'YearsCodePro', 'Age1stCode', 'Age']]
y = df['ConvertedCompYearly']
linreg = LinearRegression()
print(cross_val_score(linreg, X, y, cv=5, scoring="neg_mean_absolute_error"))

column_trans = make_column_transformer(
    (OneHotEncoder(), ["Country"]),
    remainder="passthrough")
X = df[['YearsCode', 'YearsCodePro', 'Age1stCode', 'Age', 'Country']]
column_trans.fit_transform(X)
pipe = make_pipeline(column_trans, linreg)
cross_val_score(pipe, X, y, cv=5, scoring="neg_mean_absolute_error")

dl = DataLoader(path=path)
df = dl.df.drop(['EdLevel', 'Country', 'DevType','LanguageHaveWorkedWith'], axis=1)
print(df.head())

train_dataset = df.sample(frac=0.8, random_state=0)
test_dataset = df.drop(train_dataset.index)
train_features = train_dataset.copy()
test_features = test_dataset.copy()
train_labels = train_features.pop('ConvertedCompYearly')
test_labels = test_features.pop('ConvertedCompYearly')
train_dataset.describe().transpose()[['mean', 'std']]

normalizer = tf.keras.layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))
print(normalizer.mean.numpy())


first = np.array(train_features[:1])

with np.printoptions(precision=2, suppress=True):
  print('First example:', first)
  print()
  print('First example Normalized:', normalizer(first).numpy())

lr_model = keras.Sequential([
    normalizer,
    keras.layers.Dense(1)
])
lr_model.summary()

lr_model.compile(
    optimizer=tf.optimizers.Adam(learning_rate=0.001),
    loss='mean_absolute_error'
)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# lr_history = lr_model.fit(
#     train_features,
#     train_labels,
#     validation_split = 0.2,
#     epochs=50,
#     verbose=0)
# 
# MODELS = {
#     "lr": lr_model.evaluate(test_features, test_labels, verbose=0)
# }
# 
# print(MODELS["lr"])

def plot_loss(history):
  plt.plot(history.history['loss'])
  plt.plot(history.history['val_loss'])
  plt.title('model loss')
  plt.ylabel('loss')
  plt.xlabel('epoch')
  plt.legend(['train', 'test'], loc='upper left')
  plt.show()

plot_loss(lr_history)

def build_model():
  model = keras.Sequential([
      normalizer,
      keras.layers.Dense(64, activation='relu'),
      keras.layers.Dense(64, activation='relu'),
      keras.layers.Dense(1)
  ])

  model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
                loss='mean_absolute_error')
  return model

dnn1_model = build_model()
print(dnn1_model.summary())

# Commented out IPython magic to ensure Python compatibility.
# %%time
#   history1 = dnn1_model.fit(
#       train_features,
#       train_labels,
#       validation_split=0.2,
#       epochs=50)
# 
#   MODELS['dnn1'] = dnn1_model.evaluate(test_features, test_labels, verbose=0)
# 
#   print(MODELS['dnn1'])

plot_loss(history1)

def build_model(hp):
  model = keras.Sequential()

  model.add(normalizer)
  model.add(keras.layers.Dense(hp.Int("units", min_value=32, max_value=256, step=32), activation='relu'))

  for i in range(hp.Int("n_layers", min_value=1, max_value=4)):
    model.add(keras.layers.Dense(hp.Int(f"units-{i}", min_value=32, max_value=256, step=32), activation='relu'))

  model.add(keras.layers.Dense(1))

  model.compile(optimizer=tf.keras.optimizers.Adam(0.001),

      loss='mean_absolute_error')
  return model

tuner = kt.RandomSearch(
    build_model,
    objective = "val_loss",
    max_trials = 3,
    executions_per_trial = 1,

)

tuner.search(x=train_features,
             y=train_labels,
             epochs=10,
             batch_size=64,
             validation_data=(test_features, test_labels))

print(tuner.get_best_hyperparameters()[0].values)

print(tuner.results_summary())

best_model = tuner.get_best_models()[0]
print(best_model.summary())

# Commented out IPython magic to ensure Python compatibility.
#  %%time
  history_best = best_model.fit(
      train_features,
      train_labels,
      validation_split=0.2,
      epochs=25)

  MODELS['best'] = best_model.evaluate(test_features, test_labels, verbose=0)

  print(MODELS['best'])

plot_loss(history_best)

pred_input = np.array([1, 1, 1, 1])

pred_input = pred_input.reshape(1, -1)
pred = best_model.predict(pred_input)[:, 0]
pred[0]

def transform_df_ohe_country(df):


  # encode
  ohe = OneHotEncoder(categories = "auto")
  feature_arr = ohe.fit_transform(df[['Country']]).toarray()
  # merge encoded into df
  df = merge_ohe(df, ohe, feature_arr)
  # drop country
  df = df.drop(['Country'], axis=1)

  return df, ohe

def merge_ohe(df, ohe, feature_arr):
  feature_labels = np.array(ohe.categories_).ravel()
  df_features = pd.DataFrame(feature_arr, columns=feature_labels)
  df.reset_index(drop=True, inplace=True)
  df_features.reset_index(drop=True, inplace=True)
  df = pd.concat([df, df_features], axis=1)
  return df

def transform_df_mlb_delimited_string(df, column):

  df[column] = df[column].apply(lambda x: x.split(';'))

  mlb = MultiLabelBinarizer()
  encoded = mlb.fit_transform(df.pop(column))

  df = merge_mlb(df, mlb, encoded)

  return df, mlb

def merge_mlb(df, mlb, encoded):
  return df.join(pd.DataFrame(encoded, columns=mlb.classes_, index=df.index))

def transform_df_oe(df):
  oe = OrdinalEncoder(categories=[['Less than Associates', 'Associates',
                                   'Bachelors', 'Masters', 'Doctorate']])
  df['EdLevel'] = oe.fit_transform(df['EdLevel'].values.reshape(-1,1))
  return df, oe

import pickle

df = dl.df
df, country_ohe = transform_df_ohe_country(df)
df, dev_type_mlb = transform_df_mlb_delimited_string(df, 'DevType')
df, languages_mlb = transform_df_mlb_delimited_string(df, 'LanguageHaveWorkedWith')
df, ed_level_oe = transform_df_oe(df)

encodings = {
  "country_ohe": country_ohe,
  "dev_type_mlb": dev_type_mlb,
  "languages_mlb": languages_mlb,
  "ed_level_oe": ed_level_oe
}

# save ohe
with open("encodings.pickle", "wb") as f:
    pickle.dump(encodings, f)

train_dataset = df.sample(frac=0.8, random_state=0)
test_dataset = df.drop(train_dataset.index)
train_features = train_dataset.copy()
test_features = test_dataset.copy()
train_labels = train_features.pop('ConvertedCompYearly')
test_labels = test_features.pop('ConvertedCompYearly')

train_features.head()

list(df.columns)

def build_model(hp):
  model = keras.Sequential()
  model.add(keras.layers.Dense(hp.Int("units", min_value=32, max_value=256, step=32), activation='relu'))

  for i in range(hp.Int("n_layers", min_value=1, max_value=3)):
    model.add(keras.layers.Dense(hp.Int(f"units-{i}", min_value=32, max_value=256, step=32), activation='relu'))

  model.add(keras.layers.Dense(1))

  model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
      # loss='mean_squared_error'
      loss='mean_absolute_error')

  return model

tuner = kt.RandomSearch(
    build_model,
    objective = "val_loss",
    max_trials = 3,
    executions_per_trial = 1,
    directory = f'${int(time.time())}'
)

tuner.search(x=train_features,
             y=train_labels,
             epochs=10,
             batch_size=64,
             validation_data=(test_features, test_labels))

test_features.values

best_model = tuner.get_best_models()[0]

# Commented out IPython magic to ensure Python compatibility.
# %%time
# callback = tf.keras.callbacks.EarlyStopping(monitor="val_loss",patience=5,restore_best_weights=True)
# history_best = best_model.fit(
#     train_features,
#     train_labels,
#     validation_split=0.2,
#     epochs=150,
#     callbacks=[callback])
# 
# MODELS['best'] = best_model.evaluate(test_features, test_labels, verbose=0)
# 
# print(MODELS['best'])

plot_loss(history_best)

best_model.evaluate(test_features, test_labels, verbose=0)

def make_input(input_dict):
  df_input = pd.DataFrame(data={
      "EdLevel": [input_dict["ed_level"]],
      "Age1stCode": [input_dict["age_first_code"]],
      "YearsCode": [input_dict["years_code"]],
      "YearsCodePro": [input_dict["years_code_pro"]],
      "Age": [input_dict["age"]],
  })
  # encode Country
  country_enc = country_ohe.transform(pd.DataFrame(
      data={"Country": [input_dict["country"]]})).toarray()
  df = merge_ohe(df_input, country_ohe, country_enc)

  # encode Devtype
  dev_type_enc = dev_type_mlb.transform(pd.Series([input_dict["dev_type"]]))
  df = merge_mlb(df, dev_type_mlb, dev_type_enc)

  # encode LanguageHaveWorkedWith
  languages_enc = languages_mlb.transform(pd.Series([input_dict["languages"]]))
  df = merge_mlb(df, languages_mlb, languages_enc)

  # encode Edlevel
  df['EdLevel'] = ed_level_oe.transform(df['EdLevel'].values.reshape(-1,1))

  return df.values

pred_input = make_input({"age_first_code": 16, "years_code": 4,
                         "years_code_pro": 3, "age": 33,
                         "country": "United States of America",
                         "dev_type": ["Developer, full-stack"],
                         "languages": ["Python", "JavaScript", "SQL"],
                         "ed_level": "Bachelors"})
pred_input

pred = best_model.predict(pred_input)[:, 0]
pred[0]