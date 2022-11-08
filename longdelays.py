
import readexcel as rex
import pandas as pd
import networkx as nx
import graphviz as gv
import datetime as dt

# NOTE: need to check the excel sheet for A0601000, (A1201020 looks similar)
# the plot shows strange bad alignment of start->BL start and end->BL end

out_format = 'pdf'

def render_nx(g,ps, first_code,last_code, output_format=out_format):
    dot=gv.Digraph(comment='sched',strict=True, format=output_format)

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
                mylabel=f"{typ}/{n}\n{name}\nd={dur} / bd={bldur}\nBS={BS} / S={S}\nF={end} / BF={BLend}\n{diff_start}/{diff_end}"
                #dot.node(n,label=mylabel,color='black' if typ=='T' else 'purple')
                dot.node(n,label=mylabel,color='black' if diff_end==0 or diff_start==0 else 'purple')
            e = (p[i], p[i+1])
            if e not in all_edges:
                all_edges.add(e)
                dot.edge(e[0],e[1], label=f'', color='black')
    
    print("done with all nodes/edges")
    fname=f'nx_{first_code}_{last_code}.gv'
    dot.render(fname).replace('\\', '/')
    dot.render(fname, view=True)


xer = rex.read_xer_dump()
df  = rex.read_excel_report()
g, roots, leaves = rex.convert_to_nx(df, xer)

df_top = df.sort_values(by="diff_finish", ascending=False).iloc[0:20].sort_values(by="BL Project Finish")
df_out = df_top[['Activity ID', 'Activity Name', 'BL Project Start', 'Start', 'BL Project Finish','Finish', 'diff_start', 'diff_finish']]

print(df.columns)
print(df_out)

first = 'A1503600'
last  = 'A1503790'
first = last
last  = 'A0100000'
ps = nx.all_simple_paths(g, first, last)
render_nx(g,ps,first, last)
