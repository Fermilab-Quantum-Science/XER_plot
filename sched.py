
import graphviz as gv
import networkx as nx
import sys
import datetime as dt

def read_graph(fname):
    g = nx.read_gpickle(fname)
    return g

def has_delayed_node(g, path):
    rc=False
    for n in path:
        rc |= g.nodes[n]['start_date']!=g.nodes[n]['target_start']
    return rc

def reduce_path(g,path):
    npath=[]
    for n in path:
        if g.nodes[n]['start_date']==g.nodes[n]['target_start']: break
        npath.append(n)
    return npath

def render_nx(g,ps, first_code,last_code, output_format='pdf'):
    dot=gv.Digraph(comment='sched',strict=True, format=output_format)

    # can color nodes if node attr until_start < dt.timedelta(seconds=0)
    # or until_end < dt.timedelta(seconds=0)

    print(f"doing rendering")
    lps=list(ps)
    all_nodes={ n for p in lps for n in p}
    print(f"converted path list to list of nodes, len of all={len(all_nodes)}, len of paths={len(lps)}")

    reduced_paths=[reduce_path(g,p) for p in lps]
    reduced_all={ n for p in reduced_paths for n in p}
    print(f'reduced paths len={len(reduced_paths)}, len all={len(reduced_all)}')
    sys.exit(0)

    for n in all_nodes:
        S=g.nodes[n]['start_date']
        TS=g.nodes[n]['target_start']
        mylabel=f"{g.nodes[n]['type']}/{n}\nd={g.nodes[n]['duration']}\nTS={g.nodes[n]['target_start']}\nS={g.nodes[n]['start_date']}\nF={g.nodes[n]['end_date']}"
        dot.node(n,label=mylabel,color='black' if TS==S else 'red')

    for p in lps:
        # print(p)
        for i in range(len(p)-1):
            w=0 #g[p[i]][p[i+1]]['weight']
            crit = 'N' #g[p[i]][p[i+1]]['crit']
            dot.edge(p[i],p[i+1], label=f'{w}', color='blue' if crit=="N" else 'red')

    fname=f'nx_{first_code}_{last_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)

if __name__ == '__main__':

    if len(sys.argv)<2 or (len(sys.argv)>1 and (sys.argv[1]=='help' or sys.argv[1]=='--help')):
        print("usage: file_name start_task_code")
        sys.exit(0)    

    starting_code = 'A1207060'
    earliest_code = 'A0100000'
    fname = sys.argv[1]

    if len(sys.argv)>2:
        starting_code = sys.arv[2]
    else:
        print(f'using starting code of {starting_code}')

    g = read_graph(fname)
    ps = nx.all_simple_paths(g, starting_code, earliest_code)
    render_nx(g,ps, starting_code, earliest_code)