
import argparse
import sys
import os

class Fake:
    earlier_code='A0100000'
    later_code='A1503600'
    output_format='png'
    wbs_filter=False
    wbs_item=None
    show_diffs=False
    show_dates=False
    do_reduction=True
    render=True
    do_only_preds=False
    special_list=[earlier_code, later_code]
    special=f'{earlier_code},{later_code}'

def get_args():
    if 'site-packages' in sys.argv[0]: # os.path.basename(sys.argv[0]):
        # provide a fake for interactive application use
        return Fake()

    parser = argparse.ArgumentParser()
    parser.add_argument("-e","--earlier-code", default=Fake.earlier_code, dest="earlier_code",help="Earliest task code to track back to")
    parser.add_argument("-l","--later-code", default=Fake.later_code, dest="later_code",help="Latest task code to starting tracking back from")
    parser.add_argument("-f","--format", default=Fake.output_format, dest="output_format",help="Output format for viewing graph (png/pdf)")
    parser.add_argument("-s","--special", default=Fake.special, dest="special",help="List of task codes to show as squares in graph (comma separated)")
    parser.add_argument("-D","--BL-equals-planned", default=Fake.show_diffs, action='store_true', dest="show_diffs",help="Only show tasks where BL==planned start time")
    parser.add_argument("-d","--show-dates", default=Fake.show_dates, action='store_true', dest="show_dates",help="Show dates on graph")
    parser.add_argument("-t","--no-transitive-reduction", default=Fake.do_reduction, action='store_false', dest="do_reduction",help="Do not run transitive reduction algorithm")
    parser.add_argument("-r","--no-render", default=Fake.render, action='store_false', dest="render",help="Do not view the graph")
    parser.add_argument("-p","--only-preds", default=Fake.do_only_preds, action='store_true', dest="do_only_preds",help="Do ALL graphs of -l to predecessors to -e, with and witout -t")
    parser.add_argument("-w","--wbs-filter-level", default=Fake.wbs_item, dest="wbs_item",help="only include items at this level and ones connected to it")
    pp = parser.parse_args()

    pp.special_list=[ x.strip() for x in pp.special.split(',')]
    pp.wbs_filter = False if pp.wbs_item == None else True

    # leave in the dot format
    #if pp.wbs_filter:
    #    pp.wbs_item = pp.wbs_item.split('.')

    return pp
