from datetime import datetime

import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.account_locked.conftest import setup_account_locked, cleanup_re_activate_and_sign_in,\
    cleanup_enabling_internet
from set_top_box.conf_constants import FeaturesList, HydraBranches
from set_top_box.client_api.home.conftest import rebind_hsn, cleanup_ftux
from set_top_box.shared_context import ExecutionContext


# @pytest.mark.account_locked
@pytest.mark.notapplicable(Settings.is_devhost(), "Feature requires app restart")
@pytest.mark.notapplicable(Settings.is_external_mso(), "IptvProvisioningApi is not allowed to be used on MSOs like RCN etc.")
@pytest.mark.usefixtures("cleanup_enabling_internet")
@pytest.mark.usefixtures("setup_account_locked")
@pytest.mark.usefixtures("cleanup_re_activate_and_sign_in")
@pytest.mark.timeout(Settings.timeout)
class TestAccountLockedScreen(object):
    """
    Managed boxes (excluding Technicolor with hospitality = Yes):
        The Hydra app restarts to the Account Locked screen
    Technicolor box with hospitality = Yes:
        the box reboots to the Hospitality screen
    Unmanaged boxes:
        Account Locked overlay shown over the Home screen in the Hydra app
    """

    # @pytest.mark.hospitality
    # @pytest.mark.fasu
    def test_4863028_5314172_fasu_acc_locked_screen_title(self):
        """
        Verify Account Lockout screen title

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863028
            https://testrail.tivo.com//index.php?/cases/view/5314172
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()

    # @pytest.mark.hospitality
    def test_4863052_from_active_to_cancelled_when_turned_off(self):
        """
        Verify user is navigated to Account Locked screen on first sign in
        while rebooting the device with user's account locked

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863052
        """
        # Service Login feature specific behavior (serviceLogin may not be called in some cases) DRD:
        # https://confluence.corp.xperi.com/pages/viewpage.action?spaceKey=EngrTeams&title=ServiceLogin+frequency+control
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_13):
            self.acc_locked_page.pause(33 * 60, "Waiting before starting the test for sign in to happen after reboot")
        self.acc_locked_page.reboot_device()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.reconnect_dut_after_reboot(180)
        self.acc_locked_page.managing_hydra_app_after_box_reboot(is_account_locked=True)
        self.acc_locked_assertions.verify_if_account_locked_shown(offline=True)

    # @pytest.mark.hospitality
    @pytest.mark.msofocused_solutions
    @pytest.mark.xray('FRUM-48551', 'FRUM-48547')
    def test_4863054_acc_locked_from_cancelled_to_active(self):
        """
        Verify user is navigated to Home screen using Sign In option
        in Account Locked screen after account unlocked

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863054

        Xray:
            https://jira.xperi.com/browse/FRUM-834 (Account Locked -> from Cancelled to Active - Sign In Option)
            https://jira.xperi.com/browse/FRUM-48553 (Cancel Account -> Hospitality -> Initial Entry)
            https://jira.xperi.com/browse/FRUM-48547 (Cancel Account -> Hospitality -> Re-activate -> Continue)
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        self.acc_locked_page.re_activate_device()
        self.acc_locked_page.managing_sign_in_after_acc_status_change(is_re_activated=True)
        self.acc_locked_assertions.verify_view_mode(self.acc_locked_labels.LBL_HOME_SCREEN_VIEW_MODE)

    # @pytest.mark.hospitality
    def test_4863059_press_home_btn_on_acc_locked_screen(self):
        """
        Verify HOME button behavior on Account Locked screen

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863059
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        self.acc_locked_assertions.press_bail_button_and_verify_if_account_locked_shown()

    # @pytest.mark.hospitality
    def test_4863024_select_sign_in_opt_acc_locked_screen_locked_acc(self):
        """
        Verify user is staying in Account Locked screen on selecting Sign In option with account locked

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863024
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        self.acc_locked_page.managing_sign_in_after_acc_status_change(is_re_activated=False)
        self.acc_locked_assertions.verify_if_account_locked_shown(before_restart=False)

    # @pytest.mark.hospitality
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Account Locked overlay does not have such option")
    def test_4863034_select_network_settings_opt_acc_locked_screen(self):
        """
        Verify user is navigating to Network & Internet Android menu on selecting
        Network Settings action in Account Locked screen

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863034
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        self.acc_locked_page.select_menu(self.acc_locked_labels.LBL_ACC_LOCKED_NETWORK_SETTINGS_OPT)
        self.acc_locked_assertions.verify_device_settings_screen_opened(self.system_labels.LBL_NETWORK_AND_INTERNET)

    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Account Locked overlay does not have such option")
    @pytest.mark.notapplicable(
        (Settings.is_technicolor() or Settings.is_jade() or Settings.is_jade_hotwire()) and ExecutionContext.service_api
        .get_feature_status(FeaturesList.HOSPITALITY, True), "Hospitality screen does not have such option")
    def test_4863048_select_device_sys_info_opt_acc_locked_screen(self):
        """
        Verify user is navigating to About Android menu on selecting
        Device System Information action in Account Locked screen

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863048
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        self.acc_locked_page.select_menu(self.acc_locked_labels.LBL_ACC_LOCKED_DEVICE_SYS_INFO_OPT)
        self.acc_locked_assertions.verify_device_settings_screen_opened(self.system_labels.LBL_DEVICE_SYS_INFO)

    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Account Locked overlay does not have such option")
    @pytest.mark.notapplicable(
        (Settings.is_technicolor() or Settings.is_jade() or Settings.is_jade_hotwire()) and ExecutionContext.service_api
        .get_feature_status(FeaturesList.HOSPITALITY, True), "Hospitality screen does not have such option")
    def test_4863029_select_hydra_app_sys_info_opt_acc_locked_screen(self):
        """
        Verify user is navigating to TiVo System Info screen on selecting
        TiVo System Information action in Account Locked screen

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/4863029
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        self.acc_locked_page.select_menu(self.acc_locked_labels.LBL_ACC_LOCKED_TIVO_SYS_INFO_OPT)
        self.acc_locked_assertions.verify_view_mode(self.acc_locked_labels.LBL_SYSTEM_INFO_SCREEN_VIEW_MODE)

    # @pytest.mark.disconnected_state
    # @pytest.mark.fasu
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    def test_11124140_fasu_phase2_disconnect_cancel_wait_7_min_connect(self):
        """
        Verify TiVo app behavior in Disconnected state (soft disconnect)
        when the Disconnected time is more then Retry Policy time

        Disconnect - Cancel Device - wait 7 mins - Connect - wait 3 mins - deviceCancel notification

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/11124140
        """
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.acc_locked_page.cancel_device()
        init_time = datetime.now()
        self.home_assertions.verify_connected_disconnected_state_happened(error_code=self.home_labels.LBL_ERROR_CODE_C228)
        cur_time = datetime.now()
        # Due to new feature introduced in Hydra 1.16 https://jira.xperi.com/browse/IPTV-22111
        waiting_time = 310 if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_16) else 420
        self.acc_locked_page.pause(waiting_time - (cur_time - init_time).seconds, "Staying in the disconnected state a bit",
                                   is_negative_time_to_0=True)
        right_before_enabling_inet = datetime.now()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)
        internet_enabled_time = (datetime.now() - right_before_enabling_inet).total_seconds()
        wait_device_cancel_notification = 293 - internet_enabled_time \
            if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_16) else 183
        self.acc_locked_page.managing_hydra_app_after_canceling_acc(timeout=wait_device_cancel_notification)
        self.acc_locked_assertions.verify_if_account_locked_shown()

    # @pytest.mark.disconnected_state
    # @pytest.mark.fasu
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    def test_5603439_fasu_phase2_disconnect_cancel_activate_connect_wait_7_mins(self):
        """
        Verify TiVo app behavior in Disconnected state (soft disconnect)
        when the Disconnected time is more then Retry Policy time

        Disconnect - Cancel Device - Re-activate Device - wait 7 mins - Connect - wait 3 mins - deviceCancel notification

        Expected behavior according to https://jira.tivo.com/browse/IPTV-17359

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/5603439
        """
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.acc_locked_page.cancel_device()
        init_time = datetime.now()
        self.acc_locked_page.re_activate_device()
        self.home_assertions.verify_connected_disconnected_state_happened(error_code=self.home_labels.LBL_ERROR_CODE_C228)
        cur_time = datetime.now()
        # Due to new feature introduced in Hydra 1.16 https://jira.xperi.com/browse/IPTV-22111
        waiting_time = 310 if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_16) else 420
        self.acc_locked_page.pause(waiting_time - (cur_time - init_time).seconds, "Staying in the disconnected state a bit",
                                   is_negative_time_to_0=True)
        right_before_enabling_inet = datetime.now()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)
        internet_enabled_time = (datetime.now() - right_before_enabling_inet).total_seconds()
        wait_device_cancel_notification = 293 - internet_enabled_time \
            if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_16) else 183
        self.acc_locked_page.managing_hydra_app_after_canceling_re_activating_acc(timeout=wait_device_cancel_notification,
                                                                                  is_re_activated=True)
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)

    @pytest.mark.usefixtures("cleanup_re_activate_and_sign_in")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_external_mso())
    @pytest.mark.frumos_15
    def test_tvescancel_and_reset(self):
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.iptv_prov_api.reset_device(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn), Settings.tsn)
        # Modal errors after receiving device reset notification should be considered as product defect
        # Behavior for Managed boxes after receiving device reset:
        #   Hydra app is self closed and it loads to the Account Locked screen after starting
        self.home_page.confirm_modal_ui_errors()
        self.acc_locked_page.verify_reset_screen(self)
        self.home_page.confirm_modal_ui_errors()
        if not self.service_api.get_authentication_license_plate_url(True):
            self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                        Settings.pcid)
        else:
            self.home_page.bind_license(self)
        self.acc_locked_page.re_activate_device()
        self.home_page.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 180000)

    @pytest.mark.usefixtures("cleanup_re_activate_and_sign_in")
    @pytest.mark.usefixtures("cleanup_ftux")
    @pytest.mark.xray('FRUM-62298')
    @pytest.mark.sol_provisioning
    def test_frum_62298_url_customer_support(self):
        """
        FRUM-62298
        verify account locked message after suspend/cancel the device and reboot the device
        """
        self.home_page.back_to_home_short()
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        branding_value_cancel = self.api.branding_ui()
        if not branding_value_cancel:
            pytest.fail("Failed to get Branding UI Value")
        self.acc_locked_assertions.verify_account_locked_message(branding_value_cancel)
