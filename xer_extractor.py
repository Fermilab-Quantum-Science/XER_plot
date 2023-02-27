from xerparser.reader import Reader
import csv
import os
import sys

# Extractor

datepart = 'Dec2022FY24ScenarioUpdated'

def write_tab(tab,mid):
    name = tab[0][1]
    head = tab[1]
    fname = f'extracted/tab_{name}_{mid}.csv'

    f = open(fname,'w',newline='', encoding='utf-8')
    w = csv.writer(f)
    w.writerow(head)
    w.writerows(tab[2:])
#    for r in tab[2:]:
#        w.writerow(r)


if __name__ == "__main__":

    fname=f"schedule_{datepart}.xer" if len(sys.argv)==1 else sys.argv[1]
    fout_prefix=os.path.splitext(fname)[0]
    middle = fout_prefix.split('_')[1]
    xer = Reader(fname)

tabs = [
    xer.activityresources.get_tsv()
    ,xer.wbss.get_tsv()
    ,xer.resources.get_tsv()
    ,xer.relations.get_tsv()
    ,xer.activities.get_tsv()
]

for t in tabs:
    write_tab(t, middle)


