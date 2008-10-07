from Products.CMFPlone.MigrationTool import registerUpgradePath

def executeMigrations():
    import v2_1, v2_5, v3_0, v3_1

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # So the basic concepts is you put a bunch of migrations in here.

    # If False is specified as the actual migration function, this means
    # this upgrade path is not available anymore.

    # Plone 1.0

    registerUpgradePath('1.0', '1.0.1', False)
    registerUpgradePath('1.0.1', '1.0.2', False)
    registerUpgradePath('1.0.2', '1.0.3', False)
    registerUpgradePath('1.0.3', '1.0.4', False)
    registerUpgradePath('1.0.4', '1.0.5', False)

    # Plone 2.0

    registerUpgradePath('1.0.5', '2.0-beta2', False)
    registerUpgradePath('2.0-beta2', '2.0-beta3', False)
    registerUpgradePath('2.0-beta3', '2.0-rc2', False)
    registerUpgradePath('2.0-rc2', '2.0-rc3', False)
    registerUpgradePath('2.0-rc3', '2.0-rc4', False)
    registerUpgradePath('2.0-rc4', '2.0-rc5', False)
    registerUpgradePath('2.0-rc5', '2.0', False)
    registerUpgradePath('2.0', '2.0-rc6', False)
    registerUpgradePath('2.0-rc6', '2.0-final', False)

    # Plone 2.0.x

    registerUpgradePath('2.0-final', '2.0.1', False)
    registerUpgradePath('2.0.1', '2.0.2', False)
    registerUpgradePath('2.0.2', '2.0.3', False)
    registerUpgradePath('2.0.3', '2.0.4', False)
    registerUpgradePath('2.0.4', '2.0.5-rc1', False)
    registerUpgradePath('2.0.5-rc1', '2.0.5-rc2', False)
    registerUpgradePath('2.0.5-rc2', '2.0.5', False)

    # Plone 2.1

    registerUpgradePath('2.0.5', '2.1-alpha1', False)
    registerUpgradePath('2.1-alpha1', '2.1-alpha2', False)
    registerUpgradePath('2.1-alpha2', '2.1-beta1', False)
    registerUpgradePath('2.1-beta1', '2.1-beta2', False)
    registerUpgradePath('2.1-beta2', '2.1-rc1', False)
    registerUpgradePath('2.1-rc1', '2.1-rc2', False)
    registerUpgradePath('2.1-rc2', '2.1-rc3', False)
    registerUpgradePath('2.1-rc3', '2.1', False)

    # Currently supported migrations

    # Plone 2.1.x

    registerUpgradePath('2.1', '2.1.1', v2_1.final_two11.final_two11)
    registerUpgradePath('2.1.1', '2.1.2-rc1', v2_1.two11_two12.two11_two12rc1)

    registerUpgradePath('2.1.2-rc1', '2.1.2-rc2', null)
    registerUpgradePath('2.1.2-rc2', '2.1.2', v2_1.two11_two12.two12rc2_two12)
    registerUpgradePath('2.1.2', '2.1.3-rc1', v2_1.two12_two13.two12_two13)

    registerUpgradePath('2.1.3-rc1', '2.1.3', null)
    registerUpgradePath('2.1.3', '2.1.4-rc1', null)

    registerUpgradePath('2.1.4-rc1', '2.1.4', null)

    # Plone 2.5

    registerUpgradePath('2.1.4', '2.5-alpha1', v2_5.alphas.two5_alpha1)

    registerUpgradePath('2.5-alpha1', '2.5-alpha2', v2_5.alphas.alpha1_alpha2)
    registerUpgradePath('2.5-alpha2', '2.5-beta1', v2_5.betas.alpha2_beta1)

    registerUpgradePath('2.5-beta1', '2.5-beta2', v2_5.betas.beta1_beta2)
    registerUpgradePath('2.5-beta2', '2.5-rc1', v2_5.rcs.beta2_rc1)

    registerUpgradePath('2.5-rc1', '2.5-rc2', null)
    registerUpgradePath('2.5-rc2', '2.5-rc3', null)
    registerUpgradePath('2.5-rc3', '2.5', null)

    # Plone 2.5.x

    registerUpgradePath('2.5', '2.5.1-rc1', v2_5.final_two51.final_two51)
    
    registerUpgradePath('2.5.1-rc1', '2.5.1', v2_5.final_two51.final_two51)
    registerUpgradePath('2.5.1', '2.5.2-rc1', v2_5.two51_two52.two51_two52)

    registerUpgradePath('2.5.2-rc1', '2.5.2', null)
    registerUpgradePath('2.5.2', '2.5.3-rc1', v2_5.two52_two53.two52_two53)

    registerUpgradePath('2.5.3-rc1', '2.5.3-final', null)

    registerUpgradePath('2.5.3-final', '2.5.4-final',
                        v2_5.two53_two54.two53_two54)
    registerUpgradePath('2.5.4-final', '2.5.4-2', null)
    registerUpgradePath('2.5.4-2', '2.5.5', null)

    # Plone 3.0

    registerUpgradePath('2.5.5', '3.0-alpha1', v3_0.alphas.three0_alpha1)

    registerUpgradePath('3.0-alpha1', '3.0-alpha2', v3_0.alphas.alpha1_alpha2)
    registerUpgradePath('3.0-alpha2', '3.0-beta1', v3_0.alphas.alpha2_beta1)

    registerUpgradePath('3.0-beta1', '3.0-beta2', v3_0.betas.beta1_beta2)
    registerUpgradePath('3.0-beta2', '3.0-beta3', v3_0.betas.beta2_beta3)
    registerUpgradePath('3.0-beta3', '3.0-rc1', v3_0.betas.beta3_rc1)

    registerUpgradePath('3.0-rc1', '3.0-rc2', v3_0.rcs.rc1_rc2)
    registerUpgradePath('3.0-rc2', '3.0', v3_0.rcs.rc2_final)

    # Plone 3.0.x

    registerUpgradePath('3.0', '3.0.1', v3_0.final_three0x.final_three01)
    registerUpgradePath('3.0.1', '3.0.2', v3_0.final_three0x.three01_three02)
    registerUpgradePath('3.0.2', '3.0.3', null)
    registerUpgradePath('3.0.3', '3.0.4', v3_0.final_three0x.three03_three04)
    registerUpgradePath('3.0.4', '3.0.5', v3_0.final_three0x.three04_three05)
    registerUpgradePath('3.0.5', '3.0.6', null)

    # Plone 3.1
    registerUpgradePath('3.0.6', '3.1-beta1', v3_1.betas.three0_beta1)
    registerUpgradePath('3.1-beta1', '3.1-rc1', null)
    registerUpgradePath('3.1-rc1', '3.1', null)

    # Plone 3.1.x
    registerUpgradePath('3.1', '3.1.1', null)
    registerUpgradePath('3.1.1', '3.1.2', v3_1.final_three1x.three11_three12)
    registerUpgradePath('3.1.2', '3.1.3', null)
    registerUpgradePath('3.1.3', '3.1.4', null)
    registerUpgradePath('3.1.4', '3.1.5', v3_1.final_three1x.three14_three15)
    registerUpgradePath('3.1.5', '3.1.5.1', null)
    registerUpgradePath('3.1.5.1', '3.1.6', null)
    registerUpgradePath('3.1.6', '3.1.7 (svn/unreleased)', null)

