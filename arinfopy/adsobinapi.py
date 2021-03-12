###############################################################################
#
# arinfopy parser for ADSO/bin files.
# Copyright (C) 2013 by Giuseppe Carlino (Simularia s.r.l.)
#                       g.carlino@simularia.it
# Modified 2018 for ADSO/bin writing by Bruno Guillaume (ARIA Technologies)
#                        bguillaume@aria.fr
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
#
#
# Simularia S.r.l.
# via Sant'Antonio da Padova 12
# Torino, Italy
# www.simularia.it
# info@simularia.it
#
###############################################################################

# import argparse
# import logging
# import os
import struct
from datetime import datetime, timedelta
import pytz

import numpy as np
# import pkg_resources

# Size of data type and data padding
size = {'int': 4,
        'real': 4,
        'char8': 8,
        'pad': (4 + 4)}


class adsowritebin(object):
    '''Class to write data to ADSO/BIN file.'''

    def __init__(self):
        '''
        Constructor
        '''

    def putRecord1(self, ident1):
        pad1 = struct.pack('@i', size['char8'])
        typedef = '@' + str(size['char8']) + 's'
        idpack = struct.pack(typedef, str.encode(ident1))
        pad2 = struct.pack('@i', size['char8'])
        return pad1+idpack+pad2

    def putRecord2(self, model1):
        pad1 = struct.pack('@i', size['char8'])
        typedef = '@' + str(size['char8']) + 's'
        mopack = struct.pack(typedef, str.encode(model1))
        pad2 = struct.pack('@i', size['char8'])
        return pad1+mopack+pad2

    def putRecord3(self, rec3):
        l0 = []
        l0.append(rec3['ijozer'])
        l0.append(rec3['imozer'])
        l0.append(rec3['ianzer'])
        l0.append(rec3['ihezer'])
        l0.append(rec3['imizer'])
        l0.append(rec3['isezer'])
        l0.append(rec3['ijozei'])
        l0.append(rec3['imozei'])
        l0.append(rec3['ianzei'])
        l0.append(rec3['ihezei'])
        l0.append(rec3['imizei'])
        l0.append(rec3['isezei'])
        l0.append(rec3['immai'])
        l0.append(rec3['jmmai'])
        l0.append(rec3['kmmai'])
        l0.append(rec3['nreper'])
        l0.append(rec3['nvar3d'])
        l0.append(rec3['nvar2d'])
        l0.append(rec3['nevt'])
        l0.append(rec3['itmax'])
        l0.append(rec3['nevtpr'])
        l0.append(rec3['itmopro'])
        l0.append(rec3['IINDEX'])
        l0.append(rec3['IKSURF'])
        l0.append(0)
        l0.append(0)
        l0.append(0)
        nlen = size['int']*27
        pad1 = struct.pack('@i', nlen)
        r3pack = struct.pack('@27i', *l0)
        pad2 = struct.pack('@i', nlen)
        return pad1+r3pack+pad2
    # ## DRAFT
    # bytes=[... for i in range()] # list
    # return struct.pack(fmt, *bytes)

    def putRecord4(self, rec4, kmmai):
        fnum = []
        for i in range(kmmai):
            fnum.append(rec4['sgrid'][i])
        fnum.append(rec4['dxmai'])
        fnum.append(rec4['dymai'])
        fnum.append(rec4['xlso'])
        fnum.append(rec4['ylso'])
        fnum.append(rec4['xlatso'])
        fnum.append(rec4['ylatso'])
        fnum.append(0)
        fnum.append(0)
        fnum.append(0)
        fnum.append(0)
        fnum.append(rec4['ztop'])
        nReals = 11 + kmmai
        typedef = '@' + str(nReals) + 'f'
        nlen = size['real']*nReals
        pad1 = struct.pack('@i', nlen)
        r4pack = struct.pack(typedef, *fnum)
        pad2 = struct.pack('@i', nlen)
        return pad1+r4pack+pad2

    def putRecord5(self, rec5):
        # nreper=len(creper)
        nreper = 0
        nvar3d = len(rec5['nomvar3d'])
        nvar2d = len(rec5['nomvar2d'])

        nlen = (nreper + 2 * nvar3d + 2 * nvar2d)*size['char8']
        pad1 = struct.pack('@i', nlen)
        pad2 = struct.pack('@i', nlen)

        typedef = '@' + str(size['char8']) + 's'
        r5pack = b''
        for i in range(nreper):
            r5pack += struct.pack(typedef, str.encode(rec5['creper'][i]))
        for i in range(nvar3d):
            r5pack += struct.pack(typedef, str.encode(rec5['nomvar3d'][i]))
        for i in range(nvar3d):
            r5pack += struct.pack(typedef, str.encode(rec5['univar3d'][i]))
        for i in range(nvar2d):
            r5pack += struct.pack(typedef, str.encode(rec5['nomvar2d'][i]))
        for i in range(nvar2d):
            r5pack += struct.pack(typedef, str.encode(rec5['univar2d'][i]))
        return pad1+r5pack+pad2

    def putRecord6(self):
        ''' not yet implemented'''
        pass

    def putRecord7(self, rec7, immai, jmmai, kmmai):
        # rec7={'var3d':[vartab31,vartab32,...],'var2d':[vartab21,vartab22,..]}
        # tables are numpy arrays order in following convention:
        # np.array[kmmai,jmmai,immai], # which have been pre-stored in
        # order 'C': (i+(j-1)*immai+(k-1)*immai*jmmai)

        nvar3d = len(rec7['var3d'])
        nvar2d = len(rec7['var2d'])

        r7pack = b''
        for i in range(nvar3d):
            l1d = list(rec7['var3d'][i].reshape(immai*jmmai*kmmai))
            # print('nvar3d:',i,rec7['var3d'][i])
            nReals = immai*jmmai*kmmai
            nlen = nReals*size['real']
            pad1 = struct.pack('@i', nlen)
            pad2 = struct.pack('@i', nlen)
            typedef = '@' + str(nReals) + 'f'
            r7pack += pad1+struct.pack(typedef, *l1d)+pad2
        for i in range(nvar2d):
            l2d = list(rec7['var2d'][i].reshape(immai*jmmai))
            # print('nvar2d:',i,rec7['var2d'][i])
            nReals = immai*jmmai
            nlen = nReals*size['real']
            pad1 = struct.pack('@i', nlen)
            pad2 = struct.pack('@i', nlen)
            typedef = '@' + str(nReals) + 'f'
            r7pack += pad1+struct.pack(typedef, *l2d)+pad2
        return r7pack


class adsobin(object):
    '''Class to read data from ADSO/BIN file.'''

    def __init__(self, filename):
        '''
        Consutctor: open and read ADSO/BIN file
        '''

        self.filename = filename
        with open(self.filename, 'rb') as f:
            self.__data = f.read()

        # Get the size of records and deadlne
        self.size = self.getDeadlineBlockSize()
        # Single deadline offsets
        # to get each deadline offset you need to sum the proper deadline
        # blocksize
        self.offset = {
                'rec1': 0,
                'rec2': self.size['rec1'],
                'rec3': (self.size['rec1'] + self.size['rec2']),
                'rec4': (self.size['rec1'] + self.size['rec2'] +
                         self.size['rec3']),
                'rec5': (self.size['rec1'] + self.size['rec2'] +
                         self.size['rec3'] + self.size['rec4']),
                'rec6': (self.size['rec1'] + self.size['rec2'] +
                         self.size['rec3'] + self.size['rec4'] +
                         self.size['rec5']),
                'rec7': (self.size['rec1'] + self.size['rec2'] +
                         self.size['rec3'] + self.size['rec4'] +
                         self.size['rec5'] + self.size['rec6'])
                }

    def getRecord1(self, deadline=1):
        '''
        Returns file header
        -----DECLARATION OF THE "BINAIRA" TYPE
        Record 1 -> character*8
        '''
        start = (deadline - 1) * self.size['blockSize'] + self.offset['rec1']
        start, binData = self.__readADSOChunk(start, self.__data)
        _ident1 = struct.unpack('@8s', binData)[0].decode("utf-8")
        # logger.debug('ident1 : {}'.format(_ident1))
        return _ident1

    def getVersion(self):
        '''
        Returns string with ADSO/BIN fileversion
        '''
        # Read record 1 of first deadline
        header = self.getRecord1(1)
        if header == 'BBBBBBBB':
            version = '0'
        else:
            version = header[-3:]
        return version

    def getRecord2(self, deadline=1):
        '''
        Returns file generator
        Record 2 -> character*8 code that generated the file
        '''
        # logger.debug('--- Read Record 2 ---')
        start = (deadline - 1) * self.size['blockSize'] + self.offset['rec2']
        start, binData = self.__readADSOChunk(start, self.__data)
        _ident2 = struct.unpack('@8s', binData)[0].decode("utf-8")
        # logger.debug('ident2 : {}'.format(_ident2))
        return _ident2

    def getRecord3(self, deadline=1, offset=None):
        '''
        Read record 3 of deadline.
        -----RECORD NUMBER 3---------------------------------
        27 integers (4 bytes each)
               6 integers time frame
               6 integers of first time frame of the file
               3 integers immai, jmmai, kmmai
                               with num of horiz grid points in x, y and z dir
               integer nreper
                               number of reference points
                               ignored in Spray 3.1 (it can be=0)
               integer nvar3d
                               number of 3D stored fields
               integer nvar2d
                               number of 2D stored fields
               4 integers ignored
               2 integers IINDEX, IKSURF
                              vertical addressing order of 3D arrays (=1)
               3 integers ignored
        '''
        # logger.debug('--- Read Record 3 ---')
        #  if offset != None:
        if offset is not None:
            start = offset
        else:
            start = (deadline - 1) * self.size['blockSize'] + \
                self.offset['rec3']
        __nStart, __binData = self.__readADSOChunk(start, self.__data)
        __num = struct.unpack('@27i', __binData)
        __rec3 = {'ijozer': __num[0], 'imozer': __num[1], 'ianzer': __num[2],
                  'ihezer': __num[3], 'imizer': __num[4], 'isezer': __num[5],
                  'ijozei': __num[6], 'imozei': __num[7], 'ianzei': __num[8],
                  'ihezei': __num[9], 'imizei': __num[10], 'isezei': __num[11],
                  'immai': __num[12], 'jmmai': __num[13], 'kmmai': __num[14],
                  'nreper': __num[15], 'nvar3d': __num[16],
                  'nvar2d': __num[17], 'nevt': __num[18], 'itmax': __num[19],
                  'nevtpr': __num[20], 'itmopro': __num[21],
                  'IINDEX': __num[22], 'IKSURF': __num[23]}
        if __rec3['ianzer'] < 1000:
            __rec3['ianzer'] += 2000
        if __rec3['ianzei'] < 1000:
            __rec3['ianzei'] += 2000

        return __rec3

    def getRecord4(self, deadline=1):
        '''
        Read record 4 of deadline
        -----RECORD NUMBER 4-------------------------------------
        Record 4 -> 11+kmmai reals
                 kmmai real SGRID
                         vertical terrain following coordinates vector
                 2 real dxmai, dymai
                         linear directions of horiz grid in meters
                 2 real xlso, ylso
                         x & y Cartesian coords of domain orig (km)
                 2 real xlatso, ylonso
                         lat lon of the origin
                 4 real ignored
                 1 real ZTOP
                         absolute heigh of domain top plane in meters
        '''
        # logger.debug('--- Read Record 4 ---')
        start = (deadline - 1) * self.size['blockSize'] + self.offset['rec4']
        start, binData = self.__readADSOChunk(start, self.__data)

        rec3 = self.getRecord3(deadline)
        nReals = 11 + rec3['kmmai']
        typedef = '@' + str(nReals) + 'f'
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

        rec4 = {'sgrid': sgrid,
                'dxmai': dxmai,
                'dymai': dymai,
                'xlso': xlso,
                'ylso': ylso,
                'xlatso': xlatso,
                'ylatso': ylatso,
                'ztop': ztop}
        return rec4

    def getRecord5(self, deadline=1):
        '''
        Read record 5 of deadline
        -----RECORD NUMBER 5 : CHARACTER ARRAYS-------------------
        Vector of character*8 strings
                       NREPER character *8
                               site name at ref point
                       NVAR3D charecter*8 NOMVAR3D
                               names of 3D variables
                       NVAR3D character*8 UNIVAR3D
                               unit of meas of 3D variables
                       NVAR2D character*8 NOMVAR2D
                               names of 2D variables
                       NVAR2D character*8 UNIVAR2D
                               unit of meas of 2D variables
        '''
        # logger.debug('--- Read Record 5 ---')
        start = (deadline - 1) * self.size['blockSize'] + self.offset['rec5']
        start, binData = self.__readADSOChunk(start, self.__data)

        rec3 = self.getRecord3(deadline)
        # nStrings = rec3['nreper'] + 2 * rec3['nvar3d'] + 2 * rec3['nvar2d']
        # typedef = '@' + str(nStrings * size['char8']) + 's'
        # logger.debug('typedef: {}'.format(typedef))

        # sStrings = struct.unpack(typedef, binData)

        # creper = ''
        # nomvar3D = ''
        # univar3d = ''
        # nomvar2d = ''
        # univar2d = ''

        # creper = [struct.unpack('@8s', binData[i:rec3['nreper']*8])[0]
        #           for i in range(rec3['nreper'])]
        offset = (rec3['nreper']) * 8
        nomvar3d = [struct.unpack('@8s', binData[offset+i*8:offset +
                    (i+1)*8])[0].decode('utf-8') for i in
                    range(rec3['nvar3d'])]
        offset = (rec3['nreper'] + rec3['nvar3d']) * 8
        univar3d = [struct.unpack('@8s', binData[offset+i*8:offset +
                    (i+1)*8])[0].decode('utf-8') for i in
                    range(rec3['nvar3d'])]
        offset = (rec3['nreper'] + 2*rec3['nvar3d']) * 8
        nomvar2d = [struct.unpack('@8s', binData[offset+i*8:offset +
                    (i+1)*8])[0].decode('utf-8') for i in
                    range(rec3['nvar2d'])]
        offset = (rec3['nreper'] + 2*rec3['nvar3d'] + rec3['nvar2d']) * 8
        univar2d = [struct.unpack('@8s', binData[offset+i*8:offset +
                    (i+1)*8])[0].decode('utf-8') for i in
                    range(rec3['nvar2d'])]

        # Strip whitespaces in nomva3d and nomvar2d
        # nomvar3d = [name.strip() for name in nomvar3d]
        # nomvar2d = [name.strip() for name in nomvar2d]
        rec5 = {'nomvar3d': nomvar3d,
                'univar3d': univar3d,
                'nomvar2d': nomvar2d,
                'univar2d': univar2d}
        # logger.debug('rec5: {}'.format(rec5))
        return rec5

    def getRecord6(self, start):
        '''
        Read record 6 of deadline
        -----RECORD NUMBER 6 : KEY POINTS COORDINATES--------------
           3*NREPER REALS
        '''
        # logger.debug('--- Read Record 6 ---')
        pass

    def getRecord7(self, deadline=1):
        '''
        Read record 7 of deadline
        -----RECORD NUMBER 7 : 3D FIELDS----------------------------
               Record 5 to 5+NVAR3D-1
                       NVAR3D 3D arrays with variables on the 3D grid
                       orderd as indicated by NOMVAR3D names vector
        '''
        # logger.debug('--- Read Record 7 ---')
        start = (deadline - 1) * self.size['blockSize'] + self.offset['rec7']
        rec3 = self.getRecord3(deadline)
        rec5 = self.getRecord5(deadline)
        rec7 = {}
        for i, name in enumerate(rec5['nomvar3d']):
            # logger.debug('Read 3D variable # {}'.format(i))
            start, binData = self.__readADSOChunk(start, self.__data)
            nReals = rec3['immai'] * rec3['jmmai'] * rec3['kmmai']
            typedef = '@' + str(nReals) + 'f'
            # rec7['%s' % name.strip()] = list(struct.unpack(typedef, binData))
            rec7[name] = list(struct.unpack(typedef, binData))

        for i, name in enumerate(rec5['nomvar2d']):
            # logger.debug('Read 2D variable # {}'.format(i))
            start, binData = self.__readADSOChunk(start, self.__data)
            nReals = rec3['immai'] * rec3['jmmai']
            typedef = '@' + str(nReals) + 'f'
            # rec7['%s' % name.strip()] = list(struct.unpack(typedef, binData))
            rec7[name] = list(struct.unpack(typedef, binData))

        return rec7

    def getDataset(self, variable):
        """
        Return all data (all dimensions) for the requested variable, as
        numpy array.
        The array can be either 4D (time, x, y, z) or 3D (time, x, y).
        If the variable does not exist an empty numpy.array is returned.
        """

        # Get list of 2D and 3D variable and dimensions
        try:
            rec5 = self.getRecord5(deadline=1)
            rec3 = self.getRecord3(deadline=1)

            nx = rec3['immai']
            ny = rec3['jmmai']
            nz = rec3['kmmai']

            nomvar3d = [name.strip() for name in rec5['nomvar3d']]
            nomvar2d = [name.strip() for name in rec5['nomvar2d']]

            # # List of deadlines
            # deadlines = self.getDeadlines()
            ndeadlines = len(self)
        except Exception:
            raise

        # Size of 2D & 3D block of data
        b2Dsize = nx * ny * size['real'] + size['pad']
        b3Dsize = nx * ny * nz * size['real'] + size['pad']

        # Is variable 2D or 3D?
        is3D = False
        try:
            # Position of 3D variable (0-based) & offset
            vc = nomvar3d.index(variable)
            is3D = True
            # data block size in each deadline
            dataSize = int(nx * ny * nz * size['real'])
            # Init the array
            allData = np.empty([ndeadlines, nx, ny, nz])
            dataShape = [nx, ny, nz]
        except ValueError:
            vc = nomvar2d.index(variable)
            dataSize = int(nx * ny * size['real'])
            allData = np.empty([ndeadlines, nx, ny])
            dataShape = [nx, ny]

        # Loop on deadlines
        for deadline in range(len(self)):
            # Get deadline offset
            offset = deadline * self.size['blockSize'] + self.offset['rec7']

            if is3D:
                offset = offset + vc * b3Dsize + int(size['pad'] / 2)
                nReals = nx * ny * nz
            else:
                offset = offset + len(rec5['nomvar3d']) * \
                    b3Dsize + vc * b2Dsize + int(size['pad'] / 2)
                nReals = nx * ny

            try:
                # Subset data and extract slice
                offset = int(offset)
                binData = self.__data[offset:offset+dataSize]
                typedef = '@' + str(nReals) + 'f'
                dData = list(struct.unpack(typedef, binData))

                # Fill the numpy array
                dData = np.array(dData)
                dData = dData.reshape(dataShape, order='F')
                allData[deadline:] = dData
            except Exception:
                raise

        return allData

    def getSlice(self, variable, slice=1, deadline=1):
        '''
        Read a slice of data from a given deadline of a given variable.
        '''

        #   Go to deadline offset
        offset = (deadline - 1) * self.size['blockSize'] + self.offset['rec7']
        try:
            rec5 = self.getRecord5(deadline)
            rec3 = self.getRecord3(deadline)
        except Exception:
            raise

        nomvar3d = [name.strip() for name in rec5['nomvar3d']]
        nomvar2d = [name.strip() for name in rec5['nomvar2d']]

        # Check if required variable is in the list of available ones

        # Size of 3D block of data
        b3Dsize = rec3['immai'] * rec3['jmmai'] * \
            rec3['kmmai'] * size['real'] + size['pad']

        # Size of 2D block of data
        b2Dsize = rec3['immai'] * rec3['jmmai'] * size['real'] + size['pad']

        # Size of 2D slice
        b2Dslice = int(rec3['immai'] * rec3['jmmai'] * size['real'])

        try:
            # Position of 3D variable (0-based)
            vc = nomvar3d.index(variable)

            # 3D variable offset
            offset = offset + vc * b3Dsize

            # slice offset
            offset = offset + int(size['pad'] / 2) + \
                (slice - 1) * b2Dslice
        except ValueError:
            pass

        try:
            # Position of 2D variable (0 based)
            vc = nomvar2d.index(variable)

            # 2D variable offset
            offset = offset + len(rec5['nomvar3d']) * \
                b3Dsize + vc * b2Dsize + int(size['pad'] / 2)
        except ValueError:
            pass

        try:
            # Subset data and extract slice
            offset = int(offset)
            binData = self.__data[offset:offset+b2Dslice]
            nReals = rec3['immai'] * rec3['jmmai']
            typedef = '@' + str(nReals) + 'f'
            slice = list(struct.unpack(typedef, binData))
        except UnboundLocalError:
            print('variable {} does not exist.'.format(variable))
        except Exception:
            raise

        slice = np.array(slice)
        return slice

    def __len__(self):
        '''
        Get number of deadlines.
        '''
        remDeadlines = len(self.__data) % self.size['blockSize']
        if remDeadlines != 0:
            # logger.debug('len(self.__data): {}'.format(len(self.__data)))
            # logger.debug('nBytesDeadline  : {}'.format(
            #     self.size['blockSize']))
            raise Exception('ADSOpy error.')
        nDeadlines = int(len(self.__data) / self.size['blockSize'])
        return nDeadlines

    def getDeadlineBlockSize(self):
        '''
        Returns dictionary with the size of each record in bytes
        and the size of the whole deadline in bytes.
        '''
        # Read record 3 of 1st deadline
        rec3 = self.getRecord3(offset=32)

        # Compute size of each block
        nRec1 = size['char8'] + size['pad']
        nRec2 = size['char8'] + size['pad']
        nRec3 = 27 * size['int'] + size['pad']
        nRec4 = (11 + rec3['kmmai']) * size['real'] + size['pad']
        nRec5 = (rec3['nreper'] * size['char8'] +
                 rec3['nvar3d'] * size['char8'] +
                 rec3['nvar3d'] * size['char8'] +
                 rec3['nvar2d'] * size['char8'] +
                 rec3['nvar2d'] * size['char8']) + size['pad']
        if rec3['nreper'] != 0:
            nRec6 = 3 * rec3['nreper'] * size['real'] + size['pad']
        else:
            nRec6 = 0
        nRec7 = (rec3['nvar3d'] * (size['pad'] + rec3['immai'] *
                 rec3['jmmai'] * rec3['kmmai'] * size['real']) +
                 rec3['nvar2d'] * (size['pad'] + rec3['immai'] *
                 rec3['jmmai'] * size['real']))

        nBytesDeadline = (nRec1 + nRec2 + nRec3 + nRec4 + nRec5 + nRec6 +
                          nRec7)
        deadlineBlock = {'rec1': nRec1,
                         'rec2': nRec2,
                         'rec3': nRec3,
                         'rec4': nRec4,
                         'rec5': nRec5,
                         'rec6': nRec6,
                         'rec7': nRec7,
                         'blockSize': nBytesDeadline}
        return deadlineBlock

    def __readADSOChunk(self, rStart, rData):
        """
        Function to read from ADSO/BIN
        Note: Fortran unformatted file add 4 bytes at the beginning and at the
        end of each chunk of written data

       INPUT:  rStart      -> initial offset
                rData       -> binary data as read from input file
        OUTPUT: rEnd        -> final offest
                rBinData    -> binary object read to be parsed with
                               struct.unpack
        """

        # logger.debug('Read chunk of bytes from ADSO/BIN file.')
        # logger.debug('Length of bin data: {}'.format(len(rData)))
        # logger.debug('Initial offset: {}'.format(rStart))
        rPad = 4
        rStart = int(rStart)
        rLength = struct.unpack('@I', rData[rStart:rStart+rPad])[0]
        rStart += rPad
        rBinData = rData[rStart:rStart+rLength]
        rEnd = rStart+rLength+rPad      # Final offest
        # logger.debug('Bytes to be read: {}'.format(rLength))
        # logger.debug('Final offset: {}'.format(rEnd))
        return [rEnd, rBinData]

    def getDeadlines(self):
        '''
        Return a list with datetime of deadlines.
        '''
        __deadlines = []
        for nd in range(len(self)):
            rec3 = self.getRecord3(nd + 1)
            dtdeadline = datetime(rec3['ianzer'],
                                  rec3['imozer'],
                                  rec3['ijozer'],
                                  rec3['ihezer'] % 24,
                                  rec3['imizer'],
                                  rec3['isezer'],
                                  tzinfo=pytz.UTC)
            if rec3['ihezer'] == 24:
                dtdeadline = dtdeadline + timedelta(days=1)
            __deadlines.append(dtdeadline)
        return __deadlines
