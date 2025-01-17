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
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination)

class ScnFromPipePropertiesAlgorithm(QgsProcessingAlgorithm):
    """
    Build an epanet scenary file from pipe diameter and roughness.
    """

    # DEFINE CONSTANTS

    LINKS_INPUT = 'LINKS_INPUT'
    D_FIELD_INPUT = 'D_FIELD_INPUT'
    R_FIELD_INPUT = 'R_FIELD_INPUT'
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
        return ScnFromPipePropertiesAlgorithm()

    def name(self):
        """
        Returns the unique algorithm name, used for identifying the algorithm.
        """
        return 'scn_from_pipe_properties'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Scenario from pipe properties')

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
        return self.tr("Make an epanet scenario file from pipe diameter and roughness.")

    def initAlgorithm(self, config=None):
        """
        Define the inputs and outputs of the algorithm.
        """
        
        # ADD THE INPUT
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINKS_INPUT,
                self.tr('Input links layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.D_FIELD_INPUT,
                self.tr('Field containing diameter'),
                'diameter',
                self.LINKS_INPUT
            )
        )
        self.addParameter(
            QgsProcessingParameterField (
                self.R_FIELD_INPUT,
                self.tr('Field containing roughness'),
                'roughness',
                self.LINKS_INPUT
            )
        )
        
        
        # ADD A FILE DESTINATION
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Epanet scenario file'),
                fileFilter='*.scn'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        RUN PROCESS
        """
        
        # INPUT        
        
        links = self.parameterAsSource(parameters, self.LINKS_INPUT, context)
        dfield = self.parameterAsString(parameters, self.D_FIELD_INPUT, context)
        rfield = self.parameterAsString(parameters, self.R_FIELD_INPUT, context)
        
        # OUTPUT
        
        scnfile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        
        # WRITE FILE
        
        cnt = 0
        file = open(scnfile, 'w')
        file.write('; File generated automatically by nettools.py \n')
        file.write('[DIAMETERS] \n')
        file.write(';Pipe    Diameter \n')
        
        
        for feature in links.getFeatures():
            if feature['type'] in ['PIPE', 'CVPIPE']:
                cnt += 1    
                file.write('{}    {} \n'.format(feature['id'],feature[dfield]))
 
        file.write(' \n')
        file.write('[ROUGHNESS] \n')
        file.write(';Pipe    Roughness \n')
        
        for feature in links.getFeatures():
            if feature['type'] in ['PIPE', 'CVPIPE']:
                file.write('{}    {} \n'.format(feature['id'],feature[rfield]))
        
        file.close()
        
        msg = 'Pipe diameter and roughness add: {}.'.format(cnt)
        feedback.pushInfo(msg)

        # PROCCES CANCELED
        
        if feedback.isCanceled():
            return {}
        
        # OUTPUT

        return {self.OUTPUT: scnfile}
