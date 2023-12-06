import jpype
import jpype.imports
from jpype.types import *

import mpxj
import os

import get_args as getargs

#import net.sf.mpxj.ProjectFile;
#import net.sf.mpxj.reader.UniversalProjectReader;
#from mpxj import ProjectFile
#import net.sf.mpxj.primavera.PrimaveraPMFileReader

if __name__ == "__main__":

    args = getargs.get_args()
    fname=f"input/schedule_{args.date_part}.xer"
    fout_prefix=os.path.splitext(fname)[0]
    middle = fout_prefix.split('_')[1]
    fname = os.path.abspath(fname)

    jpype.startJVM()
    import java.lang
    import java.util
    from java.lang import System
    from java.io import FileInputStream
    from net.sf.mpxj.sample import MpxjConvert
    from net.sf.mpxj import ProjectFile
    from net.sf.mpxj.primavera import PrimaveraPMFileReader
    from net.sf.mpxj.primavera import PrimaveraXERFileReader
    from net.sf.mpxj.reader import UniversalProjectReader

    # MpxjConvert().process('example.mpp', 'example.mpx')
    x=System.getProperty("user.dir")
    print(x)

    reader = PrimaveraXERFileReader()
    inp = FileInputStream(fname);
    print(reader.listProjects(inp))
    proj = reader.read(fname)
    t = proj.getTables()
    print(type(t))

    #reader = PrimaveraPMFileReader()
    #proj = reader.read(fname)

    print("This is the project methods ---> ")
    for n in dir(proj):
        print(n)
    #print("This is the reader methods ---->")
    #for n in dir(reader):
    #    print(n)

    jpype.shutdownJVM()

