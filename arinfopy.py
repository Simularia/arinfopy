#!/usr/bin/env python
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

# Size of data type and data padding
size = {'int': 4,
        'real': 4,
        'char8': 8,
        'pad': (4 + 4)}


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
                    self.size['rec3'] + self.size['rec4'] + self.size['rec5']),
                'rec7': (self.size['rec1'] + self.size['rec2'] +
                    self.size['rec3'] + self.size['rec4'] + self.size['rec5'] +
                    self.size['rec6'])
                }


    def getRecord1(self, deadline):
        '''
        Returns file header

        -----DECLARATION OF THE "BINAIRA" TYPE
        Record 1 -> character*8
        '''
        start = (deadline - 1) * self.size['blockSize'] + self.offset['rec1']
        start, binData = self.__readADSOChunk(start, self.__data)
        _ident1 = struct.unpack('@8s',binData)[0].decode("utf-8")
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


    def getRecord2(self, deadline):
        '''
        Returns file generator

        Record 2 -> character*8 code that generated the file
        '''
        # logger.debug('--- Read Record 2 ---')
        start = (deadline - 1) * self.size['blockSize'] + self.offset['rec2']
        start, binData = self.__readADSOChunk(start, self.__data)
        _ident2 = struct.unpack('@8s',binData)[0].decode("utf-8")
        # logger.debug('ident2 : {}'.format(_ident2))
        return _ident2


    def getRecord3(self, deadline = 1, offset = None):
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
        if offset != None:
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
                'nreper': __num[15], 'nvar3d': __num[16], 'nvar2d': __num[17],
                'nevt': __num[18], 'itmax': __num[19], 'nevtpr': __num[20],
                'itmopro': __num[21], 'IINDEX': __num[22], 'IKSURF': __num[23]}
        if __rec3['ianzer'] < 1000:
            __rec3['ianzer'] += 2000
        if __rec3['ianzei'] < 1000:
            __rec3['ianzei'] += 2000

        return __rec3


    def getRecord4(self, deadline):
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


    def getRecord5(self, deadline):
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
        nStrings = rec3['nreper'] + 2 * rec3['nvar3d'] + 2 * rec3['nvar2d']
        typedef = '@' + str(nStrings * size['char8']) + 's'
        # logger.debug('typedef: {}'.format(typedef))

        sStrings = struct.unpack(typedef, binData)

        creper = ''
        nomvar3D = ''
        univar3d = ''
        nomvar2d = ''
        univar2d = ''

        creper = [struct.unpack('@8s', binData[i:rec3['nreper']*8])[0] for i in
                range(rec3['nreper'])]
        offset = (rec3['nreper']) * 8
        nomvar3d = [struct.unpack('@8s', binData[offset+i*8:offset +
            (i+1)*8])[0].decode('utf-8') for i in range(rec3['nvar3d'])]
        offset = (rec3['nreper'] + rec3['nvar3d']) * 8
        univar3d = [struct.unpack('@8s', binData[offset+i*8:offset +
            (i+1)*8])[0].decode('utf-8') for i in range(rec3['nvar3d'])]
        offset = (rec3['nreper'] + 2*rec3['nvar3d']) * 8
        nomvar2d = [struct.unpack('@8s', binData[offset+i*8:offset +
            (i+1)*8])[0].decode('utf-8') for i in range(rec3['nvar2d'])]
        offset = (rec3['nreper'] + 2*rec3['nvar3d'] + rec3['nvar2d']) * 8
        univar2d = [struct.unpack('@8s', binData[offset+i*8:offset
            +(i+1)*8])[0].decode('utf-8') for i in range(rec3['nvar2d'])]

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


    def getRecord7(self, deadline):
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
            rec7['%s' % name] = list(struct.unpack(typedef, binData))

        for i, name in enumerate(rec5['nomvar2d']):
            # logger.debug('Read 2D variable # {}'.format(i))
            start, binData = self.__readADSOChunk(start, self.__data)
            nReals = rec3['immai'] * rec3['jmmai']
            typedef = '@' + str(nReals) + 'f'
            rec7['%s' % name] = list(struct.unpack(typedef, binData))

        return rec7


    def __len__(self):
        '''
        Get number of deadlines.
        '''
        remDeadlines = len(self.__data) % self.size['blockSize']
        if remDeadlines != 0:
            # logger.debug('len(self.__data): {}'.format(len(self.__data)))
            # logger.debug('nBytesDeadline  : {}'.format(
                # self.size['blockSize']))
            raise Exception('ADSOpy error.')
        nDeadlines = int(len(self.__data) / self.size['blockSize'])
        return nDeadlines


    def getDeadlineBlockSize(self):
        '''
        Returns dictionary with the size of each record in bytes
        and the size of the whole deadline in bytes.
        '''
        # Read record 3 of 1st deadline
        rec3 = self.getRecord3(offset = 32)

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
        nRec7 = (rec3['nvar3d'] * (size['pad'] + rec3['immai'] * rec3['jmmai']
            * rec3['kmmai'] * size['real']) +
            rec3['nvar2d'] * (size['pad'] + rec3['immai'] * rec3['jmmai'] *
                size['real']))

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
        end of each chunk of data written

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
        rLength = struct.unpack('@I', rData[rStart:rStart+rPad])[0]
        rStart += rPad
        rBinData = rData[rStart:rStart+rLength]
        rEnd = rStart+rLength+rPad      # Final offest
        # logger.debug('Bytes to be read: {}'.format(rLength))
        # logger.debug('Final offset: {}'.format(rEnd))
        return [rEnd, rBinData]


    def deadlines(self):
        '''
        Print out list of deadlines in ADSO/BIN file.
        '''
        print('\n--- ADSO/bin file info ---')
        for nd in range(len(self)):
            rec3 = self.getRecord3(nd + 1)
            dtdeadline = datetime(rec3['ianzer'],
                    rec3['imozer'],
                    rec3['ijozer'],
                    rec3['ihezer'] % 24,
                    rec3['imizer'],
                    rec3['isezer'])
            if rec3['ihezer'] == 24:
                dtdeadline = dtdeadline + timedelta(days = 1)
            print('{} {:>3d} {}'.format(
                os.path.basename(self.filename),
                nd + 1,
                dtdeadline.strftime('%d/%m/%Y h %H:%M:%S')))


    def minmax(self):
        '''
        Print out min/max values for each deadline in ADSO/BIN file.
        '''
        print('\n--- ADSO/bin file info ---')
        for nd in range(len(self)):
            rec3 = self.getRecord3(nd + 1)
            rec5 = self.getRecord5(nd + 1)
            rec7 = self.getRecord7(nd + 1)
            dtdeadline = datetime(rec3['ianzer'],
                    rec3['imozer'],
                    rec3['ijozer'],
                    rec3['ihezer'] % 24,
                    rec3['imizer'],
                    rec3['isezer'])
            if rec3['ihezer'] == 24:
                dtdeadline = dtdeadline + timedelta(days = 1)
            print('-' * 70)
            print('Fields read at deadline # {:>3d}: {}'.format(nd + 1,
                dtdeadline.strftime('%d/%m/%Y %H:%M:%S')))
            print('-' * 70)
            for n3d, name in enumerate(rec5['nomvar3d']):
                print(('3D # {:>3d}: {:>10s}  min = {:12.4f} max = {:12.4f} ' +
                        ' [{:s}])').
                        format(n3d + 1,
                            name.strip(),
                            min(rec7[name]),
                            max(rec7[name]),
                            rec5['univar3d'][n3d].strip()))
            for n2d, name in enumerate(rec5['nomvar2d']):
                print(('2D # {:>3d}: {:>10s}  min = {:12.4f} max = {:12.4f} ' +
                        ' [{:s}]').
                        format(n2d + 1,
                            name.strip(),
                            min(rec7[name]),
                            max(rec7[name]),
                            rec5['univar2d'][n2d].strip()))


    def summary(self):
        '''
        Print out summary information about ADSO/BIN file.
        '''
        # Read rec3, rec4, rec5 of last deadline
        rec3 = self.getRecord3(len(self))
        rec4 = self.getRecord4(len(self))
        rec5 = self.getRecord5(len(self))

        firstdl = datetime(rec3['ianzei'],
                rec3['imozei'],
                rec3['ijozei'],
                rec3['ihezei'] % 24,
                rec3['imizei'],
                rec3['isezei'])
        if rec3['ihezei'] == 24:
            firstdl = firstdl + timedelta(days = 1)
        lastdl = datetime(rec3['ianzer'],
                rec3['imozer'],
                rec3['ijozer'],
                rec3['ihezer'] % 24,
                rec3['imizer'],
                rec3['isezer'])
        if rec3['ihezer'] == 24:
            lastdl = lastdl + timedelta(days = 1)
        dtsecs = (lastdl - firstdl).total_seconds() / len(self)

        print('\n--- ADSO/bin file info ---')
        print('Input archive               : {}'.format(
            os.path.basename(self.filename)))
        print('Version                     : {}'.format(self.getVersion()))
        print('File generator              : {}'.format(self.getRecord2(1)))
        print('First deadline              : {}'.format(firstdl.isoformat()))
        print('Last deadline               : {}'.format(lastdl.isoformat()))
        print('Deadline frequency (s)      : {}'.format(dtsecs))
        print('# of deadlines              : {}'.format(len(self)))
        print('# of gridpoints (x, y, z)   : {}   {}   {}'.format(
            rec3['immai'], rec3['jmmai'], rec3['kmmai']))
        print('Grid cell sizes (x, y)      : {:.3f} {:.3f}'.format(
            rec4['dxmai'], rec4['dymai']))
        print('Coord. of SW corner (metric): {:.3f}   {:>.3f}'.format(
            rec4['xlso'], rec4['ylso']))
        print('Coord. of SW corner (geo)   : {:.3f}   {:.3f}'.format(
            rec4['xlatso'], rec4['ylatso']))
        print('Top of the domain           : {:.3f}'.format(rec4['ztop']))
        print('Levels                      : ' + ('{:.2f} ' *
            len(rec4['sgrid'])).format(*rec4['sgrid']))
        print('nvar2d, nvar3d              : {:d}   {:d}'.format(
            rec3['nvar2d'], rec3['nvar3d']))
        if rec3['nvar2d'] > 0 :
            print('2D variabels                : ' + ('{:<s} ' *
                rec3['nvar2d']).format(*rec5['nomvar2d']))
        if rec3['nvar3d'] > 0 :
            print('3D variables                : ' + ('{:<s} ' *
                rec3['nvar3d']).format(*rec5['nomvar3d']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description =
            'arinfopy parser for ADSO/bin files.')
    parser.add_argument('inifile', help = 'File to be parsed')
    parser.add_argument('-minmax',
            help = "Show min/max values for each deadline",
            action = "store_true")
    parser.add_argument('-deadlines',
            help = "Show deadlines",
            action = "store_true")
    parser.add_argument('-v', '--verbose',
            help = 'Increse output verbosity.',
            action="store_true")
    args = parser.parse_args()

    # Create Logger
    logger = logging.getLogger(__name__)
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
   # flogname = 'elisestat_' + datetime.now().isoformat() + '.log'
   # flog = logging.FileHandler(flogname)
   # flog.setLevel(logging.INFO)
   # flog.setFormatter(formatter)
   # logger.addHandler(flog)

    mData = adsobin(args.inifile)
    if args.deadlines:
        mData.deadlines()
    elif args.minmax:
        mData.minmax()
    else:
        mData.summary()
