

import graphviz as gv
import networkx as nx
import sys
import datetime as dt
import dumpsheet as ds

output_format = 'png'
alldb = set()

def nx_add_node(first_id, g, xer, tot):
    first = xer.activities.find_by_id(first_id)

    if first.task_code in alldb:return

    extra = "M" if first.task_type=='TT_FinMile' else "T"

    now = dt.datetime.now()
    st_date = first.target_start_date
    en_date = first.target_end_date
    ES = first.early_start_date
    EF = first.early_end_date
    LS = first.late_start_date
    LF = first.late_end_date
    duration = first.duration
    stat_code = first.status_code
    dur = (en_date - st_date).days
    till_end = en_date-now
    till_start = now-st_date

    if not ES:
        ES = st_date
        LS = st_date
        EF = en_date
        LF = en_date

    # print(f'adding {first.task_code}; {st_date};{en_date};{stat_code};{st_date<now};{en_date>now}')

    if duration != dur or duration != (EF-ES).days:
        print(f'adding {first.task_code}; {extra}; sched_dur={duration}; en-st={dur}; EF-ES={(EF-ES).days}; LF-LS={(LF-LS).days}')
    else:
        print(f'adding {first.task_code}; {extra}; sched_dur={duration}')
    
    g.add_node(first.task_code, name=first.task_name, type=extra
        , target_start=st_date, target_end=en_date, duration=duration
        , until_end=till_end, until_start=till_start
        , early_start=ES, early_end=EF, late_start=LS, late_end=LF
        , start_date=first.start_date, end_date=first.end_date
        )
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

    # print(f'done with node {first.task_code} level {tot}')
    return True

# forward - from root to leaf, fill in start day as ES (and EF)
# since dates are set, the only thing to do is propagate the t0 date so that
# early_start - t0_date can be calculated (turn it into days).  I think I 
# can do this for early_end, and perhaps for late_start and late_end.
# forward action for critical path using ES, EF, and duration
def process_longest_dur(g,root, leaf):

    ps=list(g.successors(leaf)) # earlier tasks
    #print(f'successors of leaf {leaf} are {ps}')
    my_dur = g.nodes[leaf]['duration']
    early_start = g.nodes[leaf]['early_start']
    early_end = g.nodes[leaf]['early_end']
    late_start = g.nodes[leaf]['late_start']
    late_end = g.nodes[leaf]['late_end']

    if not early_end or not early_start: 
        print(leaf,g.nodes[leaf]['type'],"-------------")

    # or should duration be my_dur? No.
    # this should be early_end - t0_date I think.
    duration = (early_end - early_start).days

    if len(ps)==0:
        # warning - this is hit on every path exploration
        #print(f'at end of processing {leaf}')
        LS=(late_start-early_start).days
        LF=LS+my_dur
        g.nodes[leaf]['longest_dur'] = my_dur
        g.nodes[leaf]['t0_date'] = early_start
        g.nodes[leaf]['ES'] = 0
        g.nodes[leaf]['EF'] = my_dur
        g.nodes[leaf]['LS'] = None #LS
        g.nodes[leaf]['LF'] = None #LF
        return (early_start,duration)

    # example of finding the list of duractions for all predecessors
    # durs=[g.nodes[x]['duration'] for x in ps]

    # this is wrong calculation.  Needs to be max along each pred path

    rcs = [process_longest_dur(g,root,p) for p in ps]    
    durs = [x[1] for x in rcs]
    maxEF = max(durs)
    t0_date = rcs[0][0]
    EF = (early_end - t0_date).days
    g.nodes[leaf]['longest_dur'] = maxEF
    g.nodes[leaf]['t0_date'] = t0_date # get this from return from this function
    g.nodes[leaf]['ES'] = maxEF
    g.nodes[leaf]['EF'] = maxEF + my_dur
    g.nodes[leaf]['LS'] = None #(late_start - t0_date).days # needs filling later
    g.nodes[leaf]['LF'] = None #(late_end - t0_date).days   # needs filling later

    return (t0_date,maxEF+my_dur)

# root = earliest task (first)
# leaf = latest task (last)
# backwards action for critical path using EF, LS, duration
def process_edges(g,root,leaf):
    #print(f"proc edges: root={root}; leaf={leaf}")

    LS=g.nodes[root]['LS']
    if LS: return LS 

    EF=g.nodes[root]['EF']
    dur=g.nodes[root]['duration']

    ss=list(g.successors(root))   # earlier tasks
    ps=list(g.predecessors(root)) # later tasks
    #print(f'successors of root {root} are {ss}')
    #print(f'predecessors of root {root} are {ps}')

    if len(ps)==0: # at latest task in tree
        g.nodes[root]['LF'] = EF
        LS=EF-dur
        LF=EF
        g.nodes[root]['LS'] = LS
        return LS

    if True:
        prev_LSs=[process_edges(g,p,leaf) for p in ps]
        LF = min(prev_LSs)
        LS=LF-dur
        g.nodes[root]['LF']=LF
        g.nodes[root]['LS']=LS

    #print(f'done with successors of leaf {leaf} for root {root}')
    return LS

# don't do this
def nx_mark_crit(g,root,leaf):
    EF=g.nodes[root]['EF']

    ss=list(g.successors(root))   # earlier tasks
    ps=list(g.predecessors(root)) # later tasks

    for p in ss:
        g[root][p]['crit'] = "Y" if g.nodes[p]['EF']==g.nodes[p]['LF'] else "N"

def render_nx(g,ps, first_code, last_code):
    dot=gv.Digraph(comment='sched',strict=True, format=output_format)

    # can color nodes if node attr until_start < dt.timedelta(seconds=0)
    # or until_end < dt.timedelta(seconds=0)

    lps=list(ps)
    all_nodes={ n for p in lps for n in p}

    for n in all_nodes:
        EF=g.nodes[n]['EF']
        LF=g.nodes[n]['LF']
        mylabel=f"{g.nodes[n]['type']}/{n}\nd={g.nodes[n]['duration']}\nES={g.nodes[n]['ES']}\nEF={g.nodes[n]['EF']}\nLS={g.nodes[n]['LS']}\nLF={g.nodes[n]['LF']}"
        dot.node(n,label=mylabel,color='red' if EF==LF else 'black')


    for p in lps:
        # print(p)
        for i in range(len(p)-1):
            w=0 #g[p[i]][p[i+1]]['weight']
            crit = 'N' #g[p[i]][p[i+1]]['crit']
            dot.edge(p[i],p[i+1], label=f'{w}', color='blue' if crit=="N" else 'red')

    fname=f'nx_{first_code}_{last_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)


def process_nx(first_code, last_code):
    xer,acts,rels = ds.just_read_file()
    typ = 'TT_FinMile'

    first = xer.activities.find_by_code(first_code)
    g=nx.DiGraph()
    print("starting build of graph")
    nx_add_node(first.task_id,g,xer,0)
    print("starting find of paths")
    ps = nx.all_simple_paths(g, first_code, last_code)

    roots = [v for v, d in g.out_degree() if d == 0]
    leaves = [v for v, d in g.in_degree() if d == 0]

    print(f'predecessor roots={roots}, leaves={leaves}')
    return (g,roots, leaves, ps)

def just_write_graph(fname_prefix, last_code='A0100000', first_code='A1503340'):
    g,root,leaf,ps=process_nx(first_code, last_code)
    nx.write_gpickle(g,f'{fname_prefix}_{first_code}_{last_code}.gz')

import args

if __name__ == '__main__':

    first_code, last_code, special = args.process_args(sys.argv)
    # using networkx to find all paths from last to first
    g,root,leaf,ps=process_nx(first_code, last_code)
    process_longest_dur(g,root[0],leaf[0])
    print("finished with longest dur")
    process_edges(g,root[0],leaf[0])
    #nx_mark_crit(g,root[0],leaf[0])
    render_nx(g,ps, root[0], leaf[0])

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

