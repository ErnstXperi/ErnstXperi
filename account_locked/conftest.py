import pytest

from set_top_box.client_api.home.assertions import HomeAssertions
from set_top_box.client_api.account_locked.assertions import AccountLockedAssertions
from set_top_box.client_api.program_options.assertions import ProgramOptionsAssertions
from set_top_box.client_api.guide.assertions import GuideAssertions
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger
from set_top_box.factory.page_factory import PageFactory
from set_top_box.factory.label_factory import LabelFactory
from set_top_box.conftest import get_actual_tsn


__log = Logger(__name__)


@pytest.fixture(autouse=True, scope="class")
def setup_account_locked(request):
    """
    Configure steps to be executed before the test cases run

    Args:
        request
    """
    request.cls.program_options_assertions = ProgramOptionsAssertions(request.cls.screen)

    request.cls.guide_page = PageFactory("guide", Settings, request.cls.screen)
    request.cls.guide_assertions = GuideAssertions(request.cls.screen)

    request.cls.system_labels = LabelFactory("system", Settings)
    request.cls.system_page = PageFactory("system", Settings, request.cls.screen)
    request.cls.system_page.system_labels = request.cls.system_labels

    request.cls.home_page = PageFactory("home", Settings, request.cls.screen)
    request.cls.home_page.guide_page = request.cls.guide_page
    request.cls.home_assertions = HomeAssertions(request.cls.screen)
    request.cls.home_assertions.home_page = request.cls.home_page
    request.cls.home_labels = LabelFactory("home", Settings)
    request.cls.home_page.home_labels = request.cls.home_labels

    request.cls.acc_locked_labels = LabelFactory("account_locked", Settings)
    request.cls.acc_locked_page = PageFactory("account_locked", Settings, request.cls.screen)
    request.cls.acc_locked_page.acc_locked_labels = request.cls.acc_locked_labels
    request.cls.acc_locked_page.system_labels = request.cls.system_labels
    request.cls.acc_locked_page.home_page = request.cls.home_page
    request.cls.acc_locked_page.home_assertions = request.cls.home_assertions
    request.cls.acc_locked_page.home_labels = request.cls.home_labels

    request.cls.acc_locked_assertions = AccountLockedAssertions(request.cls.screen)
    request.cls.acc_locked_assertions.acc_locked_page = request.cls.acc_locked_page
    request.cls.acc_locked_assertions.acc_locked_page.acc_locked_labels = request.cls.acc_locked_labels
    request.cls.acc_locked_assertions.acc_locked_page.home_labels = request.cls.home_labels
    request.cls.acc_locked_assertions.acc_locked_labels = request.cls.acc_locked_labels
    request.cls.acc_locked_assertions.system_labels = request.cls.system_labels
    request.cls.acc_locked_assertions.system_page = request.cls.system_page

    request.cls.my_shows_page = PageFactory("my_shows", Settings, request.cls.screen)
    request.cls.home_page.my_shows_page = request.cls.my_shows_page

    request.getfixturevalue('clean_ftux_and_sign_in')


@pytest.fixture(autouse=False, scope="function")
def cleanup_re_activate_and_sign_in(request):
    """
    Re-activating account, if cancelled, and signing in, if unmanaged device.
    Can be used as for managed as for unmanaged devices
    """
    __log.info("Setup. Updating Settings.tsn value since TSN changes after cancelling and re-activating account")
    # TSN changing is detected for licenseplate
    setattr(Settings, "tsn", get_actual_tsn())

    def tear_down():
        __log.info("Tearing down")
        # TODO
        # Use setup_re_activating_account fixture here
        device_status = request.cls.pps_api_helper.get_device_details(Settings.ca_device_id)[0]["status"]
        if device_status != "active":
            request.cls.acc_locked_page.re_activate_device()
        else:
            __log.info("Account status is active, re-ativation skipped")
            # Now we need to check if Hydra app knows about active state
        if not request.cls.screen.base.verify_foreground_app(Settings.app_package):
            # Starting Hydra app if it's not up or brining the app to foreground if it's up.
            # Without this step, test_4863048_select_device_sys_info_opt_acc_locked_screen fails after
            # test_4863034_select_network_settings_opt_acc_locked_screen since Account Locked screen is shown due to
            # specific behavior of screen dump while being in non-Hydra screens.
            request.cls.acc_locked_page.launch_application()
        request.cls.acc_locked_page.screen.refresh()
        if request.cls.acc_locked_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE in request.cls.acc_locked_page.view_mode():
            # This is workaround for an issue when tests begin to fail because cannot go out of the Account Locked screen
            # after running test_4863052_from_active_to_cancelled_when_turned_off on an unmanaged device licenseplate.
            # TODO: Need to investigate the issue
            request.cls.acc_locked_page.select_menu(request.cls.acc_locked_labels.LBL_ACC_LOCKED_SIGN_IN_OPT)
            request.cls.acc_locked_page.wait_for_screen_ready(request.cls.acc_locked_labels.EXM_HOME_SCREEN, 90000)
        else:
            request.cls.home_page.relaunch_hydra_app()
            if Settings.is_unmanaged() and not Settings.is_cc3():
                request.cls.home_page.proceed_with_sign_in()
            else:
                request.cls.acc_locked_page.wait_for_screen_ready(request.cls.acc_locked_labels.EXM_HOME_SCREEN, 90000)
    request.addfinalizer(tear_down)


@pytest.fixture(autouse=False, scope="function")
def cleanup_enabling_internet(request):
    """
    Enabling internet

    Args:
        request: pytest fixture
    """
    def tear_down():
        if Settings.transport == "SSH":
            __log.info("Tearing down. Enabling internet connection...")
            request.cls.acc_locked_page.manage_network_change("set up")
            state = request.cls.acc_locked_page.manage_network_change("show")
            if state != "up":
                raise AssertionError(f"Failed to check internet connection state - {state}")
    request.addfinalizer(tear_down)
