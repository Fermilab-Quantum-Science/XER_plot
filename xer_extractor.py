from xerparser.reader import Reader
import csv
import os
import sys
import get_args as getargs

# Extractor

datepart = 'Dec2022FY24ScenarioUpdated'
datepart = 'Dec2022Current'

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

    args = getargs.get_args()
    fname=f"input/schedule_{args.date_part}.xer"
    fout_prefix=os.path.splitext(fname)[0]
    middle = fout_prefix.split('_')[1]
    xer = Reader(fname)

    tabs = [
        xer.activityresources.get_tsv()
        ,xer.wbss.get_tsv()
        ,xer.resources.get_tsv()
        ,xer.relations.get_tsv()
        ,xer.activities.get_tsv()
        ,xer.udfvalues.get_tsv()
        ,xer.udftypes.get_tsv()
        ,xer.roles.get_tsv()
    ]

    for t in tabs:
        write_tab(t, middle)


