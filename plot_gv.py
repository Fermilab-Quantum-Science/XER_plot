
from tkinter import W
import graphviz as gv
import networkx as nx
from xerparser.reader import Reader
import sys
import datetime as dt

output_format = 'png'

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
    fname=f'gv_{first.task_code}_{last.task_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)


def process_gv(first_code, last_code, special):
    xer = Reader("../MAGIS Status with August 2022 Input.xer")
    acts = list(xer.activities)
    rels = list(xer.relations)
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


def just_read_file():
    xer = Reader("../MAGIS Status with August 2022 Input.xer")
    acts = list(xer.activities)
    rels = list(xer.relations)
    return (xer,acts,rels)


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

    inter={
        '1':['A1004010','A1503500','A1503240','A1503770','A1206100','A1503790','A1503570','A1503520','A1206110']
        ,'2':['A0201090','A0214020','A1503570','A1503530']
        ,'3':['A0307030','A0301050','A1503760','A1503330','A1802570','A0309020','A1802380','A1503220','A1004030','A1503590','A1503540']
        ,'4':['A0501050','A0201090','A0607010','A1203180','A0508020','A1802360','A1004020','A0214020','A1802370','A1803230','A1803240']
        ,'5':['A1503280','A1802240','A1803330','A1802330','A1802340','A1004040','A1503560','A1503600']
        ,'none':[]
    }
    inter_names={
        '5':'Laser-atom interactions',
        '4':'First atoms',
        '3':'First laser beam',
        '2':'Two atom sources installed',
        '1':'Shaft modular sections installed'
    }


    # other interesting starting / ending points
    # remember that last means furtherest predecessor, or earlier one
    # root = first (earliest), leaf = last (latest)
    # successors of leaf point earlier (confusing)
    # predecessors of leaf point latest (confusing)

    #first_code='A1503560' # laser-atom interactions
    #first_code='A1503570' # INDICTOR - shaft modular section installed
    #last_code='A1004010'  # DAQ for modular assembly shipped
    #last_code='A0101000'  # DOE project start
    #last_code='A1503790'  # installation of 17 modular sections

    if len(sys.argv)==2 and (sys.argv[1]=='help' or sys.argv[1]=='--help'):
        print("usage: <key from below> <latest task code> <earliest task code>")
        for k,v in inter_names.items():
            print(f'{k}\t{v}')
        sys.exit(0)    

    if len(sys.argv)>1:
        special=sys.argv[1]
    else:
        special=['1']

    print(f'using list named {inter_names[special]}')
    special = inter[special]

    # default codes to use
    first_code = special[-1]
    last_code = special[0]

    if len(sys.argv) >3:
        first_code=sys.argv[2]
        last_code=sys.argv[3]

    # more examples
    #first_code='A1503560' # laser-atom interactions
    #first_code='A1206110' # Milestone - Phase 2 shaft installation complete
    #first_code='A1004010'  # DAQ for modular assembly shipped
    #first_code='A1503240' # construction bid
    #last_code='A1004010'  # DAQ for modular assembly shipped
    #last_code='A1503500'  # CRITICAL - civil design for shaft complete
    #last_code='A0101000'  # DOE project start
    #last_code='A0100000'  # start?


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

