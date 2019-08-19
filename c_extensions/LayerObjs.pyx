from cpython cimport array
from cython.parallel import prange
import cython
from libc.math cimport isnan,fabs
cimport numpy as cnp
import numpy as np


cdef extern from "layer_cxx.h" nogil:
    void fillData(int b1[][5], int b2[][5],int hgt[][125],short out[][125], int b1_n,int fill_value)


def createBinary(cnp.ndarray[cnp.int32_t,ndim = 2] b1, cnp.ndarray[cnp.int32_t,ndim = 2] b2, cnp.ndarray[cnp.int32_t,ndim = 2] hgt,int fill):
    cdef int n1
    cdef cnp.ndarray[short,ndim = 2] out
    n1 = hgt.shape[0]
    n2 = hgt.shape[1]

    out = np.zeros((n1,n2),dtype = np.int16)

    fillData(<int (*)[5]> b1.data,<int (*)[5]> b2.data,<int (*)[125]> hgt.data,<short (*)[125]> out.data,n1,fill)

    return out

#%%%%%%%%%%%%%%%%%%%%%%%%%%%Layer match functions below needs to be worked on!!!%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

cdef double inner_find_height(double[:] lh,double lhBin,int fill_value):
    '''
    '''
    cdef int i = 0
    cdef int missCheck = 0
    cdef double tempDiff = 0.
    cdef double minimum = 100000000.
    cdef double hgt_out = -999

    print(lh[0])
    while(i < 5 and missCheck == 0):
        if(lh[i] == <double> fill_value):
            missCheck = 1
        else:
            tempDiff = lh[i] - lhBin
            #if(minimum > fabs(tempDiff)):
            #    minimum = fabs(tempDiff)
            #    hgt_out = lh[i]
            if(tempDiff >= 0. and minimum >= tempDiff):
                minimum = tempDiff
                hgt_out = lh[i]
                #print(tempDiff,lh[i],lhBin)
        i+=1

    return hgt_out

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef void find_height(
        double[:,:] hgt_bins,
        long[:] inClds,
        long[:] inIndc,
        double[:,:] layerHeight,
        long[:] outClds,
        double[:] outLayerHeight,
        short[:,:] valueCheck,
        int numClds,
        int numIndc,
        int fill_value
        ):# nogil:
    '''
    Purpose:
    Input:
    Output:
    '''
    cdef int i = 0
    cdef int cnt = 0
    cdef short layers = 5

    for i in range(numClds):
        for j in range(numIndc):
            if(valueCheck[i,j] == 1):
                outClds[cnt] = inClds[i]
                outLayerHeight[cnt] = inner_find_height(layerHeight[inIndc[j],:],hgt_bins[i,j],fill_value)
                cnt += 1

def match_level(
        cnp.ndarray[double,ndim = 2] hgt_bins, 
        cnp.ndarray[long,ndim = 1] inClds, 
        cnp.ndarray[long,ndim = 1] inIndc, 
        cnp.ndarray[double,ndim = 2] layerHeight, 
        int numClds,
        int numIndc,
        int outData_size,
        int fill_value,
        ):
    '''
    Purpose: This function wraps the test function defined above that finds the correct top and base heights for all cloud objects

    Input:
        Arrays:
            hgt_bins (double): This is a 2d-array with size (numClds,numIndc). This array holds the height bins associated with each cloudsat overpass
            inClds (long): This array contains the number associated with all cloud objects being examined in this function.
            inIndc (long): This array contains the indexes associated with pixels with cloud objects occuring on them
            layerHeight (double): This array contains either the layer base or top heights determined by cloudsat/CALIPSO
        Scalars:
            numClds (int): Number of cloud objects
            numIndc (int): Number of x-indices associated with hgt_bins
            outData_size (int): Size of the output arrays
            fill_value (int): value to check layerHeight against

    Output:

    '''

    cdef cnp.ndarray[long,ndim = 1] outClouds = np.empty(outData_size,dtype = long)
    cdef cnp.ndarray[double,ndim = 1] outLHgt   = np.empty(outData_size,dtype = np.float)
    cdef cnp.ndarray[short,ndim = 2] valueTest = np.zeros((numClds,numIndc),dtype = np.int16)

    valueTest[~np.isnan(hgt_bins)] = 1

    find_height(
            hgt_bins,
            inClds,
            inIndc,
            layerHeight,
            outClouds,
            outLHgt,
            valueTest,
            numClds,
            numIndc,
            fill_value
            )

    return outClouds,outLHgt
