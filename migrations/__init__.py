try:
    from Products.CMFPlone import MigrationTool
    import beta2_beta3, beta1_beta2, alpha_beta
except:
    print "Ack.  MigrationTool could not be found"

def registerMigrations():
    # so the basic concepts is you put  a bunch of migrations is here

    MigrationTool.registerUpgradePath( '1.0alpha4' ,
                                       '1.0beta1',
                                       alpha_beta.migrate )
                                       
    MigrationTool.registerUpgradePath( '1.0beta1',
                                       '1.0beta2',
                                       beta1_beta2.onetwo )
                                       
    MigrationTool.registerUpgradePath( '1.0beta2',
                                       '1.0beta3',
                                       beta2_beta3.twothree )

