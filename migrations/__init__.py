
try:
    from Products.CMFPlone import MigrationTool
    import rc2_final, rc1_rc2, beta3_rc1, beta2_beta3, beta1_beta2, alpha_beta
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

    MigrationTool.registerUpgradePath( '1.0beta3',
                                       '1.0rc1',
                                       beta3_rc1.threerc1 )
    
    MigrationTool.registerUpgradePath( '1.0rc1',
                                       '1.0rc2',
                                       rc1_rc2.rc1rc2 )
                                       
    MigrationTool.registerUpgradePath( '1.0rc2',
                                       '1.0',
                                       rc2_final.rc2Final )
                                       
