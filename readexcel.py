
from asyncio import _leave_task
import pandas as pd
import graphviz as gv
import networkx as nx
import sys
import datetime as dt
import csv
import math

out_format = 'pdf'

def has_delayed_node(g, path):
    rc=False
    for n in path:
        rc |= g.nodes[n]['start'].date()!=g.nodes[n]['BL_start'].date()
    return rc

def reduce_path(g,path):
    npath=[]
    for n in path:
        #print(f"typ start={type(g.nodes[n]['start'])},  typ BL_start={type(g.nodes[n]['BL_start'])}")
        if g.nodes[n]['start'].date()==g.nodes[n]['BL_start'].date(): break
        npath.append(n)
    if len(npath)==0: print(f"path in {len(path)}, path out {len(npath)}")
    return npath

def render_nx(g,ps, first_code,last_code, output_format=out_format):
    dot=gv.Digraph(comment='sched',strict=True, format=output_format)

    # can color nodes if node attr until_start < dt.timedelta(seconds=0)
    # or until_end < dt.timedelta(seconds=0)

    print(f"doing rendering")

    #reduced_paths=[reduce_path(g,p) for p in lps]
    #reduced_all={ n for p in reduced_paths for n in p}
    #print(f'reduced paths len={len(reduced_paths)}, len all={len(reduced_all)}')
    #sys.exit(0)

    all_nodes=set()
    all_edges=set()

    now = dt.datetime.now().date()
    later = now + dt.timedelta(days=6*30)

    for p in ps:
        for i in range(len(p)-1):
            n = p[i]
            end=g.nodes[n]['end'].date()
            BLend=g.nodes[n]['BL_end'].date()
            diff = (end-BLend).days if type(BLend)==dt.date and type(end)==dt.date else 0 
            toshort = (diff>35 or diff < -35)
            #print(f'diff={diff}')
            #if n=='A1802940': print(f'{n}: {end}, {BLend}, {diff}')
            if n=='A0903010': print(f'{n}: {end}, {BLend}, {diff}')
            if n not in all_nodes and end!=BLend and end>now: # and end<later:
                all_nodes.add(n)
                S=g.nodes[n]['start'].date()
                BS=g.nodes[n]['BL_start'].date()
                name=g.nodes[n]['name']
                dur=g.nodes[n]['duration']
                typ=g.nodes[n]['type']
                bldur=g.nodes[n]['BL_duration']
                mylabel=f"{typ}/{n}\n{name}\nd={dur} / bd={bldur}\nBS={BS} / S={S}\nF={end} / BF={BLend}"
                dot.node(n,label=mylabel,color='black' if typ=='T' else 'red')
            e = (p[i], p[i+1])
            if e not in all_edges:
                all_edges.add(e)
                dot.edge(e[0],e[1], label=f'', color='black')
    
    print("done with all nodes/edges")
    fname=f'nx_{first_code}_{last_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)


def convert_to_nx(df,xer):
    typ = 'TT_FinMile'
    g=nx.DiGraph()
    preds={}

    for idx,r in df.iterrows():
        #print(f'{r}')
        node=r['Activity ID'].strip()
        if node.startswith('A')==False: continue
        name=r['Activity Name']
        duration=r['Planned Duration']
        BLduration=r['BL Project Duration']
        BLstart=r['BL Project Start']
        BLend=r['BL Project Finish']
        #start=xer.loc[node]['start'] 
        start = r['Start'] # this date is bad format for some 
        #end=xer.loc[node]['end'] # not all good formatting 
        end = r['Finish']
        pred=r['Predecessors']
        #print(node, type(pred), pred)
        # print(f'{node} | {start} | {BLstart} | {end} | {BLend}')
        extra = "M" if name.find('Milestone')>=0  or name.find('milestone')>=0 else "T"
        preds[node] = pred.split(', ') if type(pred)==type("") else []
        g.add_node(node, name=name, type=extra
            , start=start, end=end
            , duration=duration, BL_duration=BLduration
            , BL_end=BLend, BL_start=BLstart
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
    df = pd.read_csv("sheet.csv", infer_datetime_format=True)
    for n in cols:
        df[n]=pd.to_datetime(df[n])
    df.set_index("activity", inplace=True)
    #print(df.dtypes)
    return df

def read_excel_report():
    df = pd.read_excel("../Schedule with August 2022 Input - Outdated Baseline - 100422.xlsx", header=0, skiprows=1)
    df['good'] = df['Activity Name'].transform(lambda x : not math.isnan(x) if type(x)==float else True)
    df = df[df['good']==True]
    df['Finish']=df['Finish'].transform(lambda x: pd.to_datetime(x[0:11]) if type(x)==str else x)
    df['Start']=df['Start'].transform(lambda x: pd.to_datetime(x[0:11]) if type(x)==str else x)
    df['BL Project Start']=df['BL Project Start'].transform(lambda x: pd.to_datetime(x[0:11]) if type(x)==str else x)
    df['BL Project Finish']=df['BL Project Finish'].transform(lambda x: pd.to_datetime(x[0:11]) if type(x)==str else x)
    df['diff'] = df.apply(lambda x: x['Finish']-x['BL Project Finish'], axis=1)
    return df

if __name__ == '__main__':

    if len(sys.argv)<2 or (len(sys.argv)>1 and (sys.argv[1]=='help' or sys.argv[1]=='--help')):
        print("usage: file_name start_task_code")
        sys.exit(0)    

    starting_code = 'A1207060'
    earliest_code = 'A0100000'
    fname = sys.argv[1]

    if len(sys.argv)>2:
        starting_code = sys.arv[2]
    else:
        print(f'using starting code of {starting_code}')

    test_last_code='A0307030' # earliest
    test_first_code='A1503540' # latest

    xer = read_xer_dump()
    df  = read_excel_report()

    print(df.dtypes)
    g, roots, _leaves = convert_to_nx(df, xer)
    print("converted")
    ps = nx.all_simple_paths(g, starting_code, earliest_code)
    print("found simple paths")
    #lps=list(ps)
    print("converted to list")
    reduced_paths=[reduce_path(g,p) for p in ps]
    #reduced_all={ n for p in reduced_paths for n in p}
    print("reduced to set of nodes")
    print(f'len reduced={len(reduced_paths)}')
    #print(reduced_all)
    render_nx(g,reduced_paths, test_first_code, test_last_code)

# print row 3
# df.loc[[2]]
# df.columns
# first row, one specific column
# df.loc[0,'column_name']
# extract a column
# df[['Start']]
# df.loc[0,'Predecessors'].split(sep=', ')
