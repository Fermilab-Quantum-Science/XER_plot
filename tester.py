
import dumpsheet as ds
import sys
import pandas as pd
import csv

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)

xer,acts,rels = ds.just_read_file("schedule_Aug2022.xer")

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
    #df_wbs.set_index("parent_wbs_id",inplace=True)
    #df_wbs.reset_index(names=["parent_wbs_id"],inplace=True)
    df_wbs.set_index("wbs_id",inplace=True)

    items=xer.activities.get_tsv()[2:]
    header=xer.activities.get_tsv()[1]
    df_acts = pd.DataFrame(list(items),columns=header)
    df_acts_i = df_acts #.set_index('task_code')

    return (df_acts_i, df_wbs)

# print(df_acts_i.head(5))
# now use the wbs_id as key to df_wbs, and run up the WBS tree to top
# print task_code -> [WBS tree]
# print(df_wbs.columns)
# print(df_wbs.loc[6370897])
# print(df_wbs.loc[13425503]) # children of parent of all
#for x in df_acts.iterrows(): id = x

# MAGIS working schedule = 13425503
# Head of all = 6370897

def get_path(wbsid_start, df_wbs):
    last=None
    lastid=None
    #currid = df_acts_i.loc['A0206010'].wbs_id
    currid = wbsid_start
    path=[]
    while currid!=13425503: 
        curr=df_wbs.loc[ currid ]
        nextid=curr.parent_wbs_id
        name=curr.wbs_name
        #print(f"current {currid}, parent {nextid}, name {name}")
        last=curr
        lastid=currid
        currid=nextid
    return (lastid, last.wbs_name)

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

#sys.exit(0)

f = open("report_Aug2022_parents.csv",'w',newline='')
w = csv.writer(f)
w.writerow(
    ["task_id", "task_code", "wbs_id", "area", "parent_wbs_id", "parent_name"]
    )

id_set = set()
for i,r in df_acts.iterrows():
    lastid, lastname = get_path(r['wbs_id'], df_wbs)
    id_set.add(lastid)
area={v:k for k,v in enumerate(id_set)}

for i,r in df_acts.iterrows():
#for id,code in zip(df_acts.wbs_id, df_acts.task_code):
    lastid, lastname = get_path(r['wbs_id'], df_wbs)
    w.writerow([r['task_id'],r['task_code'], r['wbs_id'], area[lastid], lastid, lastname])
    #print(f'{code}, {id}, {lastid}, {lastname}')
