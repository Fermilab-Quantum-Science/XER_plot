import graphviz as gv
import networkx as nx
from xerparser.reader import Reader
import sys

def make_sample_graph():
    dot = gv.Digraph(comment='sched')
    dot.node("A","name1")
    dot.node("B","name2")
    dot.edge("A","B", constraint='false')
    dot.render('doctest-output/tmp.gv').replace('\\', '/')
    dot.render('doctest-output/tmp.gv', view=True)


def process_up(first_id,dot, tot, parent_ms=False):
    first = xer.activities.find_by_id(first_id)
    succs = xer.relations.get_successors(first.task_id)

    if tot>5: return

    for s in succs:
        sact = xer.activities.find_by_id(s.task_id)
        extra = sact.task_name if sact.task_type=='TT_FinMile' else "T"
        if first.task_type == 'TT_FinMile' or True:
            if sact.task_type != 'TT_FinMile' or True:
                dot.node(str(sact.task_id), f'{sact.task_code}/{extra[0:18]}')

            print(f'  up edge id={s.task_id}, pred={s.pred_task_id}')
            dot.edge(str(s.task_id), str(s.pred_task_id), color='gray')

    for s in succs:    
        process_up(s.task_id,dot,tot+1,parent_ms)


def process_node(first_id,dot, tot,parent_ms=False):
    first = xer.activities.find_by_id(first_id)
    print(f'adding node {first.task_id}, {first.task_code} / {first.task_name}')

    if first.task_type != 'TT_FinMile':
        pass # return
    else:
        dot.node(str(first.task_id), f'{first.task_code}/{first.task_name[0:]}')

    if tot>3: return

    preds = xer.relations.get_predecessors(first.task_id)

    for p in preds:
        pact = xer.activities.find_by_id(p.pred_task_id)
        extra = "M" if pact.task_type=='TT_FinMile' else "T"
        if first.task_type == 'TT_FinMile' or True:
            if pact.task_type != 'TT_FinMile':
                dot.node(str(pact.task_id), f'{extra}/{pact.task_code}')

            #print(f'  adding edge {p.task_id}, {p.pred_task_id}')
            dot.edge(str(p.task_id), str(p.pred_task_id), color='blue')

    for p in preds:    
        process_node(p.pred_task_id,dot,tot+1,parent_ms)
    #print(f'finishing node {first.task_id}')

def do_one(first_id, first, xer):
    # interesting attributes
    first = xer.activities.find_by_code(first_id)
    print(dir(xer.activities))
    print(f"starting point: task_id={first.task_id}, task_code={first.task_code}, {first.task_name}, task_type={first.task_type}")

    dot=gv.Digraph(comment='sched',strict=True, format='png')
    process_node(first.task_id,dot,0)
    process_up(first.task_id,dot,0)
    fname=f'graph_{first_id}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)

def process(func):
    xer = Reader("../MAGIS Status with August 2022 Input.xer")
    acts = list(xer.activities)
    rels = list(xer.relations)
    typ = 'TT_FinMile'

    if len(sys.argv) >1:
        first_id=sys.argv[1]
        ids=[first_id]
    else:
        print("Using list")
        ids=['A1503560' # laser-atom interactions
            ,'A1503530' # two atom sources installed
            ,'A0201090' # atom source two 100% complete
            ,'A1206110' # Milestone - Phase 2 shaft installation complete
            ,'A1503540' # CRITICAL Milestone - First laser beam
            ,'A1803230' # INDICATOR Milestone - First Atoms
            ,'A1503520' # CRITICAL - Shaft Modular Sections Installed
        ]
        ids=['A1503780']

    for id in ids:
        func(id, first, xer)

def using_nx(id, first, xer):
    dot=gv.Digraph(comment='sched',strict=True, format='png')
    process_node(first.task_id,dot,0)
    process_up(first.task_id,dot,0)
    fname=f'graph_{first_id}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)

# using graphviz directly
process(do_one)

# using networkx to find all paths from last to first
process(using_nx)



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

