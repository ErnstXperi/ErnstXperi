from core_api.stb.assertions import CoreAssertions
from tools.logger.logger import Logger
from set_top_box.test_settings import Settings
from set_top_box.conf_constants import HydraBranches


class AccountLockedPage(CoreAssertions):
    __log = Logger(__name__)

    def cancel_device(self):
        """
        Cancel Device consists of 2 actions:
            1. Update device details in PPS - set "status": "cancelled"
            2. Send tveServiceCancel
        """
        self.log.info("Cancelling device...")
        self.pps_api_helper.update_device_details(Settings.ca_device_id, {"status": "cancelled"})
        return self.iptv_prov_api.tve_service_cancel(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn), Settings.tsn)

    def re_activate_device(self):
        """
        To re-activate a device, you need to update status in device details
        """
        self.log.info("Re-activating device...")
        self.pps_api_helper.update_device_details(Settings.ca_device_id, {"status": "active"})

    def __handling_hydra_after_receiving_device_cancel(self, timeout=10):
        """
        This implementation works for managed (except Technicolor box with hospitality = Yes) devices only.

        The Hydra app may be closed if account lockout happened when some other apps are open
        e.g. YouTube or Google Play, etc., so need to start it in this case.

        Args:
            timeout (int): time in seconds, waiting for deviceStatusUpdateNotification
        """
        self.pause(timeout, "Waiting for the account cancellation request to reach the box",
                   is_negative_time_to_0=True)
        self.handling_hydra_app_after_exit(Settings.app_package)

    def managing_hydra_app_after_canceling_acc(self, timeout=10):
        """
        This implementation works for managed (except Technicolor box) devices only.

        The Hydra app may be closed if account lockout happened when some other apps are open
        e.g. YouTube or Google Play, etc., so need to start it in this case.

        Args:
            timeout (int): time in seconds, waiting for deviceStatusUpdateNotification
        """
        self.__log.info("Managing the Hydra app after cancelling account")
        self.__handling_hydra_after_receiving_device_cancel(timeout)
        self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_SCREEN, 90000)

    def managing_hydra_app_after_canceling_re_activating_acc(self, timeout=10, is_re_activated=True):
        """
        This implementation works for managed (except Technicolor box) devices only.

        This method may come in handy when device cancelling and re-activating is made
        during the box being in the disconnected state.

        The Hydra app may be closed if account lockout happened when some other apps are open
        e.g. YouTube or Google Play, etc., so need to start it in this case.

        Args:
            timeout (int): time in seconds, waiting for deviceStatusUpdateNotification
            is_re_activated (bool): if True, handling selection after account re-activation
                                    if False, handling selection with cancelled account
        """
        self.__log.info("Managing the Hydra app after cancelling and re-activating account")
        self.__handling_hydra_after_receiving_device_cancel(timeout)
        if is_re_activated:
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 180000)
        else:
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_SCREEN, 90000)

    def managing_hydra_app_after_box_reboot(self, is_account_locked=True):
        """
        Handling managed boxes (except Technicolor box) after box reboot.
        Box reboot should be made before calling this function.

        Args:
            is_account_locked (bool): True - Account Locked should be shown, False - Home screen should be seen
        """
        self.__log.info("Managing the Hydra app after box reboot")
        if self.acc_locked_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE not in self.view_mode():
            self.handling_hydra_app_after_exit(Settings.app_package, after_reboot=True)
        if is_account_locked:
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_SCREEN, 90000)
        else:
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 180000)

    def managing_sign_in_after_acc_status_change(self, is_re_activated=True):
        """
        Handling managed boxes after selecting Sign In in the Account Locked screen.
        Method applicable when Account Locked screen is shown and need to select the Sign In option on it.

        Args:
            is_re_activated (bool): if True, handling selection after account re-activation
                                    if False, handling selection with cancelled account
        """
        self.__log.info(f"Managing the Hydra app after selecting Sign In; account active = {is_re_activated}")
        self.select_menu(self.acc_locked_labels.LBL_ACC_LOCKED_SIGN_IN_OPT)
        if is_re_activated:
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 90000)
        else:
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_SCREEN, 16000)

    def verify_reset_screen(self, tester):
        # TODO
        # This method is a duplicated of verify_if_account_locked_shown() which is located in assertions.py,
        # so need to replace usage of this method with verify_if_account_locked_shown().
        # verify_if_account_locked_shown() covers all platforms.
        self.log.info("checking for screen")
        self.wait_for_screen_ready()
        if Settings.is_technicolor():
            self.log.info("Goes to hospitality screen")
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOSPITALITY_SCREEN, timeout=50000)
            self.verify_view_mode(self.acc_locked_labels.LBL_HOSPITALITY_SCREEN_VIEW_MODE)
        else:
            self.log.info("Goes to account locked screen")
            # refresh is needed here to get the latest dump
            self.screen.refresh()
            dump_after = self.screen.get_screen_dump_item()
            self.__log.info(f"getting dump for the page = {dump_after}")
            self.wait_for_screen_ready(self.acc_locked_labels.LBL_SIGN_IN_SCREEN_VIEW_MODE, 90000)
            self.press_ok_button()
            dump_after_again = self.screen.get_screen_dump_item()
            self.__log.info(f"getting dump for the page = {dump_after_again}")
            self.wait_for_screen_ready(self.acc_locked_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE, 90000)
