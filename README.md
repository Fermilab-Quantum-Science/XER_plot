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

Here are a few mechanical tasks which could be intermediate milestones for installation of 17 sections.  We???ll need civil also.

* A1802580 - Assembly of 17, phase 1 (start)
* A0507010 - connection node integration (start)
* A0603020 - Magnetic shield and coupler procurement (start)
* A1802490 - vacuum system - interferometry spool fabrication
* A0705020 - bake procurement
* A1803820 - strongback frame procurement


