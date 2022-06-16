import os
import pandas as pd
from requests import head

out_path = 'out/'

dirs = os.listdir(out_path)

merged_status = None
merged_time = None

for dirname in dirs:
    if os.path.isdir(out_path + dirname):
        filename = out_path + dirname + '/results.csv'
        print(filename)
        columns = ['number',dirname+'_status', dirname+'_time']
        csv = pd.read_csv(filename, header=None, names=columns)

        new_csv_status = csv[['number',dirname+'_status']].copy()
        new_csv_status.rename(columns={dirname+'_status': dirname}, inplace=True)
        new_csv_time = csv[['number',dirname+'_time']].copy()
        new_csv_time.rename(columns={dirname+'_time': dirname}, inplace=True)
        

        if (merged_status is None):
           merged_status = new_csv_status
           merged_time = new_csv_time 
        else: 
            merged_status = merged_status.merge(new_csv_status, on='number')
            merged_time = merged_time.merge(new_csv_time, on='number')

merged_status.to_csv('merged_status.csv')
merged_time.to_csv('merged_time.csv')
