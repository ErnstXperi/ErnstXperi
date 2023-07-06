from hamcrest import assert_that, contains_string, is_

from core_api.stb.assertions import CoreAssertions
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger
from set_top_box.conf_constants import FeaturesList, BailButtonList


class AccountLockedAssertions(CoreAssertions):
    """
    Unmanaged devices on CableCo3 should be set to Licenseplate (default state)
    """
    __log = Logger(__name__)

    def verify_if_account_locked_shown(self, offline=False, before_restart=True):
        """
        Verifying if Account Locked is shown on Hydra UI.

        For Technicolor box with hospitality = Yes: Hospitality screen shown
        For Unmanaged Boxes with:
         - SAML Sign In: Account Locked overlay shown, and then signing in fails
         - Licenseplate: Account Locked overlay also is shown, but the app displays Account Locked screen after restart
        For Managed boxes: Account Locked screen shown

        Args:
            offline (bool): if account was cancelled while Hydra app was down,
                            applicable to unmanaged boxes only
            before_restart (bool): if True, checking if Account Locked overlay shown,
                                   if False, checking if SAML Sign In screen is shown if SAML domain,
                                             and checking Account Locked screen is shown if licenseplate,
                                   applicable to unmanaged boxes only
        """
        self.__log.info("Verifying if Account Locked screen displayed")
        is_hospitality = False
        if Settings.is_technicolor() or Settings.is_jade() or Settings.is_jade_hotwire():
            is_hospitality = self.service_api.get_feature_status(FeaturesList.HOSPITALITY)
            if is_hospitality is None:
                raise AssertionError(f"Failed to get feature status for {FeaturesList.HOSPITALITY}")
        if not self.screen.base.verify_foreground_app(Settings.app_package):
            raise AssertionError("Hydra app is not on foreground")
        if (Settings.is_technicolor() or Settings.is_jade() or Settings.is_jade_hotwire()) and is_hospitality:
            self.verify_view_mode(self.acc_locked_labels.LBL_HOSPITALITY_SCREEN_VIEW_MODE)
        elif Settings.is_managed():
            self.verify_view_mode(self.acc_locked_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE)
        else:
            # Unmanaged box
            if offline:
                self.acc_locked_page.managing_acc_locked_when_box_offline(is_just_started=False)
            else:
                if before_restart:
                    self.verify_overlay_title(self.acc_locked_labels.LBL_ACC_LOCKED_OVERLAY_TITLE)
                else:
                    if Settings.is_cc3():
                        # Unmanaged boxes with licenseplate go to Account Locked screen:
                        #  - When starting with cancelled account
                        #  - When selecting Sign In in the Account Locked screen while cancelled account
                        self.verify_view_mode(self.acc_locked_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE)
                    else:
                        # Unmanaged boxes with SAML Sign In go to Sign In screen (error overlays handled in
                        # managing_acc_locked_when_box_offline)
                        self.verify_view_mode(self.acc_locked_labels.LBL_SIGN_IN_SCREEN_VIEW_MODE)

    def press_bail_button_and_verify_if_account_locked_shown(self, bail_button=BailButtonList.HOME):
        """
        Press the bail button and verify if Account Locked screen is displayed
        Account Locked screen should be displayed before using this method

        Applicable to Managed devices and Fire TV (other unamanged devices do not have the Home button)

        Some bail buttons are not present on the remote of an unmanaged boxs (except restricted list e.g. home)
        """
        self.__log.info(f"Pressing the {bail_button} button and verifying that Account Locked stil displayed")
        if bail_button == BailButtonList.HOME:
            self.acc_locked_page.jump_to_home_xplatform(refresh=False)
        elif bail_button == BailButtonList.GUIDE:
            self.acc_locked_page.press_guide_button(refresh=False)
        elif bail_button == BailButtonList.BACK:
            self.acc_locked_page.press_back_button(refresh=False)
        else:
            raise ValueError(f"Handling the {bail_button} button is not implemented yet")
        self.acc_locked_page.pause(5, "Waiting a bit to see if transitioning happens (expected: no transition)")
        self.verify_if_account_locked_shown()

    def verify_device_settings_screen_opened(self, screen_title):
        """
        Verifying if the Device Settings screen opened

        Args:
            screen_title (str): Device Settings screen title
        """
        self.__log.info(f"Verifying if '{screen_title}' Device Settings screen opened")
        actual_title = self.system_page.get_device_settings_screen_title()
        ui_dump = self.screen.base.get_uiautomator_dump()
        assert_that(actual_title.lower(), is_(screen_title.lower()),
                    f"The Device screen title did not match, actual: {actual_title.lower()}, expected: {screen_title.lower()}"
                    f"\n\n UI Dump: \n\n{ui_dump}")

    def verify_account_locked_message(self, branding_value_cancel):
        self.log.info("Verifying Account Locked Message")
        cust_support_name = branding_value_cancel['urlCustomerSupport']["value"]
        phone_cus_num = branding_value_cancel['phoneCustomerSupportNumber']["value"]
        value = self.acc_locked_labels.LBL_ACCOUNT_LOCKED_MESSAGE[0].format(cust_support_name, phone_cus_num)
        expected_list = [value, self.acc_locked_labels.LBL_ACCOUNT_LOCKED_MESSAGE[1]]
        dump = self.screen.get_screen_dump_item('accountLockout')
        screen_dump_after = dump.get('textOnTop').values()
        for eachitem in screen_dump_after:
            if eachitem['text'] not in expected_list:
                assert_that(False, "Account locked message doesn't match")
