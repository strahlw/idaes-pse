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
This module contains miscellaneous utility functions for use in IDAES models.
"""
import xml.dom.minidom

import pyomo.environ as pyo
from pyomo.core.base.expression import _GeneralExpressionData
from pyomo.core.base.plugin import ModelComponentFactory
from pyomo.core.base.indexed_component import (
    UnindexedComponent_set, )
from pyomo.core.base.util import disable_methods


# Author: Andrew Lee
def add_object_reference(self, local_name, remote_object):
    """
    Method to create a reference in the local model to a remote Pyomo object.
    This method should only be used where Pyomo Reference objects are not
    suitable (such as for referencing scalar Pyomo objects where the None
    index is undesirable).

    Args:
        local_name : name to use for local reference (str)
        remote_object : object to make a reference to

    Returns:
        None
    """
    try:
        object.__setattr__(self, local_name, remote_object)
    except AttributeError:
        raise AttributeError(
            "{} failed to construct reference to {} - remote "
            "object does not exist.".format(self.name, remote_object)
        )


# Author: Jaffer Ghouse
def extract_data(data_dict):
    """
    General method that returns a rule to extract data from a python
    dictionary. This method allows the param block to have a database for
    a parameter but extract a subset of this data to initialize a Pyomo
    param object.
    """

    def _rule_initialize(m, *args):
        if len(args) > 1:
            return data_dict[args]
        else:
            return data_dict[args[0]]

    return _rule_initialize


# Author: John Eslick
def TagReference(s, description=""):
    """
    Create a Pyomo reference with an added description string attribute to
    describe the reference. The intended use for these references is to create
    a time-indexed reference to variables in a model corresponding to plant
    measurment tags.

    Args:
        s: Pyomo time slice of a variable or expression
        description (str): A description the measurment

    Returns:
        A Pyomo Reference object with an added doc attribute
    """
    r = pyo.Reference(s)
    r.description = description
    return r


# Author John Eslick
def svg_tag(
    tags,
    svg,
    outfile=None,
    idx=None,
    tag_map=None,
    show_tags=False,
    byte_encoding="utf-8",
):
    """
    Replace text in a SVG with tag values for the model. This works by looking
    for text elements in the SVG with IDs that match the tags or are in tag_map.

    Args:
        tags: A dictionary where the key is the tag and the value is a Pyomo
            Refernce.  The refernce could be indexed. In yypical IDAES
            applications the references would be indexed by time.
        svg: a file pointer or a string continaing svg contents
        outfile: a file name to save the results, if None don't save
        idx: if None not indexed, otherwise an index in the indexing set of the
            reference
        tag_map: dictionary with svg id keys and tag values, to map svg ids to
            tags
        show_tags: Put tag labels of the diagram instead of numbers
        byte_encoding: If svg is given as a byte-array, use this encoding to
            convert it to a string.

    Returns:
        String for SVG
    """
    if isinstance(svg, str):  # assume this is svg content string
        pass
    elif isinstance(svg, bytes):
        svg = svg.decode(byte_encoding)
    elif hasattr(svg, "read"):  # file-like object to svg
        svg = svg.read()
    else:
        raise TypeError("SVG must either be a string or a file-like object")
    # Make tag map here because the tags may not make valid XML IDs if no
    # tag_map provided we'll go ahead and handle XML @ (maybe more in future)
    if tag_map is None:
        tag_map = dict()
        for tag in tags:
            new_tag = tag.replace("@", "_")
            tag_map[new_tag] = tag
    # Search for text in the svg that has an id in tags
    doc = xml.dom.minidom.parseString(svg)
    texts = doc.getElementsByTagName("text")
    for t in texts:
        id = t.attributes["id"].value
        if id in tag_map:
            # if it's multiline change last line
            tspan = t.getElementsByTagName("tspan")[-1].childNodes[0]
            try:
                if show_tags:
                    val = tag_map[id]
                elif idx is None:
                    val = pyo.value(tags[tag_map[id]], exception=False)
                else:
                    val = pyo.value(tags[tag_map[id]][idx], exception=False)
            except ZeroDivisionError:
                val = "Divide_by_0"
            try:
                tspan.nodeValue = "{:.4e}".format(val)
            except ValueError:  # whatever it is can't be scientific notation
                tspan.nodeValue = val

    new_svg = doc.toxml()
    # If outfile is provided save to a file
    if outfile is not None:
        with open(outfile, "w") as f:
            f.write(new_svg)
    return new_svg


# Author: John Eslick
def copy_port_values(destination, source):
    """
    Copy the variable values in the source port to the destination port. The
    ports must containt the same variables.

    Args:
        (pyomo.Port): Copy values from this port
        (pyomo.Port): Copy values to this port

    Returns:
        None
    """
    for k, v in destination.vars.items():
        if isinstance(v, pyo.Var):
            for i in v:
                v[i].value = pyo.value(source.vars[k][i])


# -----------------------------------------------------------------------------
# Creating a Component derived from Pyomo's Expression to use in cases
# where an Expression could be mistaken for a Var.
# Author: Andrew Lee
class _GeneralVarLikeExpressionData(_GeneralExpressionData):
    """
    An object derived from _GeneralExpressionData which implements methods for
    common APIs on Vars.

    Constructor Arguments:
        expr: The Pyomo expression stored in this expression.

        component: The Expression object that owns this data.

    Public Class Attributes:
        expr: The expression owned by this data.

    Private class attributes:
        _component: The expression component.
    """

    # Define methods for common APIs on Vars in case user mistakes
    # an Expression for a Var
    @property
    def value(self):
        # Overload value so it behaves like a Var
        return pyo.value(self.expr)

    @value.setter
    def value(self, expr):
        # Overload value seter to prevent users changing the expression body
        raise TypeError(
            "%s is an Expression and does not have a value which can be set."
            % (self.name))

    def setlb(self, val=None):
        raise TypeError(
            "%s is an Expression and can not have bounds. "
            "Use an inequality Constraint instead."
            % (self.name))

    def setub(self, val=None):
        raise TypeError(
            "%s is an Expression and can not have bounds. "
            "Use an inequality Constraint instead."
            % (self.name))

    def fix(self, val=None):
        raise TypeError(
            "%s is an Expression and can not be fixed. "
            "Use an equality Constraint instead."
            % (self.name))

    def unfix(self):
        raise TypeError(
            "%s is an Expression and can not be unfixed."
            % (self.name))

@ModelComponentFactory.register(
    "Named expressions that can be used in places of variables.")
class VarLikeExpression(pyo.Expression):
    """
    A shared var-like expression container, which may be defined over a index.

    Constructor Arguments:
        initialize: A Pyomo expression or dictionary of expressions used
        to initialize this object.

        expr: A synonym for initialize.

        rule: A rule function used to initialize this object.
    """

    _ComponentDataClass = _GeneralVarLikeExpressionData
    NoConstraint    = (1000,)
    Skip            = (1000,)

    def __new__(cls, *args, **kwds):
        if cls is not VarLikeExpression:
            return super(VarLikeExpression, cls).__new__(cls)
        if not args or (args[0] is UnindexedComponent_set and len(args) == 1):
            return super(VarLikeExpression, cls).__new__(
                AbstractSimpleVarLikeExpression)
        else:
            return super(VarLikeExpression, cls).__new__(
                IndexedVarLikeExpression)


class SimpleVarLikeExpression(_GeneralVarLikeExpressionData,
                              VarLikeExpression):

    def __init__(self, *args, **kwds):
        _GeneralVarLikeExpressionData.__init__(self, expr=None, component=self)
        VarLikeExpression.__init__(self, *args, **kwds)

    #
    # From Pyomo: Leaving this method for backward compatibility reasons.
    # (probably should be removed)
    # Note: Doesn't seem to work without it
    #
    def add(self, index, expr):
        """Add an expression with a given index."""
        if index is not None:
            raise KeyError(
                "SimpleExpression object '%s' does not accept "
                "index values other than None. Invalid value: %s"
                % (self.name, index))
        if (type(expr) is tuple) and \
           (expr == pyo.Expression.Skip):
            raise ValueError(
                "Expression.Skip can not be assigned "
                "to an Expression that is not indexed: %s"
                % (self.name))
        self.set_value(expr)
        return self


@disable_methods({'set_value', 'is_constant', 'is_fixed', 'expr'})
class AbstractSimpleVarLikeExpression(SimpleVarLikeExpression):
    pass


class IndexedVarLikeExpression(VarLikeExpression):

    #
    # From Pyomo: Leaving this method for backward compatibility reasons
    # Note: It allows adding members outside of self._index.
    #       This has always been the case. Not sure there is
    #       any reason to maintain a reference to a separate
    #       index set if we allow this.
    #
    def add(self, index, expr):
        """Add an expression with a given index."""
        if (type(expr) is tuple) and (expr == pyo.Expression.Skip):
            return None
        cdata = _GeneralVarLikeExpressionData(expr, component=self)
        self._data[index] = cdata
        return cdata

    # Define methods for common APIs on Vars in case user mistakes
    # an Expression for a Var
    def setlb(self, val=None):
        raise TypeError(
            "%s is an Expression and can not have bounds. "
            "Use inequality Constraints instead."
            % (self.name))

    def setub(self, val=None):
        raise TypeError(
            "%s is an Expression and can not have bounds. "
            "Use inequality Constraints instead."
            % (self.name))

    def fix(self, val=None):
        raise TypeError(
            "%s is an Expression and can not be fixed. "
            "Use equality Constraints instead."
            % (self.name))

    def unfix(self):
        raise TypeError(
            "%s is an Expression and can not be unfixed."
            % (self.name))
