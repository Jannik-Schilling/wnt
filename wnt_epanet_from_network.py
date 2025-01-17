# -*- coding: utf-8 -*-

"""
/***************************************************************************
 WaterNetworkTools
                                 A QGIS plugin
 Water Network Modelling Utilities
 
                              -------------------
        begin                : 2019-07-19
        copyright            : (C) 2019 by Andrés García Martínez
        email                : ppnoptimizer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Andrés García Martínez'
__date__ = '2019-07-19'
__copyright__ = '(C) 2019 by Andrés García Martínez'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination)
from . import tools

class EpanetFromNetworkAlgorithm(QgsProcessingAlgorithm):
    """
    Build an epanet model file from node and link layers.
    """

    # DEFINE CONSTANTS

    NODES_INPUT = 'NODES_INPUT'
    LINKS_INPUT = 'LINKS_INPUT'
    TMPL_INPUT = 'TMPL_INPUT'
    OUTPUT = 'OUTPUT'
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        """
        Create a instance and return a new copy of algorithm.
        """
        return EpanetFromNetworkAlgorithm()

    def name(self):
        """
        Returns the unique algorithm name, used for identifying the algorithm.
        """
        return 'epanet_from_network'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Epanet file from network')

    def group(self):
        """
         Returns the name of the group this algorithm belongs to.
        """
        return self.tr('Water Network tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to.
        """
        return 'wnt'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm.
        """
        msg = "Make an epanet inp file from nodes and links. \n"
        msg += "Pipe diameter and roughness are ignored."
        return self.tr(msg)

    def initAlgorithm(self, config=None):
        """
        Define the inputs and outputs of the algorithm.
        """
        
        # ADD THE INPUT
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.NODES_INPUT,
                self.tr('Input nodes layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINKS_INPUT,
                self.tr('Input links layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        self.addParameter(
            QgsProcessingParameterFile (
                self.TMPL_INPUT,
                self.tr('Epanet template file'),
                extension='inp'
            )
        )
            
        # ADD A FILE DESTINATION
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Epanet model file'),
                fileFilter='*.inp'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        RUN PROCESS
        """
        # INPUT
        
        nodes = self.parameterAsSource(parameters, self.NODES_INPUT, context)
        links = self.parameterAsSource(parameters, self.LINKS_INPUT, context)
        template = self.parameterAsFile(parameters, self.TMPL_INPUT, context)
        
        # OUTPUT
        
        epanet = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
            )
        
        # BUILD NETWORK
        
        newnet = tools.Network()
        
        ncnt = 0
        ntot = nodes.featureCount()
        for f in nodes.getFeatures():
            ncnt += 1
            newnode = tools.Node(f['id'])
            newnode.set_wkt(f.geometry().asWkt())
            msg = 'Bad node type'
            assert f['type'] in ['JUNCTION', 'RESERVOIR', 'TANK'], msg
            newnode.set_type(f['type'])
            newnode.elevation = f['elevation']
            newnet.nodes.append(newnode)
            
            if ncnt % 100 == 0:
                feedback.setProgress(50*ncnt/ntot) # Update the progress bar 
            
            
        lcnt = 0
        ltot = links.featureCount()
        for f in links.getFeatures():
            lcnt += 1
            newlink = tools.Link(f['id'],f['start'],f['end'])
            newlink.set_wkt(f.geometry().asWkt())
            msg = 'Bad link type'
            assert f['type'] in ['PIPE', 'PUMP', 'PRV', 'PSV', 'PBV', 'FCV', \
                                'TCV','GPV'], msg
            newlink.set_type(f['type'])
            newnet.links.append(newlink)
            
            if lcnt % 100 == 0:
                feedback.setProgress(50+50*lcnt/ltot) # Update the progress bar       
        
        newnet.to_epanet(epanet, template)
        
        epanet = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
            )
        
        msg = 'Saved: {} nodes and {} links.'.format(ncnt,lcnt)
        feedback.pushInfo(msg) 
        
        # PROCCES CANCELED
        
        if feedback.isCanceled():
            return {}
        
        # OUTPUT

        return {self.OUTPUT: epanet}
