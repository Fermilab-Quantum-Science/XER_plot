
import test as p6
from xerparser.reader import Reader
import csv
import sys

# this script reads the p6 XER file and puts basis information
# into an CSV file named sheet.csv

# for information on P6 XER files and reading from excel, see
# https://www.planacademy.com/understanding-primavera-xer-files/

xer,acts,rels = p6.just_read_file()

f = open("sheet.csv",'w',newline='')
w = csv.writer(f)
w.writerow(
    ["activity", "start", "end", "duration", "target_start", "target_end", 
    "early_start", "early_end", "late_start", "late_end"]
)

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
