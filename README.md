There are two method in there: one using networkx to trace all paths, and one using graphviz directly.

Let me know if you want to do a zoom call about installation and running.
run it like this:

$ python ./test.py <first_activity> <last_activity>

where first_activity is the latest activity or milestone you want traced, and last_activity is where to trace it to through predecessors.
It produces pdf files, but that can readily be changed to png or other formats.

These are the things I installed on the loaner laptop through MS store to make it go:

 * Python 3.10
 * Visual Studio Code

Also go get graphviz6 from https://www.graphviz.org/download/ and install it anywhere you want.
I do not have admin on the laptop, so I had to go to the windows control panel and add the graphviz bin directory to my user path manually.
You should be able to bring up a windows powershell and type dot --help.

In VS Code, hit the extensions button on the left panel, look for Python (intellisense - pylance) and install it.  
Go to file->open folder and open the directory brought down from github (I can send you a zip/tar file if you want).  
Hit Terminal->new terminal
type 

 * $ pip3 install graphviz
 * $ pip3 install networkx
 * $ pip3 install xerparser

Seems like a lot, but much of it is the standard python development environment that only needs installation once. 

By the way, it should be very easy to color the nodes indicating if the tasks are started, in-progress, not started, not started and late, started but late, etc..

# Note

Use longdelays.py.   There is an option --help for what it can do now.
It is the latest code and the name is misleading.   
There will be options added to filter out nodes for a bigger view. 

# example of producing a graph

Option ```-l``` means later in time task code, option ```-e``` means earlier in time task code.

```
python ./longdelays.py -l A1503600 -e A0100000
```

The program now supports many options, including output in PDF or PNG, or adding date information to the nodes.

# important tasks from Linda

Here are a few mechanical tasks which could be intermediate milestones for installation of 17 sections.  We’ll need civil also.

* A1802580 - Assembly of 17, phase 1 (start)
* A0507010 - connection node integration (start)
* A0603020 - Magnetic shield and coupler procurement (start)
* A1802490 - vacuum system - interferometry spool fabrication
* A0705020 - bake procurement
* A1803820 - strongback frame procurement

# tables

xer.activityresources.get_tsv() : '%T', 'TASKRSRC'

['%F', 'taskrsrc_id', 'task_id', 'proj_id', 'cost_qty_link_flag', 'role_id', 'acct_id', 'rsrc_id', 'pobs_id', 'skill_level', 'remain_qty', 'target_qty', 'remain_qty_per_hr', 'target_lag_drtn_hr_cnt', 'target_qty_per_hr', 'act_ot_qty', 'act_reg_qty', 'relag_drtn_hr_cnt', 'ot_factor', 'cost_per_qty', 'target_cost', 'act_reg_cost', 'act_ot_cost', 'remain_cost', 'act_start_date', 'act_end_date', 'restart_date', 'reend_date', 'target_start_date', 'target_end_date', 'rem_late_start_date', 'rem_late_end_date', 'rollup_dates_flag', 'target_crv', 'remain_crv', 'actual_crv', 'ts_pend_act_end_flag', 'guid', 'rate_type', 'act_this_per_cost', 'act_this_per_qty', 'curv_id', 'rsrc_type', 'cost_per_qty_source_type', 'create_user', 'create_date', 'cbs_id', 'has_rsrchours', 'taskrsrc_sum_id']

xer.wbss.get_tsv()[0]  : ['%T', 'PROJWBS']

xer.wbss.get_tsv()[1] :
['%F', 'wbs_id', 'proj_id', 'obs_id', 'seq_num', 'est_wt', 'proj_node_flag', 'sum_data_flag', 'status_code', 'wbs_short_name', 'wbs_name', 'phase_id', 'parent_wbs_id', 'ev_user_pct', 'ev_etc_user_value', 'orig_cost', 'indep_remain_total_cost', 'ann_dscnt_rate_pct', 'dscnt_period_type', 'indep_remain_work_qty', 'anticip_start_date', 'anticip_end_date', 'ev_compute_type', 'ev_etc_compute_type', 'guid', 'tmpl_guid', 'plan_open_state']

xer.resources.get_tsv()[0] : ['%T', 'RSRC']

xer.resources.get_tsv()[1] : 
['%F', 'rsrc_id', 'parent_rsrc_id', 'clndr_id', 'role_id', 'shift_id', 'user_id', 'pobs_id', 'guid', 'rsrc_seq_num', 'email_addr', 'employee_code', 'office_phone', 'other_phone', 'rsrc_name', 'rsrc_short_name', 'rsrc_title_name', 'def_qty_per_hr', 'cost_qty_type', 'ot_factor', 'active_flag', 'auto_compute_act_flag', 'def_cost_qty_link_flag', 'ot_flag', 'curr_id', 'unit_id', 'rsrc_type', 'location_id', 'rsrc_notes', 'load_tasks_flag', 'level_flag', 'last_checksum']

xer.relations.get_tsv()[0] : ['%T', 'TASKPRED']

xer.relations.get_tsv()[1]  
['%F', 'task_pred_id', 'task_id', 'pred_task_id', 'proj_id', 'pred_proj_id', 'pred_type', 'lag_hr_cnt', 'comments', 'float_path', 'aref', 'arls']

xer.activities.get_tsv()[0] : ['%T', 'TASK']

xer.activities.get_tsv()[1] 
['%F', 'task_id', 'proj_id', 'wbs_id', 'clndr_id', 'phys_complete_pct', 'rev_fdbk_flag', 'est_wt', 'lock_plan_flag', 'auto_compute_act_flag', 'complete_pct_type', 'task_type', 'duration_type', 
'status_code', 'task_code', 'task_name', 'rsrc_id', 'total_float_hr_cnt', 'free_float_hr_cnt', 'remain_drtn_hr_cnt', 'act_work_qty', 'remain_work_qty', 'target_work_qty', 'target_drtn_hr_cnt', 
'target_equip_qty', 'act_equip_qty', 'remain_equip_qty', 'cstr_date', 'act_start_date', 'act_end_date', 'late_start_date', 'late_end_date', 'expect_end_date', 'early_start_date', 'early_end_date', 'restart_date', 'reend_date', 'target_start_date', 'target_end_date', 'rem_late_start_date', 'rem_late_end_date', 'cstr_type', 'priority_type', 'suspend_date', 'resume_date', 'float_path', 
'float_path_order', 'guid', 'tmpl_guid', 'cstr_date2', 'cstr_type2', 'driving_path_flag', 'act_this_per_work_qty', 'act_this_per_equip_qty', 'external_early_start_date', 'external_late_end_date', 'create_date', 'update_date', 'create_user', 'update_user', 'location_id']

