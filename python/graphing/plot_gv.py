
import graphviz as gv
import networkx as nx
from xerparser.reader import Reader
import sys
import datetime as dt
import dumpsheet as ds

output_format = 'png'

def make_sample_graph():
    dot = gv.Digraph(comment='sched')
    dot.node("A","name1")
    dot.node("B","name2")
    dot.edge("A","B", constraint='false')
    dot.render('tmp.gv').replace('\\', '/')
    dot.render('tmp.gv', view=True)

gvdb = {}

def gv_add_node(first_id, last, dot, xer, tot, special):
    first = xer.activities.find_by_id(first_id)
    #print(f'adding node {first.task_id}, {first.task_code} / {first.task_name}')
    rc=False

    if first.task_id in gvdb:
        #print(f'{first.task_id} already processed completely')
        return gvdb[first.task_id]

    if first.task_type == 'TT_FinMile':
        desc = f'{first.task_code}\n{first.task_name[0:]}'
        col='purple'
    else:
        desc = f'{first.task_code}\n{first.task_name[0:25]}'
        col='black'

    shape = 'rect' if first.task_code in special else 'ellipse'

    if first.task_id == last.task_id:
        dot.node(str(first.task_id), label=desc,color=col, shape=shape)
        #print("hit first == last")
        return True

    preds = xer.relations.get_predecessors(first.task_id)

    if len(preds)==0:
        # print(f"hit end of path {first.task_code}")
        return False

    for p in preds:
        tmp = gvdb.get(p.pred_task_id,None)
        #if tmp!=None and tmp==True: continue
        if gv_add_node(p.pred_task_id,last, dot,xer, tot+1, special):
        # pact = xer.activities.find_by_id(p.pred_task_id)
            dot.edge(str(p.task_id), str(p.pred_task_id), color='blue')
            rc=True

    if rc:
        #print(f'adding intermediate node {first.task_code}')
        dot.node(str(first.task_id), label=desc,color=col,shape=shape)

    gvdb[first.task_id] = rc

    # depth of recursion allowed
    # if tot>3: return
    #print(f'finishing node {first.task_id}')
    return rc

def use_gv(first, last, xer, special):
    print(f"starting point: task_id={first.task_id}, task_code={first.task_code}, {first.task_name}, task_type={first.task_type}")

    dot=gv.Digraph(comment='sched',strict=True, format=output_format)
    gv_add_node(first.task_id,last, dot,xer,0,special)
    # gv_go_up(first.task_id,dot,xer,0)
    fname=f'output/gv_{first.task_code}_{last.task_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)


def process_gv(first_code, last_code, special):
    xer,acts,rels = ds.just_read_file()
    typ = 'TT_FinMile'

    first = xer.activities.find_by_code(first_code)
    last = xer.activities.find_by_code(last_code)

    # first= xer.activities.find_by_code('A1206140')
    # print(dir(first))
    # now = dt.datetime.now()
    # st_date = first.target_start_date
    # en_date = first.target_end_date
    # stat_code = first.status_code
    # dur = en_date - st_date
    # till_end = en_date-now
    # till_start = now-st_date
    # print(f'{first.task_code} {stat_code} {st_date} {en_date} {till_start} {till_end}')
    # sys.exit(0)

    use_gv(first, last, xer, special)

import args

if __name__ == '__main__':

    first_code, last_code, special = args.process_args(sys.argv)
    # using graphviz directly
    process_gv(first_code, last_code,special)

# example of get successors and predecessors
#print(xer.relations.get_successors(acts[0].task_id))
#print(xer.relations.get_predecessors(acts[0].task_id))

# example of going through all relations
#for pred in xer.relations:
#    print(pred, pred.task_pred_id, pred.pred_task_id)
# print(r.relations.get_predecessors(9478273))

# don't do it like this
#p = list(xer._predecessors)
#t = list(xer._tasks)

