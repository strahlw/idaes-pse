##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2020, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
Methods for defining equibilibrium reactions
"""
from pyomo.environ import Var


# ----------------------------------------------------------------------------
class mole_frac_power_law_equil():
    def build_parameters(rblock, config):
        order_init = {}
        ppack = rblock.parent_block().config.property_package
        for p in ppack.phase_list:
            for j in ppack.component_list:
                if "reaction_order" in config.parameter_data:
                    try:
                        order_init[p, j] = config.parameter_data[
                            "reaction_order"][p, j]
                    except KeyError:
                        order_init[p, j] = 0
                else:
                    # Assume elementary reaction and use stoichiometry
                    try:
                        # Here we use the stoic. coeff. directly
                        # However, solids should be excluded as they normally
                        # do not appear in the equilibrium relationship
                        pobj = ppack.get_phase(p)
                        if not pobj.is_solid_phase():
                            order_init[p, j] = config.stoichiometry[p, j]
                        else:
                            order_init[p, j] = 0
                    except KeyError:
                        order_init[p, j] = 0

        rblock.reaction_order = Var(
                ppack.phase_list,
                ppack.component_list,
                initialize=order_init,
                doc="Reaction order",
                units=None)

    def return_expression(b, rblock, r_idx, T):
        e = None
        # Get reaction orders and construct power law expression
        for p in b.state_ref.params.phase_list:
            for j in b.state_ref.params.component_list:
                o = rblock.reaction_order[p, j]

                if e is None and o != 0:
                    e = b.state_ref.mole_frac_phase_comp[p, j]**o
                elif e is not None and o != 0:
                    e = e*b.state_ref.mole_frac_phase_comp[p, j]**o

        return b.k_eq[r_idx] == e
