
from asyncio import _leave_task
import pandas as pd
import graphviz as gv
import networkx as nx
import sys
import datetime as dt
import csv
import math

out_format = 'pdf'

# attend to NaT and make sure everything is dt.date
def check_fix_date(d):
    # checking type(d)==pd.NaT does not seem to work at all
    if type(d)==float:
        return dt.date(1900,1,2)

    #if type(d)==pd.Timestamp: print(f'------------ Timestamp found type {d} = {type(d)}')
    #if type(d)==dt.datetime: print(f"------------- datetime found: {type(d)}")
    if type(d)!=dt.datetime and type(d)!=pd.Timestamp and type(d)!=dt.date: 
        #print(f'-------- weird found {type(d)}, {d}')
        return dt.date(1900,1,1)

    return d.date() if type(d)==dt.datetime or type(d)==pd.Timestamp else d

def convert_fix_date(attr):
    #print(f'convert_fix_date: {attr}, type = {type(attr)}')
    return check_fix_date(pd.to_datetime(attr[0:11]) if type(attr)==str else attr)

def convert_to_nx(df,xer, xer_edges, parents):
    typ = 'TT_FinMile'
    g=nx.DiGraph()
    preds={}

    iedges=xer_edges.reset_index()
    iedges.set_index("task_id", inplace=True)

    for idx,r in df.iterrows():
        #print(f'{r}')
        node=r['Activity ID'].strip()
        if node.startswith('A')==False: continue
        name=r['Activity Name']
        duration=r['Planned Duration']
        BLduration=r['BL Project Duration']
        BLstart=check_fix_date(r['BL Project Start'])
        BLend=check_fix_date(r['BL Project Finish'])
        start = check_fix_date(r['Start']) 
        end = check_fix_date(r['Finish'])
        # do not use these xer dates until they are verified with PM
        #start=xer.loc[node]['start'] 
        #end=xer.loc[node]['end'] # not all good formatting 
        pred=r['Predecessors']
        diff_finish=r['diff_finish']
        diff_start=r['diff_start']
        parent=parents.loc[node]
        #print(node, type(pred), pred)
        # print(f'{node} | {start} | {BLstart} | {end} | {BLend}')
        extra = "M" if name.find('Milestone')>=0  or name.find('milestone')>=0 else "T"
        area = parent.area

        if False:
            # this is where we pull the predecessors out of the spreadsheet
            preds[node] = pred.split(', ') if type(pred)==type("") else []
        else:
            preds[node] = list(iedges.loc[[node]].pred_task_id) if node in iedges.index else []
            #preds[node] = list(iedges.get(node, default=[]))

        #print(preds[node])

        g.add_node(node, name=name, type=extra
            , start=start, end=end
            , duration=duration, BL_duration=BLduration
            , BL_end=BLend, BL_start=BLstart
            ,diff_finish = diff_finish, diff_start=diff_start, area=area
        )

    for k,v in preds.items():
        for p in v:
            g.add_edge(k,p)

    roots = [v for v, d in g.out_degree() if d == 0]
    leaves = [v for v, d in g.in_degree() if d == 0]

    print(f'predecessor roots={roots}, leaves={leaves}')
    return (g,roots, leaves)

def read_xer_dump():
    cols=["start", "end", "duration", "target_start", "target_end", 
    "early_start", "early_end", "late_start", "late_end"]
    df = pd.read_csv("report_Aug2022.csv", infer_datetime_format=True)
    for n in cols:
        df[n]=pd.to_datetime(df[n])
    df.set_index("activity", inplace=True)
    #print(df.dtypes)
    return df

def read_xer_edges():
    df = pd.read_csv("report_Aug2022_edges.csv", infer_datetime_format=True)
    df.set_index(["task_id","pred_task_id"], inplace=True)
    return df

def read_xer_parents():
    df = pd.read_csv("report_Aug2022_parents.csv", infer_datetime_format=True)
    df.set_index(["task_code"], inplace=True)
    return df

def read_excel_report():
    df = pd.read_excel("schedule_Aug2022.xlsx", header=0, skiprows=1)
    df['good'] = df['Activity Name'].transform(lambda x : not math.isnan(x) if type(x)==float else True)
    df = df[df['good']==True]
    df['Finish']=df['Finish'].transform(convert_fix_date)
    df['Start']=df['Start'].transform(convert_fix_date)
    df['BL Project Start']=df['BL Project Start'].transform(convert_fix_date)
    df['BL Project Finish']=df['BL Project Finish'].transform(convert_fix_date)
    df['diff_finish'] = df.apply(lambda x: (x['Finish']-x['BL Project Finish']).days, axis=1)
    df['diff_start'] = df.apply(lambda x: (x['Start']-x['BL Project Start']).days, axis=1)
    return df

def just_read_graph(fname):
    g = nx.read_gpickle(fname)
    return g

if __name__ == '__main__':

    if len(sys.argv)<2 or (len(sys.argv)>1 and (sys.argv[1]=='help' or sys.argv[1]=='--help')):
        print("usage: file_name <start_task_code>")
        print("this script writes out a networkx graph to file file_name containing all nodes and edges.")
        sys.exit(0)    

    starting_code = 'A1207060'
    earliest_code = 'A0100000'
    fname_prefix = sys.argv[1]

    if len(sys.argv)>2:
        starting_code = sys.argv[2]
    else:
        print(f'using starting code of {starting_code}')

    test_last_code='A0307030' # earliest
    test_first_code='A1503540' # latest

    xer = read_xer_dump()
    df  = read_excel_report()

    #print(df.dtypes)
    g, roots, leaves = convert_to_nx(df, xer)
    print("converted to networkx")
    nx.write_gpickle(g,f'{fname_prefix}.gz')

    #ps = nx.all_simple_paths(g, starting_code, earliest_code)
    #print("found simple paths")
    #print(list(ps))
    #lps=list(ps)
    #print("converted to list")
