#!/usr/bin/env python2
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
#
#   2013-04-05 Giuseppe Carlino Simularia s.r.l
#       
#   Requires python 2.6.x
#
############################################################################### 
import sys, struct, os
from datetime import datetime, timedelta


DEBUG = True
if DEBUG  :
    os.system('python --version')
    os.system('which python')


# Function to read from ADSO/BIN 
#   fortran unformatted file add 4 bytes at the beginning and at the end
#       of each chunk of data written
# 
#           to be moved to a separete file
# 
#   INPUT:  rStart      -> initial offset
#           rData       -> binary data as read from input file
# 
#   OUTPUT: rEnd        -> final offest
#           rBinData    -> binary object read to be parsed with struct.unpack
# 
def readADSOChunk(rStart, rData):
    rDEBUG = False
    if rDEBUG :
        print
        print'========================================================='
        print'Read chunk of bytes from ADSO/BIN file.'
        print'Length of bin data: ', len(rData)
        print'Initial offset: ', rStart
    rPad = 4
    rLength = struct.unpack('@I', rData[rStart:rStart+rPad])[0]
    rStart += rPad
    rBinData = rData[rStart:rStart+rLength]
    rEnd = rStart+rLength+rPad      # Final offest
    if rDEBUG :
        print'Bytes to be read: ', rLength
        print"Final offset: ", rEnd
        print'========================================================='
        print
    return rEnd, rBinData








print
print 'Input archive               : ', sys.argv[1]
print

#
# Open, read and close ADSO/bin file
#
with open(str(sys.argv[1]), "rb") as f :
    data = f.read()
f.close()


necdis = 0  # Number of deadlines
start = 0   # offset for the binary files
dtsecs = 0  # deadline frequency

# Loop on binary data
while start < len(data) :

    # Count number of deadlines
    necdis = necdis+1

    if DEBUG :
        print
        print '-------------------'
        print 'Deadline # %s ' % necdis
        print '-------------------'
            
    # 
    # -----DECLARATION OF THE "BINAIRA" TYPE
    # 
    # 
    # Record 1 & 2-> 16 characters
    # 
    #                   character*8
    #                   character*8 code that generated the file
    if DEBUG :
        print
        print '--- Read Record 1 ---'

    start, binData = readADSOChunk(start,data)
    ident1 = struct.unpack('@8s',binData)[0].decode("utf-8")

    start, binData = readADSOChunk(start,data)
    ident2 = struct.unpack('@8s',binData)[0].decode("utf-8")

    if DEBUG :
         print 'ident1 :', ident1
         print 'ident2 :', ident2

    
    
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
    if DEBUG :
        print
        print '--- Read Record 3 ---'
    
    start, binData = readADSOChunk(start, data)
    num = struct.unpack('@27i',binData)
    ijozer = num[0]
    imozer = num[1]
    ianzer = num[2]
    ihezer = num[3]
    imizer = num[4]
    isezer = num[5]
    ijozei = num[6]
    imozei = num[7]
    ianzei = num[8]
    ihezei = num[9]
    imizei = num[10]
    isezei = num[11]
    immai = num[12]
    jmmai = num[13]
    kmmai = num[14]
    nreper = num[15]
    nvar3d = num[16]
    nvar2d = num[17]
    nevt = num[18]
    itmax = num[19]
    nevtpr = num[20]
    itmopro = num[21]
    IINDEX = num[22]
    IKSURF = num[23]

    # Read current deadline
    currentdl = datetime(2000+ianzer, imozer, ijozer, ihezer % 24, imizer, isezer)
    
    # Correct if hour = 24 since in datetime 0 <= hour < 24
    if ihezer == 24:
        currentdl = currentdl + timedelta(1)
    
    # Set first deadline
    if necdis == 1 :
        firstdl = currentdl
    
    # Compute deadline frequency in seconds
    if necdis == 2:
        dtsecs = (currentdl - firstdl).seconds
    
    if DEBUG :
        print 'firstdl   :', firstdl
        print 'currentdl :', currentdl
        print 'nvar3d    :', nvar3d
        print 'nvar2d    :', nvar2d
        print 'kmmai     :', kmmai

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
    if DEBUG :
        print
        print'--- Read Record 4'

    start, binData = readADSOChunk(start, data)

    nReals = 11+kmmai

    typedef = '@' + str(nReals) + 'f'
    if DEBUG :
        print 'typedef: ', typedef

    fnum = struct.unpack(typedef, binData)

    sgrid=fnum[0:kmmai]
    i=kmmai
    dxmai = fnum[i]
    dymai = fnum[i+1]
    xlso = fnum[i+2] 
    ylso = fnum[i+3]
    xlatso = fnum[i+4]
    ylatso = fnum[i+5]
    ztop = fnum[i+10]

    if DEBUG:
        print 'ztop :', ztop

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
    if DEBUG :
        print
        print '--- Read Record 5'

    start, binData = readADSOChunk(start, data)

    nStrings = nreper + 2*nvar3d + 2*nvar2d
    typedef = '@' + str(nStrings*8) + 's'
    if DEBUG :
        print 'typedef: ', typedef

    sStrings = struct.unpack(typedef, binData)
    # print(sStrings[0])

    creper = ''
    nomvar3D = ''
    univar3d = ''
    nomvar2d = ''
    univar2d = ''

    creper = [struct.unpack('@8s', binData[i:nreper*8])[0] for i in range(nreper)]

    offset = (nreper) * 8
    nomvar3d = [struct.unpack('@8s', binData[offset+i*8:offset + (i+1)*8])[0] for i in range(nvar3d)]

    offset = (nreper + nvar3d) * 8
    univar3d = [struct.unpack('@8s', binData[offset+i*8:offset + (i+1)*8])[0] for i in range(nvar3d)]

    offset = (nreper + 2*nvar3d) * 8
    nomvar2d = [struct.unpack('@8s', binData[offset+i*8:offset + (i+1)*8])[0] for i in range(nvar2d)]

    offset = (nreper + 2*nvar3d + nvar2d) * 8
    univar2d = [struct.unpack('@8s', binData[offset+i*8:offset +(i+1)*8])[0] for i in range(nvar2d)]

    # 
    # -----RECORD NUMBER 6 : KEY POINTS COORDINATES--------------
    # 
    #   3*NREPER REALS
    # 

    # 
    # -----RECORD NUMBER 7 : 3D FIELDS----------------------------
    # 
    # #
    # #       Record 5 to 5+NVAR3D-1
    # #               NVAR3D 3D arrays with variables on the 3D grid
    # #               orderd as indicated by NOMVAR3D names vector
    # #       
    if DEBUG :
        print
        print '--- Read 3D fields'
    
    for i in range(nvar3d)  :
        if DEBUG:
            print '--- Read 3D variable #', i
        # if DEBUG :
        #     print
        #     print '--- Read 3D variable # ', i
        start, binData = readADSOChunk(start, data)


    for i in range(nvar2d)  :
        if DEBUG :
        #     print
             print '--- Read 2D variable #', i
        start, binData = readADSOChunk(start, data)

# # Check if we are at the end of file
#     if start == len(data) :
#         break
    


#  Info output
print
print '--- ADSO/bin file info ---'
print 'File generator              : ', str(ident2)
print 'first deadline              : ', firstdl
# print 'first deadline              : ', ijozer, imozer, ianzer, ihezer, imizer, isezer 
print 'last deadline               : ', currentdl
# print 'Deadline frequency (s)      : ', (currentdl - firstdl).total_seconds() / necdis
print 'Deadline frequency (s)      : ', dtsecs
print '# of deadlines              : ', necdis
print '# of gridpoints (x, y, z)   : ', immai, jmmai, kmmai
print 'grid cell sizes (x, y)      :  %.3f    %.3f' % (dxmai, dymai)
print 'coord. of SW corner (metric):  %.3f    %.3f' % (xlso, ylso)
print 'coord. of SW corner (geo)   :  %.3f    %.3f' % (xlatso, ylatso)
print 'top of the domain           :  %.3f' % ztop

sys.stdout.write('levels                      :  ')
for val in sgrid :
    sys.stdout.write('%.1f  ' % val)
sys.stdout.write('\n')

print 'nvar2d, nvar3d              :  %i  %i' % (nvar2d, nvar3d)


if nvar2d > 0 :
    print '2D variabels                :  %s' % '  '.join(map(str,nomvar2d))
    # print '2D variables udm            :  %s' % ' '.join(map(str,univar2d))
if nvar3d > 0 :
    print '3D variables                :  %s' % '  '.join(map(str,nomvar3d))
    # print '3D variables udm            :  %s' % ' '.join(map(str,univar3d))

print
