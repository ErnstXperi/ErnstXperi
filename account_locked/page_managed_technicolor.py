from set_top_box.client_api.account_locked.page import AccountLockedPage as DefaultHomePg
from tools.logger.logger import Logger
from set_top_box.conf_constants import FeaturesList
from set_top_box.test_settings import Settings


class ManagedTechnicolorAccountLockedPage(DefaultHomePg):
    """
    Technicolor boxes:
        - Sapphire
        - Jade
        - Jade Hotwire
    """
    __log = Logger(__name__)

    def managing_hydra_app_after_canceling_acc(self, timeout=10):
        """
        This implementation works for Technicolor boxes only.

        Technicolor boxes behave themselves differently, if hospitality = Yes.
        Once Cancel Device made, Android OS reboots and then the Hydra app shows the Hospitality screen.

        Args:
            timeout (int): time in seconds, waiting for DeviceClearNotification
        """
        self.__log.info("Managing the Hydra app after cancelling account")
        is_hospitality = self.service_api.get_feature_status(FeaturesList.HOSPITALITY)
        if is_hospitality is None:
            raise AssertionError(f"Failed to get feature status for {FeaturesList.HOSPITALITY}")
        if is_hospitality:
            self.pause(timeout, "Waiting for the deviceClear notification to reach the box",
                       is_negative_time_to_0=True)
            self.reconnect_dut_after_reboot(180)  # once the box gets the notification, it starts rebooting
            self.handling_hydra_app_after_exit(Settings.app_package)
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOSPITALITY_SCREEN, 200000)
        else:
            # Account Locked screen will be shown if hospitality feature is off with cancelled account
            super().managing_hydra_app_after_canceling_acc(timeout)

    def managing_hydra_app_after_canceling_re_activating_acc(self, timeout=10, is_re_activated=True):
        """
        This implementation works for Technicolor boxes only.

        This method may come in handy when device cancelling and re-activating is made
        during the box being in the disconnected state.

        Args:
            timeout (int): time in seconds, waiting for DeviceClearNotification
            is_re_activated (bool): if True, handling selection after account re-activation
                                    if False, handling selection with cancelled account
        """
        self.__log.info("Managing the Hydra app after cancelling and re-activating account")
        is_hospitality = self.service_api.get_feature_status(FeaturesList.HOSPITALITY)
        if is_hospitality is None:
            raise AssertionError(f"Failed to get feature status for {FeaturesList.HOSPITALITY}")
        self.pause(timeout, "Waiting for the account cancellation request to reach the box")
        if is_hospitality:
            self.handling_hydra_app_after_exit(Settings.app_package)
            if is_re_activated:
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 200000)
            else:
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOSPITALITY_SCREEN, 200000)
        else:
            # Account Locked screen will be shown if hospitality feature is off with cancelled account
            super().managing_hydra_app_after_canceling_re_activating_acc(timeout, is_re_activated)

    def managing_hydra_app_after_box_reboot(self, is_account_locked=True):
        """
        Handling Technicolor box with hospitality = Yes after box reboot.
        Box reboot should be made before calling this function.

        Note:
            When account cancelled while box is off, Hydra app gets cancelled status on sign in and box itself makes
            reboot.

        Args:
            is_account_locked (bool): True - Hospitality screen should be shown, False - Home screen should be seen
        """
        self.__log.info("Managing the Hydra app after box reboot")
        is_hospitality = self.service_api.get_feature_status(FeaturesList.HOSPITALITY)
        if is_hospitality is None:
            raise AssertionError(f"Failed to get feature status for {FeaturesList.HOSPITALITY}")
        if is_hospitality:
            self.reconnect_dut_after_reboot(180)  # box reboot after reaching sing in, since Hydra got notification
            self.handling_hydra_app_after_exit(Settings.app_package)
            if is_account_locked:
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOSPITALITY_SCREEN, 200000)
            else:
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 200000)
        else:
            # Account Locked screen will be shown if hospitality feature is off with cancelled account
            super().managing_hydra_app_after_box_reboot(is_account_locked)

    def managing_sign_in_after_acc_status_change(self, is_re_activated=True):
        """
        Handling managed Technicolor box with hospitality = Yes after selecting Continue in the Hospitality screen.

        Args:
            is_re_activated (bool): if True, handling selection after account re-activation
                                    if False, handling selection with cancelled account
        """
        self.__log.info(f"Managing the Hydra app after selecting Continue; account active = {is_re_activated}")
        is_hospitality = self.service_api.get_feature_status(FeaturesList.HOSPITALITY)
        if is_hospitality is None:
            raise AssertionError(f"Failed to get feature status for {FeaturesList.HOSPITALITY}")
        if is_hospitality:
            self.select_menu(self.acc_locked_labels.LBL_HOSPITALITY_CONTINUE)
            if is_re_activated:
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 200000)
            else:
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOSPITALITY_SCREEN, 16000)
        else:
            # Account Locked screen will be shown if hospitality feature is off with cancelled account
            super().managing_sign_in_after_acc_status_change(is_re_activated)
