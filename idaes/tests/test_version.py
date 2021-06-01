###############################################################################
# ** Copyright Notice **
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES), and is copyright (c) 2018-2021 by the
# software owners: The Regents of the University of California, through Lawrence
# Berkeley National Laboratory,  National Technology & Engineering Solutions of
# Sandia, LLC, Carnegie Mellon University, West Virginia University Research
# Corporation, et al.  All rights reserved.
#
# NOTICE.  This Software was developed under funding from the U.S. Department of
# Energy and the U.S. Government consequently retains certain rights. As such, the
# U.S. Government has been granted for itself and others acting on its behalf a
# paid-up, nonexclusive, irrevocable, worldwide license in the Software to
# reproduce, distribute copies to the public, prepare derivative works, and
# perform publicly and display publicly, and to permit other to do so.
###############################################################################
"""
Tests for versioning
"""
# third-party
import pytest
# pkg
import idaes
from idaes import ver


@pytest.mark.unit
def test_idaes_version():
    assert idaes.__version__


@pytest.mark.unit
def test_ver_class():
    v = ver.Version(1, 2, 3)
    assert str(v) == '1.2.3'
    v = ver.Version(1, 2, 3, 'beta', 1)
    assert str(v) == '1.2.3.b1'
    v = ver.Version(1, 2, 3, 'development')
    assert str(v) == '1.2.3.dev'
    pytest.raises(ValueError, ver.Version, 1, 2, 3, 'howdy')


class MyVersionedClass(ver.HasVersion):
    def __init__(self):
        super(MyVersionedClass, self).__init__(1, 2, 3)


@pytest.mark.unit
def test_has_version():
    x = MyVersionedClass()
    assert str(x.version) == '1.2.3'


@pytest.mark.unit
def test_bump_version():
    v = ver.Version(1, 2, 3)
    assert tuple(v) == (1, 2, 3)
    v.micro += 1
    assert tuple(v) == (1, 2, 4)
