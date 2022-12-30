import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import numpy as np
from datetime import datetime


# Fetch the service account key JSON file contents
cred = credentials.Certificate('rubinfo-db-firebase-adminsdk-og7zv-8de157c810.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://rubinfo-db-default-rtdb.firebaseio.com/"
})


df =  pd.read_csv("CLEAN_2010_2022.csv")

for index, row in df.iterrows():
    # if index == 5:
    #     break
    # Create a dictionary from the row data
    data = row.to_dict()
    date = datetime.strptime(data['Date'], "%d/%m/%Y")
    year = date.year
    month = date.month

    ref = 'Prices/' + str(year) + '/' + str(month) + '/'
    db_ref = db.reference(ref)
    db_ref.push(data)


# result = ref.get()
# print(result)  

