from Products.CMFPlone import MigrationTool

import one03_one04
import one02_one03
import one01_one02
import final_one_zero_one
import oneX_twoBeta2
import twoBeta2_twoBeta3

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # so the basic concepts is you put  a bunch of migrations is here

    MigrationTool.registerUpgradePath( '1.0',
                                       '1.0.1',
                                       final_one_zero_one.onezeroone )

    MigrationTool.registerUpgradePath( '1.0.1',
                                       '1.0.2',
                                       one01_one02.onezerotwo )

    MigrationTool.registerUpgradePath( '1.0.2',
                                       '1.0.3',
                                       one02_one03.onezerothree )

    MigrationTool.registerUpgradePath( '1.0.3',
                                       '1.0.4',
                                       one03_one04.onezerofour )

    MigrationTool.registerUpgradePath( '1.0.4',
                                       '1.0.5',
                                       null )

    #Migrations to Plone 2.0 require a External Method.
    #We will rework the migration tool

    #MigrationTool.registerUpgradePath( '1.0.5',
    #                                   '2.0-beta2',
    #                                   oneX_twoBeta2.oneX_twoBeta2)

    #MigrationTool.registerUpgradePath( '2.0-beta2',
    #                                  '2.0-beta3',
    #                                  twoBeta2_twoBeta3.twoBeta2_twoBeta3)

