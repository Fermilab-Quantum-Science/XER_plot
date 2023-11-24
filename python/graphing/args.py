import sys

# some interesting codes
ids=['A1503560' # laser-atom interactions
    ,'A1503530' # two atom sources installed
    ,'A0201090' # atom source two 100% complete
    ,'A1206110' # Milestone - Phase 2 shaft installation complete
    ,'A1503540' # CRITICAL Milestone - First laser beam
    ,'A1803230' # INDICATOR Milestone - First Atoms
    ,'A1503520' # CRITICAL - Shaft Modular Sections Installed
]

inter={
    '1':['A1004010','A1503500','A1503240','A1503770','A1206100','A1503790','A1503570','A1503520','A1206110']
    ,'2':['A0201090','A0214020','A1503570','A1503530']
    ,'3':['A0307030','A0301050','A1503760','A1503330','A1802570','A0309020','A1802380','A1503220','A1004030','A1503590','A1503540']
    ,'4':['A0501050','A0201090','A0607010','A1203180','A0508020','A1802360','A1004020','A0214020','A1802370','A1803230','A1803240']
    ,'5':['A1503280','A1802240','A1803330','A1802330','A1802340','A1004040','A1503560','A1503600']
    ,'none':[]
}
inter_names={
    '5':'Laser-atom interactions',
    '4':'First atoms',
    '3':'First laser beam',
    '2':'Two atom sources installed',
    '1':'Shaft modular sections installed'
}


# other interesting starting / ending points
# remember that last means furtherest predecessor, or earlier one
# root = first (earliest), leaf = last (latest)
# successors of leaf point earlier (confusing)
# predecessors of leaf point latest (confusing)

#first_code='A1503560' # laser-atom interactions
#first_code='A1503570' # INDICTOR - shaft modular section installed
#last_code='A1004010'  # DAQ for modular assembly shipped
#last_code='A0101000'  # DOE project start
#last_code='A1503790'  # installation of 17 modular sections


def process_args(argv):
    if len(argv)==2 and (argv[1]=='help' or argv[1]=='--help'):
        print("usage: <key from below> <latest task code> <earliest task code>")
        for k,v in inter_names.items():
            print(f'{k}\t{v}')
        sys.exit(0)    

    if len(argv)>1:
        special=sys.argv[1]
    else:
        special='1' # ['1']

    print(f'using list named {inter_names[special]}')
    special = inter[special]

    # default codes to use
    first_code = special[-1]
    last_code = special[0]

    if len(argv) >3:
        first_code=sys.argv[2]
        last_code=sys.argv[3]

    # more examples
    #first_code='A1503560' # laser-atom interactions
    #first_code='A1206110' # Milestone - Phase 2 shaft installation complete
    #first_code='A1004010'  # DAQ for modular assembly shipped
    #first_code='A1503240' # construction bid
    #last_code='A1004010'  # DAQ for modular assembly shipped
    #last_code='A1503500'  # CRITICAL - civil design for shaft complete
    #last_code='A0101000'  # DOE project start
    #last_code='A0100000'  # start?

    return (first_code, last_code, special)

