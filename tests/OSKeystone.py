from OS import OSKeystone

osKSAuth = OSKeystone.OSKeystoneAuth(filename="configs/config_admin.json")
session = osKSAuth.createKeyStoneSession()

osKSUser = OSKeystone.OSKeystoneUser(session=session)
osKSRole = OSKeystone.OSKeystoneRoles(session=session)

osKSRole.getUserRole(user_id="f5f8677373fa4c4e8331ba69f5814bfa")