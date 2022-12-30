import pandas as pd
import numpy as np
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import LSTM, Dense

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
from bs4 import BeautifulSoup
from datetime import datetime

import csv

# pip install h5py
# pip install typing-extensions
# pip install wheel

def init_db():
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate('rubinfo-db-firebase-adminsdk-og7zv-8de157c810.json')
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://rubinfo-db-default-rtdb.firebaseio.com/"
    })

def get_csv(filename):
    return pd.read_csv(filename)

def web_scrape():
    latest_date=''
    latest_bl_price = ''
    # Make a request to the website
    response = requests.get('http://www3.lgm.gov.my/mre/daily.aspx')

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    #fetch date
    try:
        latest_date = soup.find('table', {'id': 'tblRubberPrices'}).find('td', {'id': 'Current'}).find('center').find('font', color='maroon').text
        #fetch bulk latex price
        td_element = soup.find('table', {'id': '_ctl0_ContentPlaceHolder1_tblBulkNoon'})
        latest_bl_price = td_element.find('tr').find('td', {'class': 'gveven'}).find('span', {'id': '_ctl0_ContentPlaceHolder1_lblBulkNoon_S'}).text
    except:
        pass
 
    return latest_date, latest_bl_price

def train(df):
    close_data = df['Bulk Latex'].values
    close_data = close_data.reshape((-1,1))

    # split_percent = 0.80
    # split = int(split_percent*len(close_data))

    close_train = close_data
    # close_test = close_data[split:]

    # date_train = df['Date'][:split]
    # date_test = df['Date'][split:]

    look_back = 2

    train_generator = TimeseriesGenerator(close_train, close_train, length=look_back, batch_size=20)     
    # test_generator = TimeseriesGenerator(close_test, close_test, length=look_back, batch_size=1)

    # train model
    model = Sequential()
    model.add(
        LSTM(100,
            activation='relu',
            input_shape=(look_back,1))
    )

    model.add(Dense(25))

    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    num_epochs = 10

    model.fit(
        train_generator,
        steps_per_epoch=len(train_generator),
        epochs=num_epochs,
        verbose=0
    )
    return model, close_data, look_back

def predict(num_prediction, model, close_data, look_back):
    prediction_list = close_data[-look_back:]
    
    for _ in range(num_prediction):
        x = prediction_list[-look_back:]
        x = x.reshape((1, look_back, 1))
        out = model.predict(x, verbose=0)[0][0]
        prediction_list = np.append(prediction_list, out)
    prediction_list = prediction_list[look_back-1:]
        
    return prediction_list

def main():
    filename = "CLEAN_2010_2022.csv"
    # Scrape date and latex price at LGM website
    latest_date_web, latest_latex_price = web_scrape()
    latest_latex_price = float(latest_latex_price)

    # Read csv, extract latest date 
    df = get_csv(filename)
    latest_date_csv = df.tail(1)['Date'].values[0]

    # print (latest_date_web)
    # print (latest_date_csv)

    # Check if there is scrape date or compare if latest date csv not equal to scrape date
    # if (not latest_date_web or (latest_date_web == latest_date_csv)):
    #     return # if equal, do nothing. Wait for another day

    # if not, add the data into csv 
    # Open the CSV file in append mode
    latest_data = [latest_date_web, latest_latex_price]
    with open(filename, 'a', newline='') as f:
        # Create a CSV writer
        writer = csv.writer(f)
        # Write the new data to the CSV file
        writer.writerow(latest_data)
    print('done')

    # preprocess the data, retrain, generate prediction
    df.loc[len(df)] = latest_data

    model, close_data, look_back = train(df)
    num_prediction = 30
    forecast = predict(num_prediction, model, close_data, look_back)

    # push latest data into firebase, update prediction into the firebase
    init_db()
    ref = 'Predictions'
    db_ref = db.reference(ref)
    # Push predictions into firebase
    for i, prediction in enumerate(forecast):
        if i == 0:
            continue
        data =  { 'Day':  i,  
          'Price': prediction  
          }  
        db_ref.push(data)
    
    # Get year and month for database ref
    date = datetime.strptime(latest_date_web, "%d/%m/%Y")
    year = date.year
    month = date.month

    # Push latest data into firebase
    ref = 'Prices/' + str(year) + '/' + str(month) + '/'
    db_ref = db.reference(ref)
    data =  { 
            'Date': latest_date_web,  
            'Bulk Latex': latest_latex_price  
            } 
    db_ref.push(data)

    # End
    # Wait for another day

    
    # Run main at 12.30 every day 
    # Scrape date and latex price at LGM website
    # Read csv, extract latest date 
    # Compare if latest date csv not equal to scrape date
    # if equal, do nothing. Wait for another day
    # if not, add the data into csv 
    # preprocess the data, retrain, generate prediction
    # push latest data into firebase, update prediction into the firebase
    # Wait for another day

if __name__ == "__main__":
    # Run main at 12.30 every day 
    main()



# close_train = close_train.reshape((-1))
# close_test = close_test.reshape((-1))
# prediction = prediction.reshape((-1))

# trace1 = go.Scatter(
#     x = date_train,
#     y = close_train,
#     mode = 'lines',
#     name = 'Data'
# )
# trace2 = go.Scatter(
#     x = date_test,
#     y = prediction,
#     mode = 'lines',
#     name = 'Prediction'
# )
# trace3 = go.Scatter(
#     x = date_test,
#     y = close_test,
#     mode='lines',
#     name = 'Actual'
# )
# layout = go.Layout(
#     title = "Bulk Latex Price",
#     xaxis = {'title' : "Date"},
#     yaxis = {'title' : "Price"}
# )
# fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
# fig.show()