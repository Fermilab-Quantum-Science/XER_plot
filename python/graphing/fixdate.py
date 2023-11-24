
import pandas as pd
import graphviz as gv
import networkx as nx
import sys
import datetime as dt
import csv


dates=[
    "21-Nov-24"
    ,"21-Nov-24"
    ,"01-Apr-2020 A"
    ,"01-Apr-2020 A"
    ,"01-Jun-2020 A"
    ,"01-Mar-2021 A"
    ,"01-Oct-2019 A"
    ,"01-Sep-2022*"
    ,"02-Apr-2020 A"
]

d = { 'A': list(range(len(dates)))
    , 'B': dates
}

df = pd.DataFrame(data=d)
df['B']=pd.to_datetime(df['B'], format='%Y-%b-s')

print(df)
