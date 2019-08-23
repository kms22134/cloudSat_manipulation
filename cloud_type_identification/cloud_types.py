from os import path,walk,remove
import subprocess
from h5py import File
from xarray import open_dataset
from numpy import array,unravel_index,unique,isin
from numpy import isnan,nan
from scipy.sparse import coo_matrix
from pandas import Series,DataFrame

class CloudType(object):
    '''
    '''

    def __init__(self,pArgs,):
        '''
        Purpose: this funtion initializes this class

        inputs:
            pArgs: command line arguments of type argparse
        '''

        self.pfPath = pArgs.precipColumn
        self.glPath = pArgs.geoprofLidar
        self.ncDir  = pArgs.netCDF

    def run(self,fTypeHDF = 'h5'):
        '''
        purpose: run command line tool cloudType
        '''

        self._unit_conversions()

        self.fType = fTypeHDF

        if(not self._path_decision(self.pfPath) and not self._path_decision(self.glPath)):
            self.pfPath = self._packed(self.pfPath)
            self.glPath = self._packed(self.glPath)
        elif(not self._path_decision(self.pfPath) and self._path_decision(self.glPath)):
            self.pfPath = self._packed(self.pfPath)
        elif(self._path_decision(self.pfPath) and not self._path_decision(self.glPath)):
            self.glPath = self._packed(self.glPath)
        #else:
        #    raise Exception("add condition")

        self.pfFiles = self._ravel_files(self.pfPath,self.fType)
        self.glFiles = self._ravel_files(self.glPath,self.fType)
        self.ncFiles = self._ravel_files(self.ncDir,'nc')

        self.pfDateTags = self._hdf_dateTag(self.pfFiles)
        self.glDateTags = self._hdf_dateTag(self.glFiles)

        for i,self.ncFile in enumerate(self.ncFiles):
            ncDateTag    = path.basename(self.ncFile)
            ncDateTag    = path.splitext(ncDateTag)[0]
            ncDateTag    = ncDateTag.split('_')[0]

            #%%%%%%%%%%%%%%%%%%%%%%%%%if either the 2C-RAIN-PROFILE or 2C-PRECIP-COLUMN file do not exist delete output netcdf%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            try: self.pfFile = self.pfFiles[self.pfDateTags.index(ncDateTag)]
            except: 
                remove(self.ncFile)
                continue
            try: self.glFile = self.glFiles[self.glDateTags.index(ncDateTag)]
            except: 
                remove(self.ncFile)
                continue

            self.pfh5Obj = File(self.pfFile,'r')#read 2C-RAIN-PROFILE data
            self.glh5Obj = File(self.glFile,'r')#read 2C-RAIN-PROFILE data

            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%read datasets%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            self.pfDataset                                  = self.pfh5Obj['2C-PRECIP-COLUMN']
            self.glDataset                                  = self.glh5Obj['2B-GEOPROF-LIDAR']
            self.pfDataFields,self.pfGeoFields,self.pfSwath = self._h5_outside_datasets(self.pfDataset)  
            self.glDataFields,self.glGeoFields,self.glSwath = self._h5_outside_datasets(self.glDataset)  

            self.height = self.glGeoFields['Height'][:,]##cloudsat height variable

            self.freezing_level = array(self.pfDataFields['Freezing_level'][:,].tolist()).flatten()
            self.freezing_level = self._scaleAdjust('Freezing_level',self.freezing_level,self.pfSwath)
            self.freezing_level = self._maskData('Freezing_level',self.freezing_level,self.pfSwath)
            self.freezing_level = self.freezing_level * self.kmTom
            self._extract_sparce_datasets()

            self._sparce_to_full()

            self.identify_warm_clouds()
            ## match lts to cloud objects
            ##identify stratocumulus clouds
            ##identify shallow cumulus

    def identify_warm_clouds(self,):
        '''
        '''
        self.freezing_level[isnan(self.freezing_level)] = -1e10

        hgtMsk = self.height <= self.freezing_level[:,None]
        tmpWrm = self.full_objs[hgtMsk]
        tmpWrm,wrmCnt = unique(tmpWrm[tmpWrm != 0],return_counts = True)

        tmpFull,fullCnt = unique(self.full_objs[self.full_objs != 0],return_counts = True)

        wrmMsk  = isin(tmpFull,tmpWrm)
        wrmfrac = wrmCnt / fullCnt[wrmMsk]

        self.warm_clouds = tmpWrm[wrmfrac == 1]



    def _packed(self,dirIn):
        '''
        Purpose: this function works with tar archives
        '''
        inputDir                 = path.split(dirIn)[1]
        inputDir,compressionType = path.splitext(inputDir)
        inputDir                 = path.splitext(inputDir)[0]
        ##%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if(compressionType == '.xz'):
            subprocess.call(['tar','xJvf',dirIn])
        elif(compressionType == '.gz'):
            subprocess.call(['tar','xzvf',dirIn])
        else:
            raise Exception("add decompression of other variables")
        #%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        return f'{getcwd()}/{inputDir}'

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _path_decision(self,directory):
        return path.isdir(directory)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%5
    def _ravel_files(self,inDir,fType):
        inFiles = []
        for dp,dn,filenames in walk(inDir):
            for f in filenames:
                if(path.splitext(f)[-1] == f'.{fType}'): inFiles.append(path.join(dp,f))
        sorted(inFiles)

        return inFiles
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%5

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%5
    def _hdf_dateTag(self,files):
        self.hdfDateTags = []
        for f in files:
            tmpF = path.basename(f)
            tmpF = path.splitext(tmpF)[0]
            tmpF = tmpF.split('_')[0]
            self.hdfDateTags.append(tmpF)

        return self.hdfDateTags

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _h5_outside_datasets(self,dset):
        '''
        '''
        
        geoFields  = dset['Geolocation Fields']
        dataFields = dset['Data Fields']
        swath      = dset['Swath Attributes']

        return dataFields,geoFields,swath

    def _unit_conversions(self,):
        self.kmTom = 1000.

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _scaleAdjust(self,variable,var,swath):
        '''
        purpose: remove scale and offset from h5-data variable

        inputs:
            variable (string):     variable name in h5 file
            var      (ndarray):    data associated with variable
            swath    (h5 dataset): variable attributes

        outputs:
            scaled and offset version of var (see return statement)
        '''
    
        varSwath = [s for s in swath.keys() if variable in s and '_t' not in s]
        factor   = swath[[s for s in varSwath if 'factor' in s][0]][0][0]
        offset   = swath[[s for s in varSwath if 'offset' in s][0]][0][0]

        return (var * factor) + offset

    def _maskData(self,variable,var,swath):
        '''
        '''
        varSwath = [s for s in swath.keys() if variable in s and '_t' not in s]
        fill       = swath[[s for s in varSwath if 'missing' in s][0]][0][0]
        validRange = swath[[s for s in varSwath if 'range' in s][0]][0][0]

        var[isnan(var)] = fill
        var[~((var <= max(validRange)) & (var >= min(validRange)))] = fill
        var[var == fill] = nan

        return var

    def _extract_sparce_datasets(self,):
        self.ncData           = open_dataset(self.ncFile)
        self.orbitShape       = self.ncData.cloudSat_shape.values
        self.sparceObjects    = self.ncData.sparce_objects.values
        self.sparceIndices    = self.ncData.sparce_1d_indx.values
        self.xIndc,self.yIndc = unravel_index(self.sparceIndices,self.orbitShape)

    def _sparce_to_full(self,):
        self.full_objs = array(coo_matrix((self.sparceObjects,(self.xIndc,self.yIndc)),shape = self.orbitShape).todense())
