import os
import pandas as pd
from requests import head

out_path = 'out/'

dirs = os.listdir(out_path)

merged = None

for dirname in dirs:
    if os.path.isdir(out_path + dirname):
        filename = out_path + dirname + '/results.csv'
        print(filename)
        columns = ['number',dirname]
        csv = pd.read_csv(filename, header=None, names=columns)

        if (merged is None):
           merged = csv 
        else: 
            merged = merged.merge(csv, on='number')

merged.to_csv('merged.csv')
