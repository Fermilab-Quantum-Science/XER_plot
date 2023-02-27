
import csv
import os
import sys
import pandas as pd
import networkx as nx
import graphviz as gv
import datetime as dt
import get_args as getargs
import longdelays as funs

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


datepart = 'Dec2022FY24ScenarioUpdated'

tabs = ['PROJWBS', 'RSRC', 'TASKPRED', 'TASKRSRC', 'TASK']

def read_tab(table,mid):
    fname = f'extracted/tab_{table}_{mid}.csv'

    cols=["start", "end", "duration", "target_start", "target_end", 
    "early_start", "early_end", "late_start", "late_end"]

    df = pd.read_csv(fname, infer_datetime_format=True)

    #for n in cols:
    #    df[n]=pd.to_datetime(df[n])
    #df.set_index("activity", inplace=True)
    return df

def wbs_name(tab, wbs_id):
    #  wbs_short_name, wbs_name, parent_wbs_id
    #  proj_node_flag == 'Y' <------ means end!
    full_short=[]
    full_long=[]
    id = tab.loc[[wbs_id]].iloc[0]
    #print(f'id={id}\ntypeid={type(id)}')

    while(id.proj_node_flag=='N'):
        #print(f'id={id}\ntypeid={type(id)}')
        #print('short name = ', id.wbs_short_name)
        #print( id.parent_wbs_id)
        full_short.append(id.wbs_short_name)
        full_long.append(id.wbs_name)
        id = tab.loc[[id.parent_wbs_id]].iloc[0]
    
    full_short.reverse()
    full_long.reverse()
    return '.'.join(full_short), full_short, full_long


def make_task_graph(tables, args):
    g=nx.DiGraph()
    tab = tables['PROJWBS'].set_index("wbs_id")
    tabr = tables['TASKRSRC'].set_index("task_id")

    for i,r in tables['TASK'].iterrows():

        id = r['task_id']
        #print(id, type(id))
        name = r['task_name']
        extra = "M" if name.find('Milestone')>=0  or name.find('milestone')>=0 else "T"
        wbs, short, long = wbs_name(tab, r['wbs_id'])

        if id in tabr.index:
            rrec = tabr.loc[[id]].iloc[0]
            rtype= rrec.rsrc_type
            rcost= rrec.target_cost
        else:
            rtype= "-"
            rcost= "-"
        # print(wbs, short, long)

        g.add_node(r['task_id']
            ,id=r['task_code'] 
            ,name=name 
            ,type=extra
            , target_start=r['target_start_date'], target_end=r['target_end_date']
            , early_start=r['target_start_date'], early_end=r['target_end_date']
            , late_start=r['target_start_date'], late_end=r['target_end_date']
            , driving_flag=r['driving_path_flag'] 
            , status=r['status_code']
            , task_type=r['task_type']
            , dur_type=r['duration_type']
            , target_dur_hr=r['target_drtn_hr_cnt']
            , target_work_qty=r['target_work_qty']
            , target_cost = rcost
            , rsrc_type = rtype
            , area=short[0]
            , wbs=wbs
        )

    for i,r in tables['TASKPRED'].iterrows():
        g.add_edge(r['task_id'], r['pred_task_id'])

    return g

class GNode:
    def __init__(self,g,n):
        print(f'building GNode for {n}')
        self.n = g.nodes[n]['id']
        self.t_end=g.nodes[n]['target_end']
        self.e_end=g.nodes[n]['early_end']
        self.l_end = g.nodes[n]['late_end']
        self.t_start=g.nodes[n]['target_start']
        self.e_start=g.nodes[n]['early_start']
        self.l_start=g.nodes[n]['late_start']
        self.name=g.nodes[n]['name']
        self.dur=g.nodes[n]['target_dur_hr']
        self.drv=g.nodes[n]['driving_flag']
        self.wbs=g.nodes[n]['wbs']
        self.status=g.nodes[n]['status']
        self.task_type=g.nodes[n]['task_type']
        self.typ=g.nodes[n]['type']
        self.rsrc=g.nodes[n]['rsrc_type']
        self.cost=g.nodes[n]['target_cost']
        area=int(g.nodes[n]['area'])
        self.areacol=funs.colors[area]
        #print(self.areacol)
        self.shape = 'rect' if self.typ=='M' else 'ellipse'

    def long_name(self):
        rc = f"{self.typ}/{self.n}\n{self.name}\nTS={self.t_start} / TE={self.t_end}"
        rc = rc + f"\ndrv={self.drv}/wbs={self.wbs}/d={self.dur}"
        rc = rc + f"\nstatus={self.status}/cost={self.cost}/rsrc={self.rsrc}"
        if self.t_start!=self.e_start or self.t_end!=self.e_end:
            rc = rc + f'\nES={self.e_start} / EE={self.e_end}' 
        if self.t_start!=self.l_start or self.t_end!=self.l_end:
            rc = rc + f'\nLS={self.l_start}/LE={self.l_end}'
        return rc

    def short_name(self):
        return f"{self.typ}/{self.n}\n{self.name}\ndrv={self.drv}/wbs={self.wbs}"


def render_all(g,args):
    dot=gv.Digraph(comment='sched',strict=True, format=args.output_format)
    for n in g.nodes(data=True):
        node = GNode(g,n[0])
        col='crimson' if n[0] in args.special_list else 'black'
        pw = 1.0 if col=='black' else 15.0
        mylabel=node.long_name() if args.show_dates else node.short_name()
        #print(mylabel, col, node.shape, n[0])
        dot.node(str(n[0]),label=mylabel,color=col,shape=node.shape, fillcolor=node.areacol, style='filled',penwidth=str(pw))
    for e in g.edges():
        dot.edge(str(e[0]),str(e[1]), label=f'', color='black')

    reduced = "wr" if args.do_reduction else "wor"
    fname=f'output/nx_{args.wbs_item}_{reduced}'
    #dot.render(fname+'.dot', view=False).replace('\\', '/')
    dot.render(fname, view=args.render).replace('\\', '/')



if __name__ == "__main__":

    args = getargs.get_args()
    tables = {t:read_tab(t,args.date_part) for t in tabs}

    g_init = make_task_graph(tables, args)

    if args.wbs_filter:
        g = funs.filter_by_wbs(g_init,args.wbs_item)

    render_all(g,args)


#    for i,r in tables['RSRC'].iterrows():
#        print(i,r)
#        if r['proj_node_flag']!='N': print(i,r)
#        print(r['task_code'],r['task_name'])

#    for n,df in tables.items():
#        print(n, df.columns)

# TASK
# interesting fields:
#  early_start_date, late_start_date, early_end_date, late_end_date
#  driving_path_flag, status_code, task_type, duration_type
#  target_start_date, target_end_date
#  target_drtn_hr_cnt, target_work_qty, task_code, task_name
# pointers:
#  wbs_id, rsrc_id
# index: 
#  task_id

# PROJWBS
#  seq_num, wbs_short_name, wbs_name, parent_wbs_id
#  proj_node_flag == 'Y' <------ means end!
# index:
#  wbs_id

# TASKPRED
#  task_id, pred_task_id

# TASKRSRC
#  task_id, target_qty, target_cost, rsrc_type
#  target_start_date, target_end_date
# index:
#  taskrsrc_id

# RSRC (leave out for now)