
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


# datepart = 'Dec2022FY24ScenarioUpdated'

tabs = ['PROJWBS', 'RSRC', 'TASKPRED', 'TASKRSRC', 'TASK', 'ROLE']

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

        # print(id, r['act_start_date'], r['act_end_date'])

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
            , task_id=id
            , target_start=r['target_start_date'], target_end=r['target_end_date']
            , early_start=r['early_start_date'], early_end=r['early_end_date']
            , late_start=r['late_start_date'], late_end=r['late_end_date']
            , actual_start=r['act_start_date'], actual_end=r['act_end_date']
            , driving_flag=r['driving_path_flag'] 
            , status=r['status_code']
            , task_type=r['task_type']
            , dur_type=r['duration_type']
            , target_dur_hr=r['target_drtn_hr_cnt']
            , target_work_qty=r['target_work_qty']
            , total_float_hr=r['total_float_hr_cnt']
            , free_float_hr=r['free_float_hr_cnt']
            , target_cost = rcost
            , rsrc_type = rtype
            , area=short[0]
            , wbs_high=long[0]
            , wbs_low=long[-1]
            , wbs=wbs
        )

    for i,r in tables['TASKPRED'].iterrows():
        g.add_edge(r['task_id'], r['pred_task_id'], pred_type=r['pred_type'])

    return g

# late <- (TK_Active | TK_NotStart) & (target_end < now)
# delayed <- TK_NotStart & (target_start < now)
# 

        # category information
        # assembly: has assemble, assembly
        # qualify: qualification, qualify
        # procurement: procure, procurement
        # other: ??
        # ground level installation: install, installation
        # shaft installation: 
        # design: 
        # integration: 

def get_category(n):
    cat = 'other'
    if 'test' in n.lower(): cat = 'test' 
    if 'verify' in n.lower(): cat = 'test' 
    if 'qualif' in n.lower(): cat = 'qual' 
    if "assembl" in n.lower(): cat = 'assemble'
    if "procure" in n.lower(): cat = 'procure'
    if 'install' in n.lower(): cat = 'install' 
    if 'integrat' in n.lower(): cat = 'integrate' 
    if 'shaft' in n.lower(): cat = 'shaft' 
    if 'require' in n.lower():  cat = 'require' 
    if 'design' in n.lower():  cat = 'design' 
    if "ground" in n.lower(): cat = 'ground'
    return cat

# this is not correct - not sure how to make it so.
def get_group_bad(area):
    grp=''
    if area=='16' or area=='17': grp='17-16'
    if area=='02': grp+='-2'
    elif area=='05' or area=='08': grp+='-5-8'
    elif area=='08': grp+='-8'
    elif area=='09' or area=='12': grp+='-9-12'
    elif area=='12': grp='-12'
    elif area=='06': grp='-6'
    elif area=='10': grp='-10'
    elif area=='13': grp='-13'
    elif area=='04': grp='-4'
    elif area=='03' or area=='11': grp='3-11'
    elif area=='11': grp='-11'
    elif area=='03': grp='-3'
    return grp

def get_group(an, ahigh, alow):
    n=an.lower()
    high=ahigh.lower()
    low=alow.lower()
    grp='none'
    if 'cooling' in n: grp='cooling' # ok
    if 'comb' in n or 'comb' in high: grp='comb' # ok
    if '(lts)' in n or '(lts)' in low: grp='laser-tran' # ok
    if 'interlock' in n: grp='interlocks' # ok
    if 'compress' in n: grp='air' # ok
    elif 'room' in n: grp='laser-room' # ok

    if 'interfero' in n or 'interfero' in high: grp='interferometry' # ok
    if 'vacuum' in n or 'vacuum' in high or 'vacuum' in low: grp='vac-sys' # ok
    if 'chamber' in n or 'tube' in n: grp='vac-tube' # ok
    if 'control' in n or 'control' in high: grp='controls' #ok
    # if 'DAQ' in n and 'sensor' in n: grp='DAQ-sensor' # leaving this one out for now
    if 'DAQ comput' in high: grp='DAQ-comp' # ok
    if 'electrical power' in n or 'electrical power' in low: grp='electrical'
    if 'mobile work' in n or 'mobile work' in low: grp='mobile'
    if 'platform' in n or 'platform' in low: grp='platform'
    if 'adjustable' in low: grp='supports'

    if 'fixture' in low: grp='assem-fix'
    if 'fixture' in low and 'install' in n: grp='install-fix'
    if 'fixture' in low and 'assembly' in n: grp='assem-fix'
    if 'crane' in n: grp='crane'
    if 'retroreflective mirror' in n or 'retroreflective mirror' in low: grp='mirror'
    if 'section camera' in n: grp='diag-camera'
    if 'science camera' in n: grp='sci-camera'
    if 'strongback' in n: grp='strongback'
    if 'rod end' in n: grp='rod'
    if 'magnetic field system' in high: grp='mag-field'
    if 'magnetic shield' in low: grp='mag-field'
    if 'strontium atom sourc' in high: grp='atom-src'
    if 'atom source' in n: grp='atom-src'
    if 'connection node' in high: grp='atom-connect'
    if 'wall of shaft' in low: grp='shaft-wall'

    return grp


def filter_by_paths(g, ps, later_id, earlier_id):
    print(f"filtering by paths")
    anp=set()
    # nodes is list of (node_num, node_data)
    for p in ps:
        for n in p:
            anp.add(n)

    # for n in g.nodes(data=True):
    #     if n[1]['wbs'].startswith(wbs): 
    #         anp.add(n[0])
    #         for e in g.in_edges(n[0]):
    #             anp.add(e[0])
    #             anp.add(e[1])
    #         for e in g.out_edges(n[0]):
    #             anp.add(e[0])
    #             anp.add(e[1])

    return g.subgraph(list(anp))

class GNode:
    header = ['code', 'name', 'wbs', 'area', 'status', 'drv_flag','task_type', 'type', 'rsrc_type', 'cost','dur', 
              'category', 'group', 'wbs_high', 'wbs_low', 'task_id', 'total_float', 'free_float',
              'target_start', 'target_end', 'early_start','early_end','late_start','late_end','actual_start','actual_end']

    def record(self):
        return [self.n, self.name, self.wbs, self.area, self.status, self.drv, self.task_type, self.typ, 
                self.rsrc, self.cost, self.dur, self.category, self.group, self.wbs_high, self.wbs_low, self.task_id,
                self.total_float_hr, self.free_float_hr,
                self.t_start, self.t_end, self.e_start, self.e_end, self.l_start, self.l_end,self.a_start, self.a_end]

    def __init__(self,g,n):
        #print(f'building GNode for {n}')
        now = dt.datetime.now().date()
        self.n = g.nodes[n]['id']
        self.task_id = g.nodes[n]['task_id']
        self.t_end=g.nodes[n]['target_end']
        self.e_end=g.nodes[n]['early_end']
        self.l_end = g.nodes[n]['late_end']
        self.t_start=g.nodes[n]['target_start']
        self.e_start=g.nodes[n]['early_start']
        self.l_start=g.nodes[n]['late_start']
        self.a_start=g.nodes[n]['actual_start']
        self.a_end=g.nodes[n]['actual_end']
        self.name=g.nodes[n]['name']
        self.dur=g.nodes[n]['target_dur_hr']
        self.total_float_hr=g.nodes[n]['total_float_hr']
        self.free_float_hr=g.nodes[n]['free_float_hr']
        self.drv=g.nodes[n]['driving_flag']
        self.wbs=g.nodes[n]['wbs']
        self.status=g.nodes[n]['status']
        self.task_type=g.nodes[n]['task_type']
        self.typ=g.nodes[n]['type']
        self.rsrc=g.nodes[n]['rsrc_type']
        self.cost=g.nodes[n]['target_cost']
        self.area=int(g.nodes[n]['area'])
        self.wbs_high=g.nodes[n]['wbs_high']
        self.wbs_low=g.nodes[n]['wbs_low']
        self.category=get_category(self.name)
        self.group=get_group(self.name, self.wbs_high, self.wbs_low)
        self.areacol=funs.colors[self.area]
        #print(self.areacol)
        tmp_end = pd.to_datetime(self.t_end).date()
        tmp_start = pd.to_datetime(self.t_start).date()
        self.late = (self.status=='TK_Active' or self.status=='TK_NotStart') and tmp_end<now
        self.delayed = (self.status=='TK_NotStart') and tmp_start<now
        #print(f'flag = {tmp_late}, {tmp_delayed}')
        self.fontcolor = 'yellow' if self.late else 'white' if self.delayed else 'black'
        self.shape = 'box3d' if self.drv=='Y' else 'rect' if self.typ=='M' else 'ellipse'


    def long_name(self):
        rc = f"{self.typ}/{self.n}\n{self.name}\nTS={self.t_start} / TE={self.t_end}"
        if self.t_start!=self.e_start or self.t_end!=self.e_end:
            rc = rc + f'\nES={self.e_start} / EE={self.e_end}' 
        if self.t_start!=self.l_start or self.t_end!=self.l_end:
            rc = rc + f'\nLS={self.l_start} / LE={self.l_end}'
        rc = rc + f"\nwbs={self.wbs} / drv={self.drv} / dur={self.dur} / stat={self.status} / float={self.total_float_hr}"
        if self.cost != '-' or self.rsrc != '-':
            rc = rc + f"\ncost={self.cost}/rsrc={self.rsrc}"
        return rc

    def short_name(self):
        return f"{self.typ}/{self.n}\n{self.name}\ndrv={self.drv}/wbs={self.wbs}"


def write_all(g,args):
    fname=f'output/alltasks_{args.date_part}.csv'
    f = open(fname,'w',newline='', encoding='utf-8')
    w = csv.writer(f)
    w.writerow(GNode.header)
    #w.writerows(tab[2:])
    collect_areas = set()
    for n in g.nodes(data=True):
        node = GNode(g,n[0])
        collect_areas.add(node.area)
        w.writerow(node.record())
    return collect_areas

def write_areas(g_init,areas,args):
    print(f'writing all areas')
    fname=f'output/allareas_{args.date_part}.csv'
    f = open(fname,'w',newline='', encoding='utf-8')
    w = csv.writer(f)
    w.writerow(["code", "path"])
    for a in areas:
        g = funs.filter_by_wbs(g_init,f'{a:02d}')
        for n in g.nodes(data=True):
            node = GNode(g,n[0])
            w.writerow([node.n,a])

def render_all(g,args):

    dot=gv.Digraph(comment='sched',strict=True, format=args.output_format)
    for n in g.nodes(data=True):
        node = GNode(g,n[0])
        col='crimson' if n[0] in args.special_list else 'black'
        pw = 1.0 if col=='black' else 15.0
        mylabel=node.long_name() if args.show_dates else node.short_name()
        #print(mylabel, col, node.shape, n[0])
        dot.node(str(n[0]),label=mylabel,color=col,shape=node.shape, fillcolor=node.areacol, fontcolor=node.fontcolor, style='filled',penwidth=str(pw))

    for e in g.edges(data=True):
        dot.edge(str(e[0]),str(e[1]), label=f'{e[2]["pred_type"]}', color='black')

    reduced = "wr" if args.do_reduction else "wor"
    fname=f'output/nx_{args.wbs_item}_{reduced}'
    #dot.render(fname+'.dot', view=False).replace('\\', '/')
    dot.render(fname, view=args.render).replace('\\', '/')

def filter_driving(g,args):
    anp=set()
    # nodes is list of (node_num, node_data)
    for n in g.nodes(data=True):
        if n[1]['driving_flag']=='Y': 
            anp.add(n[0])
            #for e in g.in_edges(n[0]):
            #    anp.add(e[0])
            #    anp.add(e[1])
            #for e in g.out_edges(n[0]):
            #    anp.add(e[0])
            #    anp.add(e[1])
    print(f'added {anp}')
    return g.subgraph(list(anp))

def filter_no_inout(g):
    anp=set()
    for n in g.nodes(data=True):
        if len(g.in_edges(n[0])) == 0:
            print(f"zero in edges: {n[0]}")
        if len(g.out_edges(n[0])) == 0:
            print(f"zero out edges: {n[0]}")

if __name__ == "__main__":

    args = getargs.get_args()
    tables = {t:read_tab(t,args.date_part) for t in tabs}

    g_init = make_task_graph(tables, args)
    
    if args.write_csv:
        areas=write_all(g_init, args)
        sys.exit(0)
    
    g = g_init
    filter_no_inout(g)

    if args.only_wbs_paths:
        areas=write_all(g_init, args)
        write_areas(g,areas, args)
        sys.exit(0)

    if args.wbs_filter:
        g = funs.filter_by_wbs(g,args.wbs_item)
        render_all(g,args)
        sys.exit(0)

    if args.only_driving:
        g = filter_driving(g,args)
        render_all(g,args)
        sys.exit(0)

    # otherwise track from later id back to earlier id
    later_id=tables['TASK'].loc[tables['TASK']['task_code']==args.later_code].task_id.iloc[0]
    earlier_id=tables['TASK'].loc[tables['TASK']['task_code']==args.earlier_code].task_id.iloc[0]
    ps = nx.all_simple_paths(g_init, later_id, earlier_id)
    g = filter_by_paths(g, ps, later_id, earlier_id)
    render_all(g,args)
    print(f'number of simple paths: {len(list(ps))}')

    

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