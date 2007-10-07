# -*- coding: utf-8 -*-
# Setup script to build the Humility Theme. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""

"""
__author__ = "Cody Precord"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    sys.argv.append("bdist_egg")
    sys.argv.append("--dist-dir=../.")
    setup(
        name='Humility',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="GPLv2",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['humility'],
        package_data={'humility' : ['pixmaps/AUTHORS', 'pixmaps/COPYING', 
                                    'pixmaps/menu/*.png', 'pixmaps/toolbar/*.png',
                                    'pixmaps/mime/*.png',]},
        entry_points='''
        [Editra.plugins]
        Humility = humility:HumilityTheme
        '''
        )
