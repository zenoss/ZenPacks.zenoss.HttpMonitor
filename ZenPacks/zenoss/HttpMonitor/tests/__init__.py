##############################################################################
#
# Copyright (C) Zenoss, Inc. 2022, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging
import os
import sys
from xml.sax.handler import ContentHandler
from transaction._transaction import Transaction
from Products.Five import zcml
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenRelations.ImportRM import ImportRM, SpoofedOptions

log = logging.getLogger('zen.HttpMonitor')


ZENPACK_DEPENDENCIES = (
    'ZenPacks.zenoss.HttpMonitor',
)

DEVICECLASS_DEPENDENCIES = (
    '/HTTP',
)

EVENTCLASS_DEPENDENCIES = (
    '/Perf',
    '/Status',
)

REPORTCLASS_DEPENDENCIES = tuple()


class MinimalImportRM(ImportRM):
    """
    A minimal ImportRM which doesn't log in or load ZenPack ZCML.
    """

    def __init__(self, app):
        self.log = logging.getLogger('zen.MinimalImportRM')
        self.app = app
        ContentHandler.__init__(self)
        self.options = SpoofedOptions()
        self.dataroot = None
        self.getDataRoot()


class ModelTestCase(BaseTestCase):
    plugins = None
    results_cache = None

    def afterSetUp(self):
        super(ModelTestCase, self).afterSetUp()

        # BaseTestCast.afterSetUp already hides transaction.commit. So we also
        # need to hide transaction.abort.
        self._transaction_abort = Transaction.abort
        Transaction.abort = lambda *x: None

        # Install a minimal version of the ZenPack.
        map(self.dmd.Devices.createOrganizer, (DEVICECLASS_DEPENDENCIES))
        map(self.dmd.Events.createOrganizer, (EVENTCLASS_DEPENDENCIES))
        map(self.dmd.Reports.createOrganizer, (REPORTCLASS_DEPENDENCIES))

        self.dmd.REQUEST = None

        im = MinimalImportRM(self.app)

        for zenpack in ZENPACK_DEPENDENCIES:
            __import__(zenpack)
            zp_module = sys.modules[zenpack]

            objects_file = '%s/objects/objects.xml' % (
                zp_module.__path__[0])

            if os.path.isfile(objects_file):
                log.info('Loading objects for %s.', zenpack)
                im.loadObjectFromXML(objects_file)

        # Required to prevent erroring out when trying to define viewlets in
        # ../browser/configure.zcml.
        import zope.viewlet
        zcml.load_config('meta.zcml', zope.viewlet)

        import ZenPacks.zenoss.HttpMonitor
        zcml.load_config('configure.zcml', ZenPacks.zenoss.HttpMonitor)

        # self.applyDataMap = ApplyDataMap()._applyDataMap

        self.plugins = {}
        self.results_cache = {}

    def beforeTearDown(self):
        if hasattr(self, '_transaction_abort'):
            Transaction.abort = self._transaction_abort
