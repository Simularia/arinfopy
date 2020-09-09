###############################################################################
#
# arinfopy parser for ADSO/bin files.
# Copyright (C) 2019 by Giuseppe Carlino (Simularia s.r.l.)
#                       g.carlino@simularia.it
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
#
#
# Simularia S.r.l.
# Via Sant'Antonio da Padova 12
# Torino, Italy
# www.simularia.it
# info@simularia.it
#
###############################################################################

import argparse
import logging
import os
from datetime import datetime, timedelta
import pkg_resources

from ..adsobinapi import adsobin


def arinfopy():
    parser = argparse.ArgumentParser(description='arinfopy parser for '
                                     'ADSO/bin files.')
    parser.add_argument('inifile', help='File to be parsed')
    parser.add_argument('-minmax',
                        help="Show min/max values for each deadline",
                        action="store_true")
    parser.add_argument('-deadlines',
                        help="Show deadlines", action="store_true")
    parser.add_argument('-v', '--verbose',
                        help='Increse output verbosity.',
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

    # Connect to adsobin file
    mData = adsobin(args.inifile)
    # Extract information
    if args.deadlines:
        # mData.deadlines()
        deadlines(mData)
    elif args.minmax:
        # mData.minmax()
        minmax(mData)
    else:
        # mData.summary()
        summary(mData)


def deadlines(adata):
    '''
    Print out list of deadlines in ADSO/BIN file.
    '''
    print('\n--- ADSO/bin file info ---')
    for nd in range(len(adata)):
        rec3 = adata.getRecord3(nd + 1)
        dtdeadline = datetime(rec3['ianzer'],
                              rec3['imozer'],
                              rec3['ijozer'],
                              rec3['ihezer'] % 24,
                              rec3['imizer'],
                              rec3['isezer'])
        if rec3['ihezer'] == 24:
            dtdeadline = dtdeadline + timedelta(days=1)
        print('{} {:>3d} {}'.format(
            os.path.basename(adata.filename),
            nd + 1,
            dtdeadline.strftime('%d/%m/%Y h %H:%M:%S')))


def minmax(adata):
    '''
    Print out min/max values for each deadline in ADSO/BIN file.
    '''
    print('\n--- ADSO/bin file info ---')
    for nd in range(len(adata)):
        rec3 = adata.getRecord3(nd + 1)
        rec5 = adata.getRecord5(nd + 1)
        rec7 = adata.getRecord7(nd + 1)
        dtdeadline = datetime(rec3['ianzer'],
                              rec3['imozer'],
                              rec3['ijozer'],
                              rec3['ihezer'] % 24,
                              rec3['imizer'],
                              rec3['isezer'])
        if rec3['ihezer'] == 24:
            dtdeadline = dtdeadline + timedelta(days=1)
        print('-' * 70)
        print('Fields read at deadline # {:>3d}: {}'
              .format(nd + 1, dtdeadline.strftime('%d/%m/%Y %H:%M:%S')))
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


def summary(adata):
    '''
    Print out summary information about ADSO/BIN file.
    '''
    # Read rec3 of first deadline
    rec3 = adata.getRecord3(1)
    firstdl = datetime(rec3['ianzer'],
                       rec3['imozer'],
                       rec3['ijozer'],
                       rec3['ihezer'] % 24,
                       rec3['imizer'],
                       rec3['isezer'])
    if rec3['ihezei'] == 24:
        firstdl = firstdl + timedelta(days=1)

    # Read rec3, rec4, rec5 of last deadline
    rec3 = adata.getRecord3(len(adata))
    rec4 = adata.getRecord4(len(adata))
    rec5 = adata.getRecord5(len(adata))
    lastdl = datetime(rec3['ianzer'],
                      rec3['imozer'],
                      rec3['ijozer'],
                      rec3['ihezer'] % 24,
                      rec3['imizer'],
                      rec3['isezer'])
    if rec3['ihezer'] == 24:
        lastdl = lastdl + timedelta(days=1)
    ndeadlines = len(adata)
    if ndeadlines == 1:
        dtsecs = 0
    else:
        dtsecs = (lastdl - firstdl).total_seconds() / (ndeadlines - 1)

    version = pkg_resources.require("arinfopy")[0].version
    print('\n')
    print('--- ADSO/bin file info (arinfopy v{}) ---'.format(version))
    print('Input archive               : {}'.format(
        os.path.basename(adata.filename)))
    print('Version                     : {}'.format(adata.getVersion()))
    print('File generator              : {}'.format(adata.getRecord2(1)))
    print('First deadline              : {}'.format(firstdl.isoformat()))
    print('Last deadline               : {}'.format(lastdl.isoformat()))
    print('Deadline period (s)         : {}'.format(dtsecs))
    print('# of deadlines              : {}'.format(ndeadlines))
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
                                              len(rec4['sgrid']))
          .format(*rec4['sgrid']))
    print('nvar2d, nvar3d              : {:d}   {:d}'.format(
        rec3['nvar2d'], rec3['nvar3d']))
    if rec3['nvar2d'] > 0:
        print('2D variabels                : ' + ('{:<s} ' *
                                                  rec3['nvar2d'])
              .format(*rec5['nomvar2d']))
    if rec3['nvar3d'] > 0:
        print('3D variables                : ' + ('{:<s} ' *
                                                  rec3['nvar3d'])
              .format(*rec5['nomvar3d']))
    print('\n')
