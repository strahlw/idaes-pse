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
Tests for update_workshop_materials
"""
import idaes.util.update_workshop_materials as up
import pytest

@pytest.mark.unit
def test_update_workshop_materials():
    # Note: This tests that the methods in update_workshop_materials.py
    # successfully download install_idaes_workshop_materials.py from Pyomo.org
    # We purposely do NOT test code within that downloaded module since we do
    # not want to automatically execute code during testing that was downloaded
    # from outside the IDAES repository.
    
    # download the module from pyomo.org
    download_dest = up.download_install_module()

    # check that the file contains the desired function (execute())
    download_succeeded = False
    with open(download_dest, 'r') as fd:
        for line in fd:
            if line.startswith('def execute():'):
                download_succeeded = True
                break

    assert download_succeeded == True

if __name__ == '__main__':
    test_update_workshop_materials()
    
