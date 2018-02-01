from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


__all__ = ['main_app', 'draw_cgps_blueprint']

from . import version
from caom2 import CalibrationLevel
from caom2utils import ObsBlueprint, FitsParser

import argparse
import logging
import math
import re
import sys


APP_NAME = 'cgps2caom2'

# Regular expressions for file_ids.  Note that these are all in lower
# case as are CGPS file_ids, not mixed case as are CGPS file names.  The
# corresponding target, band and content values are also lower case and
# may not match values derived from the FITS headers (usually upper case)
# or from the file names directly.
NAME_REGEX = {'DRAO-ST': r'cgps_(?P<target>[^_]+)_'
                         r'(?P<band>1420_mhz_[iqu]|408_mhz|hi_line)_'
                         r'(?P<content>image|beams|rescb|wght)',
              'FCRAO': r'cgps_(?P<target>[^_]+)_'
                       r'(?P<band>co_line)_'
                       r'(?P<content>image|flags)',
              'IRAS': r'cgps_(?P<target>[^_]+)_'
                      r'(?P<band>012_um|025_um|060_um|100_um)_'
                      r'(?P<content>image|beams|cfv|phn|fwhm)',
              'VLA': r'(?P<target>.{7})'
                     r'(?P<content>\.tb|_cont\.tb|_contincluded\.tb)'}

# Generate productID and bandpassName from content in file_id
BAND = {'1420_mhz_i': {'productID': '1420MHz',
                       'bandpassName': '1420 MHz'},
        '1420_mhz_q': {'productID': '1420MHz-QU',
                       'bandpassName': '1420 MHz'},
        '1420_mhz_u': {'productID': '1420MHz-QU',
                       'bandpassName': '1420 MHz'},
        '408_mhz': {'productID': '408MHz',
                    'bandpassName': '408 MHz'},
        'hi_line': {'productID': 'HI-line',
                    'bandpassName': '21 cm'},
        'co_line': {'productID': 'CO-line',
                    'bandpassName': 'CO (1-0)'},
        '012_um': {'productID': '12um',
                   'bandpassName': 'IRAS-12um'},
        '025_um': {'productID': '25um',
                   'bandpassName': 'IRAS-25um'},
        '060_um': {'productID': '60um',
                   'bandpassName': 'IRAS-60um'},
        '100_um': {'productID': '100um',
                   'bandpassName': 'IRAS-100um'},
        '.tb': {'productID': '21cm-line',
                'bandpassName': '21 cm'},
        '_cont.tb': {'productID': '21cm-cont',
                     'bandpassName': '1420 MHz'},
        '_contincluded.tb': {'productID': '21cm-lineWithCont',
                             'bandpassName': '21 cm'}}

# provenance reference field by collection
REFERENCE = {'CGPS': 'http://dx.doi.org/10.1086/375301',
             'VGPS': 'http://dx.doi.org/10.1086/505940'}

# IRAS band parameters, consistent with IRIS collection
# This is keyed by the productID rather than band/content
ENERGY = {'1420MHz': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                      'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                      'Chunk.energy.axis.axis.cunit': 'Hz',  # CUNIT3
                      'Chunk.energy.axis.function.delta': '30.0E6',  # CDELT3
                      'Chunk.energy.specsys': 'TOPOCENT'},  # SPECSYS
          '1420MHz-QU': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                         'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                         'Chunk.energy.axis.axis.cunit': 'Hz',  # CUNIT3
                         'Chunk.energy.axis.function.delta': '30.0E6',  # CDELT3
                         'Chunk.energy.specsys': 'TOPOCENT'},  # SPECSYS
          '408MHz': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                     'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                     'Chunk.energy.axis.axis.cunit': 'Hz',  # CUNIT3
                     'Chunk.energy.axis.function.delta': '4.0E6',  # CDELT3
                     'Chunk.energy.specsys': 'TOPOCENT'},  # SPECSYS
          'HI-line': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                      'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                      'Chunk.energy.axis.axis.ctype': 'VRAD',  # CTYPE3
                      'Chunk.energy.axis.axis.cunit': 'm/s',  # CUNIT3
                      'Chunk.energy.specsys': 'LSRK'},  # SPECSYS
          'CO-line': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                      'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                      'Chunk.energy.axis.axis.ctype': 'VRAD',  # CTYPE3
                      'Chunk.energy.axis.axis.cunit': 'm/s',  # CUNIT3
                      'Chunk.energy.specsys': 'LSRK'},  # SPECSYS
          '12um': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                   'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                   'Chunk.energy.axis.axis.ctype': 'WAVE',  # CTYPE3
                   'Chunk.energy.axis.axis.cunit': 'm',  # CUNIT3
                   'Chunk.energy.specsys': 'TOPOCENT',  # SPECSYS
                   'Chunk.energy.axis.function.delta': '7.0E-6'},  # CDELT3
          '25um': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                   'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                   'Chunk.energy.axis.axis.ctype': 'WAVE',  # CTYPE3
                   'Chunk.energy.axis.axis.cunit': 'm',  # CUNIT3
                   'Chunk.energy.specsys': 'TOPOCENT',  # SPECSYS
                   'Chunk.energy.axis.function.delta': '11.15e-6'},  # CDELT3
          '60um': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                   'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                   'Chunk.energy.axis.axis.ctype': 'WAVE',  # CTYPE3
                   'Chunk.energy.axis.axis.cunit': 'm',  # CUNIT3
                   'Chunk.energy.specsys': 'TOPOCENT',  # SPECSYS
                   'Chunk.energy.axis.function.delta': '32.5e-6'},  # CDELT3
          '100um': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                    'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                    'Chunk.energy.axis.axis.ctype': 'WAVE',  # CTYPE3
                    'Chunk.energy.axis.axis.cunit': 'm',  # CUNIT3
                    'Chunk.energy.specsys': 'TOPOCENT',  # SPECSYS
                    'Chunk.energy.axis.function.delta': '31.5e-6'},  # CDELT3
          '21cm-line': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                        'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                        'Chunk.energy.axis.axis.ctype': 'VRAD',  # CTYPE3
                        'Chunk.energy.axis.axis.cunit': 'm/s',  # CUNIT3
                        'Chunk.energy.specsys': 'LSRK'},  # SPECSYS
          '21cm-cont': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                        'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                        'Chunk.energy.axis.axis.ctype': 'VRAD',  # CTYPE3
                        'Chunk.energy.axis.axis.cunit': 'm/s',  # CUNIT3
                        'Chunk.energy.specsys': 'TOPOCENT'},  # SPECSYS
          '21cm-lineWithCont': {'Chunk.position.axis.axis1.cunit': 'deg',  # CUNIT1
                                'Chunk.position.axis.axis2.cunit': 'deg',  # CUNIT2
                                'Chunk.energy.axis.axis.ctype': 'VRAD',  # CTYPE3
                                'Chunk.energy.axis.axis.cunit': 'm/s',  # CUNIT3
                                'Chunk.energy.specsys': 'LSRK'}  # SPECSYS
          }

POLARIZATION = {
    'Chunk.polarization.axis.axis.ctype': 'STOKES',  # CTYPE4
    'Chunk.polarization.axis.function.naxis': '1',  # NAXIS4
    'Chunk.polarization.axis.function.refCoord.pix': '1',  # CRPIX4
    'Chunk.polarization.axis.function.refCoord.val': '1',  # CRVAL4
    'Chunk.polarization.axis.function.delta': '1'}  # CDELT4


def _geolocation(longitude, latitude, elevation_meters):
    """
    Returns a 3-tuple (X,Y,Z) giving the cartesian coordinates relative to the
    center of the Earth in meters.

    longitude : geodetic longitude in decimal degrees
    latitude  : geodetic latitude in decimal degrees
    elevation : above sealevel in meters

    The computed position is only accurate to a few kilometers, which is
    acceptable for most purposes.  Problems with high-accuracy requirements
    should find other routines.

    The equatorial and polar radii are taken from WGRS 80/84
        http://en.wikipedia.org/wiki/World_Geodetic_System
    The formulae for geodetic longitude and latitude are taken from
        http://en.wikipedia.org/wiki/Reference_ellipsoid
    """

    a = 6378137.0
    b = 6356752.3

    cos2oe = (b / a) ** 2
    sin2oe = (a + b) * (a - b) / a ** 2

    theta = math.radians(longitude)
    phi = math.radians(latitude)

    n = a / math.sqrt(1.0 - sin2oe * math.sin(phi) ** 2)
    h = elevation_meters

    return ((n + h) * math.cos(theta) * math.cos(phi),
            (n + h) * math.sin(theta) * math.cos(phi),
            (cos2oe * n + h) * math.sin(phi))


# Geocentric locations of observatories
LOCATIONS = {'IRAS': ('', '', ''),
             'DRAO-ST': _geolocation(-119.620000,
                                     48.320000,
                                     545.0),
             'FCRAO': _geolocation(-72.345000,
                                   42.391667,
                                   314.0),
             'VLA': _geolocation(-107.618333,
                                 34.078333,
                                 2124.0)}


def _cgps_make_file_id(basename):
    """
    CGPS-specific routine to convert a file basename (without the
    directory path) to the corressponding file_id used in AD.

    Arguments:
    basename : a file name without the directory path
    This is a static method taking exactly one argument.
    """
    lower_basename = basename.lower()
    base, ext = os.path.splitext(lower_basename)
    if re.match(r'.*?fwhm', base):
        file_id = lower_basename
    else:
        file_id = base
    return file_id


def _set_fits(bp, lookup):
    for key, value in lookup.items():
        bp.set(key, value)


def _metadata_from(bp, headers, uri):
    """
    Archive-specific method to fill and return the plane and
    URI-specific dictionaries from the file header.

    :param: bp blueprint
    :param: uri the ad (? TBC) URI for the header
    """

    file_id = uri.split('/')[1]  # TODO get from header

    # Extract the telescope name, target, productID, bandpassName and
    # contents of a file from the file_id using the regex's for each
    # telescope

    for telescope in NAME_REGEX:
        m = re.match(NAME_REGEX[telescope], file_id.lower())
        if m:
            md = m.groupdict()
            target = md['target']
            content = md['content']
            if 'band' in md:
                product_id = BAND[md['band']]['productID']
                bandpass_name = BAND[md['band']]['bandpassName']
            else:
                product_id = BAND[content]['productID']
                bandpass_name = BAND[content]['bandpassName']
            break
    else:
        telescope = None
        target = None
        product_id = None
        bandpass_name = None
        content = None

    print('telescope {} target {} product id {} bandpass name {} content {}'.
          format(telescope, target, product_id, bandpass_name, content))
    bp.set('Plane.productID', product_id)

    # Deal with FITS files first
    if isinstance(headers, list) and  len(headers) > 0 and 'INSTRUME' in headers[0]:
        hdu0 = headers[0]
        if telescope:
            # Structural metadata
            if telescope == 'VLA':
                collection = 'VGPS'
            else:
                collection = 'CGPS'  # TODO how to set collection

            # For CGPS, it is better to take the target name from the
            # ADC_AREA header.  For VGPS, it is better to retain the
            # target name extracted from the file name.
            if collection == 'CGPS':
                target = hdu0.get('ADC_AREA')

            bp.set('Observation.observationID',
                   '{}_{}'.format(target, telescope))

            # Fill the observation-level metadata
            bp.set('Observation.target.name', target)
            geo_x, geo_y, geo_z = LOCATIONS[telescope]
            bp.set('Observation.telescope.name', telescope)
            bp.set('Observation.telescope.geoLocationX', geo_x)
            bp.set('Observation.telescope.geoLocationY', geo_y)
            bp.set('Observation.telescope.geoLocationZ', geo_z)

            bp.set('Observation.instrument.name', telescope)

            # release dates
            if collection == 'CGPS':
                release = hdu0.get('PUB_RELD')
            else:
                release = hdu0.get('DATE-OBS')
            bp.set('Observation.metaRelease', release)
            bp.set('Plane.metaRelease', release)
            bp.set('Plane.dataRelease', release)

            # Plane-level metadata
            bp.set('Plane.calibrationLevel', CalibrationLevel.CALIBRATED)

            if telescope in ('DRAO-ST', 'FCRAO'):
                provenance_name = '{} {}'.format(hdu0.get('ADC_ARCH'),
                                                 hdu0.get('ADC_TYPE'))
            elif telescope == 'IRAS':
                provenance_name = 'CGPS MOSAIC HIRES'
            else:
                assert telescope == 'VLA'
                provenance_name = hdu0.get('ORIGIN')
            bp.set('Plane.provenance.name', provenance_name)

            if collection == 'CGPS':
                producer = hdu0.get('OBSERVER')
            else:
                producer = '"VLA Galactic Plane Survey (VGPS) Consortium"'
            bp.set('Plane.provenance.producer', producer)
            bp.set('Plane.provenance.reference', REFERENCE[collection])

            # bp.set('Artifact.uri', uri)

            if collection == 'VGPS' or content == 'image':
                product_type = 'science'

                # WCS is only significant for science artifacts

                # Artifact-level metadata (plus a few plane-level metadata
                # that can only be determined from the science artifacts)
                bp.configure_position_axes((1,2))
                bp.configure_energy_axis(3)
                _set_fits(bp, ENERGY[product_id])
                if collection == 'CGPS':
                    if content == 'image':
                        bp.configure_polarization_axis(4)
                        _set_fits(bp, POLARIZATION)
                        if product_id == '1420MHz-QU':
                            crval4 = '%d' % (int(math.floor(hdu0.get('CRVAL4'))))
                            _set_fits(bp, {'CRVAL4': crval4})
                elif collection == 'VGPS':
                    bp.configure_polarization_axis(4)
                    _set_fits(bp, POLARIZATION)

                if telescope in ('DRAO-ST', 'FCRAO'):
                    bp.set('Chunk.energy.restfrq', hdu0.get('OBSFREQ'))
                elif telescope == 'VLA':
                    bp.set('Chunk.energy.restfrq', hdu0.get('FREQ0'))
                bp.set('Chunk.energy.bandpassName', bandpass_name)

                # Determine the data product type from the axis count
                # Beware that content=image parsed from the file_id does
                # NOT mean the file contains an image!
                # Also, only the science artifact determines the
                #  data_product_type.
                data_product_type = ''
                if 'NAXIS' in hdu0:
                    naxis = hdu0.get('NAXIS')
                    if (naxis == 2 or
                            (naxis > 2 and hdu0.get('NAXIS3') == 1)):
                        data_product_type = 'image'
                    elif naxis > 2:
                        data_product_type = 'cube'
                else:
                    data_product_type = 'catalog'
                bp.set('Plane.dataProductType', data_product_type)

            else:
                product_type = 'auxiliary'
            bp.set('Artifact.productType', product_type)

    elif content == 'fwhm':
        # fwhm files are text files without FITS headers,
        # but the required metadata can be extracted from the corresponding
        # image file.
        bp.set('Plane.productID', 'catalog')
        bp.set('Artifact.productType', 'science')

        # TODO this is all metadata that's been set for an image file that's
        # part of the same observation - how to go about ingesting fwhm
        # files in the correct order?

        # image_file_id = _cgps_make_file_id(
        #     re.sub(r'(.*?)_fwhm', r'\1_image', file_id))
        # image_uri = 'ad:CGPS/{}'.format(image_file_id)
        # coll, obs, prod = self.findURI(image_uri)
        # if not coll:
        #     logging.error(
        #         'For {} the image file {} has not already been ingested'.format(
        #             file_id, image_file_id))
        #
        # # TODO how to set collection - self.collection = coll
        # bp.set('Observation.observationID', obs)
        #
        # for item in ['obs.metaRelease',
        #              'telescope.name',
        #              'telescope.geoLocationX',
        #              'telescope.geoLocationY',
        #              'telescope.geoLocationZ',
        #              'target.name',
        #              'plane.metaRelease',
        #              'plane.dataRelease',
        #              'plane.calibrationLevel',
        #              'provenance.name',
        #              'provenance.producer',
        #              'provenance.reference']:
        #     value = self.get_plane_value(coll, obs, prod, item)
        #     if isinstance(value, str):
        #         self.add_to_plane_dict(item, value)
        #     else:
        #         self.log.console('item ' + item + ' not found for ' +
        #                          imageURI,
        #                          logging.ERROR)
        #
        # fileURI = self.fitsfileURI(self.archive, file_id)
        # inputURI = self.planeURI(coll, obs, prod)



def draw_cgps_blueprint(uri, headers):
    logging.debug('Begin blueprint customization for CGPS {}.'.format(uri))
    blueprint = ObsBlueprint()

    _metadata_from(blueprint, headers, uri)

    logging.debug('Blueprint customatization complete for CGPS {}.'.format(uri))
    return blueprint


def main_app():
    parser = argparse.ArgumentParser()
    parser.description = (
        'Augment CGPS observation with information in one or more fits files.')

    if version.version is not None:
        parser.add_argument('-V', '--version', action='version',
                            version=version)

    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument('-d', '--debug', action='store_true',
                           help='debug messages')
    log_group.add_argument('-q', '--quiet', action='store_true',
                           help='run quietly')
    log_group.add_argument('-v', '--verbose', action='store_true',
                           help='verbose messages')

    parser.add_argument('--dumpconfig', action='store_true',
                        help=('output the utype to keyword mapping to '
                              'the console'))

    parser.add_argument('--ignorePartialWCS', action='store_true',
                        help='do not stop and exit upon finding partial WCS')

    parser.add_argument('-o', '--out', dest='out_obs_xml',
                        type=argparse.FileType('wb'),
                        help='output of augmented observation in XML',
                        required=False)

    in_group = parser.add_mutually_exclusive_group(required=True)
    in_group.add_argument('-i', '--in', dest='in_obs_xml',
                          type=argparse.FileType('r'),
                          help='input of observation to be augmented in XML')
    in_group.add_argument('--observation', nargs=2,
                          help='observation in a collection',
                          metavar=('collection', 'observationID'))

    parser.add_argument('--config', required=False,
                        help=('optional CAOM2 utype to keyword config file to '
                              'merge with the internal configuration'))

    parser.add_argument('--log', help='log file name > (instead of console)')
    parser.add_argument('--keep', action='store_true',
                        help='keep the locally stored files after ingestion')
    parser.add_argument('--test', action='store_true',
                        help='test mode, do not persist to database')
    parser.add_argument('--cert', help='Proxy Cert&Key PEM file')

    parser.add_argument('productID',
                        help='product ID of the plane in the observation')
    parser.add_argument('fileURI', help='URI of a fits file', nargs='+')

    if len(sys.argv) < 2:
        # correct error message when running python3
        parser.print_usage(file=sys.stderr)
        sys.stderr.write("{}: error: too few arguments\n".format(APP_NAME))
        sys.exit(-1)

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.WARN, stream=sys.stdout)

    logging.debug('Begin blueprint construction for CGPS {}.'.format('uri'))
    blueprint = ObsBlueprint()
    logging.debug('Blueprint construction completed for CGPS.'.format('uri'))
    return blueprint
