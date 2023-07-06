"""
    @author: iurii.nartov@tivo.com
    @created: Oct-31-2019
"""

import pytest

from hamcrest import assert_that, contains_string, is_not, is_

from set_top_box.client_api.home.assertions import HomeAssertions
from set_top_box.client_api.watchvideo.assertions import WatchVideoAssertions
from set_top_box.client_api.apps_and_games.assertions import AppsAndGamesAssertions
from set_top_box.client_api.ott_deeplinking.assertions import DeeplinkAssertions
from set_top_box.client_api.program_options.assertions import ProgramOptionsAssertions
from set_top_box.client_api.text_search.assertions import TextSearchAssertions
from set_top_box.client_api.my_shows.assertions import MyShowsAssertions
from set_top_box.client_api.guide.assertions import GuideAssertions
from set_top_box.client_api.Menu.assertions import MenuAssertions
from set_top_box.client_api.wtw.assertions import WhatToWatchAssertions
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger
from set_top_box.factory.page_factory import PageFactory
from set_top_box.factory.label_factory import LabelFactory
from set_top_box.conftest import setup_bind_hsn

__logger = Logger(__name__)


@pytest.fixture(autouse=True, scope="class")
def setup_apps_and_games(request):
    """
    Configure steps to be executed before the test cases run

    Args:
        request
    """
    request.cls.home_page = PageFactory("home", Settings, request.cls.screen)
    request.cls.home_assertions = HomeAssertions(request.cls.screen)
    request.cls.home_labels = LabelFactory("home", Settings)
    request.cls.menu_page = PageFactory("Menu", Settings, request.cls.screen)
    request.cls.menu_labels = LabelFactory("Menu", Settings)
    request.cls.menu_assertions = MenuAssertions(request.cls.screen)
    request.cls.menu_assertions.menu_labels = request.cls.menu_labels

    request.cls.my_shows_labels = LabelFactory("my_shows", Settings)
    request.cls.my_shows_page = PageFactory("my_shows", Settings, request.cls.screen)
    request.cls.my_shows_assertions = MyShowsAssertions(request.cls.screen)

    request.cls.text_search_labels = LabelFactory("text_search", Settings)
    request.cls.text_search_page = PageFactory("text_search", Settings, request.cls.screen)
    request.cls.text_search_page.text_search_labels = request.cls.text_search_labels
    request.cls.text_search_assertions = TextSearchAssertions(request.cls.screen)

    request.cls.guide_page = PageFactory("guide", Settings, request.cls.screen)
    request.cls.guide_assertions = GuideAssertions(request.cls.screen)
    request.cls.guide_labels = LabelFactory("guide", Settings)

    request.cls.program_options_page = PageFactory("program_options", Settings, request.cls.screen)
    request.cls.program_options_assertions = ProgramOptionsAssertions(request.cls.screen)

    request.cls.apps_and_games_page = PageFactory("apps_and_games", Settings, request.cls.screen)
    request.cls.apps_and_games_assertions = AppsAndGamesAssertions(request.cls.screen)
    request.cls.apps_and_games_labels = LabelFactory("apps_and_games", Settings)
    request.cls.apps_and_games_assertions.apps_and_games_labels = request.cls.apps_and_games_labels

    request.cls.ott_deeplinking_page = PageFactory("ott_deeplinking", Settings, request.cls.screen)
    request.cls.ott_deeplinking_labels = LabelFactory("ott_deeplinking", Settings)
    request.cls.ott_deeplinking_assertions = DeeplinkAssertions(request.cls.screen)

    request.cls.wtw_labels = LabelFactory("wtw", Settings)
    request.cls.wtw_page = PageFactory("wtw", Settings, request.cls.screen)
    request.cls.wtw_assertions = WhatToWatchAssertions(request.cls.screen)
    request.cls.wtw_assertions.wtw_page = request.cls.wtw_page
    request.cls.wtw_page.wtw_labels = request.cls.wtw_labels
    request.cls.wtw_assertions.wtw_labels = request.cls.wtw_labels
    request.cls.wtw_page.home_labels = request.cls.home_labels
    request.cls.wtw_assertions.home_labels = request.cls.home_labels
    request.cls.wtw_page.labels = request.cls.wtw_labels = LabelFactory("wtw", Settings)

    request.cls.watchvideo_assertions = WatchVideoAssertions(request.cls.screen)
    request.cls.watchvideo_page = PageFactory("watchvideo", Settings, request.cls.screen)
    request.cls.watchvideo_labels = request.cls.liveTv_labels = LabelFactory("watchvideo", Settings)

    request.cls.vod_labels = LabelFactory("VOD", Settings)

    request.getfixturevalue('device_reboot_to_imporve_device_perf')
    request.getfixturevalue('clean_ftux_and_sign_in')
    request.getfixturevalue('disable_parental_controls')


@pytest.fixture(autouse=False, scope="function")
def setup_sideload_test_app(request):
    """
    Installs a test app over adb, applicable only for AndroidDriver

    Args:
        request
    """
    result = request.cls.apps_and_games_page.screen.base.install(Settings.TEST_APP_FOR_APPSGAMES, is_hydra_app=False,
                                                                 retries=1, reinstall=False, reboot=False)
    if not result:
        pytest.fail("Failed to install '" + Settings.TEST_APP_FOR_APPSGAMES + "'")


@pytest.fixture(autouse=False, scope="function")
def setup_cleanup_bind_hsn(request):
    """
    Binds the HSN to account
    Applicable only for Managed boxes

    Args:
        request
    """
    def tear_down():
        __logger.info("Tearing down")
        if setup_bind_hsn(request):
            request.cls.home_page.relaunch_hydra_app()
    request.addfinalizer(tear_down)


@pytest.fixture(autouse=False, scope="function")
def setup_cleanup_start_tivo_app(request):
    """
    Starts the Hydra app

    Args:
        request
    """
    def tear_down():
        __logger.info("Tearing down. Starting the app just in case...")
        Settings.driver.start_app(Settings.app_package)
    request.addfinalizer(tear_down)


@pytest.fixture(autouse=False, scope="function")
def setup_cleanup_content_provider_app(request):
    """
    Installs content provider app over adb, applicable only for AndroidDriver

    Args:
        request
    """
    result = request.cls.driver.install(Settings.CONTENT_PROVIDER_APP, retries=1, reinstall=False, reboot=False)
    if not result:
        pytest.skip("Failed to install '" + Settings.CONTENT_PROVIDER_APP + "'")
    yield
    request.cls.driver.uninstall_app(Settings.CONTENT_PROVIDER_APP_PACKAGE)
    request.cls.home_page.clear_cache_launch_hydra_app()
    request.cls.home_page.relaunch_hydra_app(reboot=True)


@pytest.fixture(autouse=False, scope="function")
def setup_cleanup_pluto_tv_app(request):
    """
    Installs Pluto TV app over adb, applicable only for AndroidDriver
    """
    package = 'emo-st-cc11-tivoplus'
    s_api = request.cls.service_api
    request.cls.iptv_prov_api.service_group_store('lp_plutotivoplus_100', 'DG',
                                                  request.cls.service_api.get_mso_partner_id(Settings.tsn))
    if package not in request.cls.iptv_prov_api.get_account_entitlement_package_names(s_api.getPartnerCustomerId(Settings.tsn),
                                                                                      s_api.get_mso_partner_id(Settings.tsn)):
        request.cls.iptv_prov_api.account_entitlement_publish(
            [{'package': package, 'start_date': '2015-12-02 09:30:00', 'end_date': '2099-12-02 11:30:59'}],
            request.cls.service_api.getPartnerCustomerId(Settings.tsn),
            request.cls.service_api.get_mso_partner_id(Settings.tsn))
    else:
        __logger.info(f"Package '{package}' is already published for PCID '{Settings.pcid}'.")
    result = request.cls.driver.install(Settings.PLUTO_TV_APP, retries=1, reinstall=True, reboot=False)
    if not result:
        pytest.skip("Failed to install '" + Settings.PLUTO_TV_APP + "'")
    yield
    if request.cls.driver.is_app_installed(request.cls.apps_and_games_labels.PLUTO_PACKAGE_NAME):
        request.cls.driver.uninstall_app(request.cls.apps_and_games_labels.PLUTO_PACKAGE_NAME)
    else:
        __logger.info("App has been already uninstalled during test execution.")
    if package in request.cls.iptv_prov_api.get_account_entitlement_package_names(s_api.getPartnerCustomerId(Settings.tsn),
                                                                                  s_api.get_mso_partner_id(Settings.tsn)):
        request.cls.iptv_prov_api.account_entitlement_remove(
            [package],
            request.cls.service_api.getPartnerCustomerId(Settings.tsn),
            request.cls.service_api.get_mso_partner_id(Settings.tsn))
    else:
        __logger.info(f"Package '{package}' is already removed for PCID '{Settings.pcid}'.")
    request.cls.iptv_prov_api.service_group_remove('lp_plutotivoplus_100', 'DG',
                                                   request.cls.service_api.get_mso_partner_id(Settings.tsn))


@pytest.fixture(autouse=False, scope="function")
def pluto_tv_app_install(request):
    """
    Installs Pluto TV app from Google play store
    """
    if request.cls.driver.is_app_installed(request.cls.apps_and_games_labels.PLUTO_PACKAGE_NAME):
        __logger.info("Pluto TV app is installed on device")
    else:
        request.cls.screen.base.app_install_google_play_store(app_name=Settings.PLUTO_TV_PACKAGE_NAME,
                                                              install=request.cls.ott_deeplinking_labels.
                                                              LBL_GOOGLE_PLAY_INSTALL_BUTTON,
                                                              launch=request.cls.apps_and_games_labels.LBL_OPEN)
        if request.cls.driver.is_app_installed(request.cls.apps_and_games_labels.PLUTO_PACKAGE_NAME):
            __logger.info("Pluto TV app is installed on device")
        else:
            __logger.info("Pluto TV app installation failed")
            assert_that(True,
                        request.cls.driver.is_app_installed(
                            request.cls.apps_and_games_labels.PLUTO_PACKAGE_NAME),
                        "Pluto TV not installed")


@pytest.fixture(autouse=False, scope="function")
def enable_app(request):
    def tear_down():
        __logger.info("Enabling back the app")
        request.cls.driver.enable_app(request.cls.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
    request.addfinalizer(tear_down)


@pytest.fixture(autouse=False, scope="function")
def skip_old_os_version():
    __logger.info("Checking OS version of the device")
    if int(Settings.os_version) < 10:
        pytest.skip("Requires Android Version 10 and above to get LST iid, but actual is '{}'".format(Settings.
                                                                                                      os_version))
