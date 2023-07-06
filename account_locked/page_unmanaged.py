from set_top_box.client_api.account_locked.page import AccountLockedPage as DefaultHomePg
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger
from set_top_box.conf_constants import HydraBranches


class UnmanagedAccountLockedPage(DefaultHomePg):
    __log = Logger(__name__)

    def __hydra_behavior_when_cancelled_activated_acc(self, is_re_activated=True):
        """
        Shows resulting screen with passed cancelled/activated account state.

        Args:
            is_re_activated (bool): if True, handling signing in after account re-activation
                                    if False, handling signing in with cancelled account
        """
        self.__log.info(f"Hydra behavior when cancelled/activated account = {is_re_activated}")
        is_lp_enabled = self.service_api.get_authentication_configuration_search(True)  # if license plate is enabled
        if is_re_activated:
            self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 90000)
            self.verify_view_mode(self.acc_locked_labels.LBL_HOME_SCREEN_VIEW_MODE)
        else:
            # For licenseplate, there's no overlay during signing in, error is shown in the Home screen's prediction bar
            if is_lp_enabled and Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_9):
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_SCREEN, 30000)
                self.verify_view_mode(self.acc_locked_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE)
            elif is_lp_enabled and Settings.hydra_branch() <= Settings.hydra_branch(HydraBranches.STREAMER_1_7):
                # In Hydra 1.5, 1.6, 1.7 another error overlay was shown after selecting OK in the error overlay during
                # signing in with cancelled account
                self.verify_overlay_shown()
                self.select_menu(self.home_labels.LBL_OK)
                self.verify_overlay_shown()
            else:
                # For unmanaged boxes with non-licenseplate MSOs
                #
                # NOTE:
                # Sometimes, different error codes may appear, so switching to overlay presence checking
                self.verify_overlay_shown()
                self.select_menu(self.home_labels.LBL_OK)
                if not self.wait_for_screen_ready(self.acc_locked_labels.EXM_SAML_SIGN_IN_SCREEN, 30000):
                    self.verify_view_mode(self.acc_locked_labels.LBL_SIGN_IN_SCREEN_VIEW_MODE)

    def managing_hydra_app_after_canceling_acc(self, timeout=10):
        """
        This implementation works for unmanaged devices only.

        Once Cancel Device made, Account Locked overlay shown for unmanaged boxes.

        Args:
            timeout (int): time in seconds, waiting for deviceStatusUpdateNotification
        """
        self.__log.info("Managing the Hydra app after cancelling account")
        # Waiting for the account cancellation request to reach the box
        timout_millis = timeout * 1000
        self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_OVERLAY, timout_millis)

    def managing_hydra_app_after_canceling_re_activating_acc(self, timeout=10, is_re_activated=True):
        """
        This implementation works for unmanaged devices only.

        This method may come in handy when device cancelling and re-activating is made
        during the box being in the disconnected state.

        Args:
            timeout (int): time in seconds, waiting for deviceStatusUpdateNotification
            is_re_activated (bool): if True, handling selection after account re-activation
                                    if False, handling selection with cancelled account
        """
        self.__log.info("Managing the Hydra app after cancelling and re-activating account")
        # Waiting for the account cancellation request to reach the box
        timout_millis = timeout * 1000
        self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_OVERLAY, timout_millis)
        self.verify_overlay_title(self.acc_locked_labels.LBL_ACC_LOCKED_OVERLAY_TITLE)
        self.select_menu(self.acc_locked_labels.LBL_EXIT_HYDRA_APP)
        self.handling_hydra_app_after_exit(Settings.app_package)
        self.__hydra_behavior_when_cancelled_activated_acc(is_re_activated)

    def managing_acc_locked_when_box_offline(self, is_just_started=True):
        """
        Use as an auxiliary method.
        Handling unmanaged boxes when the box is offline.
        Box reboot should be made before calling this function.

        Args:
            is_just_started (bool): if the Hydra app is just started, behavior can differ from one when app works for some time
        """
        if is_just_started:
            self.wait_for_screen_ready(timeout=30000)
        # For licenseplate, there's no overlay during signing in, error is shown in the Home screen's prediction bar
        if Settings.is_cc3() and Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_13):
            if is_just_started:
                self.wait_for_screen_ready(self.acc_locked_labels.EXM_ACC_LOCKOUT_SCREEN, 30000)
            self.verify_view_mode(self.acc_locked_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE)
        elif Settings.is_cc3() and Settings.hydra_branch() == Settings.hydra_branch(HydraBranches.STREAMER_1_11):
            if is_just_started:
                self.wait_for_screen_ready(self.acc_locked_labels.LBL_ERROR_CODE_C635, 15000)
                self.verify_overlay_shown()
                self.select_menu(self.home_labels.LBL_OK)
            self.home_assertions.verify_connected_disconnected_state_happened(
                error_code=self.home_labels.LBL_ERROR_CODE_C601)
        elif Settings.is_cc3() and Settings.hydra_branch() == Settings.hydra_branch(HydraBranches.STREAMER_1_9):
            if is_just_started:
                self.verify_overlay_shown()
                self.select_menu(self.home_labels.LBL_OK)
            # C219 appears first, then in a few minutes error code changes to C601
            self.home_assertions.verify_connected_disconnected_state_happened(
                error_code=self.home_labels.LBL_ERROR_CODE_C219)
        elif Settings.is_cc3() and Settings.hydra_branch() <= Settings.hydra_branch(HydraBranches.STREAMER_1_7):
            # In Hydra 1.5, 1.6, 1.7 another error overlay was shown after selecting OK in the error overlay during
            # signing in with cancelled account
            self.verify_overlay_shown()
            self.select_menu(self.home_labels.LBL_OK)
            self.verify_overlay_shown()
        else:
            # For unmanaged boxes with non-licenseplate MSOs
            #
            # waiting a bit for Account Error C613 error overlay appearing,
            # it's ok that this overlay appears when account was cancelled while the Hydra app wasn't up,
            # and it's not OK when this overlay appears on Hydra loading after Exit App button was selected
            # in the Account Locked overlay or the Hydra app was closed after Account Locked overlay being timed out
            # NOTE:
            # Sometimes, different error codes may appear, so switching to overlay presence checking
            if is_just_started:
                self.verify_overlay_shown()
            self.home_page.proceed_with_sign_in()
            self.verify_view_mode(self.acc_locked_labels.LBL_SIGN_IN_SCREEN_VIEW_MODE)

    def managing_hydra_app_after_box_reboot(self, is_account_locked=True):
        """
        Handling unmanaged boxes after box reboot.
        Box reboot should be made before calling this function.

        Args:
            is_account_locked (bool): if expected account state is locked
        """
        self.__log.info("Managing the Hydra app after box reboot")
        self.launch_application()
        if is_account_locked:
            self.managing_acc_locked_when_box_offline()
        else:
            if not self.wait_for_screen_ready(self.acc_locked_labels.EXM_HOME_SCREEN, 90000):
                self.verify_view_mode(self.acc_locked_labels.LBL_HOME_SCREEN_VIEW_MODE)

    def managing_sign_in_after_acc_status_change(self, is_re_activated=True):
        """
        Handling signing in on unmanaged boxes after account status change.
        Account Locked overlay should be displayed to use this method.
        Method applicable when Account Locked overlay is show and need to select the Exit app option.

        Args:
            is_re_activated (bool): if True, handling signing in after account re-activation
                                    if False, handling signing in with cancelled account
        """
        self.__log.info(f"Managing signing in after account status change; account active = {is_re_activated}")
        self.select_menu(self.acc_locked_labels.LBL_EXIT_HYDRA_APP)
        if self.screen.base.verify_foreground_app(Settings.app_package):
            raise AssertionError("Hydra app did not exit after selecting Exit Hydra app in the Account Locked overlay")
        self.launch_application()
        if not Settings.is_cc3():
            if not self.wait_for_screen_ready(self.acc_locked_labels.EXM_SAML_SIGN_IN_SCREEN, 60000):
                self.verify_view_mode(self.acc_locked_labels.LBL_SIGN_IN_SCREEN_VIEW_MODE)
            self.home_page.sign_in()
        self.__hydra_behavior_when_cancelled_activated_acc(is_re_activated)
