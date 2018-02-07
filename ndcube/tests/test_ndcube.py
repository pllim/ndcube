# -*- coding: utf-8 -*-
'''
Tests for NDCube
'''
from collections import namedtuple

import pytest
import sunpy.map
import numpy as np
import astropy.units as u

from ndcube import NDCube
from ndcube.utils.wcs import WCS, _wcs_slicer
from ndcube.tests import helpers

DimensionPair = namedtuple('DimensionPair', 'shape axis_types')

# sample data for tests
# TODO: use a fixture reading from a test file. file TBD.
ht = {
    'CTYPE3': 'HPLT-TAN',
    'CUNIT3': 'deg',
    'CDELT3': 0.5,
    'CRPIX3': 0,
    'CRVAL3': 0,
    'NAXIS3': 2,
    'CTYPE2': 'WAVE    ',
    'CUNIT2': 'Angstrom',
    'CDELT2': 0.2,
    'CRPIX2': 0,
    'CRVAL2': 0,
    'NAXIS2': 3,
    'CTYPE1': 'TIME    ',
    'CUNIT1': 'min',
    'CDELT1': 0.4,
    'CRPIX1': 0,
    'CRVAL1': 0,
    'NAXIS1': 4
}
wt = WCS(header=ht, naxis=3)
data = np.array([[[1, 2, 3, 4], [2, 4, 5, 3], [0, -1, 2, 3]],
                 [[2, 4, 5, 1], [10, 5, 2, 2], [10, 3, 3, 0]]])

hm = {
    'CTYPE1': 'WAVE    ',
    'CUNIT1': 'Angstrom',
    'CDELT1': 0.2,
    'CRPIX1': 0,
    'CRVAL1': 10,
    'NAXIS1': 4,
    'CTYPE2': 'HPLT-TAN',
    'CUNIT2': 'deg',
    'CDELT2': 0.5,
    'CRPIX2': 2,
    'CRVAL2': 0.5,
    'NAXIS2': 3,
    'CTYPE3': 'HPLN-TAN',
    'CUNIT3': 'deg',
    'CDELT3': 0.4,
    'CRPIX3': 2,
    'CRVAL3': 1,
    'NAXIS3': 2,
}
wm = WCS(header=hm, naxis=3)

mask_cubem = data > 0
mask_cube = data >= 0
uncertaintym = data
uncertainty = np.sqrt(data)
cubem = NDCube(
    data,
    wm,
    mask=mask_cubem,
    uncertainty=uncertaintym,
    extra_coords=[('time', 0, u.Quantity(range(data.shape[0]), unit=u.pix)),
                  ('hello', 1, u.Quantity(range(data.shape[1]), unit=u.pix)),
                  ('bye', 2, u.Quantity(range(data.shape[2]), unit=u.pix))])
cube = NDCube(
    data,
    wt,
    mask=mask_cube,
    uncertainty=uncertainty,
    missing_axis=[False, False, False, True],
    extra_coords=[('time', 0, u.Quantity(range(data.shape[0]), unit=u.pix)),
                  ('hello', 1, u.Quantity(range(data.shape[1]), unit=u.pix)),
                  ('bye', 2, u.Quantity(range(data.shape[2]), unit=u.pix))])


@pytest.mark.parametrize(
    "test_input,expected,mask,wcs,uncertainty,dimensions,extra_coords", [
        (cubem[:, 1], NDCube, mask_cubem[:, 1],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), 1)), data[:, 1],
         DimensionPair(
             shape=u.Quantity((2, 4), unit=u.pix),
             axis_types=['HPLN-TAN', 'WAVE']),
         {
             'bye': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             },
             'hello': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             }
         }),
        (cubem[:, 0:2], NDCube, mask_cubem[:, 0:2],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), slice(0, 2, None))),
         data[:, 0:2],
         DimensionPair(
             shape=u.Quantity((2, 2, 4), unit=u.pix),
             axis_types=['HPLN-TAN', 'HPLT-TAN', 'WAVE']),
         {
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             },
             'hello': {
                 'axis': 1,
                 'value': u.Quantity(range(2), unit=u.pix)
             },
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             }
         }),
        (cubem[:, :], NDCube, mask_cubem[:, :],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), slice(None, None, None))),
         data[:, :],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLN-TAN', 'HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cubem[1, 1], NDCube, mask_cubem[1, 1],
         _wcs_slicer(wm, [False, False, False], (1, 1)), data[1, 1],
         DimensionPair(
             shape=u.Quantity((4, ), unit=u.pix), axis_types=['WAVE']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cubem.dimensions.shape[2].value)),
                         unit=u.pix)
                 }
             }),
        (cubem[1, 0:2], NDCube, mask_cubem[1, 0:2],
         _wcs_slicer(wm, [False, False, False],
                     (1, slice(0, 2, None))), data[1, 0:2],
         DimensionPair(
             shape=u.Quantity((2, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis': 0,
                     'value': u.Quantity(range(2), unit=u.pix)
                 },
                 'bye': {
                     'axis':
                     1,
                     'value':
                     u.Quantity(
                         range(int(cubem.dimensions.shape[2].value)),
                         unit=u.pix)
                 }
             }),
        (cubem[1, :], NDCube, mask_cubem[1, :],
         _wcs_slicer(wm, [False, False, False],
                     (1, slice(None, None, None))), data[1, :],
         DimensionPair(
             shape=u.Quantity((3, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'hello': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[:, 1], NDCube, mask_cube[:, 1],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), 1)), uncertainty[:, 1],
         DimensionPair(
             shape=u.Quantity((2, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'TIME']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'bye': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[:, 0:2], NDCube, mask_cube[:, 0:2],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), slice(0, 2, None))),
         uncertainty[:, 0:2],
         DimensionPair(
             shape=u.Quantity((2, 2, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE', 'TIME']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis': 1,
                 'value': u.Quantity(range(2), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[:, :], NDCube, mask_cube[:, :],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), slice(None, None, None))),
         uncertainty[:, :],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE', 'TIME']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[1, 1], NDCube, mask_cube[1, 1],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, 1)), uncertainty[1, 1],
         DimensionPair(
             shape=u.Quantity((4, ), unit=u.pix), axis_types=['TIME']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cube.dimensions.shape[2].value)),
                         unit=u.pix)
                 }
             }),
        (cube[1, 0:2], NDCube, mask_cube[1, 0:2],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, slice(0, 2, None))), uncertainty[1, 0:2],
         DimensionPair(
             shape=u.Quantity(
                 (2, 4), unit=u.pix), axis_types=['WAVE', 'TIME']), {
                     'time': {
                         'axis': None,
                         'value': u.Quantity(1, unit=u.pix)
                     },
                     'hello': {
                         'axis': 0,
                         'value': u.Quantity(range(2), unit=u.pix)
                     },
                     'bye': {
                         'axis':
                         1,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[2].value)),
                             unit=u.pix)
                     }
                 }),
        (cube[1, :], NDCube, mask_cube[1, :],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, slice(0, 2, None))), uncertainty[1, :],
         DimensionPair(
             shape=u.Quantity(
                 (3, 4), unit=u.pix), axis_types=['WAVE', 'TIME']), {
                     'time': {
                         'axis': None,
                         'value': u.Quantity(1, unit=u.pix)
                     },
                     'hello': {
                         'axis':
                         0,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[1].value)),
                             unit=u.pix)
                     },
                     'bye': {
                         'axis':
                         1,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[2].value)),
                             unit=u.pix)
                     }
                 }),
    ])
def test_slicing_second_axis(test_input, expected, mask, wcs, uncertainty,
                             dimensions, extra_coords):
    assert isinstance(test_input, expected)
    assert np.all(test_input.mask == mask)
    helpers.assert_wcs_are_equal(test_input.wcs, wcs[0])
    assert test_input.missing_axis == wcs[1]
    assert test_input.uncertainty.array.shape == uncertainty.shape
    assert test_input.dimensions[1] == dimensions[1]
    assert np.all(test_input.dimensions[0].value == dimensions[0].value)
    assert test_input.dimensions[0].unit == dimensions[0].unit
    helpers.assert_extra_coords_equal(test_input.extra_coords, extra_coords)


@pytest.mark.parametrize(
    "test_input,expected,mask,wcs,uncertainty,dimensions,extra_coords", [
        (cubem[1], NDCube, mask_cubem[1],
         _wcs_slicer(wm, [False, False, False], 1), data[1],
         DimensionPair(
             shape=u.Quantity((3, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'hello': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cubem[0:2], NDCube, mask_cubem[0:2],
         _wcs_slicer(wm, [False, False, False], slice(0, 2, None)), data[0:2],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLN-TAN', 'HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis': 0,
                 'value': u.Quantity(range(2), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cubem[:], NDCube, mask_cubem[:],
         _wcs_slicer(wm, [False, False, False], slice(None, None, None)),
         data[:],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLN-TAN', 'HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[1], NDCube, mask_cube[1],
         _wcs_slicer(wt, [True, False, False, False], 1), uncertainty[1],
         DimensionPair(
             shape=u.Quantity(
                 (3, 4), unit=u.pix), axis_types=['WAVE', 'TIME']), {
                     'time': {
                         'axis': None,
                         'value': u.Quantity(1, unit=u.pix)
                     },
                     'hello': {
                         'axis':
                         0,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[1].value)),
                             unit=u.pix)
                     },
                     'bye': {
                         'axis':
                         1,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[2].value)),
                             unit=u.pix)
                     }
                 }),
        (cube[0:2], NDCube, mask_cube[0:2],
         _wcs_slicer(wt, [True, False, False, False], slice(0, 2, None)),
         uncertainty[0:2],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE', 'TIME']),
         {
             'time': {
                 'axis': 0,
                 'value': u.Quantity(range(2), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[:], NDCube, mask_cube[:],
         _wcs_slicer(wt, [True, False, False, False], slice(None, None, None)),
         uncertainty[:],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE', 'TIME']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
    ])
def test_slicing_first_axis(test_input, expected, mask, wcs, uncertainty,
                            dimensions, extra_coords):
    assert isinstance(test_input, expected)
    assert np.all(test_input.mask == mask)
    helpers.assert_wcs_are_equal(test_input.wcs, wcs[0])
    assert test_input.missing_axis == wcs[1]
    assert test_input.uncertainty.array.shape == uncertainty.shape
    assert test_input.dimensions[1] == dimensions[1]
    assert np.all(test_input.dimensions[0].value == dimensions[0].value)
    assert test_input.dimensions[0].unit == dimensions[0].unit
    helpers.assert_extra_coords_equal(test_input.extra_coords, extra_coords)


@pytest.mark.parametrize(
    "test_input,expected,mask,wcs,uncertainty,dimensions,extra_coords", [
        (cubem[:, :, 1], NDCube, mask_cubem[:, :, 1],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), slice(None, None, None), 1)),
         data[:, :, 1],
         DimensionPair(
             shape=u.Quantity((2, 3), unit=u.pix),
             axis_types=['HPLN-TAN', 'HPLT-TAN']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             }
         }),
        (cubem[:, :, 0:2], NDCube, mask_cubem[:, :, 0:2],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), slice(None, None, None),
                      slice(0, 2, None))), data[:, :, 0:2],
         DimensionPair(
             shape=u.Quantity((2, 3, 2), unit=u.pix),
             axis_types=['HPLN-TAN', 'HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis': 2,
                 'value': u.Quantity(range(2), unit=u.pix)
             }
         }),
        (cubem[:, :, :], NDCube, mask_cubem[:, :, :],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), slice(None, None, None),
                      slice(None, None, None))), data[:, :, :],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLN-TAN', 'HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cubem[:, 1, 1], NDCube, mask_cubem[:, 1, 1],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), 1, 1)), data[:, 1, 1],
         DimensionPair(
             shape=u.Quantity((2, ), unit=u.pix), axis_types=['HPLN-TAN']), {
                 'time': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cubem.dimensions.shape[0].value)),
                         unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 }
             }),
        (cubem[:, 1, 0:2], NDCube, mask_cubem[:, 1, 0:2],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), 1, slice(0, 2, None))),
         data[:, 1, 0:2],
         DimensionPair(
             shape=u.Quantity((2, 2), unit=u.pix),
             axis_types=['HPLN-TAN', 'WAVE']), {
                 'time': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cubem.dimensions.shape[0].value)),
                         unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis': 1,
                     'value': u.Quantity(range(2), unit=u.pix)
                 }
             }),
        (cubem[:, 1, :], NDCube, mask_cubem[:, 1, :],
         _wcs_slicer(wm, [False, False, False],
                     (slice(None, None, None), 1, slice(None, None, None))),
         data[:, 1, :],
         DimensionPair(
             shape=u.Quantity((2, 4), unit=u.pix),
             axis_types=['HPLN-TAN', 'WAVE']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'bye': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cubem[1, :, 1], NDCube, mask_cubem[1, :, 1],
         _wcs_slicer(wm, [False, False, False],
                     (1, slice(None, None, None), 1)), data[1, :, 1],
         DimensionPair(
             shape=u.Quantity((3, ), unit=u.pix), axis_types=['HPLT-TAN']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cubem.dimensions.shape[1].value)),
                         unit=u.pix)
                 },
                 'bye': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 }
             }),
        (cubem[1, :, 0:2], NDCube, mask_cubem[1, :, 0:2],
         _wcs_slicer(wm, [False, False, False],
                     (1, slice(None, None, None), slice(0, 2, None))),
         data[1, :, 0:2],
         DimensionPair(
             shape=u.Quantity((3, 2), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cubem.dimensions.shape[1].value)),
                         unit=u.pix)
                 },
                 'bye': {
                     'axis': 1,
                     'value': u.Quantity(range(2), unit=u.pix)
                 }
             }),
        (cubem[1, :, :], NDCube, mask_cubem[1, :, :],
         _wcs_slicer(wm, [False, False, False],
                     (1, slice(None, None, None), slice(None, None, None))),
         data[1, :, :],
         DimensionPair(
             shape=u.Quantity((3, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'hello': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cubem.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cubem[1, 1, 1], NDCube, mask_cubem[1, 1, 1],
         _wcs_slicer(wm, [False, False, False], (1, 1, 1)), data[1, 1, 1],
         DimensionPair(shape=u.Quantity((), unit=u.pix), axis_types=[]), {
             'time': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'hello': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'bye': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             }
         }),
        (cubem[1, 1, 0:2], NDCube, mask_cubem[1, 1, 0:2],
         _wcs_slicer(wm, [False, False, False],
                     (1, 1, slice(0, 2, None))), data[1, 1, 0:2],
         DimensionPair(
             shape=u.Quantity((2, ), unit=u.pix), axis_types=['WAVE']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis': 0,
                     'value': u.Quantity(range(2), unit=u.pix)
                 }
             }),
        (cubem[1, 1, :], NDCube, mask_cubem[1, 1, :],
         _wcs_slicer(wm, [False, False, False],
                     (1, 1, slice(None, None, None))), data[1, 1, :],
         DimensionPair(
             shape=u.Quantity((4, ), unit=u.pix), axis_types=['WAVE']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cubem.dimensions.shape[2].value)),
                         unit=u.pix)
                 }
             }),
        (cube[:, :, 1], NDCube, mask_cube[:, :, 1],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), slice(None, None, None), 1)),
         uncertainty[:, :, 1],
         DimensionPair(
             shape=u.Quantity((2, 3), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             }
         }),
        (cube[:, :, 0:2], NDCube, mask_cube[:, :, 0:2],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), slice(None, None, None),
                      slice(0, 2, None))), uncertainty[:, :, 0:2],
         DimensionPair(
             shape=u.Quantity((2, 3, 2), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE', 'TIME']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis': 2,
                 'value': u.Quantity(range(2), unit=u.pix)
             }
         }),
        (cube[:, :, :], NDCube, mask_cube[:, :, :],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), slice(None, None, None),
                      slice(None, None, None))), uncertainty[:, :, :],
         DimensionPair(
             shape=u.Quantity((2, 3, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'WAVE', 'TIME']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[1].value)), unit=u.pix)
             },
             'bye': {
                 'axis':
                 2,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[:, 1, 1], NDCube, mask_cube[:, 1, 1],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), 1, 1)), uncertainty[:, 1, 1],
         DimensionPair(
             shape=u.Quantity((2, ), unit=u.pix), axis_types=['HPLT-TAN']), {
                 'time': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cube.dimensions.shape[0].value)),
                         unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 }
             }),
        (cube[:, 1, 0:2], NDCube, mask_cube[:, 1, 0:2],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), 1, slice(0, 2, None))),
         uncertainty[:, 1, 0:2],
         DimensionPair(
             shape=u.Quantity((2, 2), unit=u.pix),
             axis_types=['HPLT-TAN', 'TIME']), {
                 'time': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cube.dimensions.shape[0].value)),
                         unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis': 1,
                     'value': u.Quantity(range(2), unit=u.pix)
                 }
             }),
        (cube[:, 1, :], NDCube, mask_cube[:, 1, :],
         _wcs_slicer(wt, [True, False, False, False],
                     (slice(None, None, None), 1, slice(None, None, None))),
         uncertainty[:, 1, :],
         DimensionPair(
             shape=u.Quantity((2, 4), unit=u.pix),
             axis_types=['HPLT-TAN', 'TIME']),
         {
             'time': {
                 'axis':
                 0,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[0].value)), unit=u.pix)
             },
             'hello': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'bye': {
                 'axis':
                 1,
                 'value':
                 u.Quantity(
                     range(int(cube.dimensions.shape[2].value)), unit=u.pix)
             }
         }),
        (cube[1, :, 1], NDCube, mask_cube[1, :, 1],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, slice(None, None, None), 1)), uncertainty[1, :, 1],
         DimensionPair(
             shape=u.Quantity((3, ), unit=u.pix), axis_types=['WAVE']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cube.dimensions.shape[1].value)),
                         unit=u.pix)
                 },
                 'bye': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 }
             }),
        (cube[1, :, 0:2], NDCube, mask_cube[1, :, 0:2],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, slice(None, None, None), slice(0, 2, None))),
         uncertainty[1, :, 0:2],
         DimensionPair(
             shape=u.Quantity(
                 (3, 2), unit=u.pix), axis_types=['WAVE', 'TIME']), {
                     'time': {
                         'axis': None,
                         'value': u.Quantity(1, unit=u.pix)
                     },
                     'hello': {
                         'axis':
                         0,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[1].value)),
                             unit=u.pix)
                     },
                     'bye': {
                         'axis': 1,
                         'value': u.Quantity(range(2), unit=u.pix)
                     }
                 }),
        (cube[1, :, :], NDCube, mask_cube[1, :, :],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, slice(None, None, None), slice(None, None, None))),
         uncertainty[1, :, :],
         DimensionPair(
             shape=u.Quantity(
                 (3, 4), unit=u.pix), axis_types=['WAVE', 'TIME']), {
                     'time': {
                         'axis': None,
                         'value': u.Quantity(1, unit=u.pix)
                     },
                     'hello': {
                         'axis':
                         0,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[1].value)),
                             unit=u.pix)
                     },
                     'bye': {
                         'axis':
                         1,
                         'value':
                         u.Quantity(
                             range(int(cube.dimensions.shape[2].value)),
                             unit=u.pix)
                     }
                 }),
        (cube[1, 1, 1], NDCube, mask_cube[1, 1, 1],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, 1, 1)), uncertainty[1, 1, 1],
         DimensionPair(shape=u.Quantity((), unit=u.pix), axis_types=[]), {
             'time': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'hello': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             },
             'bye': {
                 'axis': None,
                 'value': u.Quantity(1, unit=u.pix)
             }
         }),
        (cube[1, 1, 0:2], NDCube, mask_cube[1, 1, 0:2],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, 1, slice(0, 2, None))), uncertainty[1, 1, 0:2],
         DimensionPair(
             shape=u.Quantity((2, ), unit=u.pix), axis_types=['TIME']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis': 0,
                     'value': u.Quantity(range(2), unit=u.pix)
                 }
             }),
        (cube[1, 1, :], NDCube, mask_cube[1, 1, :],
         _wcs_slicer(wt, [True, False, False, False],
                     (1, 1, slice(0, 2, None))), uncertainty[1, 1, :],
         DimensionPair(
             shape=u.Quantity((4, ), unit=u.pix), axis_types=['TIME']), {
                 'time': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'hello': {
                     'axis': None,
                     'value': u.Quantity(1, unit=u.pix)
                 },
                 'bye': {
                     'axis':
                     0,
                     'value':
                     u.Quantity(
                         range(int(cube.dimensions.shape[2].value)),
                         unit=u.pix)
                 }
             }),
    ])
def test_slicing_third_axis(test_input, expected, mask, wcs, uncertainty,
                            dimensions, extra_coords):
    assert isinstance(test_input, expected)
    assert np.all(test_input.mask == mask)
    helpers.assert_wcs_are_equal(test_input.wcs, wcs[0])
    assert test_input.missing_axis == wcs[1]
    assert test_input.uncertainty.array.shape == uncertainty.shape
    assert test_input.dimensions[1] == dimensions[1]
    assert np.all(test_input.dimensions[0].value == dimensions[0].value)
    assert test_input.dimensions[0].unit == dimensions[0].unit
    helpers.assert_extra_coords_equal(test_input.extra_coords, extra_coords)


@pytest.mark.parametrize("test_input,expected", [
    (cubem[1].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[0],
     wm.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), wm.wcs.crpix[2] - 1, 0)[-2]),
    (cubem[1].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[1],
     wm.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), wm.wcs.crpix[2] - 1, 0)[0]),
    (cubem[0:2].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[0],
     wm.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), 0)[-1]),
    (cubem[0:2].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[1],
     wm.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), 0)[1]),
    (cubem[0:2].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[2],
     wm.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), 0)[0]),
    (cube[1].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[0],
     wt.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), wt.wcs.crpix[2] - 1,
         wt.wcs.crpix[3] - 1, 0)[1]),
    (cube[1].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[1],
     wt.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), wt.wcs.crpix[2] - 1,
         wt.wcs.crpix[3] - 1, 0)[0]),
    (cube[0:2].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[0],
     wt.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), wt.wcs.crpix[3] - 1, 0)[2]),
    (cube[0:2].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[1],
     wt.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), wt.wcs.crpix[3] - 1, 0)[1]),
    (cube[0:2].pixel_to_world([
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix),
        u.Quantity(np.arange(4), unit=u.pix)
    ])[2],
     wt.all_pix2world(
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix),
         u.Quantity(np.arange(4), unit=u.pix), wt.wcs.crpix[3] - 1, 0)[0]),
])
def test_pixel_to_world(test_input, expected):
    assert np.all(test_input.value == expected)


@pytest.mark.parametrize("test_input,expected", [
    (cubem[1].world_to_pixel(
        [
            u.Quantity(np.arange(4), unit=u.deg),
            u.Quantity(np.arange(4), unit=u.m)
        ],
        origin=1)[0],
     wm.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m), wm.wcs.crpix[2] - 1, 1)[1]),
    (cubem[1].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.m)
    ])[1],
     wm.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m), wm.wcs.crpix[2] - 1, 0)[0]),
    (cubem[0:2].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.m)
    ])[0],
     wm.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m), 0)[-1]),
    (cubem[0:2].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.m)
    ])[1],
     wm.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m), 0)[1]),
    (cubem[0:2].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.m)
    ])[2],
     wm.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m), 0)[0]),
    (cube[1].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.m),
        u.Quantity(np.arange(4), unit=u.min)
    ])[0],
     wt.all_world2pix(
         u.Quantity(np.arange(4), unit=u.m),
         u.Quantity(np.arange(4), unit=u.min), wt.wcs.crpix[2] - 1,
         wt.wcs.crpix[3] - 1, 0)[1]),
    (cube[1].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.m),
        u.Quantity(np.arange(4), unit=u.min)
    ])[1],
     wt.all_world2pix(
         u.Quantity(np.arange(4), unit=u.m),
         u.Quantity(np.arange(4), unit=u.min), wt.wcs.crpix[2] - 1,
         wt.wcs.crpix[3] - 1, 0)[0]),
    (cube[0:2].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.m),
        u.Quantity(np.arange(4), unit=u.min)
    ])[0],
     wt.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m),
         u.Quantity(np.arange(4), unit=u.min), wt.wcs.crpix[3] - 1, 0)[2]),
    (cube[0:2].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.m),
        u.Quantity(np.arange(4), unit=u.min)
    ])[1],
     wt.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m),
         u.Quantity(np.arange(4), unit=u.min), wt.wcs.crpix[3] - 1, 0)[1]),
    (cube[0:2].world_to_pixel([
        u.Quantity(np.arange(4), unit=u.deg),
        u.Quantity(np.arange(4), unit=u.m),
        u.Quantity(np.arange(4), unit=u.min)
    ])[2],
     wt.all_world2pix(
         u.Quantity(np.arange(4), unit=u.deg),
         u.Quantity(np.arange(4), unit=u.m),
         u.Quantity(np.arange(4), unit=u.min), wt.wcs.crpix[3] - 1, 0)[0]),
])
def test_world_to_pixel(test_input, expected):
    assert np.allclose(test_input.value, expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [(cubem[:, :, 0].to_sunpy(), sunpy.map.mapbase.GenericMap),
     (cubem[:, 0:2, 1].to_sunpy(), sunpy.map.mapbase.GenericMap),
     (cubem[0:2, :, 2].to_sunpy(), sunpy.map.mapbase.GenericMap)])
def test_to_sunpy(test_input, expected):
    assert isinstance(test_input, expected)


@pytest.mark.parametrize("test_input", [(cubem[0, :, 0]), (cubem[:, 1, 1]),
                                        (cubem[0:2, :, 0:2])])
def test_to_sunpy_error(test_input):
    with pytest.raises(NotImplementedError):
        test_input.to_sunpy()

@pytest.mark.parametrize(
    "test_input,expected",
    [((cubem, 0*u.pix, 1.5*u.pix, "time"), cubem[0:2]),
     ((cube, 0*u.pix, 1.5*u.pix, "bye"), cube[:, :, 0:2])])
def test_crop_by_extra_coord(test_input, expected):
    print(test_input[0].crop_by_extra_coord(*tuple(test_input[1:])))
    print(expected.mask)
    helpers.assert_cubes_equal(
        test_input[0].crop_by_extra_coord(*tuple(test_input[1:])), expected)
