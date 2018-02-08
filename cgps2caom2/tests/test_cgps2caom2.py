from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.io import fits

from cgps2caom2 import main_app, draw_cgps_blueprint
from caom2 import ObservationReader
from caom2.diff import get_differences

import os
import pytest
import sys


TEST_URI = 'ad:CGPS/CGPS_MC2_1420_MHz_I_image.fits'
TEST_URI_FHWM = 'ad:CGPS/CGPS_MD1_100_um_fwhm.txt'

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TESTDATA_DIR = os.path.join(THIS_DIR, 'data')


def test_draw():
    hdr1 = fits.Header()
    hdr1['INSTRUME'] = 'TEST'
    hdr1['OBSFREQ'] = '1420406000.0'
    test_blueprint = draw_cgps_blueprint(TEST_URI, [hdr1], local=False,
                                         cert=None)
    assert test_blueprint is not None
    assert test_blueprint._plan['Observation.telescope.name'] == 'DRAO-ST'
    assert test_blueprint._plan['Chunk.energy.specsys'] == 'TOPOCENT'
    assert test_blueprint._plan['Chunk.position.axis.axis1.cunit'] == 'deg'
    assert test_blueprint._plan['Chunk.polarization.axis.function.delta'] == '1'
    assert test_blueprint._plan['Chunk.energy.restfrq'] == (['OBSFREQ'], None)
    assert test_blueprint._plan['Observation.intent'] == 'science'
    assert test_blueprint._plan['Plane.provenance.lastExecuted'] == (
    ['DATE-FTS'], None)

    # test_blueprint = draw_cgps_blueprint(
    #     TEST_URI_FHWM, [], os.path.join(TESTDATA_DIR,
    #                                     'CGPS_MD1_100_um_fwhm.txt.header'))
    # assert test_blueprint is not None
    # assert test_blueprint._plan['Plane.productID'] == 'catalog'
    # assert test_blueprint._plan['Artifact.productType'] == 'science'


# @pytest.mark.parametrize('test_name', ['MC2_DRAO-ST', 'MC2_FCRAO', 'MD1_IRAS'])
@pytest.mark.parametrize('test_name', ['MD1_IRAS'])
def test_main_app(test_name):
    product_id = 'ignored_product_id'
    location = os.path.join(TESTDATA_DIR, test_name)
    actual_file_name = os.path.join(location, '{}.actual.xml'.format(test_name))
    files = ' '.join(
        [os.path.join(location, name) for name in os.listdir(location) if
         name.endswith('header')])
    uris = ' '.join(
        ['ad:CGPS/{}'.format(name.split('.header')[0]) for name in
         os.listdir(location) if name.endswith('header')])
    sys.argv = \
        ('cgps2caom2 --debug --local {} --observation CGPS {} -o {} {} {}'.
         format(files, test_name, actual_file_name, product_id, uris)).split()
    main_app()
    expected = _read_obs(os.path.join(location, '{}.xml'.format(test_name)))
    actual = _read_obs(actual_file_name)
    result = get_differences(expected, actual, 'Observation')
    print('\n'.join(str(p) for p in result))
    assert len(result) == 0


def _read_obs(fname):
    assert os.path.exists(fname)
    reader = ObservationReader(False)
    result = reader.read(fname)
    return result
