
import dumpsheet as ds
import sys
import pandas as pd
import csv

datepart='Dec2022FY24ScenarioUpdated'
head=6370897
search_start='A1803050'
old_top=13425503

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)

xer,acts,rels = ds.just_read_file(f"input/schedule_{datepart}.xer")

# this is all the WBS information.  See wbs_id, parent_wbs_id, 

def not_needed1():
    #df_wbs.set_index("wbs_id",inplace=True)
    #print(pd.unique(df['actv_code_id']))
    #print(df_wbs.head())

    # NOTE: the parent of all is not in the set of wbs_id
    #print(df_wbs.loc[6370897]) # parent of all
    #print(df_wbs.loc[13425503]) # children of parent of all

    d=["_accounts","_activitycodes","_acttypes","_actvcodes","_calendars","_currencies","_data","_fintmpls","_nonworks","_obss","_pcattypes","_pcatvals","_predecessors","_projects","_projpcats","_rcattypes","_rcatvals","_resources","_rolerates","_roles","_rsrccats","_rsrcrates","_rsrcurves","_schedoptions","_taskprocs","_udftypes","_udfvalues","_wbss","accounts","activitycodes","activityresources","acttypes","actvcodes","calendars","create_object","currencies","current_headers","current_table","file","fintmpls","get_num_lines","nonworks","obss","pcattypes","pcatvals","projects","projpcats","rcattypes","rcatvals","relations","resourcecategories","resourcecurves","resourcerates","resources","rolerates","roles","scheduleoptions","summary","taskprocs","udftypes","udfvalues","wbss"]
    bad=["_activityresources",]

    items=xer.activitycodes.get_tsv()[2:]
    header=xer.activitycodes.get_tsv()[1]
    df_actcodes = pd.DataFrame(list(items),columns=header)
    #print(pd.unique(df_actcodes['actv_code_id']))
    #print(df_actcodes.head())

    #tsv=xer.activities.get_tsv()
    #print(tsv[1])

def get_tables(xer):
    items=xer.wbss.get_tsv()[2:]
    header=xer.wbss.get_tsv()[1]
    df_wbs = pd.DataFrame(list(items),columns=header)
    df_wbs.to_csv("input/tmp_wbs.csv")
    #df_wbs.set_index("parent_wbs_id",inplace=True)
    #df_wbs.reset_index(names=["parent_wbs_id"],inplace=True)
    df_wbs.set_index("wbs_id",inplace=True)

    items=xer.activities.get_tsv()[2:]
    header=xer.activities.get_tsv()[1]
    df_acts = pd.DataFrame(list(items),columns=header)
    df_acts.to_csv("input/tmp_acts.csv")
    df_acts_i = df_acts #.set_index('task_code')

    return (df_acts_i, df_wbs)

# print(df_acts_i.head(5))
# now use the wbs_id as key to df_wbs, and run up the WBS tree to top
# print task_code -> [WBS tree]
# print(df_wbs.columns)
# print(df_wbs.loc[6370897])
# print(df_wbs.loc[13425503]) # children of parent of all
#for x in df_acts.iterrows(): id = x

# WARNING: working schedule WBS ID can change, the head seems to remain the same
# MAGIS working schedule = 13425503
# Head of all = 6370897

def get_path(wbsid_start, df_wbs, top):
    last=None
    lastid=None
    #currid = df_acts_i.loc['A0206010'].wbs_id
    currid = wbsid_start
    path=[(0,'None')]
    while currid!=top: 
        if not currid in df_wbs.index: break
        curr=df_wbs.loc[ currid ]
        nextid=curr.parent_wbs_id
        name=curr.wbs_name
        #print(f"start {wbsid_start} current {currid}, parent {nextid}, name {name}")
        #print(curr.wbs_short_name)
        #path.append((currid,curr.wbs_name))
        path.append((curr.wbs_short_name,curr.wbs_name))
        last=curr
        lastid=currid
        currid=nextid
        #if currid not in df_wbs: break
    #print(currid, lastid, path[-3:])
    return (currid, lastid, last.wbs_name, path[-3:])

#print(f"good one = {last['wbs_id']}, name is {last['wbs_name']}")


#for t in xer._activitycodes.get_tsv()[2:40]:
#    print(t)

task_code = 'A0206010'
df_acts, df_wbs = get_tables(xer)
#wbs_id = df_acts.loc[task_code].wbs_id
#lastid, lastname = get_path(wbs_id, df_wbs)
#print(f'{task_code}, {wbs_id}, {lastid}, {lastname}')

#print(df_acts.iloc[1])
#print(df_wbs.iloc[1])
#print(df_wbs.head())

top = xer.activities.find_by_code(search_start)
print(top.task_id, top.task_name, top.wbs_id)
top_id = top.wbs_id
top_curr_id, top_last_id, top_last_name, path = get_path(top_id, df_wbs, 0)
# I want top_last_id
print(top_id, top_curr_id, top_last_id, top_last_name)
#sys.exit(0)

f = open(f"input/report_{datepart}_parents.csv",'w',newline='')
w = csv.writer(f)
w.writerow(
    ["task_id", "task_code", "wbs_id", "area", "parent_wbs_id", "parent_name", 'L3', "L2", "L1", "N3","N2","N1"]
    )

id_set = set()
for i,r in df_acts.iterrows():
    curr_id, lastid, lastname, path = get_path(r['wbs_id'], df_wbs, top_last_id)
    id_set.add(lastid)
area={v:k for k,v in enumerate(id_set)}

#for a in area.items():
#    print(f'area {a[0]}={a[1]}')

for i,r in df_acts.iterrows():
#for id,code in zip(df_acts.wbs_id, df_acts.task_code):
    #if r['task_code']=='A0902010': 
    #    print(f"---------------got it: {r}")
    currid, lastid, lastname, path = get_path(r['wbs_id'], df_wbs, top_last_id)
    w.writerow([r['task_id'],r['task_code'], r['wbs_id'], area[lastid], lastid, lastname, path[0][0],path[1][0],path[2][0],path[0][1],path[1][1],path[2][1] ])
    #print(f'{code}, {id}, {lastid}, {lastname}')
