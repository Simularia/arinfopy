#!/usr/bin/env python3
# 
###############################################################################
# 
# arinfopy parser for ADSO/bin files.
# Copyright (C) 2013 by Giuseppe Carlino (Simularia s.r.l.) g.carlino@simularia.it
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# 
#
# Simularia S.r.l.
# via Principe Tommaso 39
# Torino, Italy
# www.simularia.it
# info@simularia.it
# 
############################################################################### 


import sys
import os
import struct
import argparse
import logging
from datetime import datetime, timedelta

class adsobin(object):
    '''Class to read data from ADSO/BIN file.'''

    def __init__(self, filename):
        with open(filename, 'rb') as f:
            self.__data = f.read()


    def __len__(self):
        '''Get number of deadlines.'''
        __nBytesDeadline = self.__readDeadlineBlockSize()
        __remDeadlines = len(self.__data) % __nBytesDeadline
        if __remDeadlines != 0:
            raise
        __nDeadlines = int(len(self.__data) / __nBytesDeadline)
        return __nDeadlines


    def __readDeadlineBlockSize(self):
        # Read record 3 of 1st deadline
        __start = 32
        __rec3 = self.__readRecord3(__start)
        __pad = 8
        __int = 4
        __real = 4
        __nRec1 = __pad + 8
        __nRec2 = __pad + 8
        __nRec3 = __pad + 27 * __int
        __nRec4 = __pad + (11 + __rec3['kmmai']) * __real
        __nRec5 = __pad + (__rec3['nreper'] * 8 + 
                           __rec3['nvar3d'] * (8 + 8) + 
                           __rec3['nvar2d'] * (8 + 8))
        if __rec3['nreper'] != 0:
            __nRec6 = __pad + 3 * __rec3['nreper'] * __real
        else: 
            __nRec6 = 0
        __nRec7 = (__rec3['nvar2d'] * (__pad + __real * __rec3['immai'] *
                 __rec3['jmmai']) + 
                 __rec3['nvar3d'] * (__pad + __real * __rec3['immai'] *
                 __rec3['jmmai'] * __rec3['kmmai']))

        __nBytesDeadline = (__nRec1 + __nRec2 + __nRec3 + __nRec4 + __nRec5 +
                __nRec6 + __nRec7)

        return __nBytesDeadline

    def __readRecord3(self, start):
        __nStart, __binData = self.__readADSOChunk(start, self.__data)
        __num = struct.unpack('@27i', __binData)
        __rec3 = {'ijozer': __num[0], 'imozer': __num[1], 'ianzer': __num[2],
                'ihezer': __num[3], 'imizer': __num[4], 'isezer': __num[5],
                'ijozei': __num[6], 'imozei': __num[7], 'ianzei': __num[8],
                'ihezei': __num[9], 'imizei': __num[10], 'isezei': __num[11],
                'immai': __num[12], 'jmmai': __num[13], 'kmmai': __num[14], 
                'nreper': __num[15], 'nvar3d': __num[16], 'nvar2d': __num[17],
                'nevt': __num[18], 'itmax': __num[19], 'nevtpr': __num[20],
                'itmopro': __num[21], 'IINDEX': __num[22], 'IKSURF': __num[23]}
        return __rec3


    def __readADSOChunk(self, rStart, rData):
        """
        Function to read from ADSO/BIN 
        Note: Fortran unformatted file add 4 bytes at the beginning and at the
        end of each chunk of data written

        INPUT:  rStart      -> initial offset
                rData       -> binary data as read from input file

        OUTPUT: rEnd        -> final offest
                rBinData    -> binary object read to be parsed with
                               struct.unpack
        """

        logger.debug('Read chunk of bytes from ADSO/BIN file.')
        logger.debug('Length of bin data: {}'.format(len(rData)))
        logger.debug('Initial offset: {}'.format(rStart))
        rPad = 4
        rLength = struct.unpack('@I', rData[rStart:rStart+rPad])[0]
        rStart += rPad
        rBinData = rData[rStart:rStart+rLength]
        rEnd = rStart+rLength+rPad      # Final offest
        logger.debug('Bytes to be read: {}'.format(rLength))
        logger.debug('Final offset: {}'.format(rEnd))
        return [rEnd, rBinData]


def arinfopyNew(fInput):

    mData = adsobin(fInput)
    print('Number of deadlines: {}'.format(len(mData)))


###################


def readADSOChunk(rStart, rData):
    logger.debug('Read chunk of bytes from ADSO/BIN file.')
    logger.debug('Length of bin data: {}'.format(len(rData)))
    logger.debug('Initial offset: {}'.format(rStart))
    rPad = 4
    rLength = struct.unpack('@I', rData[rStart:rStart+rPad])[0]
    rStart += rPad
    rBinData = rData[rStart:rStart+rLength]
    rEnd = rStart+rLength+rPad      # Final offest
    logger.debug('Bytes to be read: {}'.format(rLength))
    logger.debug('Final offset: {}'.format(rEnd))
    return [rEnd, rBinData]


def arinfopy(fInput, DEBUG):
    #
    # Open, read and close ADSO/bin file
    #
    if DEBUG  :
        os.system('python --version')
        os.system('which python')

    with open(fInput, 'rb') as f:
        data = f.read()
    #f.close()


    necdis = 0  # Number of deadlines
    start = 0   # offset for the binary files
    dtsecs = 0  # deadline frequency

    # Loop on binary data
    while start < len(data) :
        # Count number of deadlines
        necdis = necdis+1

        logger.debug('Deadline # {} '.format(necdis))
                
        # 
        # -----DECLARATION OF THE "BINAIRA" TYPE
        # 
        # 
        # Record 1 & 2-> 16 characters
        # 
        #                   character*8
        #                   character*8 code that generated the file
        logger.debug('--- Read Record 1 ---')

        start, binData = readADSOChunk(start, data)
        ident1 = struct.unpack('@8s',binData)[0].decode("utf-8")

        logger.debug('ident1 : {}'.format(ident1))

        logger.debug('--- Read Record 2 ---')

        start, binData = readADSOChunk(start,data)
        ident2 = struct.unpack('@8s',binData)[0].decode("utf-8")
        
        logger.debug('ident2 : {}'.format(ident2))

        
        
        # 
        #   Blocks for all the time frames
        # 
        # 
        # -----RECORD NUMBER 3---------------------------------
        # 
        # 27 integers (4 bytes each)
        #       6 integers time frame
        #       6 integers of first time frame of the file
        #       3 integers immai, jmmai, kmmai 
        #                       with num of horiz grid points in x, y and z dir
        #       integer nreper
        #                       number of reference points
        #                       ignored in Spray 3.1 (it can be=0)
        #       integer nvar3d
        #                       number of 3D stored fields
        #       integer nvar2d
        #                       number of 2D stored fields
        #       4 integers ignored
        #       2 integers IINDEX, IKSURF
        #                      vertical addressing order of 3D arrays (=1)
        #       3 integers ignored
        logger.debug('--- Read Record 3 ---')
        
        start, binData = readADSOChunk(start, data)
        num = struct.unpack('@27i',binData)
        rec3 = {'ijozer': num[0], 'imozer': num[1], 'ianzer': num[2],
                'ihezer': num[3], 'imizer': num[4], 'isezer': num[5],
                'ijozei': num[6], 'imozei': num[7], 'ianzei': num[8],
                'ihezei': num[9], 'imizei': num[10], 'isezei': num[11],
                'immai': num[12], 'jmmai': num[13], 'kmmai': num[14], 
                'nreper': num[15], 'nvar3d': num[16], 'nvar2d': num[17],
                'nevt': num[18], 'itmax': num[19], 'nevtpr': num[20],
                'itmopro': num[21], 'IINDEX': num[22], 'IKSURF': num[23]}

        # Read current deadline
        currentdl = datetime(2000 + rec3['ianzer'], 
                             rec3['imozer'],
                             rec3['ijozer'], 
                             rec3['ihezer'] % 24, 
                             rec3['imizer'],
                             rec3['isezer'])

        # Correct if hour = 24 since in datetime 0 <= hour < 24
        if rec3['ihezer'] == 24:
            currentdl = currentdl + timedelta(1)

        # Set first deadline
        if necdis == 1 :
            firstdl = currentdl
        
        # Compute deadline frequency in seconds
        if necdis == 2:
            dtsecs = (currentdl - firstdl).seconds
        
        logger.debug('firstdl   : {}'.format(firstdl))
        logger.debug('currentdl : {}'.format(currentdl))
        logger.debug('nvar3d    : {}'.format(rec3['nvar3d']))
        logger.debug('nvar2d    : {}'.format(rec3['nvar2d']))
        logger.debug('kmmai     : {}'.format(rec3['kmmai']))
        logger.debug('nreper    : {}'.format(rec3['nreper']))

        # 
        # -----RECORD NUMBER 4-------------------------------------
        # 
        # Record 4 -> 11+kmmai reals 
        #         kmmai real SGRID
        #                 vertical terrain following coordinates vector
        #         2 real dxmai, dymai
        #                 linear directions of horiz grid in meters
        #         2 real xlso, ylso
        #                 x & y Cartesian coords of domain orig (km)
        #         2 real xlatso, ylonso
        #                 lat lon of the origin     
        #         4 real ignored
        #         1 real ZTOP
        #                 absolute heigh of domain top plane in meters
        logger.debug('--- Read Record 4')

        start, binData = readADSOChunk(start, data)

        nReals = 11+rec3['kmmai']

        typedef = '@' + str(nReals) + 'f'
        logger.debug('typedef: {}'.format(typedef))

        fnum = struct.unpack(typedef, binData)

        sgrid = fnum[0:rec3['kmmai']]
        i = rec3['kmmai']
        dxmai = fnum[i]
        dymai = fnum[i+1]
        xlso = fnum[i+2] 
        ylso = fnum[i+3]
        xlatso = fnum[i+4]
        ylatso = fnum[i+5]
        ztop = fnum[i+10]

        logger.debug('ztop : {}'.format(ztop))

        # 
        # -----RECORD NUMBER 5 : CHARACTER ARRAYS-------------------
        # 
        #  Vector of character*8 strings
        #               NREPER character *8
        #                       site name at ref point       
        #               NVAR3D charecter*8 NOMVAR3D
        #                       names of 3D variables
        #               NVAR3D character*8 UNIVAR3D
        #                       unit of meas of 3D variables
        #               NVAR2D character*8 NOMVAR2D
        #                       names of 2D variables
        #               NVAR2D character*8 UNIVAR2D
        #                       unit of meas of 2D variables
        logger.debug('--- Read Record 5')

        start, binData = readADSOChunk(start, data)

        nStrings = rec3['nreper'] + 2 * rec3['nvar3d'] + 2 * rec3['nvar2d']
        typedef = '@' + str(nStrings*8) + 's'
        logger.debug('typedef: {}'.format(typedef))

        sStrings = struct.unpack(typedef, binData)
        # print(sStrings[0])

        creper = ''
        nomvar3D = ''
        univar3d = ''
        nomvar2d = ''
        univar2d = ''

        creper = [struct.unpack('@8s', binData[i:rec3['nreper']*8])[0] for i in
                range(rec3['nreper'])]

        offset = (rec3['nreper']) * 8
        nomvar3d = [struct.unpack('@8s', binData[offset+i*8:offset +
            (i+1)*8])[0] for i in range(rec3['nvar3d'])]

        offset = (rec3['nreper'] + rec3['nvar3d']) * 8
        univar3d = [struct.unpack('@8s', binData[offset+i*8:offset +
            (i+1)*8])[0] for i in range(rec3['nvar3d'])]

        offset = (rec3['nreper'] + 2*rec3['nvar3d']) * 8
        nomvar2d = [struct.unpack('@8s', binData[offset+i*8:offset +
            (i+1)*8])[0] for i in range(rec3['nvar2d'])]

        offset = (rec3['nreper'] + 2*rec3['nvar3d'] + rec3['nvar2d']) * 8
        univar2d = [struct.unpack('@8s', binData[offset+i*8:offset
            +(i+1)*8])[0] for i in range(rec3['nvar2d'])]

        # 
        # -----RECORD NUMBER 6 : KEY POINTS COORDINATES--------------
        # 
        #   3*NREPER REALS
        # 
        logger.debug('\n--- Read Record 6')

        # 
        # -----RECORD NUMBER 7 : 3D FIELDS----------------------------
        # 
        # #
        # #       Record 5 to 5+NVAR3D-1
        # #               NVAR3D 3D arrays with variables on the 3D grid
        # #               orderd as indicated by NOMVAR3D names vector
        # #       
        logger.debug('\n--- Read Record 7 (3D fields)')
        
        for i in range(rec3['nvar3d'])  :
            logger.debug('Read 3D variable # {}\n'.format(i))
            start, binData = readADSOChunk(start, data)

        for i in range(rec3['nvar2d'])  :
            logger.debug('Read 2D variable # {}\n'.format(i))
            start, binData = readADSOChunk(start, data)

    # # Check if we are at the end of file
    #     if start == len(data) :
    #         break
        

    #  Info output
    print('\n--- ADSO/bin file info ---')
    print('File generator              :  {}'.format(ident2))
    print('First deadline              :  {}'.format(firstdl))
    print('Last deadline               :  {}'.format(currentdl))
    print('Deadline frequency (s)      :  {}'.format(dtsecs))
    print('# of deadlines              :  {}'.format(necdis))
    print('# of gridpoints (x, y, z)   :  {}   {}   {}'.format(rec3['immai'],
        rec3['jmmai'], rec3['kmmai']))
    print('Grid cell sizes (x, y)      :  {:.3f}   {:.3f}'.format(dxmai,
            dymai))
    print('Coord. of SW corner (metric):  {:.3f}   {:>.3f}'.format(xlso, ylso))             
    print('Coord. of SW corner (geo)   :  {:.3f}   {:.3f}'.format(xlatso,
        ylatso))
    print('Top of the domain           :  {:.3f}'.format(ztop))
    print(('Levels                      :  ' + '{:.2f}  ' * len(sgrid)).
            format(*sgrid))
    print('nvar2d, nvar3d              :  {:d}    {:d}'.format(rec3['nvar2d'],
        rec3['nvar3d']))
    if rec3['nvar2d'] > 0 :
        print(('2D variabels                :  ' + '{:s} ' * rec3['nvar2d']).
                format(*nomvar2d))
    if rec3['nvar3d'] > 0 :
        print(('3D variables                :  ' + '{:s} ' * rec3['nvar3d']).
                format(*nomvar3d))




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description =
            'arinfopy parser for ADSO/bin files.')
    parser.add_argument('inifile', help = 'File to be parsed')
    parser.add_argument('-v', '--verbose',
            help = 'Increse output verbosity.',
            action="store_true")
    args = parser.parse_args()
    
    # Create Logger
    logger = logging.getLogger('elisestat')
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
#    flogname = 'elisestat_' + datetime.now().isoformat() + '.log'
#    flog = logging.FileHandler(flogname)
#    flog.setLevel(logging.INFO)
#    flog.setFormatter(formatter)
#    logger.addHandler(flog)
    
    #arinfopy(args.inifile, args.verbose)
    arinfopyNew(args.inifile)
