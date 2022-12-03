
import dumpsheet as ds
import sys
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)

xer,acts,rels = ds.just_read_file()

# this is all the WBS information.  See wbs_id, parent_wbs_id, 

items=xer.wbss.get_tsv()[2:]
header=xer.wbss.get_tsv()[1]
df_wbs = pd.DataFrame(list(items),columns=header)
df_wbs.set_index("parent_wbs_id",inplace=True)
#df_wbs.set_index("wbs_id",inplace=True)
#print(pd.unique(df['actv_code_id']))
#print(df_wbs.head())

# NOTE: the parent of all is not in the set of wbs_id
print(df_wbs.loc[6370897]) # parent of all
print(df_wbs.loc[13425503]) # children of parent of all

d=["_accounts","_activitycodes","_acttypes","_actvcodes","_calendars","_currencies","_data","_fintmpls","_nonworks","_obss","_pcattypes","_pcatvals","_predecessors","_projects","_projpcats","_rcattypes","_rcatvals","_resources","_rolerates","_roles","_rsrccats","_rsrcrates","_rsrcurves","_schedoptions","_taskprocs","_udftypes","_udfvalues","_wbss","accounts","activitycodes","activityresources","acttypes","actvcodes","calendars","create_object","currencies","current_headers","current_table","file","fintmpls","get_num_lines","nonworks","obss","pcattypes","pcatvals","projects","projpcats","rcattypes","rcatvals","relations","resourcecategories","resourcecurves","resourcerates","resources","rolerates","roles","scheduleoptions","summary","taskprocs","udftypes","udfvalues","wbss"]
bad=["_activityresources",]

items=xer.activitycodes.get_tsv()[2:]
header=xer.activitycodes.get_tsv()[1]
df_actcodes = pd.DataFrame(list(items),columns=header)
#print(pd.unique(df_actcodes['actv_code_id']))
print(df_actcodes.head())

#tsv=xer.activities.get_tsv()
#print(tsv[1])
items=xer.activities.get_tsv()[2:]
header=xer.activities.get_tsv()[1]
df_acts = pd.DataFrame(list(items),columns=header)
print(df_acts.head())
# now use the wbs_id as key to df_wbs, and run up the WBS tree to top
# print task_code -> [WBS tree]
df_wbs.reset_index(names=["parent_wbs_id"],inplace=True)
df_wbs.set_index("wbs_id",inplace=True)
print(df_wbs.columns)
#print(df_wbs.loc[6370897])
print(df_wbs.loc[13425503]) # children of parent of all
for x in df_acts.iterrows():
    id = x


#for t in xer._activitycodes.get_tsv()[2:40]:
#    print(t)

sys.exit(0)

for x in d:
    item=getattr(xer,x)
    print(x,"====>",dir(item))
    itemlist=list(item)
    print(x,"---->",itemlist)
