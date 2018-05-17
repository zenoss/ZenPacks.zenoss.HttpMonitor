##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPack, ZenPackDataSourceMigrateBase

import logging

LOG = logging.getLogger("zen.migrate")


class RemoveOldGraphDefinition(ZenPackDataSourceMigrateBase):
    """
    Remove GraphDefinition ids for old versions of ZenPack.
    """
    version = Version(3, 0, 0)
    def migrate(self, pack):
        LOG.info("Attempt to remove old Graph Definition.")
        try:
            httpmonit = pack.dmd.Devices.HTTP
        except AttributeError:
            return

        templates = httpmonit.getRRDTemplates()
        for template in templates:
            if template.id == "HttpMonitor":
                LOG.info("HttpMonitor remove old Graph Definition")
                for obj in template.graphDefs.objectIds():
                    if obj == "Size" or obj == "Time":
                        template.graphDefs._delObject(obj)

RemoveOldGraphDefinition()
