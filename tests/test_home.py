"""
Created on Aug 1, 2017

@author: sghosh
"""

import os
import time
import timeit
import random
from datetime import datetime, timedelta

import pytest
from hamcrest.core import assert_that

from set_top_box.client_api.end2end.conftest import set_screen_saver_default_value  # noqa: F401
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, FeaturesList, \
    BodyConfigFeatures, DeviceInfoStoreFeatures, HydraBranches, DebugEnvPropValues, NotificationSendReqTypes, \
    RemoteCommands
from set_top_box.test_settings import Settings
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings  # noqa: F401
from set_top_box.client_api.home.conftest import *  # noqa: F401
from set_top_box.client_api.account_locked.conftest import cleanup_re_activate_and_sign_in, cleanup_enabling_internet
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions
from set_top_box.client_api.Menu.conftest import setup_cleanup_parental_and_purchase_controls, \
    setup_enable_video_window, \
    disable_parental_controls, enable_video_providers, disable_video_providers, \
    setup_lock_parental_and_purchase_controls, cleanup_favorite_channels
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_start_tivo_app
from set_top_box.client_api.guide.conftest import switch_tivo_service_rasp, toggle_mind_availability, \
    toggle_guide_rows_service_availability
from tools.logger.logger import Logger


@pytest.mark.usefixtures("setup_home")
@pytest.mark.home
class TestHomeScreen(object):
    __log = Logger(__name__)

    @pytestrail.case("C10200575")
    @pytest.mark.duplicate
    def test_999999_home_demo_test(self):
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number("7104")
        self.home_assertions.verify_screen_rendered()

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_324360_home_menu(self):
        self.menu_page.go_to_menu_screen(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MENU_SCREENTITLE)

    @pytestrail.case("C12792130")
    @pytest.mark.ibc
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_324363_home_guide(self):
        self.home_page.go_to_guide(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_GUIDE_SCREENTITLE)

    @pytestrail.case("C12792127")
    @pytest.mark.ibc
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_324362_home_my_shows(self):
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytestrail.case("C12792129")
    @pytest.mark.ibc
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_324364_home_search(self):
        self.text_search_page.go_to_search(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT)

    @pytestrail.case("C12792128")
    @pytest.mark.ibc
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_324365_home_what_to_watch(self):
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_325125_home_predictions(self):
        self.home_page.nav_to_predictions_strip()
        self.home_assertions.verify_predictions()
        # self.home_page.select_prediction_focus()

    @pytestrail.case("C11123892")
    @pytest.mark.devhost
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.branding_check
    @pytest.mark.timeout(Settings.timeout)
    def test_231822_verify_home_menu_item(self):
        """
        231822
        From TiVo Central, highlight each menu option
        Validate Homescreen with the Tivo central
        """
        self.home_page.back_to_home_short()
        for i in self.home_labels.LBL_HOME_MENU_ITEMS:
            self.home_assertions.verify_menu_item_available(i)
        self.home_page.goto_prediction()
        self.home_assertions.verify_predictions()
        self.home_assertions.verify_primary_branding_icon()

    @pytestrail.case("C10838525")
    @pytest.mark.xray('FRUM-46')
    @pytest.mark.devhost
    @pytest.mark.sanity
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    def test_270720_verify_initial_focus_in_home_screen(self):
        """
        270720
        Verify if focus is on home screen
        :return:
        """
        self.home_page.back_to_home_short()
        for i in self.home_labels.LBL_HOME_MENU_ITEMS:
            self.home_assertions.verify_menu_item_available(i)

    @pytestrail.case("C10838524")
    @pytest.mark.xray('FRUM-49')
    @pytest.mark.devhost
    @pytest.mark.sanity
    @pytest.mark.bvt
    @pytest.mark.vod
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_metronet() or Settings.is_telus(),
                               reason="Device does not have On Demand feature")
    def test_309439_select_on_demand_shortcut(self):
        """
        309439
        Verify selecting the Home VOD shortcut goes to the VOD Browse main screen.
        :return:
        """
        self.vod_page.go_to_vod(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SCREENTITLE)

    @pytestrail.case("C10838502")
    @pytest.mark.xray('FRUM-39')
    @pytest.mark.devhost
    @pytest.mark.sanity
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    def test_333417_w2w_primary_screen(self):
        """
        333417
        To verify that the Content Strips on W2WPrimaryScreen is displayed correct.
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytestrail.case("C11123895")
    @pytest.mark.bat
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    def test_333425_w2w_secondary_screen(self):
        """
        333425
        To verify that the W2WSecondaryScreen is displayed correctly.
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)
        self.home_page.verify_wtw_secondary(self)

    @pytest.mark.bvt
    @pytest.mark.duplicate
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_347944_inital_populations_of_predicitons(self):
        """
        347944
        Verify the initial populations of content tiles.
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.home_assertions.verify_prediction_tile()

    @pytestrail.case("C11123896")
    @pytest.mark.bat
    @pytest.mark.compliance
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("cleanup_EAS")
    def test_356135_trigger_EAS_alert(self):
        """
        356135
        Test triggering EAS alert
        :return:
        """
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_live_tv(channel[0], confirm=False)
        self.home_page.back_to_home_short()
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.screen.base.press_back()  # Back to home screen

    @pytestrail.case("C11123897")
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("enable_disable_stay_awake")
    def test_393581_wake_up_using_bail_buttons(self):
        """
        393581
        To verify that the user is able to wake up the device from screensaver using bail buttons
        :return:
        """
        self.home_page.back_to_home_short()
        time.sleep(80)
        # self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        focused_app = self.driver.driver.get_current_focused_app()
        if self.home_labels.LBL_DREAM not in focused_app[0]:
            pytest.fail("Screen saver did not appear.")
        self.home_page.wake_up()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_assertions.verify_home_screen()

    @pytestrail.case("C11123894")
    @pytest.mark.disabled
    @pytest.mark.timeout(Settings.timeout)
    def test_322650_voice_search(self):
        """
        322650
        Verify voice enabled when AP_voice group is on the box and the feature is enabled.
        :return:
        As the test is only applicable for Amino RCN, marking this test as Manual as stated in PARTDEFECT-958
        """
        # cmd =  """ adb shell am start -a "android.search.action.GLOBAL_SEARCH" --es query "TomHanks"  """
        if not self.home_page.voice_button_available():
            pytest.skip("Remote does not have Voice Button")
        self.home_page.back_to_home_short()
        self.home_page.voice_search(self)

    @pytestrail.case("C14379313")
    @pytest.mark.xray("FRUM-319")
    @pytest.mark.ftux
    # @pytest.mark.bat
    @pytest.mark.iplinear
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.frumos_15
    @pytest.mark.platform_cert_smoke_test
    def test_347782_first_sign_in(self):
        """
        Verify that FTUX is only displayed the first time the user signs into the app.
        Xray: https://jira.xperi.com/browse/FRUM-319
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="false")
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_FTUX_ANIMATION_SCREEN, timeout=30000)
        self.home_page.accept_legal_acceptance_screens()
        self.home_assertions.verify_ftux_animation_screen()
        if self.home_page.is_ftux_animation_view_mode():
            self.home_page.skip_ftux_animation()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_ONEPASS_FTUX)
        self.home_assertions.verify_ftux_view_mode()
        self.home_page.select_done(times=1)
        if self.home_page.is_ftux_streaming_apps_view_mode():
            self.home_assertions.verify_ftux_streamingapps_screen()
            self.home_page.select_done(times=1)
        if self.home_page.is_ftux_pc_settings_screen_view_mode():
            self.home_assertions.verify_ftux_pcsettings_screen()
            self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_HOME_VIEW_MODE, timeout=60000)
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytestrail.case("C11123893")
    @pytest.mark.bat
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_309095_schedule_one_pass_from_full_info_banner(self):
        """
        309095
        Schedule a OnePass from Full Info Banner
        :return:
        """
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel_number:
            pytest.skip("Recordable episodic channels are not found.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number[0][0])
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_page.show_info_banner()
        show = self.home_page.create_one_pass(self)
        show_name = self.my_shows_page.cleanup_text_char(show)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.home_assertions.verify_show_in_my_shows(self, show_name)
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_show_in_one_pass_manager(self, show_name)

    @pytest.mark.disabled
    @pytest.mark.timeout(Settings.timeout)
    def test_330098_home_livetv(self):
        """
        Test was disabled as outdated because predictions panel is no more displayed in watchvideo screens
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)

    @pytestrail.case("C12792607")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_331426_home_screen_background_video(self):
        """
        331426
         Verify the Home Screen Background with Video Window Yes, Video on Home Full Screen, Background Images On.
        :return:
        """
        self.menu_page.enable_full_screen_video_on_home(self)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.back_to_home_short()
        self.vod_assertions.verify_video_streaming()
        self.home_page.goto_prediction()
        self.vod_assertions.verify_video_streaming()

    @pytest.mark.xray("FRUM-318")
    @pytest.mark.msofocused
    @pytest.mark.ftux
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.frumos_15
    @pytest.mark.platform_cert_smoke_test
    def test_347821_ftux_onepassquickselect(self):
        """
        To verify the correct behavior and destination for "Done" action button in FTUX
        Xray: https://jira.xperi.com/browse/FRUM-318
        :return:
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="false")
        self.home_page.ftux_onepass_selection_and_verification(self, Settings.app_package, Settings.username)
        self.home_assertions.verify_ftux_streamingapps_screen()
        self.home_page.select_done(times=1)
        if self.home_page.is_ftux_pc_settings_screen_view_mode():
            self.home_assertions.verify_ftux_pcsettings_screen()
            self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.home_assertions.verify_home_title()

    @pytest.mark.xray("FRUM-317")
    @pytest.mark.ftux
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.is_devhost())
    # @pytest.mark.p1_regression
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    def test_347783_ftux_second_signin(self):
        """
        Verify that FTUX is not displayed for the second and more time users sign into the app.
        Xray: https://jira.xperi.com/browse/FRUM-317
        :return:
        """
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=True, skip_onepass=True,
                                                   skip_apps=True, skip_pcsetting=True, SKIP_FTUX="false")
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.home_page.relaunch_hydra_app()
        self.home_assertions.verify_home_title()

    @pytestrail.case("C12792606")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.timeout(Settings.timeout)
    def test_273853_verify_all_episodes_list_view(self):
        """
        273853
         Verify all episodes list view and verify series episode, title and streaming video icon.
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SIDE_PANEL)
        self.menu_page.select_menu_items(self.my_shows_labels.LBL_TV)
        self.wtw_assertions.verify_highlight_not_in_netflix_strip()
        self.home_page.verify_list_view_episode_screen(self)

    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.longrun
    @pytest.mark.timeout(Settings.timeout)
    def test_393697_WTW_SOCU_Source_icon_and_playback(self):
        """
        393697
         What to Watch - SOCU Offer - Source icons, options, and playback
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY)
        if not self.home_page.locate_socu_program_in_WTW(self):
            pytest.skip("Failed to get a Socu program from What to Watch")
        self.program_options_page.select_play_from_socu()
        self.home_assertions.verify_socu_playback(self)
        self.watchvideo_assertions.verify_socu_playback_started()

    @pytestrail.case("C12792132")
    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.predictionbar
    # @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.usefixtures("disable_video_providers")
    def test_107332670_prediction_bar_press_select_no_recording_no_providers_is_live(self):
        """
        107332670
         Prediction Bar - Press SELECT - No recording, no providers, is live
        :return:
        """
        self.home_page.go_to_guide(self)
        self.home_page.back_to_home_short()
        show = self.home_page.get_prediction_without_ott(self)
        if not show:
            pytest.skip("No show in prediction without OTT")
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        show = self.my_shows_page.remove_service_symbols(show[0])
        self.home_page.navigate_by_strip(show)
        self.watchvideo_assertions.press_select_and_verify_streaming(self)

    @pytestrail.case("C12792134")
    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.predictionbar
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.usefixtures("disable_video_providers")
    @pytest.mark.cloudcore_wtw_predictions
    def test_107332683_prediction_bar_press_select_recording_no_providers_is_live(self):
        """
        107332683
         Prediction Bar - Press SELECT - Recording, no providers, is live
        :return:
        """
        self.home_page.go_to_guide(self)
        self.home_page.back_to_home_short()
        show = self.home_page.get_prediction_without_ott(self)
        if not show:
            pytest.skip("No show in prediction without OTT")
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        show = self.my_shows_page.remove_service_symbols(show[0])
        self.home_page.navigate_by_strip(show)
        self.watchvideo_assertions.press_select_and_verify_streaming(self)
        self.guide_page.open_olg()
        self.screen.refresh()
        self.guide_assertions.verify_one_line_guide()
        self.guide_page.select_and_record_program(self)
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show)
        self.watchvideo_assertions.press_select_and_verify_recording_is_played(self)

    @pytestrail.case("C12792133")
    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.predictionbar
    @pytest.mark.ndvr
    @pytest.mark.platform_cert_smoke_test
    # @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_107332681_prediction_bar_press_select_recording_providers_is_live(self):
        """
        107332681
         Prediction Bar - Press SELECT - Recording, providers, is live
        :return:
        """
        self.home_page.go_to_guide(self)
        self.home_page.back_to_home_short()
        show = self.home_page.get_prediction_with_ott(self)
        if not show:
            pytest.skip("No show in prediction with OTT")
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show[0])
        self.watchvideo_assertions.press_select_and_verify_streaming(self)
        self.guide_page.open_olg()
        self.screen.refresh()
        self.guide_assertions.verify_one_line_guide()
        self.guide_page.select_and_record_program(self)
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show[0])
        self.watchvideo_assertions.press_select_and_verify_recording_is_played(self)

    @pytestrail.case("C12792135")
    @pytest.mark.p1_regression
    @pytest.mark.myshows
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_105147819_pressing_home_to_my_shows(self):
        """
        T105147819
        Verify that pressing Home/TiVo button on Home screen navigate user to My Shows screen
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.home_page.home_button_to_my_shows()
        # New implementation to validate Tivo button press IPTV-16286
        self.my_shows_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)

    @pytestrail.case("C14379314")
    @pytest.mark.xray("FRUM-321")
    @pytest.mark.ftux
    @pytest.mark.home
    @pytest.mark.usefixtures("setup_cleanup_add_google_account")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.skipif(not Settings.is_managed(), reason="Notifications options is NA for unamnaged")
    def test_74111211_check_notification(self, request):
        """
        Check notification after performing livetv myshows vod playback and unlink google account

        Testrail:
            https://testrail.tivo.com//index.php?/tests/view/74111211
        """
        request.config.cache.set("is_reboot_needed", True)  # workaround due to https://jira.xperi.com/browse/IPTV-24494
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.back_to_home_short()
        # Checking Live TV show name in NOTIFICATIONS
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.goto_notification(self)
        self.home_assertions.validate_notifications()
        # Checking Recoding name in NOTIFICATIONS
        recording = self.api.record_currently_airing_shows(
            number_of_shows=1, is_preview_offer_needed=True, genre="series")[0][0]
        # Workaround. Reboot due to a defect -  https://jira.xperi.com/browse/IPTV-25396
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_menu_by_substring(recording)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_page.navigate_to_recordings()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.goto_notification(self)
        self.home_assertions.validate_notifications()
        # Workaround. Reboot due to a defect -  https://jira.xperi.com/browse/IPTV-25396
        self.home_page.relaunch_hydra_app(reboot=True)
        # Checking VOD asset name in NOTIFICATIONS
        if Settings.is_vod_supported():
            status, result = self.vod_api.getOffer_fvod()
            # Skip VOD streaming part in case content is not available and launch vod and validate notification
            if result is None:
                self.vod_page.go_to_vod(self)
                self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)
            else:
                ep = self.vod_page.extract_entryPoint(result)
                mixID = self.vod_page.extract_mixID(result)
                contentID = self.vod_page.extract_contentId(result)
                collectionID = self.vod_page.extract_collectionId(result)
                title = self.vod_page.extract_title(result)
                self.vod_page.go_to_vod(self)
                self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)
                self.vod_page.navigate_to_entryPoint(self, ep, mixID)
                self.vod_page.select_vod(self, collectionID, contentID, title)
                self.vod_page.play_vod_entitled_content(self, result)
                self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
            self.home_page.goto_notification(self)
            self.home_assertions.validate_notifications()
            # Workaround. Reboot due to a defect -  https://jira.xperi.com/browse/IPTV-25396
            self.home_page.relaunch_hydra_app(reboot=True)
        # Checking Removed Google Account message in NOTIFICATIONS
        self.system_page.remove_google_account(Settings.google_account)
        # Workaround. Reboot due to a defect -  https://jira.xperi.com/browse/IPTV-25396
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.goto_notification(self)
        self.home_assertions.validate_notifications()
        self.system_page.signin_google_account(Settings.google_account, Settings.google_password)

    @pytestrail.case("C12792131")
    @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.parental_control
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_enable_video_window")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_335796_home_screen_streaming_video_with_locked_rating(self):
        """
        335796
        Verify streaming video behavior with locked rating in Home screen
        :return:
        """
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        channel = self.guide_page.get_streamable_rating_content(self)
        if not channel:
            pytest.skip("could not find rating channel")
        self.home_page.goto_live_tv(channel[0])
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.vod_assertions.verify_video_streaming()
        self.home_assertions.verify_pc_on_unlocked_on_home_screen(self)
        self.menu_page.go_to_parental_controls(self)
        self.vod_page.enter_pin_in_overlay(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.home_page.back_to_home_short()
        self.vod_assertions.verify_video_blanking_status(state="true")
        self.home_page.press_back_from_home_to_livetv(self)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()

    # @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("set_bridge_status_up")
    def test_74181412_wakeup_device_in_disconnected_state(self):
        '''
        T74181412 - To wake up device from screensaver with different keypresses in diconnected state
        :return:
        '''
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.wait_for_screen_saver(time=33)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.verify_key_press_to_wake_up_device(self)
        self.home_page.wait_for_screen_saver(time=33)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.press_netflix_and_verify_screen(self)
        self.home_page.wait_for_screen_saver(time=33)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.press_youtube_and_verify_screen(self)
        self.home_page.wait_for_screen_saver(time=33)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.press_guide_and_verify_screen(self, disconnect_state=True)
        self.home_page.back_to_home_short()
        home = self.home_page
        src = self.home_page.screen.base
        buttons = [  # monkey doesn't wake up device
            src.press_playpause,
            src.press_fast_forward,
            src.press_rewind,
            src.press_right,
            src.press_left,
            src.press_up,
            src.press_down]
        for button in buttons:
            home.wait_for_screen_saver(time=33)
            self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
            button()
            self.home_assertions.verify_home_title()

    @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for managed devices")
    def test_8880254_gracefull_exit_of_livetv(self):
        '''
        C8880254 - To verify graceful exit of live tv
        :return:
        '''
        channel = self.service_api.get_random_channel(Settings.tsn, "entitled", mso=Settings.mso)
        if channel is None:
            pytest.skip("Could not find any working channel")
        self.home_page.playback_for_sometime(self, channel, time=60)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.validate_disconnected_state(self)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.playback_for_sometime(self, channel)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("set_bridge_status_up")
    def test_74136606_vod_playback_after_network_reconnect(self):
        '''
        T74136606 - verify resume overlay after network disconnect and reconnect
        :return:
        '''
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            raise AssertionError("Failed to get an VOD asset")
        ep = self.vod_page.extract_entryPoint(result)
        mixID = self.vod_page.extract_mixID(result)
        contentID = self.vod_page.extract_contentId(result)
        collectionID = self.vod_page.extract_collectionId(result)
        title = self.vod_page.extract_title(result)
        self.vod_page.go_to_vod(self)
        self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)
        self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.vod_page.play_vod_entitled_content(self, result)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.relaunch_hydra_app(reboot=True)
        if not self.home_page.screen.base.verify_foreground_app(Settings.app_package):
            self.driver.driver.launch_app(Settings.app_package)
            self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_HOME_VIEW_MODE)
        self.vod_page.go_to_vod(self)
        self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)
        self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.home_page.resume_playback(self)

    @pytest.mark.compliance
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-1443")
    @pytest.mark.notapplicable(not Settings.is_telus(), reason="Canadian EAS is supported only by Telus MSO")
    def test_9390559_trigger_canadian_EAS_alert(self):
        """
        C9390559
        Verify that folowing text "ALERTE D'URGENCE" is displayed on the bottom of the screen
        :return:
        """
        self.home_page.back_to_home_short()
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_EAS_screen()
        self.screen.base.press_back()

    @pytest.mark.disconnected_state
    @pytest.mark.branding_check
    @pytest.mark.xray("FRUM-62314")
    @pytest.mark.usefixtures("set_bridge_status_up")
    def test_11683499_branding_check(self):
        '''
        T11683499 - To verify primary branding in disconnected state
        :return:
        '''
        self.home_page.back_to_home_short()
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_primary_branding_icon()

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(not Settings.is_llapr(), reason="Netflix Shortcut supported only by LLA")
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Netflix Shortcut supported only by managed devices")
    def test_229897472_selecting_netflix_shortcut(self):
        '''
        T229897472 - Verify that after pressing on "Netflix" shortcut button Netflix app is launched (if Netflix is installed)
        :return:
        '''
        self.home_assertions.select_netflix_shortcut_and_verify_netflix_launch(self)
        self.home_page.back_to_home_short()

    @pytest.mark.disconnected_state
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for managed devices")
    @pytest.mark.frumos_15
    def test_10838875_c228_prediction_bar(self):
        '''
        C10838875 - To verify C228 message in prediction bar
        :return:
        '''
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.clear_cache_launch_hydra_app()
        self.home_assertions.exit_error_overlay()
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_predictions_error_message(self, self.home_labels.LBL_ERROR_CODE_C228)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.clear_cache_launch_hydra_app()
        self.home_assertions.verify_home_title()

    @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for managed devices")
    def test_74428541_quick_tour(self):
        self.home_page.update_test_conf_and_reboot("device", SKIP_FTUX="false")
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_BRIDGE_STATUS_DOWN)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.menu_page.launch_quick_tour_from_help(self)
        self.home_assertions.validte_disconnected_state_whisper()

    @pytest.mark.disconnected_state
    @pytest.mark.notapplicable(Settings.is_managed(), "Applicable only for unmanaged devices")
    @pytest.mark.notapplicable(Settings.is_cc3(), "No Network Screen is not displayed for LicensePlate")
    @pytest.mark.usefixtures("set_bridge_status_up")
    def test_10838909_no_network_screen(self):
        '''
        T10838909 - To verify no network connection screen
        :return:
        '''
        self.home_page.back_to_home_short()
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_NO_NETWORK_OVERLAY_TITLE.upper())
        self.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_NO_NETWORK_OVERLAY_TITLE.upper())
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.screen.refresh()
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.sign_in_errors
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_11400987_daily_call_error(self):
        self.home_page.update_test_conf_and_reboot("device", QUERY_FAILURE_TYPE="ServiceLogin",
                                                   QUERY_FAILURE_TYPE_RANGES="1,2,tooManyDevices")
        if self.watchvideo_page.is_overlay_shown() and self.home_page.get_overlay_code() == self.home_labels.LBL_C634:
            self.screen.base.press_enter(2000)
        self.home_assertions.verify_home_title()

    @pytest.mark.disconnected_state
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only on managed devices")
    @pytest.mark.usefixtures("rebind_hsn")
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra below v1.13")
    def test_10838844_11400982_C601_C606_error_validation(self):
        self.home_page.back_to_home_short()
        pcid = self.api.getPartnerCustomerId()
        self.home_labels.LBL_PCID = pcid
        self.iptv_prov_api.reset_device(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn), None, Settings.hsn)
        self.home_page.clear_cache_launch_hydra_app(skip_animation=False, skip_onepass=False, skip_apps=False)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_C606_OVERLAY[2])
        self.home_assertions.verify_disconnected_state_overlay(self.home_labels.LBL_C606_OVERLAY)
        self.home_page.go_to_my_shows(self)
        error_expression = f"{self.home_labels.LBL_ERROR_CODE_C601}.*contact CableCo"
        self.home_assertions.verify_predictions_error_message(self, error_expression)
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    pcid)
        self.home_page.clear_cache_launch_hydra_app()

    @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(Settings.is_managed(), "Applicable only for unmanaged devices")
    def test_8880254_gracefull_exit_of_livetv_unmanaged(self):
        '''
        C8880254 - To verify graceful exit of live tv
        :return:
        '''
        channel = self.service_api.get_random_channel(Settings.tsn, "entitled", mso=Settings.mso)
        if channel is None:
            pytest.skip("Could not find any working channel")
        self.home_page.playback_for_sometime(self, channel, time=60)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.guide_page.relaunch_hydra_app()
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_predictions_error_message(self, self.home_labels.LBL_ERROR_CODE_C228)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.playback_for_sometime(self, channel)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_LIVETV_VIEWMODE)
        self.guide_assertions.verify_play_normal()

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_12784054_promote_what_to_watch_slot_0_press_select_wtw_filter(self):
        """
        :Description:
            Promote What To Watch - Slot 0 - Press SELECT - WTW filter
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/12784054
        """
        self.home_page.back_to_home_short()
        filtered_zero_slot_list, count_all_zero_slots = self.home_page.get_and_filter_out_zero_slots_from_api(self)
        zero_slot = self.home_page.navigate_to_and_get_zero_slot_promotion(self,
                                                                           filtered_zero_slot_list,
                                                                           count_all_zero_slots)
        caption = self.wtw_page.get_wtw_nav_caption_according_to_ad(self, zero_slot)
        self.guide_assertions.press_select_and_verify_wtw_screen()
        # After clicking on AD that leads to category, a WTW screen opens with standard title: WHAT TO WATCH
        # Then dev side is asking server about which screen should be displayed
        # (sometimes it's very fast and sometimes it's about ~1-2 seconds to see the actual title).
        # After getting an answer from the server an actual category will be added to the title.
        # To avoid fails because of too early verification need to wait few seconds
        # and refresh a screen to get an actual title
        self.wtw_page.pause(10)
        self.screen.refresh()
        self.wtw_page.verify_screen_title(caption.upper())
        self.wtw_page.nav_to_browse_options_menu(self)
        self.my_shows_assertions.verify_focused_program(caption, self.my_shows_page.menu_focus())

    @pytest.mark.p1_regression
    @pytest.mark.infocard
    @pytest.mark.frumos_11
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11))
    @pytest.mark.cloudcore_wtw_predictions
    def test_268993263_long_key_press_infocard_on_prediction_strip(self):
        """
        Verify that Info card is opened after long press OK in prediction bar on home screen

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/268993263
        """
        self.home_page.back_to_home_short()
        self.home_page.log.step('Navigating to prediction strip')
        self.screen.base.press_down()
        self.home_page.log.step('Call infocard by long press on select button')
        self.screen.base.long_press_enter()
        self.home_assertions.verify_infocard_on_long_key_press()

    @pytestrail.case('C13230088')
    @pytest.mark.xray("FRUM-798")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    def test_C13230088_Verify_that_no_action_is_performing_in_slot0_ad(self):
        self.home_page.back_to_home_short()
        filtered_zero_slot_list = self.home_page.get_Slot0_ads(self)
        zero_slot = self.home_page.navigate_to_and_get_zero_slot_promotion(self, filtered_zero_slot_list)
        self.home_assertions.verify_action_type_in_slot0_ads(zero_slot, self.home_labels.LBL_AD_ACTION_NO_OP_UI)
        self.home_page.navigate_to_destination_screen_for_no_action_ad(self)

    @pytestrail.case('C13230090')
    @pytest.mark.xray("FRUM-938")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    def test_C13230090_verify_user_is_able_to_navigate_to_top_of_app_from_slot0_ad(self):
        """
        This case is enhanced to verify netflix sourcetype once app is launched.
        """
        self.home_page.back_to_home_short()
        filtered_zero_slot_list = self.home_page.get_Slot0_ads(self)
        zero_slot = self.home_page.navigate_to_and_get_zero_slot_promotion(self, filtered_zero_slot_list)
        self.home_assertions.verify_action_type_in_slot0_ads(zero_slot, self.home_labels.LBL_AD_ACTION_UI_NAVIGATE)
        self.home_page.navigate_to_top_of_app_for_uiNavigateAction_action_type(self, zero_slot)
        # Test case enhancement
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_9)

    @pytestrail.case('C13230093')
    @pytest.mark.xray("FRUM-716")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    def test_C13230093_verify_user_is_able_to_navigate_to_VOD_program_screen_from_slot0_ad(self):
        self.home_page.back_to_home_short()
        filtered_zero_slot_list = self.home_page.get_Slot0_ads(self)
        zero_slot = self.home_page.navigate_to_and_get_zero_slot_promotion(self, filtered_zero_slot_list)
        self.home_assertions.verify_action_type_in_slot0_ads(zero_slot, self.home_labels.
                                                             LBL_AD_ACTION_WALLED_GARDEN)
        self.home_page.navigate_to_vod_program_screen_for_walledGardenBrowseUiAction_action_type(self)

    @pytestrail.case('C13527510')
    @pytest.mark.xray("FRUM-839")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    def test_C13527510_verify_user_able_to_navigate_to_livetv_from_slot0_ad(self):
        self.home_page.back_to_home_short()
        filtered_zero_slot_list = self.home_page.get_Slot0_ads(self)
        zero_slot = self.home_page.navigate_to_and_get_zero_slot_promotion(self, filtered_zero_slot_list)
        self.home_assertions.verify_action_type_in_slot0_ads(zero_slot, self.home_labels.LBL_AD_ACTION_LIVETV_UI)
        self.home_page.navigate_to_livetv_for_liveTvUiAction_action_type(self)

    @pytestrail.case('C13230089')
    @pytest.mark.xray("FRUM-897")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    def test_C13230089_verify_user_able_to_navigate_to_series_screen_from_slot0_ad(self):
        self.home_page.back_to_home_short()
        filtered_zero_slot_list = self.home_page.get_Slot0_ads(self)
        zero_slot = self.home_page.navigate_to_and_get_zero_slot_promotion(self, filtered_zero_slot_list)
        self.home_assertions.verify_action_type_in_slot0_ads(zero_slot, self.home_labels.
                                                             LBL_AD_ACTION_COLLECTION_DETAIL_UI)
        self.home_page.navigate_to_series_screen_for_collectionDetailUiAction_action_type(self)

    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    def test_C13527453_getdrmtype_iplinear(self):
        drm_type = self.api.provisioning_info_type("ipLinearConfiguration")
        self.home_assertions.verify_drm_type_ipLinear(drm_type)

    @pytest.mark.p1_regression
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    def test_C13527456_C13527455_getdrmtype_ipvod(self):
        drm_type = self.api.provisioning_info_type("ipVodConfiguration")
        self.home_assertions.verify_drm_type_ipvod(drm_type)

    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    def test_C13527454_getdrmtype_npvr(self):
        drm_type = self.api.provisioning_info_type("npvrConfiguration")
        self.home_assertions.verify_drm_type_npvr(drm_type)

    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.parametrize("feature, package_type",
                             [(FeAlacarteFeatureList.LINEAR, FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()), "Mdrm implemented only for CC5 and CC11")
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C11962119_getnotificationsend(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.api.get_notificationSend()
        self.home_page.go_to_guide(self)
        self.guide_page.verify_channel(self, self.guide_page.guide_encrypted_streaming_channel_number(self))
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.parametrize("feature, package_type",
                             [(FeAlacarteFeatureList.LINEAR, FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12947444_change_drm_type_linear_native(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)

    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.SOCU, FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12784854_change_drm_type_socu_native(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)

    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.usefixtures("cleanup_package_names_native")
    @pytest.mark.parametrize(
        "feature, package_type", [(Settings.mdrm_ndvr_feature(), FeAlacartePackageTypeList.NATIVE)])
    def test_C12785390_change_drm_type_ndvr_native(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/C12785390
        """
        recordable_channellist = self.api.get_recordable_channels()
        encrypted_channellist = self.api.get_encrypted_channel_list()
        intersection = set(recordable_channellist).intersection(encrypted_channellist)
        channel_list = list(intersection)
        if not channel_list:
            pytest.skip("No recordable encrpyted channel found")
        self.home_page.drm_update(self, request, feature, FeAlacartePackageTypeList.VERIMATRIX)
        channel_number = random.choice(channel_list)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.VERIMATRIX, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.VOD, FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12787153_change_drm_type_vod_native(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)

    @pytestrail.case('C12947453')
    @pytestrail.case('C12787146')
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.LINEAR,
                                                        FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12947453_C12787146_ipLear_change_drm_type_verimatrix_Widevine(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_guide(self)
        self.guide_page.verify_channel(self, self.guide_page.guide_encrypted_streaming_channel_number(self))
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case('C13230091')
    @pytest.mark.xray("FRUM-660")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif(Settings.is_fire_tv(), reason="OTT app deeplinking not available on Fire TV")
    def test_C13230091_verify_user_navigates_to_Deeplinked_title_in_OTT_app_from_slot0_ad(self):
        self.home_page.back_to_home_short()
        filtered_zero_slot_list = self.home_page.get_Slot0_ads(self)
        zero_slot = self.home_page.navigate_to_and_get_zero_slot_promotion(self, filtered_zero_slot_list)
        self.home_assertions.verify_action_type_in_slot0_ads(zero_slot, self.home_labels.LBL_AD_ACTION_UI_NAVIGATE)
        self.home_page.navigate_to_program_in_OTT_app_for_uiNavigateAction_action_type(self)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_11400980_c634_overlay_and_reconnect_after_foreground_event(self, get_overrides):
        """
        Verify that c634 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after foreground event.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400980
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C634")
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=360
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_17),
                               "The test is not applicable since Hydra v1.17")
    def test_11400981_c608_overlay_and_reconnect(self):
        """
        Verify that c608 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400981
        """
        if Settings.mso == "cableco3":
            params = "ManagedStreamerSignInManager,AuthenticationConfigurationSearch," \
                     "0,3,hostUnavailable,AutoTestFailExpected"
        else:
            params = "ManagedStreamerSignInManager,AuthenticationConfigurationGet," \
                     "0,3,hostUnavailable,AutoTestFailExpected"
        self.home_page.update_test_conf_and_reboot(fast=True, QUERY_RESPONSE_FAILURE_PROPERTIES=params)
        self.home_page.go_to_my_shows(self)
        self.home_page.wait_for_home_page_ds_error("C608")
        self.home_page.wait_for_condition_satisfied(self.home_page.is_prediction_bar_error_visible,
                                                    expected_result=False, timeout=400)
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "The test is not applicable since Hydra v1.18")
    def test_11400979_c605_overlay_and_reconnect(self):
        """
        Verify that c605 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400979
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True,
                                                   QUERY_RESPONSE_FAILURE_PROPERTIES="ManagedStreamerSignInManager,"
                                                                                     "AuthenticationConfigurationGet,"
                                                                                     "0,2,badArgument,"
                                                                                     "AutoTestFailExpected")
        self.home_page.wait_for_home_page_ds_error("C605")
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.wait_for_condition_satisfied(self.home_page.is_prediction_bar_error_visible,
                                                    expected_result=False, timeout=400)
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
        "The test is applicable only for Hydra v1.18 and higher"
    )
    def test_22208_c610_c806_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c610 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.xperi.com/browse/FRUM-2160
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C610")
        self.home_page.press_back_button()
        self.home_page.verify_whisper_shown("C806")
        self.home_page.press_back_button()
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=500
        )

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_11400985_c628_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c628 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400985
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C628")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=360
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_11400986_c629_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c629 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400986
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C629")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=600
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_11400983_c630_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c630 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400983
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C630")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=600
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_11400984_c631_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c631 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400984
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C631")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=600
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_11400982_c606_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c606 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/11400982
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C606")
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=540
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14707_c614_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c614 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-14707
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C614")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=500
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14714_c617_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c617 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-14714
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C617")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=500
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_15140_c690_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c690 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-15140
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C690")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=360
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_6466_c648_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c648 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-6466
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C648")
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=360
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    # TODO re-check after fix https://jira.xperi.com/browse/CLOUD-9761
    def test_6625_c649_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c649 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-6625
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C649")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=360
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_6643_c650_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c650 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-6643
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C650")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=500
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_6645_c660_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c660 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-6645
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C660")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=500
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    # TODO re-check after fix https://jira.xperi.com/browse/CLOUD-9762
    def test_17802_c675_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c675 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-17802
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C675")
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=500
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_17791_c671_overlay_and_reconnect(self, get_overrides):
        """
        Verify that c671 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-17791
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.wait_for_home_page_ds_error("C671")
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.wait_for_condition_satisfied(
            self.home_page.is_prediction_bar_error_visible, expected_result=False, timeout=420
        )
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "The test is not applicable since Hydra v1.18")
    def test_17873_c674_overlay_and_reconnect(self):
        """
        Verify that c674 error is displayed on app launch,
        error displayed on prediction strip after home screen is loaded and
        app restored to normal state after some time.

        XRay:
            https://jira.tivo.com/browse/FRUM-17873
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True,
                                                   QUERY_RESPONSE_FAILURE_PROPERTIES="ManagedStreamerSignInManager,"
                                                                                     "AuthenticationConfigurationGet,"
                                                                                     "0,2,middlemindError,"
                                                                                     "AutoTestFailExpected")
        self.home_page.wait_for_home_page_ds_error("C674")
        self.home_page.wait_for_condition_satisfied(self.home_page.is_prediction_bar_error_visible,
                                                    expected_result=False, timeout=500)
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.p1_regression
    @pytest.mark.vod
    @pytest.mark.notapplicable(Settings.is_unmanaged(),
                               reason="Test case is seperated for managed and unmanaged devices")
    def test_C14379824_managed_verify_home_after_selecting_vod_and_pressing_home(self):
        self.home_page.back_to_home_short()
        self.vod_page.go_to_vod(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SCREENTITLE)
        self.screen.base.press_down()
        self.vod_page.press_left_button()
        self.home_page.press_home_button_multiple_times(self, no_of_times=3)

    @pytest.mark.p1_regression
    @pytest.mark.vod
    @pytest.mark.notapplicable(Settings.is_managed(), reason="Test case is seperated for managed and unmanaged devices")
    def test_C14379824_unmanaged_verify_home_after_selecting_vod_and_pressing_home(self):
        self.home_page.back_to_home_short()
        self.vod_page.go_to_vod(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SCREENTITLE)
        self.screen.base.press_down()
        self.vod_page.press_left_button()
        self.screen.base.press_back()  # Back to home screen
        self.home_assertions.verify_home_title()

    @pytest.mark.p1_regression
    @pytest.mark.socu
    def test_T69584589_verify_watchTv_launches_socu(self):
        """
        Created on Jan 29th, 2021
        T69584589 - Verify that after pressing "Watch TV" button socu playback continue to play
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                           filter_socu=True, restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_strip(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.guide_assertions.verify_channel_title(self, focused_item)

    @pytest.mark.frumos_15
    @pytest.mark.msofocused
    @pytest.mark.ftux
    @pytest.mark.notapplicable(
        Settings.is_apple_tv(),
        reason="Feature is supported only by Android devices")
    @pytest.mark.notapplicable(
        Settings.is_managed() or Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
        reason="Feature is supported from streamer-1-15 release and by unmanaged devices only.")
    @pytest.mark.usefixtures("reset_tivo_eula_consent_status")
    @pytest.mark.xray("FRUM-1125")
    @pytest.mark.timeout(Settings.timeout)
    def test_388772364_accept_tivo_eula_in_ftux_screen(self):
        """
        Verify TiVo EULA screen after FTUX animation
        Xray: https://jira.xperi.com/browse/FRUM-1125
        """
        self.home_assertions.verify_ftux_eula_mode()
        self.home_page.select_menu(self.home_labels.LBL_ACCEPT)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_screen()

    @pytest.mark.sign_in_errors
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.9 and v1.11")
    def test_c11400985_c628_error_overlay(self):
        self.home_page.update_test_conf_and_reboot("device", QUERY_FAILURE_TYPE="ServiceLogin",
                                                   QUERY_FAILURE_TYPE_RANGES="1,1,internalError")
        if self.watchvideo_page.is_overlay_shown() and self.home_page.get_overlay_code() == self.home_labels.LBL_C628:
            self.screen.base.press_enter(2000)
            self.home_assertions.verify_home_title()
        else:
            self.home_assertions.verify_error_overlay_code(suppress_log=self.home_labels.LBL_C628)
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
            self.home_assertions.verify_home_title()

    @pytest.mark.sign_in_errors
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.9 and v1.11")
    def test_c11400979_c605_error_overlay(self):
        self.home_page.update_test_conf_and_reboot("device", QUERY_FAILURE_TYPE="AuthenticationConfigurationGet",
                                                   QUERY_FAILURE_TYPE_RANGES="1,5,badArgument")
        if self.watchvideo_page.is_overlay_shown() and self.home_page.get_overlay_code() == self.home_labels.LBL_C605:
            self.screen.base.press_enter(2000)
            self.home_assertions.verify_home_title()
        else:
            self.home_assertions.verify_error_overlay_code(suppress_log=self.home_labels.LBL_C605)
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
            self.home_assertions.verify_home_title()

    @pytest.mark.p1_regression
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="EAS supported only for managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    def test_14386463_verify_that_eas_message_is_not_shown_when_user_in_ott(self):
        """
        Verify that EAS message is not shown when user in OTT

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/14386463
        """
        self.screen.base.press_netflix()
        self.apps_and_games_assertions.verify_netflix_screen_with_package(self)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.apps_and_games_assertions.verify_netflix_screen_with_package(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="EAS supported only for managed devices")
    @pytest.mark.notapplicable(not Settings.is_cc3(), reason="EAS behavior described only for these MSO")
    def test_14386465_verify_that_eas_message_is_not_shown_when_user_is_in_screensaver(self):
        """
        Verify that EAS message is not shown when user in Screensaver

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/14386465
        This feature is not activated. Tracking under https://jira.tivo.com/browse/CA-10386
        """
        self.home_page.wait_for_screen_saver(time=34)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        time.sleep(5)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)

    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="EAS supported only for managed devices")
    @pytest.mark.notapplicable(not Settings.is_cc2(), reason="EAS behavior described only for these MSO")
    def test_14386466_verify_that_EAS_message_is_shown_when_user_is_in_Screensaver(self):
        """
        Verify that EAS message is shown when user in Screensaver

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/14386466
        """
        self.home_page.wait_for_screen_saver(time=34)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        time.sleep(5)
        self.home_assertions.verify_EAS_screen()

    @pytest.mark.sign_in_errors
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.9 and v1.11")
    def test_c11400983_c630_error_overlay(self):
        self.home_page.update_test_conf_and_reboot("device", QUERY_FAILURE_TYPE="ServiceLogin",
                                                   QUERY_FAILURE_TYPE_RANGES="1,1,authenticationFailed")
        if self.watchvideo_page.is_overlay_shown() and self.home_page.get_overlay_code() == self.home_labels.LBL_C630:
            self.screen.base.press_enter(2000)
            self.home_assertions.verify_home_title()
        else:
            self.home_assertions.verify_error_overlay_code(suppress_log=self.home_labels.LBL_C630)
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
            self.home_assertions.verify_home_title()

    @pytest.mark.sign_in_errors
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.9 and v1.11")
    def test_c11400986_c629_error_overlay(self):
        self.home_page.update_test_conf_and_reboot("device", QUERY_FAILURE_TYPE="ServiceLogin",
                                                   QUERY_FAILURE_TYPE_RANGES="1,1,externalError")
        if self.watchvideo_page.is_overlay_shown() and self.home_page.get_overlay_code() == self.home_labels.LBL_C629:
            self.screen.base.press_enter(2000)
            self.home_assertions.verify_home_title()
        else:
            self.home_assertions.verify_error_overlay_code(suppress_log=self.home_labels.LBL_C629)
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
            self.home_assertions.verify_home_title()

    @pytest.mark.xray("FRUM-1280")
    @pytest.mark.msofocused
    @pytest.mark.eas
    @pytest.mark.vision_tester
    @pytest.mark.p1_regression
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="EAS during Screensaver supported only on managed devices")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    def test_14386508_trigger_EAS_alert_on_screensaver_end_return_back_to_screensaver(self):
        """
        Xray: https://jira.xperi.com/browse/FRUM-1280
        Verify screensaver is shown after EAS is dismissed
        """
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.back_to_home_short()
        self.watchvideo_page.pause(3 * 60)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.home_page.pause(15, reason="Wait until eas message is dismissed and screensaver is started")
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)

    @pytest.mark.sign_in_errors
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.9 and v1.11")
    def test_c11400981_c608_error_overlay(self):
        self.home_page.update_test_conf_and_reboot("device", QUERY_FAILURE_TYPE="AuthenticationConfigurationGet",
                                                   QUERY_FAILURE_TYPE_RANGES="1,2,hostUnavailable")
        if self.watchvideo_page.is_overlay_shown() and self.home_page.get_overlay_code() == self.home_labels.LBL_C608:
            self.screen.base.press_enter(2000)
            self.home_assertions.verify_home_title()
        else:
            self.home_assertions.verify_error_overlay_code(suppress_log=self.home_labels.LBL_C608)
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
            self.home_assertions.verify_home_title()

    @pytest.mark.sign_in_errors
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.9 and v1.11")
    def test_c11400984_c631_error_overlay(self):
        self.home_page.update_test_conf_and_reboot("device", QUERY_FAILURE_TYPE="ServiceLogin",
                                                   QUERY_FAILURE_TYPE_RANGES="1,5,authenticationExpired")
        if self.watchvideo_page.is_overlay_shown() and self.home_page.get_overlay_code() == self.home_labels.LBL_C631:
            self.screen.base.press_enter()
            time.sleep(20)
            self.home_assertions.verify_home_title()
        else:
            self.home_assertions.verify_error_overlay_code(suppress_log=self.home_labels.LBL_C631)
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=1200000)
            self.home_assertions.verify_home_title()

    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("disable_video_providers")
    def test_8883022_prediction_bar_press_select_recording_no_providers_not_live(self):
        """
        Home - Prediction Bar - Press SELECT - Recording, no providers, not live

        https://testrail.tivo.com//index.php?/cases/view/8883022
        """
        recording = self.service_api.schedule_single_recording()
        self.my_shows_page.play_recording_and_check_prediction(self, recording[0][0])
        self.home_page.nav_to_show_on_prediction_strip(recording[0][0])
        self.watchvideo_assertions.press_select_and_verify_recording_is_played(self)

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               reason="Feature is for hydra-streamer-1-13 or later.")
    def test_14386481_footer_icon_user_active_animation(self):
        """
        Verify branding animation in footer while user is active at Home screen
        Testcase: https://testrail.tivo.com/index.php?/cases/view/14386481
        """
        self.home_page.go_to_my_shows(self)
        self.home_page.back_to_home_short()
        self.home_page.press_up_button(refresh=True)
        self.home_assertions.verify_footer_branding_icon_shown()
        self.home_assertions.verify_footer_branding_icon_animated()
        self.home_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.home_assertions.verify_footer_branding_icon_animated(animated=False, refresh=True)

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               reason="Feature is for hydra-streamer-1-13 or later.")
    def test_14386484_footer_icon_user_active_animation(self):
        """
        Verify branding animation in footer while user is active at My Shows screen
        Testcase: https://testrail.tivo.com/index.php?/cases/view/14386484
        """
        self.home_page.go_to_my_shows(self)
        self.home_page.press_up_button(refresh=True)
        self.home_assertions.verify_footer_branding_icon_shown()
        self.home_assertions.verify_footer_branding_icon_animated()
        self.home_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.home_assertions.verify_footer_branding_icon_animated(animated=False, refresh=True)

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               reason="Feature is for hydra-streamer-1-13 or later.")
    def test_14386480_footer_icon_user_idle_animation(self):
        """
        Verify branding animation in footer while user is idle at Home screen
        Testcase: https://testrail.tivo.com/index.php?/cases/view/14386480
        """
        self.menu_page.go_to_menu_screen(self)
        self.home_page.press_back_button(refresh=True)
        self.home_assertions.verify_footer_branding_icon_shown()
        self.home_assertions.verify_footer_branding_icon_animated(animated=False)
        self.home_page.pause(self.home_labels.LBL_FOOTER_ICON_IDLE_USER_TIMEOUT)
        self.home_assertions.verify_footer_branding_icon_animated(animated=True, refresh=True)

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               reason="Feature is for hydra-streamer-1-13 or later.")
    def test_14386483_footer_icon_user_idle_animation(self):
        """
        Verify branding animation in footer while user is idle at My Shows screen
        Testcase: https://testrail.tivo.com/index.php?/cases/view/14386483
        """
        self.home_page.go_to_my_shows(self)
        self.home_page.press_up_button(refresh=True)
        self.home_assertions.verify_footer_branding_icon_shown()
        self.home_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.home_assertions.verify_footer_branding_icon_animated(animated=False, refresh=True)
        self.home_page.pause(self.home_labels.LBL_FOOTER_ICON_IDLE_USER_TIMEOUT)
        self.home_assertions.verify_footer_branding_icon_animated(animated=True, refresh=True)

    @pytestrail.case("T312064624")
    @pytest.mark.ftux
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.usefixtures("cleanup_EAS")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.frumos_15
    @pytest.mark.platform_cert_smoke_test
    def test_312064624_verify_eas_on_ftux(self):
        """
        Testrail:
            https://testrail.tivo.com//index.php?/tests/view/312064624
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="false",
                                                   skip_animation=False, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False)
        # Sendig EAS alert on FTUX screens when TiVo app is launched for the first time
        self.home_page.accept_legal_acceptance_screens()
        self.home_page.verify_view_mode(self.home_labels.LBL_FTUX_ANIMATION_VIEW_MODE)
        # Sending EAS alert
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_eas_not_displayed()
        self.home_page.skip_ftux_animation()
        if Settings.is_unmanaged():
            if self.home_page.is_ftux_eula_view_mode():
                self.home_page.select_menu(self.home_labels.LBL_ACCEPT)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_ONEPASS_FTUX)
        self.home_page.verify_view_mode(self.home_labels.LBL_ONEPASS_FTUX_VIEW_MODE)
        # Sending EAS alert
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_eas_not_displayed()
        self.home_page.select_done(times=1)
        self.home_page.verify_view_mode(self.home_labels.LBL_STREAMINGAPPS_FTUX_VIEW_MODE)
        # Sending EAS alert
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_eas_not_displayed()
        self.home_page.select_done(times=1)
        if self.home_page.is_ftux_pc_settings_screen_view_mode():
            self.home_assertions.verify_ftux_pcsettings_screen()
            self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)
        # Sending EAS alert on FTUX screen when FTUX is opened from Setting
        self.menu_page.launch_quick_tour_from_help(self)
        self.home_page.verify_view_mode(self.home_labels.LBL_FTUX_ANIMATION_VIEW_MODE)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    @pytest.mark.timeout(Settings.timeout)
    def test_14378813_verify_dismiss_dimming_screen_button_back(self):
        """
        Dismiss Dimming screen - Buttons - Back

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14378813
        """
        self.home_page.update_test_conf_and_reboot(TIMEOUT_TO_DIMMING_SCREEN=60000)
        self.home_page.back_to_home_short()
        self.home_page.navigate_by_strip(self.home_labels.LBL_GUIDE_SHORTCUT)
        self.home_page.pause(60, "Waiting for the Dimming screen to appear")
        self.home_assertions.verify_view_mode(self.home_labels.LBL_DIMMING_SCREEN_VIEW_MODE)
        self.home_page.press_back_button()
        self.home_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)
        self.home_assertions.verify_expected_focused_menu_item(self.home_labels.LBL_GUIDE_SHORTCUT)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    @pytest.mark.timeout(Settings.timeout)
    def test_14378870_verify_dimming_screen_and_osd_behavior(self):
        """
        Dimming Screen - Black screen & OSD - Design

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14378870
        """
        self.home_page.update_test_conf_and_reboot(TIMEOUT_TO_DIMMING_SCREEN=60000)
        self.home_page.back_to_home_short()
        self.home_page.pause(60, "Waiting for the Dimming screen to appear")
        self.home_assertions.verify_view_mode(self.home_labels.LBL_DIMMING_SCREEN_VIEW_MODE)
        self.home_assertions.verify_osd_logo(self.home_labels.LBL_DIMMING_OSD_LOGO)
        self.home_assertions.verify_osd_text(self.home_labels.LBL_DIMMING_OSD_TEXT)
        self.home_assertions.verify_osd_changes_position()

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="EAS supported only for managed devices")
    def test_14388816_verify_eas_message_in_notification_panel(self):
        """
        Verify that EAS message is displayed when EAS was received in "Notification" overlay

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/14388816
        """
        self.home_page.goto_notification(self)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.screen.base.press_back()
        self.home_assertions.verify_home_title()

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="EAS supported only for managed devices")
    def test_14389288_verify_eas_message_in_device_settings(self):
        """
        Verify that EAS message is displayed if user in Android settings

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/14389288
        """
        self.menu_page.go_to_device_settings(self)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.screen.base.press_back()
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()

    # @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_20931422_domain_token_expiration_interval(self):
        self.home_page.update_test_conf_and_reboot("device", BUG_514565_HACK_DOMAIN_TOKEN_EXPIRATION_INTERVAL="200")
        self.home_page.clear_cache_launch_hydra_app()
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_BRIDGE_STATUS_DOWN)
        self.home_page.screen.relaunch_hydra_app(reboot=True)
        self.home_assertions.validate_disconnected_state(self)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, live=False)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_372870770_live_tv_recovery_in_hydra(self, get_overrides):
        """
        Verify that PartnerBusinessRulesModel do retry operation by timer inside of Hydra app

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870770
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, **get_overrides)
        self.home_page.back_to_home()
        self.home_page.get_live_tv_error_status(self, 'V404')
        self.home_page.wait_for_condition_satisfied(
            self.home_page.get_live_tv_error_status, fun_args=(self, 'V404'), timeout=360, expected_result=False
        )

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_372870780_live_tv_recovery_by_foreground_event(self, get_overrides):
        """
        Verify that PartnerBusinessRulesModel do retry operation after foreground event

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870780
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, **get_overrides)
        self.home_page.back_to_home()
        self.home_page.get_live_tv_error_status(self, 'V404')
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.wait_for_condition_satisfied(
            self.home_page.get_live_tv_error_status, fun_args=(self, 'V404'), timeout=360, expected_result=False
        )

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_372870783_vod_recovery_in_hydra(self, get_overrides):
        """
        Verify that VodBrowseModel do retry operation by timer inside of Hydra app 1

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870783
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.back_to_home()
        if not self.vod_page.get_vod_error_status(self):
            raise ValueError("VoD is available with overrides applied!")
        self.home_page.wait_for_condition_satisfied(
            self.vod_page.get_vod_error_status, fun_args=[self], timeout=360, expected_result=False
        )
        self.vod_assertions.verify_screen_title(self.vod_labels.LBL_ON_DEMAND)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_372870795_vod_recovery_by_foreground(self, get_overrides):
        """
        Verify that VodBrowseModel recovers by foreground signal

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870795
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.back_to_home()
        if not self.vod_page.get_vod_error_status(self):
            raise ValueError("VoD is available with overrides applied!")
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.wait_for_condition_satisfied(
            self.vod_page.get_vod_error_status, fun_args=[self], timeout=360, expected_result=False
        )
        self.vod_assertions.verify_screen_title(self.vod_labels.LBL_ON_DEMAND)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_372870781_rating_limits_recovery_in_hydra(self, get_overrides):
        """
        Verify that RatingInstructionsModel do retry operation by timer inside of Hydra app

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870781
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.back_to_home()
        if self.menu_page.get_parental_control_menu_item_status(self, self.menu_labels.LBL_SET_RATING_LIMITS):
            raise ValueError("Item is present with overrides applied!")
        self.home_page.wait_for_condition_satisfied(
            self.menu_page.get_parental_control_menu_item_status,
            fun_args=(self, self.menu_labels.LBL_SET_RATING_LIMITS),
            timeout=400
        )
        self.menu_assertions.verify_parental_controls_menu_items([self.menu_labels.LBL_SET_RATING_LIMITS])

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(
        Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
        "The test is applicable only for Hydra v1.13 and higher"
    )
    def test_372870793_rating_limits_recovery_by_foreground(self, get_overrides):
        """
        Verify that RatingInstructionsModel recovers by foreground signal

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870793
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, **get_overrides)
        self.home_page.back_to_home()
        if self.menu_page.get_parental_control_menu_item_status(self, self.menu_labels.LBL_SET_RATING_LIMITS):
            raise ValueError("Item is present with overrides applied!")
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.wait_for_condition_satisfied(
            self.menu_page.get_parental_control_menu_item_status,
            fun_args=(self, self.menu_labels.LBL_SET_RATING_LIMITS),
            timeout=120
        )
        self.menu_assertions.verify_parental_controls_menu_items([self.menu_labels.LBL_SET_RATING_LIMITS])

    @pytest.mark.solutions_tests
    @pytest.mark.xray("FRUM-877")
    @pytest.mark.notapplicable(Settings.is_cc11() or Settings.is_cc5())
    @pytest.mark.notapplicable(Settings.is_external_mso())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("cleanup_ftux")
    @pytest.mark.frumos_15
    def test_c5313445_c5313450_license_plate_screen_onboarding(self):
        """
        Verify the license binding flow and upon successful license binding should take to home screen
        :return:
        """
        if not self.provisioning_page.get_authentication_lp_url():
            pytest.skip("Do not follow LP binding flow")
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_out(self)
        if Settings.is_managed():
            self.screen.base.clear_data()
            self.screen.base.grant_app_permissions()
            if self.home_page.is_overlay_shown():
                self.screen.base.press_enter()
        self.pps_api_helper.remove_device_provisioning(Settings.ca_device_id)
        self.iptv_prov_api.reset_device(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn), Settings.tsn)
        self.screen.base.launch_application(Settings.app_package)
        self.home_page.bind_license(self)

    @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("set_bridge_status_up")
    def test_20931420_playback_verification_with_youtube_in_background(self):
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, live=False, filter_channel=True)
        self.home_page.playback_for_sometime(self, channel[0][0])
        self.home_page.screen.base.press_youtube()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.home_page.screen.base.pause(1800)
        self.home_page.press_home_button()
        self.watchvideo_assertions.verify_app_is_foreground(Settings.app_package, state=True)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.press_home_button()
        self.watchvideo_assertions.verify_app_is_foreground(Settings.app_package, state=True)
        self.home_page.go_to_guide(self)
        self.home_assertions.validate_disconnected_state(self)
        self.home_page.go_to_my_shows(self)
        error_expression = f"{self.home_labels.LBL_ERROR_CODE_C228}.*contact CableCo"
        self.home_assertions.verify_predictions_error_message(self, error_expression)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.screen.base.pause(60)
        self.home_page.back_to_home_short()
        self.home_page.playback_for_sometime(self, channel[0][0])

    @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("set_bridge_status_up")
    def test_20933835_guide_screen_verification(self):
        self.home_page.wait_for_screen_saver(time=40)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.verify_key_press_to_wake_up_device(self)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.screen.base.pause(120)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.p1_regression
    @pytest.mark.vod
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_4863839_info_cards_entry_points(self):
        """
        Info Cards - Entry Points:
            1) My Shows program folder
            2) Program screen.
            3) Predictions Bar.
            4) VOD Gallery

        Testrail link : https://testrail.tivo.com//index.php?/cases/view/4863839
        """

        # My Shows program folder
        program = self.api.record_currently_airing_shows(number_of_shows=1)
        if not program:
            pytest.skip("Unable to create recording")
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_menu_by_substring(self.my_shows_page.convert_special_chars(program[0][0]), False)
        self.screen.base.press_info()
        self.home_assertions.verify_infocard_on_long_key_press()

        # Program screen.
        self.home_page.go_to_guide(self)
        self.guide_page.select_and_get_more_info(self)
        self.screen.base.press_info()
        self.home_assertions.verify_infocard_on_long_key_press()

        # Predictions Bar.
        self.home_page.back_to_home_short()
        self.screen.base.press_down()
        self.screen.base.press_info()
        self.home_assertions.verify_infocard_on_long_key_press()

        # VOD Gallery
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.home_page.wait_for_screen_ready()
        self.screen.base.press_info()
        self.home_assertions.verify_infocard_on_long_key_press()

    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13))
    @pytest.mark.notapplicable(Settings.is_external_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.xray('FRUM-712')
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Messaging feature is applicable to Managed boxes only")
    @pytest.mark.usefixtures("setup_cleanup_remove_all_messages_from_client")
    def test_12790032_verify_message_functionality(self, request):
        """
        Verify that there's no message pop-up overlay when re-entering the Home screen
        after selecting Delete this message option in the overlay

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/12789829
            https://testrail.tivo.com//index.php?/cases/view/12790031
            https://testrail.tivo.com//index.php?/cases/view/12790032

        Xray:
            https://jira.xperi.com/browse/FRUM-910 (User Message general view)
            https://jira.xperi.com/browse/FRUM-1004 (Remind me later option test)
            https://jira.xperi.com/browse/FRUM-712 (Delete this option test)
        """
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.home_page.create_and_publish_message(request)
        self.home_page.press_back_button(refresh=False)
        # Checking User Message view
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_DEFAUL_SUBJECT)
        self.home_assertions.verify_overlay_body(self.home_labels.LBL_DEFAULT_TEXT)
        self.home_assertions.verify_overlay_line_separator()
        self.menu_assertions.verify_menu_item_available(
            [self.home_labels.LBL_REMIND_ME_LATER_OPTION, self.home_labels.LBL_DELETE_THIS_MESSAGE_OPTION],
            mode="equal")
        # Checking Remind me later option
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.home_assertions.verify_overlay_shown(expected=False)
        self.home_page.go_to_guide(self)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_DEFAUL_SUBJECT)
        # Checking Delete this message option
        self.home_page.select_menu(self.home_labels.LBL_DELETE_THIS_MESSAGE_OPTION)
        self.home_assertions.verify_overlay_shown(expected=False)
        self.home_page.go_to_guide(self)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_shown(expected=False)

    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13))
    @pytest.mark.notapplicable(Settings.is_external_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Messaging feature is applicable to Managed boxes only")
    @pytest.mark.usefixtures("setup_cleanup_remove_all_messages_from_client")
    def test_19782934_verify_3rd_message_shown_after_dismissing_2_prev_ones(self, request):
        """
        Verify that the 3rd message shows up after dismissing 2 previous ones when sending this 3rd message
        while staying on the Home screen with displayed previous message

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/19782934
        """
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.home_page.create_and_publish_message(request, subject=self.home_labels.LBL_SUBJECT_MESSAGE_1)
        self.home_page.create_and_publish_message(request, subject=self.home_labels.LBL_SUBJECT_MESSAGE_2)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_SUBJECT_MESSAGE_1)
        self.home_page.create_and_publish_message(request, subject=self.home_labels.LBL_SUBJECT_MESSAGE_3)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_SUBJECT_MESSAGE_1)
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_SUBJECT_MESSAGE_2)
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_SUBJECT_MESSAGE_3)

    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13))
    @pytest.mark.notapplicable(Settings.is_external_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Messaging feature is applicable to Managed boxes only")
    @pytest.mark.usefixtures("setup_cleanup_remove_all_messages_from_client")
    def test_19782326_verify_expired_message_is_not_displayed(self, request):
        """
        Verify that expired message does not appear when re-entering the Home screen

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/19782326
        """
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.home_page.create_and_publish_message(
            request,
            expr_date=(datetime.utcnow() + timedelta(minutes=2)).strftime(self.service_api.MIND_DATE_TIME_FORMAT))
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_DEFAUL_SUBJECT)
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.home_assertions.verify_overlay_shown(expected=False)
        self.home_page.go_to_guide(self)
        self.guide_page.pause(120, "Waiting for the message to expire")
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_shown(expected=False)

    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13))
    @pytest.mark.notapplicable(Settings.is_external_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Messaging feature is applicable to Managed boxes only")
    @pytest.mark.usefixtures("setup_cleanup_remove_all_messages_from_client")
    def test_frum_34739_verify_no_message_after_deleting_it_on_service(self, request):
        """
        Pop Up Overlay - Message not yet deleted by user - Remove message on Service side.
        Verify that there's no message pop-up overlay when re-entering the Home screen
        after removing message on the service.

        Xray:
            https://jira.xperi.com/browse/FRUM-34739
        """
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        message = self.home_page.create_and_publish_message(request)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_DEFAUL_SUBJECT)
        self.home_page.send_fcm_or_nsr_notification(req_type=NotificationSendReqTypes.FCM,
                                                    payload_type=RemoteCommands.REMOVE_MESSAGE,
                                                    remove_message_id=message['messageId'])
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.home_assertions.verify_overlay_shown(expected=False)
        self.home_page.go_to_guide(self)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_shown(expected=False)

    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-1278")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_start_tivo_app")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11))
    def test_20949500_game_controllers_full_automated_scenario(self):
        """
        Testrail link : https://testrail.tivo.com//index.php?/cases/view/20949500
        """
        self.home_page.back_to_home_short()
        self.screen.base.press_gamepad_x()
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_title()
        self.guide_page.highlight_first_cell()
        self.screen.base.press_gamepad_left()
        self.guide_page.wait_for_guide_next_page()
        self.guide_assertions.verify_channel_cell_is_highlighted()
        self.screen.base.press_gamepad_a()
        self.home_assertions.verify_overlay_title(self.liveTv_labels.LBL_CHANNEL_OPTIONS)
        self.screen.base.press_gamepad_b()
        self.home_assertions.verify_overlay_shown(expected=False)
        self.screen.base.press_gamepad_right()
        self.guide_page.wait_for_guide_next_page()
        self.screen.base.press_gamepad_y()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_INFO_OVERLAY)
        self.home_assertions.verify_overlay_shown()
        self.screen.base.press_gamepad_home()
        self.home_assertions.verify_home_screen_after_pressing_home()

    @pytest.mark.change_device_name
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.usefixtures("reset_language_code_to_en_us")
    def test_c20941134_c20941123_device_name_change(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20941134
        https://testrail.tivo.com/index.php?/cases/view/20941123
        Returns:
        """
        device_language = ["Spanish", "English"]
        for language in device_language:
            if language == "Spanish":
                self.system_page.change_language(user_language_code="en-ES")
            if language == "English":
                self.system_page.change_language(user_language_code="en-US")
            device_names = ["symbols", "spl_char", "spanish_char", "english_char"]
            self.screen.base.stop_app(Settings.app_package)
            self.screen.base.launch_application(Settings.app_package)
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=20000)
            for name in device_names:
                if language == "Spanish" and name == "spanish_char":
                    self.system_page.change_device_name(device_name="21 20 23 22 20 23 21 19 23", device_name_key=True)
                if name == "symbols":
                    self.system_page.change_device_name(device_name="20 20 20 23 19 80 23 80 19 23 22 23 22 23 22 23",
                                                        device_name_key=True)
                if name == "spl_char":
                    self.system_page.change_device_name(device_name="!@#$%&")
                if name == "english_char":
                    self.system_page.change_device_name(device_name="Test Automation 123")
                self.home_page.clear_cache_launch_hydra_app()
                self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=20000)
                self.home_assertions.verify_home_mode()

    @pytest.mark.ftux
    @pytest.mark.usefixtures("set_screen_saver_default_value")
    @pytest.mark.usefixtures("cleanup_set_sleep_timeout_to_never")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.skipif(Settings.is_technicolor(), reason="(PARTDEFECT-1986)Hospitality boxes dont support ftux")
    def test_20949499_enter_standby_and_wakeup_in_ftux(self):
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=True, skip_onepass=True,
                                                   skip_apps=False, skip_pcsetting=False, SKIP_FTUX="false")
        self.home_page.set_sleep_timeout(time_ms=(300 + 180 + 5 + 5) * 1000)
        self.home_page.wait_for_screen_saver(time=300 + 5)
        self.home_page.pause(180 + 5, "Waiting the box to enter standby")
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_ftux_streamingapps_screen()

    @pytest.mark.p1_regression
    @pytest.mark.livetv
    def test_20951827_verify_liveTv_is_running_in_background_when_exit_from_wtw(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20951827
        """
        self.menu_page.enable_full_screen_video_on_home(self)
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        if Settings.is_managed():
            self.screen.base.press_home()
        else:
            self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
            self.screen.base.press_back()
            self.guide_page.wait_for_screen_ready()
            self.guide_assertions.verify_guide_title()
            self.screen.base.press_back()
        self.guide_page.wait_for_screen_ready()
        self.home_assertions.verify_home_title()
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)
        for i in range(random.randint(1, 10)):
            self.screen.base.press_down()
        if Settings.is_managed():
            self.screen.base.press_home()
        else:
            self.screen.base.press_back()
        self.guide_page.wait_for_screen_ready()
        self.home_assertions.verify_home_title()
        self.vod_assertions.verify_video_streaming()

    @pytest.mark.welcome_screen
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_20950989_verify_welcome_screen_user_idle(self):
        """
        testrail: https://testrail.tivo.com/index.php?/cases/view/20950989
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, USER_IDLE_TIMEOUT_MS=60000)
        self.home_page.back_to_home_short()
        self.home_page.wait_for_screen_saver(time=90)
        self.screen.base.stop_app(Settings.app_package)
        self.screen.base.launch_application(Settings.app_package)
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_WELCOME_SCREEN, timeout=30000)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WELCOME_SCREEN)

    @pytest.mark.welcome_screen
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_20951004_verify_welcome_screen_timeout(self):
        """
        testrail: https://testrail.tivo.com/index.php?/cases/view/20951004
        """
        self.home_page.update_test_conf_and_reboot(
            "device", fast=True, USER_IDLE_TIMEOUT_MS=60000, WELCOME_SPLASH_TIMEOUT_MS=60000)
        self.home_page.back_to_home_short()
        self.home_page.wait_for_screen_saver(time=90)
        self.screen.base.stop_app(Settings.app_package)
        self.screen.base.launch_application(Settings.app_package)
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_WELCOME_SCREEN, timeout=30000)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WELCOME_SCREEN)
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_HOME_VIEW_MODE, timeout=60000)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)

    @pytest.mark.welcome_screen
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_20950996_verify_welcome_screen_dismiss_by_press_ok_button(self):
        """
        testrail: https://testrail.tivo.com/index.php?/cases/view/20950996
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, USER_IDLE_TIMEOUT_MS=60000)
        self.home_page.back_to_home_short()
        self.home_page.wait_for_screen_saver(time=90)
        self.screen.base.stop_app(Settings.app_package)
        self.screen.base.launch_application(Settings.app_package)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_WELCOME_SCREEN, timeout=30000)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WELCOME_SCREEN)
        self.home_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_HOME_VIEW_MODE, timeout=30000)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)

    @pytest.mark.welcome_screen
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_220951080_verify_welcome_screen_user_active(self):
        """
        testrail: https://testrail.tivo.com/index.php?/cases/view/20951080
        """
        self.home_page.back_to_home_short()
        self.screen.base.stop_app(Settings.app_package)
        self.screen.base.launch_application(Settings.app_package)
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_HOME_VIEW_MODE, timeout=30000)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)

    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("enable_video_providers")
    def test_8883023_prediction_bar_press_select_recording_providers_not_live(self):
        """
        Home - Prediction Bar - Press SELECT - Recording, providers, not live
        https://testrail.tivo.com//index.php?/cases/view/8883023
        """
        offer = self.service_api.get_offer_with_parameters(collection_type='series')
        if not offer:
            pytest.skip("Test requires OTT program.")
        channel = offer['channel_item'].channel_number
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        recording = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.back_to_home_short()
        self.my_shows_page.play_recording_and_check_prediction(self, recording)
        self.home_page.nav_to_show_on_prediction_strip(recording)
        self.watchvideo_assertions.press_select_and_verify_recording_is_played(self)

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(not Settings.is_apple_tv(), reason="Applicable only for Apple TV")
    def test_10197100_verify_behaviour_of_menu_button_on_appletv(self):
        """
        Verify that user is not redirected to apple tv home screen after pressing MENU.
        This case is enhanced for https://testrail.tivo.com//index.php?/cases/view/10197098
        """
        self.home_page.back_to_home_short()
        self.screen.base.press_right()  # To Highlight Watch TV
        self.screen.base.press_right()  # To highlight My Shows
        self.screen.base.press_menu()
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_assertions.verify_focus_is_on_menu(self)
        self.home_page.screen.base.pause(5)  # delay to press menu
        self.screen.base.press_menu()
        self.screen.base.verify_foreground_app(Settings.app_package)

    @pytest.mark.service_reliability
    def test_21558037_reboot_the_device(self):
        """
        (Power Cycle) to Home/TV background (no FTUX)
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.system_page.launch_device_settings_screen()
        time.sleep(2)
        self.guide_page.timestamp_test_start()
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME, reboot=True, wait_reboot=600)
        time.sleep(0.5)  # wait to load live tv in background
        self.system_page.launch_device_settings_screen()
        time.sleep(3)
        self.guide_page.timestamp_test_end()
        self.screen.base.press_back(time=5)

    @pytest.mark.service_reliability
    def test_home_button_press(self):
        """
        Test Home Button Press
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.system_page.launch_device_settings_screen()
        self.menu_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "settings")
        self.guide_page.timestamp_test_start()
        self.home_page.press_home_button()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME)
        time.sleep(2)  # wait to load live tv in background
        self.home_assertions.verify_home_title()
        self.system_page.launch_device_settings_screen()
        time.sleep(3)
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    def test_21558038_restart_ui(self):
        """
        UI restart
        """
        self.system_page.launch_device_settings_screen()
        time.sleep(2)
        self.guide_page.timestamp_test_start()
        self.home_page.force_stop_app_from_UI()
        self.home_page.launch_app_through_UI()
        time.sleep(300)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.system_page.launch_device_settings_screen()
        time.sleep(3)
        self.guide_page.timestamp_test_end()
        self.home_page.press_home_button()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()

    @pytest.mark.service_reliability
    def test_restart_app_after_clear_data(self):
        """
        Restart APP after clear data.
        """
        self.system_page.launch_device_settings_screen()
        time.sleep(2)
        self.guide_page.timestamp_test_start()
        self.system_page.go_to_apps_and_select_hydra_app_and_clear_data()
        self.home_page.force_stop_app_from_UI()
        self.home_page.launch_app_through_UI()
        self.home_page.pause(180, "Waiting for app to launch..")
        focused_app = self.driver.driver.get_current_focused_app()
        self.home_page.log.info(f"focused_app: {focused_app}")
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_LEGAL_EULA_SCREEN, timeout=60000)
        self.screen.base.stop_app("com.github.uiautomator")
        self.home_page.skip_ftux()
        self.guide_page.timestamp_test_end()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=60000)
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.ftux
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.usefixtures("set_screen_saver_default_value")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.timeout(Settings.timeout)
    def test_21566850_ftux_screen_after_waking_from_sleep(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/21566850
        """
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=True, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False, SKIP_FTUX="false")
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_ftux_view_mode()
        self.driver.set_sleep_timeout(15 * 60 * 1000)
        self.home_page.wait_for_screen_saver(time=360)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.pause(600)
        self.screen.base.press_back()
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_ftux_view_mode()

    @pytest.mark.xray('FRUM-1129', 'FRUM-1092', 'FRUM-1269')
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("relaunch_hydra_app")
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.FCM, NotificationSendReqTypes.NSR])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.is_dev_host(), reason="Does not support reboot")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_20959161_verify_select_restart_now_and_check_service_login_date(self, req_type):
        """
        Push Notification Overlay - Options - Restart now.
        Verify if 'Last service login' data is updated.

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20959172
            https://testrail.tivo.com/index.php?/cases/view/20959162
            https://testrail.tivo.com/index.php?/cases/view/20959161

        Xray:
            https://jira.xperi.com/browse/FRUM-1129 (RemoteCommands.SERVICE_CALL overlay view)
            https://jira.xperi.com/browse/FRUM-1092 (Remind me later option)
            https://jira.xperi.com/browse/FRUM-1269 (Restart now/Exit now option)
        """
        self.home_page.validate_fcm_nsr_mts_req_usage(req_type, RemoteCommands.SERVICE_CALL, True)
        self.menu_page.go_to_system_information_in_system_and_account(self)
        sl_1 = datetime.strptime(
            self.menu_page.get_option_value_from_system_information(self.menu_labels.LBL_LAST_SERVICE_LOGIN),
            "%A %B %d, %Y, %I:%M%p")
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL)
        self.home_page.press_back_button(refresh=False, repeat_count=3)
        # Checking RemoteCommands.SERVICE_CALL overlay view
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_assertions.verify_overlay_body(self.home_labels.LBL_BODY_RESTART_TO_APPLY_UPDATES)
        self.home_assertions.verify_overlay_line_separator()
        self.menu_assertions.verify_menu_item_available(
            [self.home_labels.LBL_RESTART_NOW, self.home_labels.LBL_REMIND_ME_LATER_OPTION], mode="equal")
        # Checking Remind me later option
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.home_assertions.verify_overlay_shown(expected=False)
        self.home_page.go_to_guide(self)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        # Checking Restart now/Exit now option
        self.home_page.select_menu(self.home_labels.LBL_RESTART_NOW)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.menu_page.go_to_system_information_in_system_and_account(self)
        sl_2 = datetime.strptime(
            self.menu_page.get_option_value_from_system_information(self.menu_labels.LBL_LAST_SERVICE_LOGIN),
            "%A %B %d, %Y, %I:%M%p")
        assert_that(sl_2 > sl_1, "Last service login date was not changed after making serviceLogin")

    @pytest.mark.xray('FRUM-1293')
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("relaunch_hydra_app")
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.FCM, NotificationSendReqTypes.NSR])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.is_dev_host(), reason="Does not support reboot")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_20959168_verify_select_refresh_acc_and_usr_data_and_check_service_login_date(self, req_type):
        """
        Push Notification Overlay - Options - Remind me later - Help screen - Refresh Account & User Data.
        Verify if 'Last service login' data is updated.

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20959168

        Xray:
            https://jira.xperi.com/browse/FRUM-1293
        """
        self.home_page.validate_fcm_nsr_mts_req_usage(req_type, RemoteCommands.SERVICE_CALL, True)
        self.menu_page.go_to_system_information_in_system_and_account(self)
        sl_1 = datetime.strptime(
            self.menu_page.get_option_value_from_system_information(self.menu_labels.LBL_LAST_SERVICE_LOGIN),
            "%A %B %d, %Y, %I:%M%p")
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL)
        self.home_page.press_back_button(refresh=False, repeat_count=3)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_HELP)
        self.menu_page.select_menu_items(self.menu_labels.LBL_HELP_REFRESH_ACC_AND_USER_DATA)
        self.home_assertions.verify_overlay_title(self.menu_labels.LBL_REFRESH_OVERLAY_TITLE)
        self.home_page.select_menu(self.menu_labels.LBL_REFRESH_OK_OPTION)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.menu_page.go_to_system_information_in_system_and_account(self)
        sl_2 = datetime.strptime(
            self.menu_page.get_option_value_from_system_information(self.menu_labels.LBL_LAST_SERVICE_LOGIN),
            "%A %B %d, %Y, %I:%M%p")
        assert_that(sl_2 > sl_1, "Last service login date was not changed after making serviceLogin")

    @pytest.mark.xray('FRUM-1331')
    @pytest.mark.msofocused
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.PURCHASE_PIN)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.PURCHASE_PIN)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.FCM, NotificationSendReqTypes.NSR])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.is_dev_host(), reason="Does not support reboot")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_20959476_verify_push_notification_purchase_pin_not_shown_in_pc_settings(self, request,
                                                                                     feature_status_feature,
                                                                                     device_info_store_feature,
                                                                                     req_type):
        """
        Set transactionsEnabled = false - Send ServiceLogin Push Notification - Restart box - Check Purchase PIN in UI.
        Verify that the Purchase PIN option is not available/not displayed in UI.

        Note:
            According to https://jira.tivo.com/browse/IPTV-23642, transactionsEnabled PPS param should not
            be used in this test

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20959476

        Xray:
            https://jira.xperi.com/browse/FRUM-1331
        """
        request.config.cache.set("is_relaunch_needed", False)  # False to avoid extra app relaunch
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, True)
        self.guide_page.relaunch_hydra_app()
        self.menu_page.go_to_settings(self)
        self.menu_page.select_menu_items(self.menu_page.get_parental_controls_menu_item_label())
        self.menu_assertions.verify_menu_item_available(self.menu_labels.LBL_PURCHASE_CONTROLS, expected=True)
        self.home_page.go_to_guide(self)
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, False)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_RESTART_NOW)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.menu_page.go_to_settings(self)
        self.menu_page.select_menu_items(self.menu_page.get_parental_controls_menu_item_label())
        self.menu_assertions.verify_menu_item_available(self.menu_labels.LBL_PURCHASE_CONTROLS, expected=False)

    @pytest.mark.usefixtures("relaunch_hydra_app")
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.FCM, NotificationSendReqTypes.NSR])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.is_dev_host(), reason="Does not support reboot")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_20959170_verify_push_notification_ndvr_overlay(self, req_type):
        """
        [Managed][Unmanaged] Have Service Call Overlay - Send nDVR Overlay.
        Check that nDVR Enabled/Disabled overlay is shown over the RemoteCommands.SERVICE_CALL overlay and
        RemoteCommands.SERVICE_CALL overlay is not shonw after selecting Restart the box option on nDVR overlay

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20959170

        Xray:
            https://jira.xperi.com/browse/FRUM-1283
        """
        self.home_page.validate_fcm_nsr_mts_req_usage(req_type, RemoteCommands.SERVICE_CALL, True)
        self.home_page.go_to_guide(self)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.service_api.get_ndvr_state_changed_notification()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RECORDING_DISABLED)
        self.home_page.select_menu(self.home_labels.LBL_RESTART_THE_BOX_NDVR)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.home_page.back_to_home_short()  # if RemoteCommands.SERVICE_CALL overlay is shown, this step will fail

    @pytest.mark.xray("FRUM-91316")
    @pytest.mark.update_test_conf
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_91316_verify_watch_now_option_visible_after_token_expired(self):
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.home_page.update_test_conf_and_reboot("device", BUG_514565_HACK_DOMAIN_TOKEN_EXPIRATION_INTERVAL="360")
        self.home_page.clear_cache_launch_hydra_app()
        if self.home_page.is_overlay_shown():
            raise AssertionError("Error overlay shown")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytest.mark.xray("FRUM-91309")
    @pytest.mark.internal_storage
    @pytest.mark.usefixtures("free_up_internal_memory_by_uninstalling")
    @pytest.mark.usefixtures("fill_internal_storage_by_installing_apps")
    def test_frum_91309_fill_internal_memory_and_clear_data_launch_app(self):
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        available_data = self.home_page.get_data_in_mb()
        if int(available_data) > self.home_labels.LBL_MINIMUM_MEMORY:
            pytest.fail("Internal storage is not full. install some apps")
        self.home_page.clear_cache_launch_hydra_app(skip_animation=True, skip_onepass=True, skip_apps=False)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()

    @pytest.mark.service_reliability
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_1234_expire_service_token_and_perform_login(self):
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.home_page.screen.base.driver.modify_tcdui_conf("device",
                                                            BUG_514565_HACK_DOMAIN_TOKEN_EXPIRATION_INTERVAL="300")
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.guide_page.timestamp_test_start()
        self.home_assertions.verify_domain_token_renew_silently(self)

    @pytest.mark.frumos_15
    @pytest.mark.ftux
    @pytest.mark.xray("FRUM-1226")
    @pytest.mark.msofocused
    @pytest.mark.notapplicable(Settings.mso not in (Settings.is_millicom(), Settings.is_llapr(), Settings.is_llacr()),
                               "FTUXPC screen available for LLA and Millicom only.")
    def test_C21558571_verify_ftux_pc_setting(self):
        """
        verify that user able to set the PC setting cofiguration in the FTUX PC setting screen
        Xray: https://jira.xperi.com/browse/FRUM-1226
        """
        self.home_page.clear_cache_launch_hydra_app(skip_animation=True, skip_onepass=True, skip_apps=True,
                                                    skip_pcsetting=False)
        self.home_assertions.verify_ftux_pcsettings_screen()
        self.screen.base.press_enter()
        self.menu_page.select_menu_items(self.menu_page.get_parental_controls_menu_item_label())
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SET_RATING_LIMITS)
        self.menu_page.set_rating_limits(rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)
        self.menu_page.menu_press_back()
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)
        self.menu_page.menu_press_back()
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.frumos_15
    @pytest.mark.ftux
    @pytest.mark.notapplicable(Settings.mso not in (Settings.is_millicom(), Settings.is_llapr(), Settings.is_llacr()),
                               "FTUXPC screen available for LLA and Millicom only.")
    def test_C21558569_verify_ftux_skip_option(self):
        self.home_page.clear_cache_launch_hydra_app(skip_animation=True, skip_onepass=True, skip_apps=True,
                                                    skip_pcsetting=False)
        self.home_assertions.verify_ftux_pcsettings_screen()
        self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytestrail.case("C13511482")
    @pytest.mark.usefixtures("cleanup_re_activate_and_sign_in")
    def test_13511482_new_feature_overlay(self):
        """
        Description: To verify the overlay notification for the new only feature
        test rail: https://testrail.tivo.com/index.php?/cases/view/13511482
        """
        self.home_page.clear_cache_launch_hydra_app()
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)
        time.sleep(120)
        self.home_assertions.verify_disconnected_state_overlay("OnePass and Recordings Default Settings Updated")

    @pytest.mark.xray("FRUM-91273")
    @pytest.mark.GA
    def test_frum_91273_launch_netflix_from_GA_and_verify_source_type(self):
        self.home_page.launch_app_from_GA(self, self.home_labels.LBL_NETFLIX)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_11)

    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "package not installed")
    def test_634268940_check_global_assist_triggering_feature_is_set_correctly(self):
        """
        Check GLOBAL_ASSIST_TRIGGERING feature is correctly set
        """
        result = self.screen.base.is_feature_package_installed(self.home_labels.LBL_GLOBAL_ASSIST_TRIGGERING)
        if not result:
            pytest.fail("GLOBAL_ASSIST_TRIGGERING is not set correctly")
        version = self.screen.base.driver.get_tivo_app_version(self.home_labels.LBL_KATNISS)
        self.home_assertions.verify_version(version)

    @pytestrail.case("T634292417")
    @pytest.mark.p1_regression
    def test_T634292417_check_unique_serial_num(self):
        """
        Test rail : https://testrail.tivo.com//index.php?/tests/view/634292417
        """
        self.home_assertions.verify_device_serial_number()

    @pytest.mark.predictionbar
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_389366352_prediction_bar_with_recording(self, request):
        """
            Home - Prediction Bar - Parental Controls - Played from a recording
            To Verify pressing SELECT button on a tile in Prediction Bar with recording
            Testrail:
                https://testrail.tivo.com//index.php?/tests/view/389366352
        """
        self.home_page.back_to_home_short()
        show = self.home_page.get_recordable_prediction_content(self)
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        show = self.my_shows_page.remove_service_symbols(show[0])
        programs = self.home_page.get_prediction_bar_shows(self)
        status = self.home_assertions.is_content_available_in_prediction(self, show, programs)
        if not status:
            pytest.skip("No recorded program found on prediction")
        self.home_page.navigate_by_strip(show)
        self.watchvideo_assertions.press_select_and_verify_streaming(self)
        self.guide_page.open_olg()
        self.guide_assertions.verify_one_line_guide()
        self.guide_page.select_and_record_program(self)
        request.getfixturevalue('setup_lock_parental_and_purchase_controls')
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show)
        self.home_page.select_prediction_focus()
        self.menu_assertions.verify_enter_PIN_overlay()

    @pytest.mark.test_stabilization
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    def test_486395023_check_device_properties(self):
        self.home_page.back_to_home_short()
        if Settings.is_managed():
            self.system_page.validate_device_mac_with_device_settings_mac_address()
        self.system_page.validate_device_prop_details()
        self.system_page.validate_android_id()

    @pytestrail.case("C12947447" and "C12947452")
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize(
        "feature, package_type", [(FeAlacarteFeatureList.LINEAR, FeAlacartePackageTypeList.VERIMATRIX)])
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    def test_C12947447_C12947452_IPLinear_PreferNativeorwidevine_to_Defaultorverimatrix(self, request,
                                                                                        feature, package_type):
        """
        Test rail :
         https://testrail.tivo.com/index.php?/cases/view/12947447
         https://testrail.tivo.com/index.php?/cases/view/12947452
        """
        encrpyted_channellist = self.api.get_encrypted_channel_list()
        if not encrpyted_channellist:
            pytest.skip("No encrpyted channel found on device")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_IPLINEAR_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(self, request, drm_type,
                                     self.home_labels.KEY_DRM_ANDROID_NATIVE, feature, FeAlacartePackageTypeList.NATIVE)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        channel_number = random.choice(encrpyted_channellist)
        self.guide_page.verify_channel(self, channel_number)
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C12947445" and "C12947450")
    @pytest.mark.parametrize("feature, package_type",
                             [(FeAlacarteFeatureList.LINEAR, FeAlacartePackageTypeList.VERIMATRIX)])
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    def test_C12947445_C12947450_IPLinear_DefaultorPreferVerimatrix_verimatrixorDefault(self, request, feature,
                                                                                        package_type):
        """
        Test rail :
          https://testrail.tivo.com/index.php?/cases/view/12947445
          https://testrail.tivo.com/index.php?/cases/view/12947450
        """
        encrypted_channellist = self.api.get_encrypted_channel_list()
        if not encrypted_channellist:
            pytest.skip("No encrpyted channel found on device")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_IPLINEAR_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(
            self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_DEFAULT, feature,
            FeAlacartePackageTypeList.VERIMATRIX)
        channel_number = random.choice(encrypted_channellist)
        self.guide_page.verify_channel(self, channel_number)
        self.watchvideo_assertions.verify_livetv_mode()

    @pytestrail.case("C12786350")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize(
        "feature, package_type", [(Settings.mdrm_ndvr_feature(), FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C12786350_nDVR_widevine_to_verimatrix(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/12786350
        """
        recordable_channellist = self.api.get_recordable_channels()
        encrypted_channellist = self.api.get_encrypted_channel_list()
        intersection = set(recordable_channellist).intersection(encrypted_channellist)
        channel_list = list(intersection)
        if not channel_list:
            pytest.skip("No recordable encrpyted channel found")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_NDVR_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_NATIVE,
                                     feature, FeAlacartePackageTypeList.NATIVE)
        channel_number = random.choice(channel_list)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytestrail.case("C12784855")
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.SOCU,
                                                        FeAlacartePackageTypeList.VERIMATRIX)])
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    def test_C12784855_socu_default_to_preferverimatrix(self, request, feature, package_type):
        """
                   actual_drmtype: Actual drm type present on box
                   expected_drmtype: Expected drm type on box
                   feature: Feature to check & update
                   set_drmtype: drm package to set
        """
        channel = self.guide_page.get_encrypted_socu_channel(self, filter_socu=True)
        channel_number = (channel[0][0])
        request.getfixturevalue(self.home_labels.LBL_DRM_PRESERVE_PACKAGE)
        request.getfixturevalue(self.home_labels.LBL_DRM_REMOVE_PACKAGE)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.home_assertions.verify_socu_playback(self)

    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytestrail.case('C12784858')
    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.SOCU,
                                                        FeAlacartePackageTypeList.VERIMATRIX)])
    @pytest.mark.notapplicable(not (Settings.is_cc11() or Settings.is_cc5()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12784858_socu_change_drm_type_preferVerimatrix_to_Default(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_page.update_drm_package_names_native(feature, package_type, False)
        self.home_assertions.verify_drm_package_names_native(feature, package_type, False)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_guide(self)
        self.guide_page.verify_channel(self, self.guide_page.guide_encrypted_streaming_channel_number(self))
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytestrail.case('C12784859')
    @pytestrail.case('C12787147')
    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.SOCU, FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.notapplicable(not (Settings.is_cc11() or Settings.is_cc5()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12784859_C12787147_socu_change_drm_preferVerimatrix_to_preferNative(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_guide(self)
        self.guide_page.verify_channel(self, self.guide_page.guide_encrypted_streaming_channel_number(self))
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.xray("FRUM-24573")
    @pytest.mark.usefixtures("switch_tivo_service_rasp")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Enter to Disconnected State. NoNetworkScreen is shown")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    def test_frum_24573_verify_home_actions_when_service_is_down_after_reboot(self, request):
        """
        Resiliency Mode - Home Screen - Actions
            Verify Home functionality when service is down and then device rebooted
        Xray:
            https://jira.tivo.com/browse/FRUM-24573
        """
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18):
            request.getfixturevalue("toggle_guide_rows_service_availability")  # disabling /v1/guideRows service
        self.home_page.back_to_home_short()
        self.home_page.select_strip(self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.watchvideo_assertions.verify_livetv_mode()
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_whisper_shown(self.home_labels.LBL_DISCONNECTED_WHISPER_TEXT)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_disconnected_program_name(self.guide_labels.LBL_DS_PROGRAM_CELL)

    @pytest.mark.usefixtures("cleanup_enabling_internet")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    def test_frum_28644_non_active_client_disconnect_connect_check_reconnect_between_5_and_15_min(self):
        """
        Home screen - Client is in Non-active state - Soft disconnect - Connect -\
        Verify client reconnects between 5-15 minutes (1st) and 10-30 minutes (2nd)
        Xray:
            https://jira.tivo.com/browse/FRUM-28644
        """
        top_border = 900 + 30  # 15 minutes + 30 seconds (30 seconds needed if reconnect happens right on 900th seocond)
        self.home_page.update_test_conf_and_reboot(
            MENU_INACTIVE_TIME=60000, WATCH_VIDEO_INACTIVE_TIME=180000,
            DEBUGENV="ENABLE_CONNECTION_INDICATOR;ENABLE_USER_ACTIVITY_INDICATOR;IGNORE_SCREEN_DUMP_KEYCODE_IN_QUIESCE")
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_connected_disconnected_state_happened(
            error_code=self.home_labels.LBL_ERROR_CODE_C228)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.CONNECTION_INDICATOR,
                                                           expected=False,
                                                           timeout=0)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.ACTIVITY_INDICATOR,
                                                           expected=False, timeout=60)
        # Checking reconnect time for Non-active client
        start_time = datetime.now()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.CONNECTION_INDICATOR,
                                                           expected=True,
                                                           timeout=top_border)
        end_time = datetime.now()
        minute_5 = timedelta(minutes=5)
        minute_15 = timedelta(seconds=top_border)
        self.__log.debug("test_frum_28644: end_time - start_time = {}".format(end_time - start_time))
        assert_that(end_time - start_time <= minute_15 and end_time - start_time >= minute_5,
                    "Reconnect did not happen between 5-15 minutes for Non-active client")
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.ACTIVITY_INDICATOR,
                                                           expected=False, timeout=0)

    @pytest.mark.usefixtures("cleanup_enabling_internet")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    def test_frum_28643_active_client_disconnect_connect_check_reconnect_between_1_and_5_min(self):
        """
        Home screen - Client is in Active state - Soft disconnect - Connect - Verify client reconnects between 1-5 minutes
        Xray:
            https://jira.tivo.com/browse/FRUM-28643
        """
        top_border = 300 + 30  # 5 minutes + 30 seconds (30 seconds needed if reconnect happens right on 300th seocond)
        self.home_page.update_test_conf_and_reboot(
            MENU_INACTIVE_TIME=900000, WATCH_VIDEO_INACTIVE_TIME=60000,
            DEBUGENV="ENABLE_CONNECTION_INDICATOR;ENABLE_USER_ACTIVITY_INDICATOR;IGNORE_SCREEN_DUMP_KEYCODE_IN_QUIESCE")
        self.home_page.back_to_home_short()
        self.home_page.press_right_button(refresh=False)  # to switch client to Active state
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.ACTIVITY_INDICATOR,
                                                           expected=True, timeout=0)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_connected_disconnected_state_happened(
            error_code=self.home_labels.LBL_ERROR_CODE_C228)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.CONNECTION_INDICATOR,
                                                           expected=False,
                                                           timeout=0)
        # Checking reconnect time for Active client
        start_time = datetime.now()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        minute_1 = timedelta(minutes=1)
        minute_5 = timedelta(seconds=top_border)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.CONNECTION_INDICATOR,
                                                           expected=True,
                                                           timeout=top_border)
        end_time = datetime.now()
        self.__log.debug("test_frum_28643: end_time - start_time = {}".format(end_time - start_time))
        assert_that(end_time - start_time <= minute_5 and end_time - start_time >= minute_1,
                    "Reconnect did not happen between 1-5 minutes for Active client")
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.ACTIVITY_INDICATOR,
                                                           expected=True,
                                                           timeout=0)

    @pytest.mark.usefixtures("cleanup_enabling_internet")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    def test_frum_28697_active_client_disconnect_non_active_connect_check_reconnect_between_5_and_15_min(self):
        """
        Home screen - Client is in Active state - Soft disconnect - Client gets to Non-active state - Connect -
        Verify client reconnects between 5-15 minutes
        Xray:
            https://jira.tivo.com/browse/FRUM-28697
        """
        top_border = 900 + 30  # 15 minutes + 30 seconds (30 seconds needed if reconnect happens right on 900th seocond)
        self.home_page.update_test_conf_and_reboot(
            MENU_INACTIVE_TIME=60000, WATCH_VIDEO_INACTIVE_TIME=180000,
            DEBUGENV="ENABLE_CONNECTION_INDICATOR;ENABLE_USER_ACTIVITY_INDICATOR;IGNORE_SCREEN_DUMP_KEYCODE_IN_QUIESCE")
        self.home_page.back_to_home_short()
        self.home_page.press_right_button(refresh=False)  # to switch client to Active state
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.ACTIVITY_INDICATOR,
                                                           expected=True, timeout=0)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_connected_disconnected_state_happened(
            error_code=self.home_labels.LBL_ERROR_CODE_C228)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.CONNECTION_INDICATOR,
                                                           expected=False,
                                                           timeout=0)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.ACTIVITY_INDICATOR,
                                                           expected=False, timeout=60)
        # Checking reconnect time for Non-active client
        start_time = datetime.now()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.CONNECTION_INDICATOR,
                                                           expected=True,
                                                           timeout=top_border)
        end_time = datetime.now()
        minute_5 = timedelta(minutes=5)
        minute_15 = timedelta(seconds=top_border)
        self.__log.debug("test_frum_28697: end_time - start_time = {}".format(end_time - start_time))
        assert_that(end_time - start_time <= minute_15 and end_time - start_time >= minute_5,
                    "Reconnect did not happen between 5-15 minutes for Non-active client")
        self.home_assertions.verify_indicator_state_change(indicator=DebugEnvPropValues.ACTIVITY_INDICATOR,
                                                           expected=False, timeout=0)

    # @pytest.mark.ftux
    # @pytest.mark.frumos_16
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(not Settings.is_cc2(), reason="Applicable only for CableCo2 environment.")
    def test_frum4443_privacy_disabled_first_login(self):
        """
        To verify that Legal Acceptance screens are not shown when privacy is disabled
        """
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=False, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False, SKIP_FTUX="false",
                                                   accept_eula=False)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_FTUX_ANIMATION_SCREEN)
        self.home_page.skip_ftux(accept_eula=False)
        self.home_assertions.verify_home_title()
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_menu_item_available(
            self.menu_labels.self.menu_labels.LBL_PERSONALIZED_ADS, expected=False)
        self.menu_assertions.verify_menu_item_available(
            self.menu_labels.LBL_VIEWERSHIP_DATA_SHARING, expected=False)

    # @pytest.mark.ftux
    # @pytest.mark.frumos_16
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(not Settings.is_cc11(), reason="Applicable only for CableCo11 environment.")
    def test_frum7149_first_signin_optout_status_accept_eula(self):
        """
        To verify that Operator's User Agreement screen is shown when privacy is enabled and status - optOut
        """
        self.home_page.update_test_conf_and_reboot_to_eula()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_LEGAL_EULA_SCREEN, timeout=30)
        self.home_page.select_menu(self.home_labels.LBL_ACCEPT)
        self.home_page.skip_ftux(accept_eula=False)
        self.home_assertions.verify_home_title()
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_personalized_ads_enabled()
        self.menu_assertions.verify_data_sharing_enabled()

    @pytest.mark.ftux
    @pytest.mark.frumos_16
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(not Settings.is_cc11(), reason="Applicable only for CableCo11 environment.")
    def test_frum6386_first_signin_optin_status_accept_all(self):
        """
        To verify that Legal Acceptance screens are shown when privacy is enabled and status - optIn
        """
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=False, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False, SKIP_FTUX="false",
                                                   accept_eula=False)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_LEGAL_EULA_SCREEN, timeout=30)
        self.home_page.select_menu(self.home_labels.LBL_ACCEPT)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_INTRODUCTORY_SCREEN)
        self.home_page.press_ok_button()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_PERSONALIZED_ADS_SCREEN)
        self.home_page.select_menu(self.home_labels.LBL_ALLOW_PERSONALIZED_ADS)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_DATA_SHARING_SCREEN)
        self.home_page.select_menu(self.home_labels.LBL_ALLOW_DATA_SHARING)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_FTUX_ANIMATION_SCREEN)
        self.home_page.skip_ftux(accept_eula=False)
        self.home_assertions.verify_home_title()
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_personalized_ads_enabled()
        self.menu_assertions.verify_data_sharing_enabled()

    @pytest.mark.ftux
    @pytest.mark.frumos_16
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(not Settings.is_cc11(), reason="Applicable only for CableCo11 environment.")
    def test_frum6398_first_signin_optin_status_do_not_allow_ads(self):
        """
        To verify selection of "Do not allow ads" at Legal acceptance screen
        """
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=False, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False, SKIP_FTUX="false",
                                                   accept_eula=False)
        self.home_page.select_menu(self.home_labels.LBL_ACCEPT)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_INTRODUCTORY_SCREEN)
        self.home_page.press_ok_button()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_PERSONALIZED_ADS_SCREEN)
        self.home_page.select_menu(self.home_labels.LBL_DO_NOT_ALLOW_PERSONALIZED_ADS)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_DATA_SHARING_SCREEN)
        self.home_page.select_menu(self.home_labels.LBL_ALLOW_DATA_SHARING)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_FTUX_ANIMATION_SCREEN)
        self.home_page.skip_ftux(accept_eula=False)
        self.home_assertions.verify_home_title()
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_personalized_ads_enabled(status=False)
        self.menu_assertions.verify_data_sharing_enabled()

    @pytest.mark.ftux
    @pytest.mark.frumos_16
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(not Settings.is_cc11(), reason="Applicable only for CableCo11 environment.")
    def test_frum6399_first_signin_optin_status_do_not_allow_data_sharing(self):
        """
        To verify selection of "Do not allow personal data sharing" at Legal Acceptance screen
        """
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=False, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False, SKIP_FTUX="false",
                                                   accept_eula=False)
        self.home_page.select_menu(self.home_labels.LBL_ACCEPT)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_INTRODUCTORY_SCREEN)
        self.home_page.press_ok_button()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_PERSONALIZED_ADS_SCREEN)
        self.home_page.select_menu(self.home_labels.LBL_ALLOW_PERSONALIZED_ADS)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_DATA_SHARING_SCREEN)
        self.home_page.select_menu(self.home_labels.LBL_DO_NOT_ALLOW_DATA_SHARING)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_FTUX_ANIMATION_SCREEN)
        self.home_page.skip_ftux(accept_eula=False)
        self.home_assertions.verify_home_title()
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_personalized_ads_enabled()
        self.menu_assertions.verify_data_sharing_enabled(status=False)

    @pytest.mark.ftux
    @pytest.mark.frumos_16
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(not Settings.is_cc11(), reason="Applicable only for CableCo11 environment.")
    def test_frum6400_verify_ads_and_data_sharing_changes_in_settings(self):
        """
        To verify changes of Personalized Ads and Personal Data sharing in settings screen
        """
        self.home_page.update_test_conf_and_reboot("device", clear_data=True, skip_animation=False, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False, SKIP_FTUX="false",
                                                   accept_eula=False)
        self.home_page.skip_ftux()
        self.home_assertions.verify_home_title()
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_personalized_ads_enabled()
        self.menu_page.set_personalized_ads_status(enable=False)
        self.menu_assertions.verify_personalized_ads_enabled(status=False)
        self.menu_assertions.verify_data_sharing_enabled()
        self.menu_page.set_personal_data_sharing_status(enable=False)
        self.menu_assertions.verify_data_sharing_enabled(status=False)

    @pytestrail.case("C4863301")
    @pytest.mark.ftux
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    def test_4863301_press_skip_ftux_streaming_apps_screen(self):
        """
        Verify the correct behavior and destination for "Skip this step" action button in Streaming Apps Screen
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="false")
        self.home_page.ftux_onepass_selection_and_verification(self, Settings.app_package, Settings.username)
        self.home_assertions.verify_ftux_streamingapps_screen()
        self.home_page.select_skip_this_step(self)
        if self.home_page.is_ftux_pc_settings_screen_view_mode():
            self.home_assertions.verify_ftux_pcsettings_screen()
            self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.home_assertions.verify_home_title()

    @pytest.mark.restart_reason
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_frum_69411_Clear_data_and_open_the_app(self):
        self.home_page.clear_cache_launch_hydra_app()
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_CLEAR_DATA_RESULT)

    @pytestrail.case("C12784856" and "C1278487")
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize("feature, package_type",
                             [(FeAlacarteFeatureList.SOCU, FeAlacartePackageTypeList.VERIMATRIX)])
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    def test_C12784856_C12784857_socu_preferNative_to_preferverimatrixordefault(self, request, feature, package_type):
        """
               actual_drmtype: Actual drm type present on box
               expected_drmtype: Expected drm type on box
               feature: Feature to check & update
               set_drmtype: drm package to set
               """
        channel = self.guide_page.get_encrypted_socu_channel(self, filter_socu=True)
        channel_number = (channel[0][0])
        request.getfixturevalue(self.home_labels.LBL_DRM_PRESERVE_PACKAGE)
        request.getfixturevalue(self.home_labels.LBL_DRM_REMOVE_PACKAGE)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE)
        self.home_assertions.verify_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE)
        self.home_page.relaunch_hydra_app()
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.home_assertions.verify_socu_playback(self)

    @pytest.mark.test_stabilization
    @pytest.mark.frumos_16
    def test_frum35583_1_verify_device_feature_search_response_in_adb_logs(self):
        self.menu_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_DEVICE_FEATURE_SEARCH_RESPONSE)

    @pytest.mark.test_stabilization
    @pytest.mark.frumos_16
    def test_frum35583_2_verify_device_feature_search_op_logs(self):
        self.menu_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_assertions.verify_logcontrol_op_logs_present_in_adb_logs(self)

    @pytest.mark.test_stabilization
    @pytest.mark.frumos_16
    def test_frum35583_3_verify_device_feature_search_diagnostics_logs(self):
        self.menu_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_assertions.verify_devicefeature_diagnostics_logs_in_adb_logs(self)

    @pytest.mark.restart_reason
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_frum_69413_Force_Stop_and_open_the_tivo_app(self):
        self.system_page.launch_device_settings_screen()
        time.sleep(2)
        self.home_page.force_stop_app_from_UI()
        self.guide_page.relaunch_hydra_app()
        self.home_page.wait_for_screen_ready()
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_FORCE_STOP)

    @pytest.mark.restart_reason
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_FRUM_71795_Restart_the_app_by_changing_storage_permissions(self):
        self.home_page.relaunch_hydra_app(reboot=True)
        self.system_page.launch_device_settings_screen()
        self.home_page.storage_enable_or_disable()
        self.guide_page.relaunch_hydra_app(reboot=True)
        self.home_page.wait_for_screen_ready()
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_STORAGE_PERMISSIONS)

    @pytest.mark.p1_regression
    @pytest.mark.frumos_16
    @pytest.mark.ndvr
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Managed Android only.")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16),
                               reason="Supported starting from frumos-1-16.")
    def test_frum64673_verify_recordings_button_in_home_screen(self):
        """
        testcase: https://jira.xperi.com/browse/FRUM-64673
        """
        self.home_page.back_to_home_short()
        self.home_page.press_recordings_button()
        self.my_shows_assertions.verify_recordings_menu_is_selected()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Managed Android only.")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16),
                               reason="Supported starting from frumos-1-16.")
    def test_frum76506_verify_accessibility_button_in_home_screen(self):
        """
        testcase: https://jira.xperi.com/browse/FRUM-76506
        """
        self.home_page.back_to_home_short()
        self.home_page.press_accessibility_button()
        self.home_assertions.verify_option_in_accessibility_strip(self.home_labels.TURN_SCREEN_READER_ON)

    @pytest.mark.restart_reason
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable in unmanaged devices")
    @pytest.mark.notapplicable(Settings.is_apple_tv(), "This test case is not applicable in AppleTv")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_frum_69409_Restart_the_device_by_adb_reboot(self):
        self.home_page.screen.base.driver.reboot_device()
        self.home_page.reconnect_dut_after_reboot()
        self.home_page.wait_for_screen_ready(screen_name=self.home_labels.LBL_HOME_VIEW_MODE, timeout=60000)
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_REBOOT_REASON)

    @pytest.mark.restart_reason
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable in unmanaged devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_frum_69408_Restart_the_device_from_the_device_setting_option(self):
        self.system_page.launch_device_settings_screen()
        time.sleep(2)
        self.system_page.reboot_device_through_UI()
        self.home_page.reconnect_dut_after_reboot()
        self.screen.base.wait_ui_element_appear(self.home_labels.LBL_HOME_SCREENTITLE, 30000)
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_REBOOT_REASON)

    @pytest.mark.restart_reason
    @pytest.mark.usefixtures("reset_language_code_to_en_us")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable in unmanaged devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_frum_69414_Change_the_language_in_the_app(self):
        language_changed = self.system_page.change_language(user_language_code="es-US")
        if not language_changed:
            pytest.skip("Box doesn't support es-US language")
        self.home_page.press_home_button()
        self.home_page.wait_for_screen_ready(timeout=100000)
        self.home_page.press_ok_button()
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE_SPANISH)
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_CHANGE_LANG)

    @pytest.mark.xray("FRUM-86806")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_86806_verify_SLS_request_in_logs_PQCM_cache_valid(self):
        """
        Verify power-cycling device in less than 24 hours saves app from firing ServiceEndpoints search on startup.
        Xray:
            https://jira.xperi.com/browse/FRUM-86806
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True,
                                                   SLS_INSTANCE_ID="slsCanary",
                                                   DEBUGENV="PrintRequestOpenApi,9;PrintResponseOpenApi,9")
        self.home_assertions.verify_sls_endpoints_request_in_adb_logs()
        self.screen.base.driver.clean_and_verify_log()
        self.home_page.relaunch_hydra_app()
        self.home_assertions.verify_sls_endpoints_request_in_adb_logs(status=False)

    @pytest.mark.xray("FRUM-86809")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_86809_verify_SLS_file_in_storage_PQCM_cache_valid(self):
        """
        Verify power-cycling device in less than 24 hours saves app from firing ServiceEndpoints search on startup.
        Xray:
            https://jira.xperi.com/browse/FRUM-86809
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True,
                                                   SLS_INSTANCE_ID="slsCanary",
                                                   DEBUGENV="PrintRequestOpenApi,9;PrintResponseOpenApi,9")
        file = self.home_labels.LBL_SLS_ENDPOINTS_FILE
        curr_file = self.screen.base.driver.get_cache_file_time(file)
        self.home_page.relaunch_hydra_app()
        self.home_assertions.verify_cache_file_modified(status=False, file_name=file, curr_file_time=curr_file)

    @pytest.mark.xray("FRUM-86812")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_86812_verify_SLS_request_in_logs_PQCM_cache_expired(self):
        """
        Verify power-cycling device in more than 24 hours triggers ServiceEndpointsSearch search on startup to
        refresh the cache.
        Use overriding to reduce time to 3 minutes.
        Xray:
            https://jira.xperi.com/browse/FRUM-86812
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True,
                                                   OVERRIDE_SLS_REFRESH_INTERVAL_IN_SECONDS=180,
                                                   SLS_INSTANCE_ID="slsCanary",
                                                   DEBUGENV="PrintRequestOpenApi,9;PrintResponseOpenApi,9")
        self.home_assertions.verify_sls_endpoints_request_in_adb_logs()
        self.screen.base.driver.clean_and_verify_log()
        self.home_page.pause(200)  # wait for cache expired
        self.home_assertions.verify_sls_endpoints_request_in_adb_logs()

    @pytest.mark.xray("FRUM-86811")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_86811_verify_SLS_file_in_storage_PQCM_cache_expired(self):
        """
        Verify power-cycling device in more than 24 hours triggers ServiceEndpointsSearch search on startup to
        refresh the cache.
        Use overriding to reduce time to 3 minutes.
        Xray:
            https://jira.xperi.com/browse/FRUM-86811
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True,
                                                   OVERRIDE_SLS_REFRESH_INTERVAL_IN_SECONDS=180,
                                                   SLS_INSTANCE_ID="slsCanary",
                                                   DEBUGENV="PrintRequestOpenApi,9;PrintResponseOpenApi,9")
        file = self.home_labels.LBL_SLS_ENDPOINTS_FILE
        curr_file = self.screen.base.driver.get_cache_file_time(file)
        self.home_page.pause(200)  # wait for cache expired
        self.home_assertions.verify_cache_file_modified(status=True, file_name=file, curr_file_time=curr_file)

    @pytest.mark.xray("FRUM-62304")
    @pytest.mark.home
    @pytest.mark.branding_check
    def test_frum_62304_primary_branding(self):
        """
        Verify Primary branding logo in Home and other shortcut strips
        Xray:
            https://jira.xperi.com/browse/FRUM-62304
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_primary_branding_icon()
        self.home_page.primary_branding_check(self)

    @pytest.mark.xray("FRUM-48457")
    @pytest.mark.ftux
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_48457_ftux_tutorial_video_completion(self):
        """
        Verify FTUX Tutorial Video is displayed and user is navigated to OnePassQuickScreen after its completion
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="false",
                                                   skip_animation=False, skip_onepass=False,
                                                   skip_apps=False, skip_pcsetting=False)
        self.home_page.accept_legal_acceptance_screens()
        self.home_page.verify_view_mode(self.home_labels.LBL_FTUX_ANIMATION_VIEW_MODE)
        time.sleep(360)
        if Settings.is_unmanaged():
            if self.home_page.is_ftux_eula_view_mode():
                self.home_page.select_menu(self.home_labels.LBL_ACCEPT)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_ONEPASS_FTUX)
        self.home_page.verify_view_mode(self.home_labels.LBL_ONEPASS_FTUX_VIEW_MODE)
        self.home_page.select_done(times=1)
        self.home_page.verify_view_mode(self.home_labels.LBL_STREAMINGAPPS_FTUX_VIEW_MODE)
        self.home_page.select_done(times=1)
        if self.home_page.is_ftux_pc_settings_screen_view_mode():
            self.home_assertions.verify_ftux_pcsettings_screen()
            self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.xray("FRUM-93446")
    @pytest.mark.network_detection
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.notapplicable(
        Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH"
    )
    def test_frum_93446_c229_error_booting_with_cache_recovering(self):
        """
        Verify possibility to recover from Disconnected State if TiVo app was launched with cache and
        without Mind connection.
        Xray:
            https://jira.xperi.com/browse/FRUM-93446
        """
        self.home_page.back_to_home_short()
        self.home_page.change_tivo_service_connection()
        self.home_page.relaunch_hydra_app()
        self.home_assertions.verify_predictions_error_message(self, self.home_labels.LBL_ERROR_CODE_C229)
        self.home_page.change_tivo_service_connection(enable=True)
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.apps_and_games_page.stop_netflix(self)
        self.home_page.go_to_home_screen(self)
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)
        self.home_assertions.verify_predictions()

    @pytest.mark.xray("FRUM-95524")
    @pytest.mark.network_detection
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(
        Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH"
    )
    def test_frum_95524_c228_sleep_mode(self):
        """
        Verify TiVo app behavior if WAN connection was lost while box in Sleep mode.
        Xray:
            https://jira.xperi.com/browse/FRUM-95524
        """
        self.screen.base.press_standby()
        self.home_page.pause(10, "Waiting the box enter standby")
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_sleep_mode()
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_predictions()

    @pytest.mark.xray("FRUM-95526")
    @pytest.mark.network_detection
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.notapplicable(
        Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH"
    )
    def test_frum_95526_c219_sleep_mode(self):
        """
        Verify TiVo app behavior if Mind connection was lost while box in Sleep mode.
        Xray:
            https://jira.xperi.com/browse/FRUM-95526
        """
        self.screen.base.press_standby()
        self.home_page.pause(10, "Waiting the box to enter standby")
        self.home_page.change_tivo_service_connection()
        self.home_assertions.verify_sleep_mode()
        self.home_page.change_tivo_service_connection(enable=True)
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_predictions()

    @pytest.mark.xray("FRUM-95531")
    @pytest.mark.network_detection
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(
        Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH"
    )
    def test_frum_95531_c228_sleep_mode_recovering(self):
        """
        Verify TiVo app behavior if WAN connection was lost and restored while box in Sleep mode.
        Xray:
            https://jira.xperi.com/browse/FRUM-95531
        """
        self.screen.base.press_standby()
        self.home_page.pause(10, "Waiting the box to enter standby")
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.pause(20, "Waiting the box to enter disconnected state")
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_sleep_mode()
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_predictions()

    @pytest.mark.xray("FRUM-95533")
    @pytest.mark.network_detection
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.notapplicable(
        Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH"
    )
    def test_frum_95533_c219_sleep_mode_recovering(self):
        """
        Verify TiVo app behavior if Mind connection was lost and restored while box in Sleep mode.
        Xray:
            https://jira.xperi.com/browse/FRUM-95533
        """
        self.screen.base.press_standby()
        self.home_page.pause(10, "Waiting the box to enter standby")
        self.home_page.change_tivo_service_connection()
        self.home_page.pause(20, "Waiting the box to enter disconnected state")
        self.home_page.change_tivo_service_connection(enable=True)
        self.home_assertions.verify_sleep_mode()
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_predictions()

    @pytest.mark.disconnected_state
    @pytest.mark.gatekeeper_api
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_69428_disconnectedstate_recovery(self):
        """
        Verify if the box has recovered from disconnected state after receiving response from gatekeeper api
        https://jira.xperi.com/browse/FRUM-69428
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="true",
                                                   CCB_SWITCH_OVERRIDE="ENABLE_GATEKEEPER_API_CHECK_REMOVE_IN_IPTV_"
                                                                       "23128,CCBAPPROVED",
                                                   DEBUGENV="ServiceConnectionGatekeeperImpl",
                                                   SLS_ENDPOINTS_OVERRIDE="bridge-keeper,api-tivo-lambda-wtwn-dsantha"
                                                                          ".dev.tivoservice.com,443")
        self.home_page.back_to_home_short()
        self.home_page.change_tivo_service_connection()
        self.home_page.relaunch_hydra_app()
        self.home_assertions.verify_predictions_error_message(self, self.home_labels.LBL_ERROR_CODE_C229)
        self.home_page.change_tivo_service_connection(enable=True)
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=False)
        self.home_assertions.verify_gatekeeper_logs()

    @pytest.mark.disconnected_state
    @pytest.mark.gatekeeper_api
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("restore_mind_availability")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_69435_disconnectedstate_recovery_toggle(self):
        """
        Verify gatekeeper API response and behavior on UI when Mind is toggled to unavailable and back to available and
        gatekeeper API sends some wait time in response.
        https://jira.xperi.com/browse/FRUM-69435
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="true",
                                                   CCB_SWITCH_OVERRIDE="ENABLE_GATEKEEPER_API_CHECK_REMOVE_IN_IPTV_"
                                                                       "23128,CCBAPPROVED",
                                                   DEBUGENV="ServiceConnectionGatekeeperImpl",
                                                   SLS_ENDPOINTS_OVERRIDE="bridge-keeper,api-tivo-lambda-wtwn-dsantha"
                                                                          ".dev.tivoservice.com,443")
        self.home_page.back_to_home_short()
        self.home_page.toggle_mind_availability()
        self.home_page.relaunch_hydra_app()
        self.home_assertions.verify_predictions_error_message(self, self.home_labels.LBL_ERROR_CODE_C229)
        self.home_page.toggle_mind_availability()
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=False)
        self.home_assertions.verify_gatekeeper_logs()

    @pytest.mark.xray("FRUM-93443")
    @pytest.mark.network_detection
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.notapplicable(
        Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH"
    )
    def test_frum_93443_c228_error_booting_with_cache_recovering(self):
        """
        Verify possibility to recover from Disconnected State if TiVo app was launched with cache and
        without WAN connection
        Xray:
            https://jira.xperi.com/browse/FRUM-93443
        """
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.relaunch_hydra_app()
        self.home_assertions.verify_predictions_error_message(self, self.home_labels.LBL_ERROR_CODE_C228)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.screen.base.pause(120)  # waiting for restore connection
        self.home_page.select_strip(self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.watchvideo_assertions.verify_livetv_mode()
        self.home_page.back_to_home_short()
        self.home_assertions.verify_predictions()

    @pytest.mark.xray("FRUM-48289")
    @pytest.mark.network_detection
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.notapplicable(
        Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH"
    )
    def test_frum_48289_c219_error_recovering_guide_screen(self):
        """
        Verify populating Guide after Mind connection was lost in TiVo UI and restored in TiVo UI.
        Xray:
            https://jira.xperi.com/browse/FRUM-48289
        """
        self.home_page.back_to_home_short()
        self.home_page.change_tivo_service_connection()
        self.home_assertions.verify_connected_disconnected_state_happened(
            error_code=self.home_labels.LBL_ERROR_CODE_C219)
        self.home_page.change_tivo_service_connection(enable=True)
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=False)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.disconnected_state
    @pytest.mark.gatekeeper_api
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.usefixtures("decrease_screen_saver", "cleanup_set_sleep_timeout_to_never")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_115114_c228_sleep_mode_gatekeeper_api(self):
        """
        Verify TiVo app behavior and gatekeeper response if WAN connection was lost while box in Sleep mode
        Xray:
            https://jira.xperi.com/browse/FRUM-115114
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="true",
                                                   DEBUGENV="ServiceConnectionGatekeeperImpl",
                                                   SLS_ENDPOINTS_OVERRIDE="bridge-keeper,api-tivo-lambda-wtwn-dsantha"
                                                                          ".dev.tivoservice.com,443")
        self.home_page.back_to_home_short()
        self.home_page.set_sleep_timeout(time_ms=60000)
        self.home_page.pause(65, "Waiting the box enter standby")
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_sleep_mode()
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_gatekeeper_logs()

    @pytest.mark.disconnected_state
    @pytest.mark.gatekeeper_api
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.usefixtures("set_bridge_status_up", "decrease_screen_saver", "cleanup_set_sleep_timeout_to_never")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_115112_c219_sleep_mode_gatekeeper_api(self):
        """
        Verify TiVo app behavior and gatekeeper response if Mind connection was lost while box in Sleep mode.
        Xray:
            https://jira.xperi.com/browse/FRUM-115112
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="true",
                                                   DEBUGENV="ServiceConnectionGatekeeperImpl",
                                                   SLS_ENDPOINTS_OVERRIDE="bridge-keeper,api-tivo-lambda-wtwn-dsantha"
                                                                          ".dev.tivoservice.com,443")
        self.home_page.back_to_home_short()
        self.home_page.set_sleep_timeout(time_ms=60000)
        self.home_page.pause(65, "Waiting the box to enter standby")
        self.home_page.change_tivo_service_connection()
        self.home_assertions.verify_sleep_mode()
        self.home_page.change_tivo_service_connection(enable=True)
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_gatekeeper_logs()

    @pytest.mark.disconnected_state
    @pytest.mark.gatekeeper_api
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.usefixtures("set_bridge_status_up", "decrease_screen_saver", "cleanup_set_sleep_timeout_to_never")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_115110_c228_sleep_mode_recovering_gatekeeper_api(self):
        """
        Verify TiVo app behavior and gatekeeper logs if WAN connection was lost and restored while box in Sleep mode.
        Xray:
            https://jira.xperi.com/browse/FRUM-115110
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="true",
                                                   DEBUGENV="ServiceConnectionGatekeeperImpl",
                                                   SLS_ENDPOINTS_OVERRIDE="bridge-keeper,api-tivo-lambda-wtwn-dsantha"
                                                                          ".dev.tivoservice.com,443")
        self.home_page.back_to_home_short()
        self.home_page.set_sleep_timeout(time_ms=60000)
        self.home_page.pause(65, "Waiting the box to enter standby")
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.pause(30, "Waiting the box to enter disconnected state")
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_sleep_mode()
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_gatekeeper_logs()

    @pytest.mark.disconnected_state
    @pytest.mark.gatekeeper_api
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.usefixtures("set_bridge_status_up", "decrease_screen_saver", "cleanup_set_sleep_timeout_to_never")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    def test_frum_115109_c219_sleep_mode_recovering_gatekeeper_api(self):
        """
        Verify TiVo app behavior if Mind connection was lost and restored while box in Sleep mode.
        Xray:
            https://jira.xperi.com/browse/FRUM-115109
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, SKIP_FTUX="true",
                                                   DEBUGENV="ServiceConnectionGatekeeperImpl",
                                                   SLS_ENDPOINTS_OVERRIDE="bridge-keeper,api-tivo-lambda-wtwn-dsantha"
                                                                          ".dev.tivoservice.com,443")
        self.home_page.back_to_home_short()
        self.home_page.set_sleep_timeout(time_ms=60000)
        self.home_page.pause(65, "Waiting the box to enter standby")
        self.home_page.change_tivo_service_connection()
        self.home_page.pause(30, "Waiting the box to enter disconnected state")
        self.home_page.change_tivo_service_connection(enable=True)
        self.home_assertions.verify_sleep_mode()
        self.home_page.jump_to_home_xplatform(refresh=False)
        self.home_assertions.verify_gatekeeper_logs()

    @pytest.mark.xray("FRUM-108742")
    @pytest.mark.longrun
    def test_108742_verify_hdmi_not_permitted_overlay_not_seen(self):
        """
        Verify V60 “HDMI Not Permitted” error code not seen after power OFF/ON
        BZSTREAM-8852
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        dev_details = self.screen.base.get_device_details_from_db(Settings.device_ip)
        if not dev_details.get('device_id'):
            pytest.fail(f"Device ID is not mapped for {Settings.device_ip} to Power OFF/ON")
        self.watchvideo_page.turn_off_device_power(dev_details['device_id'])
        time.sleep(60 * 90)
        self.watchvideo_page.turn_on_device_power(dev_details['device_id'])
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_home_screen_video_window(120000)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, 120000)
        self.home_assertions.verify_home_title()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.screen.refresh()
        errors_list = self.watchvideo_page.get_ui_error()
        if self.liveTv_labels.LBL_HDMI_OVERLAY in errors_list:
            pytest.fail("This overlay should not be shown as per BZSTREAM-8852. pls file product bug.")
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.xray("FRUM-112770")
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.usefixtures("setup_enable_notification_access")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Notification access is applicable to Managed boxes only")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "This test is applicable only for Hydra v1.18 and higher")
    def test_frum_112770_verify_the_behaviour_when_notification_access_is_turned_ON(self):
        """
               Verify that the Enable System Notifications overlay is not displayed on homescreen when notification
               access is turned ON in Android device settings.
               Xray:
                   https://jira.xperi.com/browse/FRUM-112770
               """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True)
        self.home_page.back_to_home_short()
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_notification_overlay_disabled()

    @pytest.mark.xray("FRUM-112771")
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.usefixtures("setup_disable_notification_access")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Notification access is applicable to Managed boxes only")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "This test is applicable only for Hydra v1.18 and higher")
    def test_frum_112771_verify_the_behaviour_when_notification_access_is_turned_OFF(self):
        """
               Verify that the Enable System Notifications overlay is not displayed on homescreen when notification
               access is turned ON in Android device settings.
               Xray:
                   https://jira.xperi.com/browse/FRUM-112770
               """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True)
        self.home_page.back_to_home_short()
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_notification_overlay_enabled()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_19
    @pytest.mark.xray("FRUM-115770")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "This test is applicable only for Hydra v1.18 and higher")
    def test_frum_115770_verify_brandingbundle_fetched_on_device_reboot(self):
        """
            This test case verifies that the brandingbundle is returned successfully by Open and Morpheus APIs and the
            bundle values are same. This test case is a P1 in scope of Open API automation.
            https://jira.xperi.com/browse/FRUM-115770
            """
        self.menu_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.api_assertions.verify_brandingbundle_is_found_same_for_morpheus_and_open_api()

    @pytest.mark.disconnected_state
    @pytest.mark.xray("FRUM-69381")
    @pytest.mark.e2e1_16
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Bails button feature only for Managed streamers")
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.timeout(Settings.timeout_mid)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_69381_disconnected_state_with_bail_buttons(self):
        """
        FRUM - 69381 Disconnect network - Verifying the disconnected state with bail buttons
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.home_page.goto_live_tv(channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.press_home_button()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()
        self.home_assertions.validate_disconnected_state(self)
        for bail_btn in self.apps_and_games_labels.LBL_BAIL_BUTTONS:
            if bail_btn == "guide":
                self.home_page.press_guide_button()
                self.home_assertions.validte_disconnected_state_whisper()
            if bail_btn == "exit":
                self.watchvideo_page.press_exit_button()
                self.home_assertions.validte_disconnected_state_whisper()
            if bail_btn == "back":
                self.watchvideo_page.press_back_button()
                self.home_assertions.validte_disconnected_state_whisper()
            if bail_btn == "vod":
                self.screen.base.press_vod_button()
                self.home_assertions.validte_disconnected_state_whisper()
            if bail_btn == "apps":
                self.home_page.press_apps_and_verify_screen(self)
                self.home_page.wait_for_screen_ready()
                self.apps_and_games_assertions.verify_screen_title(self)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=False)

    @pytest.mark.xray("FRUM-69446")
    @pytest.mark.e2e1_16
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    @pytest.mark.timeout(Settings.timeout_mid)
    def test_69446_edit_fav_channel_nwk_down_up_check_fav_panel(self):
        """
        FRUM - 69446 Disconnect network - Settings - User Preferences - Edit favorite channel
        """
        channel = self.service_api.get_channels_with_no_trickplay_restrictions(self)
        if not channel:
            pytest.skip("No channels with trickplay found.")
        self.guide_page.add_random_channel_to_favorite(self, count=2)
        fav_list = self.guide_page.get_fav_channels(self)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.validate_disconnected_state(self)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)
        self.home_page.screen.base.pause(120)
        self.home_page.goto_live_tv(random.choice(channel))
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        new_fav_list = self.watchvideo_page.get_channels_list_on_favorite_panel()
        self.watchvideo_assertions.fav_screen_matches_fav_panel(fav_list, new_fav_list, True)

    @pytest.mark.xray('FRUM-76071')
    @pytest.mark.e2e
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("back_to_home")
    @pytest.mark.e2e1_16
    def test_frum76071_pressing_netflix_button_in_privacy_optin(self):
        privacy_optin = self.api.branding_ui(field="privacy_opt_in_config")
        if not privacy_optin:
            pytest.skip("Privacy Optin is not configured by MSO")
        self.home_page.clear_cache_launch_hydra_app()
        self.home_page.is_privacy_optin_screen_view_mode()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        time.sleep(120)
        self.home_page.press_home_button()
        self.home_page.is_privacy_optin_screen_view_mode()

    @pytest.mark.xray("FRUM-72655")
    @pytest.mark.e2e1_16
    @pytest.mark.ftux
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_apple_tv(), reason="Applicable only for Android devices")
    @pytest.mark.usefixtures("relaunch_hydra_app")
    @pytest.mark.timeout(Settings.timeout)
    def test_frum72655_reboot_on_privacy_optin(self):
        """
        To Verify the behavior of Privacy optin after reboot
        """
        if not self.service_api.branding_ui(field="privacy_opt_in_config"):
            pytest.skip("Privacy Optin is not configured")
        self.home_page.clear_cache_launch_hydra_app(accept_eula=False, skip_pcsetting=False, skip_apps=False,
                                                    skip_onepass=False, skip_animation=False)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_LEGAL_EULA_SCREEN, timeout=30)
        self.home_page.relaunch_hydra_app(reboot=True)
        time.sleep(500)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_LEGAL_EULA_SCREEN, timeout=30)
        self.home_page.select_accept(times=1)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_INTRODUCTORY_SCREEN)
        self.screen.base.press_back()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_LEGAL_EULA_SCREEN, timeout=30)
        self.home_page.select_accept(times=1)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_INTRODUCTORY_SCREEN)
        self.home_page.press_ok_button()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_PERSONALIZED_ADS_SCREEN)
        self.home_page.select_accept(times=1)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_DATA_SHARING_SCREEN)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_LEGAL_EULA_SCREEN, timeout=30)

    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Applicable only for managed devices")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_demo_parameterized_signin_overlay_test(self, get_signin_overlay_data_from_yml):  # noqa: F811
        signin_overlay_details = get_signin_overlay_data_from_yml
        self.home_page.log.info(f"signin_overlay_details in test file: {signin_overlay_details}")

        if signin_overlay_details.get(f'{Settings.mso}_params'):
            params = signin_overlay_details.get(f'{Settings.mso}_params')
        else:
            params = signin_overlay_details.get('params')
        expected = signin_overlay_details.get('expected')
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True,
                                                   QUERY_RESPONSE_OVERRIDE=params)

        self.home_page.wait_for_home_page_ds_error(expected)

        self.home_page.wait_for_condition_satisfied(self.home_page.is_prediction_bar_error_visible,
                                                    expected_result=False, timeout=360)

        if signin_overlay_details.get('wtw'):
            self.home_page.go_to_what_to_watch(self)
            self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    @pytest.mark.ccu_client_resiliency
    @pytest.mark.xray('FRUM-111175')
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_17))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    def test_FRUM_111175_block_guide_service_and_recover_verify_guide_screen(self):
        """
        To verify guide screen behavior when only guide service is blocked and restored
        Xray: https://jira.xperi.com/browse/FRUM-111175
        """
        self.home_page.go_to_guide(self)
        url = self.home_page.get_tivoservice_url(sls=True, endpoint='cloudcore-guide')
        previewurl = self.home_page.get_tivoservice_url(sls=True, endpoint='cloudcore-previews')
        self.home_page.change_tivo_service_connection(url=url)
        self.home_page.change_tivo_service_connection(url=previewurl)
        self.home_page.clear_cache_launch_hydra_app()
        self.home_page.go_to_guide(self)
        self.screen.refresh()
        if not self.home_page.verify_whisper(self.home_labels.LBL_ISSUE_GUIDE, visible=True, raise_error=False):
            self.watchvideo_page.press_right_multiple_times(no_of_times=10)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_assertions.verify_guide_focussed_cell_when_service_blocked_and_unblocked(blocked=True)
        self.home_page.change_tivo_service_connection(enable=True)
        self.home_page.clear_cache_launch_hydra_app()
        self.home_page.go_to_guide(self)
        self.screen.refresh()
        dump = self.screen.get_screen_dump_item()
        received_whisper = self.screen.get_screen_dump_item('whisper', 'text') \
            if "whisper" in dump and "text" in dump.get("whisper") else None
        if received_whisper and self.home_labels.LBL_ISSUE_GUIDE in received_whisper:
            raise AssertionError("Guide service failed to restore: {}".format(received_whisper))
        self.watchvideo_page.press_right_multiple_times(no_of_times=10)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_focussed_cell_when_service_blocked_and_unblocked()

    @pytest.mark.ccu_client_resiliency
    @pytest.mark.xray('FRUM-144216')
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_17))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    def test_FRUM_144216_block_guide_service_and_verify_livetv_channel_switch_and_playback(self):
        """
        To verify guide screen behavior when only guide service is blocked and restored
        Xray: https://jira.xperi.com/browse/FRUM-111175
        """
        self.home_page.go_to_guide(self)
        url = self.home_page.get_tivoservice_url(sls=True, endpoint='cloudcore-guide')
        previewurl = self.home_page.get_tivoservice_url(sls=True, endpoint='cloudcore-previews')
        self.home_page.change_tivo_service_connection(url=url)
        self.home_page.change_tivo_service_connection(url=previewurl)
        self.home_page.clear_cache_launch_hydra_app()
        self.home_page.go_to_guide(self)
        self.screen.refresh()
        if not self.home_page.verify_whisper(self.home_labels.LBL_ISSUE_GUIDE, visible=True, raise_error=False):
            self.watchvideo_page.press_right_multiple_times(no_of_times=10)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_assertions.verify_guide_focussed_cell_when_service_blocked_and_unblocked(blocked=True)
        self.home_page.go_to_watch_tv(self)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        next_channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.guide_page.enter_channel_number(next_channel)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.ccu_client_resiliency
    @pytest.mark.xray('FRUM-144213')
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_17))
    @pytest.mark.usefixtures("restore_tivo_service_connection")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    def test_FRUM_144213_block_guide_service_and_verify_socu_playback_on_channel(self):
        channels = self.service_api.get_available_channels_with_socu_offer()
        self.home_page.go_to_guide(self)
        url = self.home_page.get_tivoservice_url(sls=True, endpoint='cloudcore-guide')
        previewurl = self.home_page.get_tivoservice_url(sls=True, endpoint='cloudcore-previews')
        self.home_page.change_tivo_service_connection(url=url)
        self.home_page.change_tivo_service_connection(url=previewurl)
        self.home_page.clear_cache_launch_hydra_app()
        self.home_page.go_to_guide(self)
        self.screen.refresh()
        if not self.home_page.verify_whisper(self.home_labels.LBL_ISSUE_GUIDE, visible=True, raise_error=False):
            self.watchvideo_page.press_right_multiple_times(no_of_times=10)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_assertions.verify_guide_focussed_cell_when_service_blocked_and_unblocked(blocked=True)
        self.home_page.go_to_watch_tv(self)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.guide_page.enter_channel_number(channels[0])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.startover_program_from_livetv_with_socu(self)
        self.watchvideo_assertions.verify_playback_play()
