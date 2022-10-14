from hmac import trans_5C
import graphviz as gv
import networkx as nx
from xerparser.reader import Reader
import sys

def make_sample_graph():
    dot = gv.Digraph(comment='sched')
    dot.node("A","name1")
    dot.node("B","name2")
    dot.edge("A","B", constraint='false')
    dot.render('tmp.gv').replace('\\', '/')
    dot.render('tmp.gv', view=True)


def gv_go_up(first_id,dot, xer, tot):
    first = xer.activities.find_by_id(first_id)
    succs = xer.relations.get_successors(first.task_id)

    if tot>5: return

    for s in succs:
        sact = xer.activities.find_by_id(s.task_id)
        extra = sact.task_name if sact.task_type=='TT_FinMile' else "T"
        if first.task_type == 'TT_FinMile' or True:
            if sact.task_type != 'TT_FinMile' or True:
                dot.node(str(sact.task_id), f'{sact.task_code}/{extra[0:20]}')

            # print(f'  up edge id={s.task_id}, pred={s.pred_task_id}')
            dot.edge(str(s.task_id), str(s.pred_task_id), color='gray')

    for s in succs:    
        gv_go_up(s.task_id,dot,xer, tot+1)

gvdb = {}

def gv_add_node(first_id, last, dot, xer, tot):
    first = xer.activities.find_by_id(first_id)
    #print(f'adding node {first.task_id}, {first.task_code} / {first.task_name}')
    rc=False

    if first.task_id in gvdb:
        print(f'{first.task_id} already processed completely')
        return gvdb[first.task_id]

    if first.task_type == 'TT_FinMile':
        desc = f'{first.task_code}/{first.task_name[0:]}'
    else:
        desc = f'{first.task_code}'

    if first.task_id == last.task_id:
        dot.node(str(first.task_id), desc)
        print("hit first == last")
        return True

    preds = xer.relations.get_predecessors(first.task_id)

    if len(preds)==0:
        # print(f"hit end of path {first.task_code}")
        return False

    for p in preds:
        tmp = gvdb.get(p.pred_task_id,None)
        #if tmp!=None and tmp==True: continue
        if gv_add_node(p.pred_task_id,last, dot,xer, tot+1):
        # pact = xer.activities.find_by_id(p.pred_task_id)
            dot.edge(str(p.task_id), str(p.pred_task_id), color='blue')
            rc=True

    if rc:
        print(f'adding intermediate node {first.task_code}')
        dot.node(str(first.task_id), desc)

    gvdb[first.task_id] = rc

    # depth of recursion allowed
    # if tot>3: return
    #print(f'finishing node {first.task_id}')
    return rc

def use_gv(first, last, xer):
    print(f"starting point: task_id={first.task_id}, task_code={first.task_code}, {first.task_name}, task_type={first.task_type}")

    dot=gv.Digraph(comment='sched',strict=True, format='pdf')
    gv_add_node(first.task_id,last, dot,xer,0)
    # gv_go_up(first.task_id,dot,xer,0)
    fname=f'gv_{first.task_code}_{last.task_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)


def process_gv(first_code, last_code):
    xer = Reader("../MAGIS Status with August 2022 Input.xer")
    acts = list(xer.activities)
    rels = list(xer.relations)
    typ = 'TT_FinMile'

    first = xer.activities.find_by_code(first_code)
    last = xer.activities.find_by_code(last_code)
    use_gv(first, last, xer)

alldb = set()

def nx_add_node(first_id, g, xer, tot):
    first = xer.activities.find_by_id(first_id)

    if first.task_code in alldb:
        return

    extra = "M" if first.task_type=='TT_FinMile' else "T"
    g.add_node(first.task_code, name=first.task_name, type=extra)
    alldb.add(first.task_code)
    preds = xer.relations.get_predecessors(first.task_id)

    for p in preds:
        # this is a bad way to do it - looking for acts by id to find code
        # could use the task_id as the identifier for nodes and edges
        pact = xer.activities.find_by_id(p.pred_task_id)
        act = xer.activities.find_by_id(p.task_id)
        extra = "M" if pact.task_type=='TT_FinMile' else "T"
        g.add_edge(act.task_code, pact.task_code)

    for p in preds:    
        nx_add_node(p.pred_task_id,g,xer,tot+1)

    print(f'done with node {first.task_code} level {tot}')
    return True

def process_nx(first_code, last_code):
    xer = Reader("../MAGIS Status with August 2022 Input.xer")
    acts = list(xer.activities)
    rels = list(xer.relations)
    typ = 'TT_FinMile'

    first = xer.activities.find_by_code(first_code)
    g=nx.DiGraph()
    print("starting build of graph")
    nx_add_node(first.task_id,g,xer,0)
    print("starting find of paths")
    ps = nx.all_simple_paths(g, first_code, last_code)

    dot=gv.Digraph(comment='sched',strict=True, format='pdf')

    for p in ps:
        print(p)
        for i in range(len(p)-1):
            dot.edge(p[i],p[i+1], color='blue')

    fname=f'nx_{first_code}_{last_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)


if __name__ == '__main__':

    # some interesting codes
    ids=['A1503560' # laser-atom interactions
        ,'A1503530' # two atom sources installed
        ,'A0201090' # atom source two 100% complete
        ,'A1206110' # Milestone - Phase 2 shaft installation complete
        ,'A1503540' # CRITICAL Milestone - First laser beam
        ,'A1803230' # INDICATOR Milestone - First Atoms
        ,'A1503520' # CRITICAL - Shaft Modular Sections Installed
    ]

    # other interesting starting / ending points
    # remember that last means furtherest predecessor, or earlier one

    #first_code='A1503560' # laser-atom interactions
    #first_code='A1503570' # INDICTOR - shaft modular section installed
    #last_code='A1004010'  # DAQ for modular assembly shipped
    #last_code='A0101000'  # DOE project start
    #last_code='A1503790'  # installation of 17 modular sections

    if len(sys.argv) >2:
        first_code=sys.argv[1]
        last_code=sys.argv[2]
    else:
        first_code='A1503560' # laser-atom interactions
        first_code='A1206110' # Milestone - Phase 2 shaft installation complete
        last_code='A1004010'  # DAQ for modular assembly shipped
        last_code='A1503500'  # CRITICAL - civil design for shaft complete

    # using graphviz directly
    process_gv(first_code, last_code)

    # using networkx to find all paths from last to first
    process_nx(first_code, last_code)



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

