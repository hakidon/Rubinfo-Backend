# Run this script in the directory ALL

import pandas as pd
month_map = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

# Year
df_all = pd.DataFrame()

for year in range(2010, 2023):

    # List of file names
    file_names = [month_name + '_' + str(year) + '.xls' for month_name, _ in month_map.items()]
    df_list = []

    df = pd.DataFrame()

    # Initialize an empty list to store the DataFrames

    # Loop through the file names
    for file_name in file_names:
        # Read the data until the row containing "Avg"
        df = pd.read_excel(file_name, usecols='A:H', skiprows=1, header=None)

        # Find the row containing "Avg"
        row_index = df[df[0] == 'Avg'].index[0]
        df = df[:row_index]

        # Extract the month and year from the file name
        month, year = file_name.split('_')
        month = month_map[month]
        year = int(year.split('.')[0])

        # Replace the rows in column "A" with the formatted date values
        df[0] = df[0].replace('/', '')
        df[0] = pd.to_datetime(df[0], format='%d-%m-%Y')
        df[0] = df[0].apply(lambda x: x.replace(month=month, year=year))


        # Add the DataFrame to the list
        df_list.append(df)

    # Concatenate the DataFrames in the list
    df_all = pd.concat([df_all, pd.concat(df_list)])

df_all.rename(columns={0: 'Date', 1: 'SMR CV', 2: 'SMR L', 3: 'SMR 5', 4: 'SMR GP', 5: 'SMR 10', 6: 'SMR 20', 7: 'Bulk Latex'}, inplace=True)

# Print the resulting DataFrame
print(df_all)  
date_format = '%Y-%m-%d'

# Save the resulting DataFrame to a CSV file
df_all.to_csv('CLEAN_2010_2022.csv', date_format=date_format, index=False)
