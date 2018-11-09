import numpy as np
import subprocess
import warnings
import resource
import nibabel as nib
import sys
import os
import glob
import shutil

def main():

    # Change to distOLS directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Work out which files we need.
    XtX_files = glob.glob("XtX*")
    XtY_files = glob.glob("XtY*")

    # Read the matrices from the first batch.
    sumXtX = np.loadtxt(os.path.join("binputs","XtX1.csv"), 
                        delimiter=",")
    sumXtY = np.loadtxt(os.path.join("binputs","XtY1.csv"), 
                        delimiter=",")
    sumYtY = np.loadtxt(os.path.join("binputs","YtY1.csv"), 
                        delimiter=",")

    # Cycle through batches and add together results.
    for batchNo in range(2,(len(XtX_files)+1)):

        # Sum the batches.
        sumXtX = sumXtX + np.loadtxt(
            os.path.join("binputs","XtX" + str(batchNo) + ".csv"), 
                         delimiter=",")

        sumXtY = sumXtY + np.loadtxt(
            os.path.join("binputs","XtY" + str(batchNo) + ".csv"), 
                         delimiter=",")
        sumYtY = sumYtY + np.loadtxt(
            os.path.join("binputs","YtY" + str(batchNo) + ".csv"), 
                         delimiter=",")

    # Dimension bug handling
    if np.ndim(sumXtX) == 0:
        sumXtX = np.array([[sumXtX]])
    elif np.ndim(sumXtX) == 1:
        sumXtX = np.array([sumXtX])

    if np.ndim(sumXtY) == 0:
        sumXtY = np.array([[sumXtY]])
    elif np.ndim(sumXtY) == 1:
        sumXtY = np.array([sumXtY])

    # np linalg inverse doesn't handle dim=[1,1]
    if np.ndim(sumXtX) == 1:
        isumXtX = 1/sumXtX
    else:
        isumXtX = np.linalg.inv(sumXtX)

    # Read in the nifti size.
    NIFTIsize = np.loadtxt(os.path.join("binputs","NIFTIsize.csv"), 
                        delimiter=",")

    beta = np.dot(isumXtX, sumXtY)
    print(beta.shape)

    # Cycle through betas and output results.
    for i in range(0,beta.shape[0]):

        betai = beta[i,:].reshape(int(NIFTIsize[0]),
                                  int(NIFTIsize[1]),
                                  int(NIFTIsize[2]))

        # tmp code to output nifti
        nifti = nib.load(os.path.join("binputs", "example.nii"))

        betaimap = nib.Nifti1Image(betai,
                                   nifti.affine,
                                   header=nifti.header)
        nib.save(betaimap, 'beta' + str(i) + '.nii')

    # if np.ndim(beta) == 0:
    #     beta = np.array([[beta]])
    # elif np.ndim(sumXtY) == 1:
    #     beta = np.array([beta])

    # Reshape beta along smallest axis for quicker
    # residual calculation
    # beta_rs = np.zeros(beta.shape[1], 1, beta.shape[0])
    # beta_rs_t = np.zeros([beta.shape[1], 1, beta.shape[0])
    # for i in range(0,beta.shape[0]):
    #     
    #    beta_rs[:, i, 0] = beta[i,:];
    #    beta_rs_t[:, 0, i] = beta[i,:];
    #
    # Residual sum of squares
    # ete = YtY - np.matmul(np.matmul(beta_rs_t, sumXtX), beta_rs)


if __name__ == "__main__":
    main()
