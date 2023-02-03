
from xerparser.reader import Reader
import csv
import os
import sys

datepart = 'Dec2022'

# this script reads the p6 XER file and puts basis information
# into an CSV file named sheet_<month><year>.csv

# for information on P6 XER files and reading from excel, see
# https://www.planacademy.com/understanding-primavera-xer-files/

def just_read_file(fname):
    xer = Reader(fname)
    acts = list(xer.activities)
    rels = list(xer.relations)
    return (xer,acts,rels)

if __name__ == "__main__":

    fname=f"schedule_{datepart}.xer" if len(sys.argv)==1 else sys.argv[1]
    fout=os.path.splitext(fname)[0]

    xer,acts,rels = just_read_file(fname)

    f = open(f"report_{datepart}.csv",'w',newline='')
    w = csv.writer(f)
    w.writerow(
        ["activity", "start", "end", "duration", "target_start", "target_end", 
        "early_start", "early_end", "late_start", "late_end"]
    )

    fe = open(f"report_{datepart}_edges.csv",'w',newline='')
    we = csv.writer(fe)
    tsv = xer.relations.get_tsv()
    we.writerow(tsv[1][1:])

    for e in tsv[2:]:
        #print(e,e[1], e[2], e[3])
        n1=xer.activities.find_by_id(int(e[2])).task_code
        n2=xer.activities.find_by_id(int(e[3])).task_code
        e[2]=n1
        e[3]=n2
        we.writerow(e[1:])

    #print(dir(xer))
    #print(dir(xer.activities))
    #sys.exit(0)

    for t in acts:
        #print(dir(t))
        #sys.exit(0)
        st_date = t.target_start_date
        en_date = t.target_end_date
        ES = t.early_start_date
        EF = t.early_end_date
        LS = t.late_start_date
        LF = t.late_end_date
        duration = t.duration
        stat_code = t.status_code
        S = t.start_date
        F = t.end_date
        restart = t.restart_date
        reend = t.reend_date
        act_start = t.act_start_date
        act_end = t.act_end_date
        expect_end = t.expect_end_date
        ext_early_st = t.external_early_start_date
        ext_early_en = t.external_late_end_date

        w.writerow([t.task_code, S, F, duration, st_date, en_date, ES, EF, LS,LF])
