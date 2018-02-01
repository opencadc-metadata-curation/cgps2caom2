from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.io import fits

from cgps2caom2 import main_app, draw_cgps_blueprint

TEST_URI = 'ad:CGPS/CGPS_MC2_1420_MHz_I_image.fits'
TEST_URI_FHWM = 'ad:CGPS/CGPS_MD1_100_um_fwhm.txt'

EXPECTED_CGPS_BLUEPRINT = '''
'''


# def test_main_app():
#     test_result = main_app()
#     assert repr(test_result) == EXPECTED_CGPS_BLUEPRINT


def test_draw():
    hdr1 = fits.Header()
    hdr1['INSTRUME'] = 'TEST'
    hdr1['OBSFREQ'] = '1420406000.0'
    test_blueprint = draw_cgps_blueprint(TEST_URI, [hdr1])
    assert test_blueprint is not None
    assert test_blueprint._plan['Observation.telescope.name'] == 'DRAO-ST'
    assert test_blueprint._plan['Chunk.energy.specsys'] == 'TOPOCENT'
    assert test_blueprint._plan['Chunk.position.axis.axis1.cunit'] == 'deg'
    assert test_blueprint._plan['Chunk.polarization.axis.function.delta'] == '1'
    assert test_blueprint._plan['Chunk.energy.restfrq'] == '1420406000.0'

    test_blueprint = draw_cgps_blueprint(TEST_URI_FHWM, [])
    assert test_blueprint is not None
    assert test_blueprint._plan['Plane.productID'] == 'catalog'
    assert test_blueprint._plan['Artifact.productType'] == 'science'
