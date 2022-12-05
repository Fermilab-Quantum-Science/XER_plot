
import readexcel as rex
import pandas as pd
import networkx as nx
import graphviz as gv
import datetime as dt
import sys
import csv
import get_args as getargs
# import args # old way to do it

# This script read the P6 XER file and the standard spreadsheet report that
# Alyssa produces (including the predessors) to produce a plot of tasks and
# milestones where BL_start != start

# NOTE: need to check the excel sheet for A0601000, (A1201020 looks similar)
# the plot shows strange bad alignment of start->BL start and end->BL end

def no_start_diff(g,ps):
    anp = []
    for p in ps:
        np=[]
        for i in range(len(p)-1):
            n = p[i]
            diff_end = g.nodes[n]['diff_finish']
            diff_start = g.nodes[n]['diff_start']
            if diff_start==0:
                np=p[i:] 
                break
        anp.append(np)
    return anp


def render_nx(g,ps, args):
    # first_code,last_code, output_format, show_dates=False, view=False):
    dot=gv.Digraph(comment='sched',strict=True, format=args.output_format)

    # can color nodes if node attr until_start < dt.timedelta(seconds=0)
    # or until_end < dt.timedelta(seconds=0)

    print(f"doing rendering")
    all_nodes=set()
    all_edges=set()

    now = dt.datetime.now().date()
    later = now + dt.timedelta(days=6*30)

    for p in ps:
        for i in range(len(p)-1):
            n = p[i]
            end=g.nodes[n]['end']
            BLend=g.nodes[n]['BL_end']
            diff_end = g.nodes[n]['diff_finish']
            diff_start = g.nodes[n]['diff_start']
            if n not in all_nodes: # and end>now: # and diff_end>0: 
                all_nodes.add(n)
                S=g.nodes[n]['start']
                BS=g.nodes[n]['BL_start']
                name=g.nodes[n]['name']
                dur=g.nodes[n]['duration']
                typ=g.nodes[n]['type']
                bldur=g.nodes[n]['BL_duration']

                shape = 'rect' if typ=='M' else 'ellipse'
                col='black' if diff_end==0 or diff_start==0 else 'purple'
                mylabel=f"{typ}/{n}\n{name}\nd={dur} / bd={bldur}\nBS={BS} / S={S}\nF={end} / BF={BLend}\n{diff_start}/{diff_end}" if args.show_dates else f"{typ}/{n}\n{name}"
                #dot.node(n,label=mylabel,color='black' if typ=='T' else 'purple')
                dot.node(n,label=mylabel,color=col,shape=shape)
            e = (p[i], p[i+1])
            if e not in all_edges:
                all_edges.add(e)
                dot.edge(e[0],e[1], label=f'', color='black')
    
    print("done with all nodes/edges")
    reduced = "wr" if args.do_reduction else "wor"
    fname=f'nx_{args.later_code}_{args.earlier_code}_{reduced}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=args.render)

def reduce_graph(g_orig, args):

    if not args.do_reduction:
        return g_orig

    g = nx.transitive_reduction(g_orig) if args.do_reduction else g_orig
    g_diff = nx.difference(g_orig,g)
    g.add_nodes_from(g_orig.nodes(data=True))

    # TR.add_nodes_from(DG.nodes(data=True))
    # TR.add_edges_from((u, v, DG.edges[u, v]) for u, v in TR.edges)
    # xer.relations.relations[4].get_tsv()
    # for x in xer.relations.get_tsv(): print(x)
    
    # first==args.later_code, last=args.earlier_code
    fname=f'nx_{args.later_code}_{args.earlier_code}_diff.csv'
    csv_out = csv.writer(open(fname, 'w', newline=''))
    csv_out.writerow(['task_code','pred_task_code','pred_type'])
    for e in g_diff.edges:
        row=edges.loc[e[0],e[1]]
        csv_out.writerow([e[0],e[1],row['pred_type']])

    return g

def process(gg_orig, args):
    g = reduce_graph(gg_orig, args)
    ps = nx.all_simple_paths(g, args.later_code, args.earlier_code)
    ps_zero = no_start_diff(g,ps) if args.show_diffs else ps

    render_nx(g,ps_zero,args) 

if __name__ == '__main__':
    #first, last, special = args.process_args(sys.argv)
    args = getargs.get_args()
    xer = rex.read_xer_dump()
    edges = rex.read_xer_edges()
    df  = rex.read_excel_report()
    g_orig, roots, leaves = rex.convert_to_nx(df, xer)

    if args.do_only_preds:
        an = g_orig.predecessors(args.earlier_code)
        an=list(an)
        #print(len(an))
        for c in an:
            print(f'processing {c}')
            args.earlier_code=c
            args.render=False
            args.output_format='pdf'
            args.do_reduction=False
            process(g_orig,args)
            args.do_reduction=True
            process(g_orig,args)
    else:
        process(g_orig, args)

    # old args to render_nx:
    # args.later_code, args.earlier_code,
    # args.output_format, args.show_dates,args.render)

    # sort and filter examples:
    # df_top = df.sort_values(by="diff_finish", ascending=False).iloc[0:20].sort_values(by="BL Project Finish")
    # df_out = df_top[['Activity ID', 'Activity Name', 'BL Project Start', 'Start', 'BL Project Finish','Finish', 'diff_start', 'diff_finish']]

    #print(df.columns)
    #print(df_out)

    #first = 'A1503600'
    #last  = 'A1503790'
    #first = last
    #first = 'A1206110'
    #first = 'A1503560'
    #first = 'A1207060' # I think this is construction complete
    #last  = 'A0100000' # 
    #last = "A0101000" # DOE placeholder start

    # expensive to convert ps to list, avoid if possible
    # ps = list(ps)
    # print('total edges = ', len(g_orig.edges))
