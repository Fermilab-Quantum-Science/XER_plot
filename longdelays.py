
import readexcel as rex
import pandas as pd
import networkx as nx

xer = rex.read_xer_dump()
df  = rex.read_excel_report()
g, roots, leaves = rex.convert_to_nx(df, xer)

df_top = df.sort_values(by="diff", ascending=False).iloc[0:20].sort_values(by="BL Project Finish")
df_out = df_top[['Activity ID', 'Activity Name', 'BL Project Start', 'Start', 'BL Project Finish','Finish', 'diff']]

print(df.columns)
print(df_out)
