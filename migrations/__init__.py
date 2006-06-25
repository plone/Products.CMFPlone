from Products.CMFPlone import MigrationTool

def executeMigrations():
    import v2_1, v2_5, v3_0

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations is here

    MigrationTool.registerUpgradePath('2.1',
                                      '2.1.1',
                                      v2_1.final_two11.final_two11)

    MigrationTool.registerUpgradePath('2.1.1',
                                      '2.1.2-rc1',
                                      v2_1.two11_two12.two11_two12rc1)

    MigrationTool.registerUpgradePath('2.1.2-rc1',
                                      '2.1.2-rc2',
                                      null)

    MigrationTool.registerUpgradePath('2.1.2-rc2',
                                      '2.1.2',
                                      v2_1.two11_two12.two12rc2_two12)

    MigrationTool.registerUpgradePath('2.1.2',
                                      '2.1.3-rc1',
                                      v2_1.two12_two13.two12_two13)

    MigrationTool.registerUpgradePath('2.1.3-rc1',
                                      '2.1.3',
                                      null)

    MigrationTool.registerUpgradePath('2.1.3',
                                      '2.5-alpha1',
                                      v2_5.alphas.two5_alpha1)

    MigrationTool.registerUpgradePath('2.5-alpha1',
                                      '2.5-alpha2',
                                      v2_5.alphas.alpha1_alpha2)

    MigrationTool.registerUpgradePath('2.5-alpha2',
                                      '2.5-beta1',
                                      v2_5.betas.alpha2_beta1)

    MigrationTool.registerUpgradePath('2.5-beta1',
                                      '2.5-beta2',
                                      v2_5.betas.beta1_beta2)

    MigrationTool.registerUpgradePath('2.5-beta2',
                                      '2.5-rc1',
                                      v2_5.rcs.beta2_rc1)

    MigrationTool.registerUpgradePath('2.5-rc1',
                                      '2.5-rc2',
                                      null)

    MigrationTool.registerUpgradePath('2.5-rc2',
                                      '2.5-rc3',
                                      null)

    MigrationTool.registerUpgradePath('2.5-rc3',
                                      '2.5',
                                      null)

    MigrationTool.registerUpgradePath('2.5',
                                      '3.0 (SVN/UNRLEASED)',
                                      v3_0.alphas.three0_alpha1)
