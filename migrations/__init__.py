from Products.CMFPlone import MigrationTool

def executeMigrations():
    import v2_1, v2_5, v3_0

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # So the basic concepts is you put a bunch of migrations in here.

    # If False is specified as the actual migration function, this means
    # this upgrade path is not available anymore.

    MigrationTool.registerUpgradePath('1.0',
                                      '1.0.1',
                                      False)

    MigrationTool.registerUpgradePath('1.0.1',
                                      '1.0.2',
                                      False)

    MigrationTool.registerUpgradePath('1.0.2',
                                      '1.0.3',
                                      False)

    MigrationTool.registerUpgradePath('1.0.3',
                                      '1.0.4',
                                      False)

    MigrationTool.registerUpgradePath('1.0.4',
                                      '1.0.5',
                                      False)

    MigrationTool.registerUpgradePath('1.0.5',
                                      '2.0-beta2',
                                      False)

    MigrationTool.registerUpgradePath('2.0-beta2',
                                      '2.0-beta3',
                                      False)

    MigrationTool.registerUpgradePath('2.0-beta3',
                                      '2.0-rc2',
                                      False)

    MigrationTool.registerUpgradePath('2.0-rc2',
                                      '2.0-rc3',
                                      False)

    MigrationTool.registerUpgradePath('2.0-rc3',
                                      '2.0-rc4',
                                      False)

    MigrationTool.registerUpgradePath('2.0-rc4',
                                      '2.0-rc5',
                                      False)

    MigrationTool.registerUpgradePath('2.0-rc5',
                                      '2.0',
                                      False)

    MigrationTool.registerUpgradePath('2.0',
                                      '2.0-rc6',
                                      False)

    MigrationTool.registerUpgradePath('2.0-rc6',
                                      '2.0-final',
                                      False)

    MigrationTool.registerUpgradePath('2.0-final',
                                      '2.0.1',
                                      False)

    MigrationTool.registerUpgradePath('2.0.1',
                                      '2.0.2',
                                      False)

    MigrationTool.registerUpgradePath('2.0.2',
                                      '2.0.3',
                                      False)

    MigrationTool.registerUpgradePath('2.0.3',
                                      '2.0.4',
                                      False)

    MigrationTool.registerUpgradePath('2.0.4',
                                      '2.0.5-rc1',
                                      False)

    MigrationTool.registerUpgradePath('2.0.5-rc1',
                                      '2.0.5-rc2',
                                      False)

    MigrationTool.registerUpgradePath('2.0.5-rc2',
                                      '2.0.5',
                                      False)

    MigrationTool.registerUpgradePath('2.0.5',
                                      '2.1-alpha1',
                                      False)

    MigrationTool.registerUpgradePath('2.1-alpha1',
                                      '2.1-alpha2',
                                      False)

    MigrationTool.registerUpgradePath('2.1-alpha2',
                                      '2.1-beta1',
                                      False)

    MigrationTool.registerUpgradePath('2.1-beta1',
                                      '2.1-beta2',
                                      False)

    MigrationTool.registerUpgradePath('2.1-beta2',
                                      '2.1-rc1',
                                      False)

    MigrationTool.registerUpgradePath('2.1-rc1',
                                      '2.1-rc2',
                                      False)

    MigrationTool.registerUpgradePath('2.1-rc2',
                                      '2.1-rc3',
                                      False)

    MigrationTool.registerUpgradePath('2.1-rc3',
                                      '2.1',
                                      False)

    # Currently supported migrations

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
                                      '2.1.4-rc1',
                                      null)

    MigrationTool.registerUpgradePath('2.1.4-rc1',
                                      '2.1.4',
                                      null)

    MigrationTool.registerUpgradePath('2.1.4',
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
                                      '2.5.1-rc1',
                                      v2_5.final_two51.final_two51)

    MigrationTool.registerUpgradePath('2.5.1-rc1',
                                      '2.5.1',
                                      v2_5.final_two51.final_two51)

    MigrationTool.registerUpgradePath('2.5.1',
                                      '2.5.2-rc1',
                                      v2_5.two51_two52.two51_two52)

    MigrationTool.registerUpgradePath('2.5.2-rc1',
                                      '2.5.2',
                                      null)

    MigrationTool.registerUpgradePath('2.5.2',
                                      '2.5.3 (svn/unreleased)',
                                      null)

    MigrationTool.registerUpgradePath('2.5.3 (svn/unreleased)',
                                      '3.0-alpha1',
                                      v3_0.alphas.three0_alpha1)

    MigrationTool.registerUpgradePath('3.0-alpha1',
                                      '3.0-alpha2 (SVN/UNRELEASED)',
                                      v3_0.alphas.alpha1_alpha2)

