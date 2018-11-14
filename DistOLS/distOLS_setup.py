import warnings as w
# These warnings are caused by numpy updates and should not be
# output.
w.simplefilter(action = 'ignore', category = FutureWarning)
import numpy as np
import subprocess
import warnings
import resource
import nibabel as nib
import sys
import os
import shutil
from DistOLS import distOLS_defaults

def main(*args):

    # If X and Y weren't given we look in defaults for all arguments.
    if len(args)<2:

        inputs = distOLS_defaults.main()

        MAXMEM = inputs[0]

        with open(inputs[1]) as a:

            Y_files = []
            i = 0
            for line in a.readlines():

                Y_files.append(line.replace('\n', ''))

        X = np.loadtxt(inputs[2]) 

        SVFlag = inputs[3]

    # else Y_files is the first input and X is the second.
    elif len(args)==2:

        Y_files = args[0]
        X = args[1]

        inputs = distOLS_defaults.main()
        MAXMEM = inputs[0]
        SVFlag = inputs[3]

    # And MAXMEM may be the third input
    else:

        Y_files = args[0]
        X = args[1]
        MAXMEM = args[2]        

        inputs = distOLS_defaults.main()
        SVFlag = inputs[3]

    # Load in one nifti to check NIFTI size
    Y0 = nib.load(Y_files[0])
    d = Y0.get_data()

    # Get the maximum memory a NIFTI could take in storage. 
    NIFTIsize = sys.getsizeof(np.zeros(d.shape,dtype='uint64'))

    # Similar to blksize in SwE, we divide by 8 times the size of a nifti
    # to work out how many blocks we use.
    blksize = np.floor(MAXMEM/8/NIFTIsize);

    # Change to distOLS directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Make a temporary directory for batch inputs
    if os.path.isdir('binputs'):
        shutil.rmtree('binputs')
    os.mkdir('binputs')

    # Example NIFTI is needed later.
    exampleNifti = nib.Nifti1Image(np.zeros(d.shape,dtype='uint64'),
                                   Y0.affine,
                                   header=Y0.header)

    # Save the result.
    nib.save(exampleNifti, os.path.join('binputs',
                                        'example.nii'))    
    np.savetxt(os.path.join("binputs","NIFTIsize.csv"), 
                   d.shape, delimiter=",") 

    # Loop through blocks
    for i in range(0, len(Y_files), int(blksize)):

        # Lower and upper block lengths
        blk_l = i
        blk_u = min(i+int(blksize), len(Y_files))
        index = int(i/int(blksize) + 1)
        
        with open(os.path.join("binputs","Y" + str(index) + ".txt"), "w") as a:

            # List all y for this batch in a file
            for f in Y_files[blk_l:blk_u]:
                a.write(str(f) + os.linesep) 

        np.savetxt(os.path.join("binputs","X" + str(index) + ".csv"), 
                   X[blk_l:blk_u], delimiter=",") 
    
    w.resetwarnings()

if __name__ == "__main__":
    main()
