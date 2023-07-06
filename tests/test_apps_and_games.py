"""
    @author: iurii.nartov@tivo.com
    @created: Oct-31-2019
"""

import time

import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_bind_hsn, setup_sideload_test_app, \
    setup_cleanup_content_provider_app, setup_cleanup_pluto_tv_app, skip_old_os_version
from set_top_box.client_api.home.conftest import cleanup_EAS, setup_disable_stay_awake, back_to_home, \
    decrease_screen_saver, launch_hydra_app_when_script_is_on_ott, cleanup_set_sleep_timeout_to_never
from set_top_box.shared_context import ExecutionContext
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, HydraBranches
from set_top_box.conf_constants import FeaturesList
from set_top_box.client_api.apps_and_games.conftest import setup_apps_and_games
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from pytest_testrail.plugin import pytestrail


@pytest.mark.apps_and_games
@pytest.mark.notapplicable(Settings.is_devhost())
@pytest.mark.usefixtures("setup_apps_and_games")
@pytest.mark.timeout(Settings.timeout)
class TestAppsAndGamesScreen(object):

    @pytestrail.case("C11116807")
    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_5593939_apps_and_games_sections_order(self):
        """
        "Featured Apps" section name should be displayed over "My Apps" one

        Testrail:
            https://testrail.corporate.local/index.php?/cases/view/5593939
        """
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.verify_sections(
            self.apps_and_games_labels.LBL_APPS_AND_GAMES_FEATURED_APPS_SECTION_TITLE,
            self.apps_and_games_labels.LBL_APPS_AND_GAMES_MY_APPS_TITLE)

    @pytestrail.case("C11116806")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-110")
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.msofocused
    def test_5590704_apps_and_games_featured_apps_first_item(self):
        """
        First item in "Featured Apps" section should be NETFLIX

        Testrail:
            https://testrail.corporate.local/index.php?/cases/view/5590704
        """
        self.apps_and_games_page.go_to_apps_and_games(self)
        first_item_label = self.apps_and_games_labels.LBL_APPS_AND_GAMES_FEATURED_APPS_FIRST_ITEM
        self.apps_and_games_assertions.verify_featured_apps_first_item(self, first_item_label)

    # @pytest.mark.p1_regression
    @pytest.mark.hospitality
    @pytest.mark.msofocused_solutions
    @pytest.mark.xray('FRUM-48542')
    @pytest.mark.usefixtures("setup_sideload_test_app", "setup_cleanup_bind_hsn")
    @pytest.mark.notapplicable(not Settings.is_technicolor() and not Settings.is_jade() and not Settings.is_jade_hotwire(),
                               "This test is applicable only for Technicolor boxes")
    @pytest.mark.notapplicable(not ExecutionContext.service_api.get_feature_status(FeaturesList.HOSPITALITY, True),
                               "This test is applicable only for accounts with Hospitality Mode = ON")
    @pytest.mark.notapplicable(Settings.is_dev_host(),
                               "There's NO ability to install application on the dev host")
    def test_5413278_apps_and_games_hospitality_device_clear_ext_app(self):
        """
        Hospitality Screen - Uninstalling External Apps - TED (test_app.apk is used)

        Testrail:
            https://testrail.corporate.local/index.php?/cases/view/5413278
        """
        # HSN binding right after device clearing due to https://jira.xperi.com/browse/CA-20547
        self.iptv_prov_api.device_clear(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn))
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    self.service_api.getPartnerCustomerId(Settings.tsn))
        self.apps_and_games_page.reconnect_dut_after_reboot(180)
        self.apps_and_games_assertions.select_continue_wait_for_home_screen_to_load(self, is_hospitality_screen_omitted=True)
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.verify_if_app_is_not_present_on_ui_apps_and_games(
            self.apps_and_games_labels.LBL_TEST_APP_PACKAGE)
        self.apps_and_games_assertions.verify_if_app_is_not_present_in_system(self.apps_and_games_labels.LBL_TEST_APP_PACKAGE)

    @pytest.mark.msofocused_solutions
    @pytest.mark.xray('FRUM-48551')
    @pytest.mark.usefixtures("setup_cleanup_bind_hsn")
    @pytest.mark.notapplicable(not Settings.is_technicolor() and not Settings.is_jade() and not Settings.is_jade_hotwire(),
                               "This test is applicable only for Technicolor boxes")
    @pytest.mark.notapplicable(not ExecutionContext.service_api.get_feature_status(FeaturesList.HOSPITALITY, True),
                               "This test is applicable only for accounts with Hospitality Mode = ON")
    @pytest.mark.notapplicable(Settings.is_dev_host(),
                               "There's NO ability to install application on the dev host")
    def test_frum_48551_verify_hospitality_view(self):
        """
        Hospitality Screen - Initial Entry - From TiVo Guide Screen

        Xray:
            https://jira.xperi.com/browse/FRUM-48551
        """
        self.home_page.go_to_guide(self)
        self.iptv_prov_api.device_clear(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn))
        self.apps_and_games_page.reconnect_dut_after_reboot(180)
        self.apps_and_games_assertions.verify_hospitality_screen_elements(self)
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    self.service_api.getPartnerCustomerId(Settings.tsn))
        self.apps_and_games_assertions.select_continue_wait_for_home_screen_to_load(self, is_hospitality_screen_omitted=False)

    @pytestrail.case("C11123950")
    @pytest.mark.bat
    @pytest.mark.usefixtures("back_to_home")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.skipif(not Settings.is_managed(),
                        reason="Apps & Games menu is present on managed streamers only")
    @pytest.mark.notapplicable(Settings.is_ruby() or Settings.is_jade(), reason="Netflix is not supported")
    def test_393698_1_ability_to_launch_and_exit_netflix_ott_app(self):
        """
        :description:
            Ability to launch NETFLIX app and exit with bail buttons
        :testtopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=393698
        :return:
        """
        apps = ["netflix"]
        self.home_page.back_to_home_short()
        #  Back button does not exit Netflix app. Ref: CA-21016
        BAIL_BUTTONS = self.apps_and_games_labels.LBL_BAIL_BUTTONS.remove("back") \
            if "back" in self.apps_and_games_labels.LBL_BAIL_BUTTONS else self.apps_and_games_labels.LBL_BAIL_BUTTONS
        self.apps_and_games_assertions.verify_bail_buttons_in_ott_app(self, apps, BAIL_BUTTONS)

    @pytestrail.case("C11123951")
    @pytest.mark.bat
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("back_to_home")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.skipif(not Settings.is_managed(),
                        reason="Apps & Games menu is present on managed streamers only")
    @pytest.mark.xray("FRUM-237")
    @pytest.mark.msofocused
    def test_393698_2_ability_to_launch_and_exit_youtube_ott_app(self):
        """
        :description:
            Ability to launch YouTube app and exit with bail buttons
        :testtopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=393698
        :return:
        """
        apps = ["youtube"]
        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.verify_bail_buttons_in_ott_app(self, apps, self.apps_and_games_labels.LBL_BAIL_BUTTONS)

    @pytestrail.case("C11123952")
    @pytest.mark.bat
    @pytest.mark.usefixtures("back_to_home")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.skipif(not Settings.is_managed(),
                        reason="Apps & Games menu is present on managed streamers only")
    def test_393698_3_ability_to_launch_and_exit_googleplay_ott_app(self):
        """
        :description:
            Ability to launch Google Play app and exit with bail buttons
        :testtopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=393698
        :return:
        """
        apps = ["google play"]
        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.verify_bail_buttons_in_ott_app(self, apps, self.apps_and_games_labels.LBL_BAIL_BUTTONS)

    @pytestrail.case("C11123949")
    @pytest.mark.bat
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.skipif(not Settings.is_amino(),
                        reason="Apps & Games menu is present on managed streamers only \
                                and CLEAR button is not present on Arris")
    def test_393698_4_clear_button_in_ott_apps(self):
        """
        :description:
            Verify that CLEAR button does nothing in OTT apps
        :testtopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=393698
        :return:
        """
        apps = ["netflix", "youtube", "google play"]
        webkit_name = self.apps_and_games_labels.TUBITV_WEBKIT_NAME
        result = self.service_api.check_groups_enabled(webkit_name)
        if result:
            apps.append("tubitv")
        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.verify_clear_button_in_ott_apps(self, apps)

    @pytest.mark.GA
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74150639_app_content_playback(self):
        """
        74150639
        Verify playback from an App
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.launch_app_from_GA(self, self.home_labels.LBL_YOUTUBE)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.apps_and_games_assertions.verify_app_content_playing()
        self.home_page.back_to_home_short()

    @pytest.mark.GA
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74094935_verify_transition_between_apps(self):
        """
        74094935
        Verify smooth transition when switching between the apps
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.home_page.launch_app_from_GA_from_any_screen(self, self.home_labels.LBL_YOUTUBE)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.apps_and_games_assertions.verify_app_content_playing()
        self.home_page.exit_ott_app_with_back_or_exit_button()
        self.watchvideo_assertions.verify_livetv_mode()
        channel_number = self.service_api.get_random_channel(Settings.tsn, "entitled", mso=Settings.mso)
        self.guide_page.goto_one_line_guide_from_live(self, channel_number)
        self.guide_page.exit_one_line_guide()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.launch_app_from_GA_from_any_screen(self, self.home_labels.LBL_YOUTUBE)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.apps_and_games_assertions.verify_app_content_playing()
        self.home_page.exit_ott_app_with_back_or_exit_button()
        self.watchvideo_assertions.verify_livetv_mode()

    @pytest.mark.GA
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74176734_verify_smoothexit_of_game_app_launch(self):
        self.home_page.back_to_home_short()
        gamename = self.home_labels.LBL_GAME_NAME
        app_package = self.home_labels.GAME_APP_PACKAGE
        self.home_page.download_game_using_GA(gamename)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.back_to_home_short()
        self.screen.base.launch_application(app_package)
        self.home_page.exit_game_app_with_exit_or_home_button()
        self.home_assertions.verify_home_title()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.home_page.screen.base.driver.uninstall(app_package)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.back_to_home_short()

    @pytest.mark.frumos_11
    @pytest.mark.stability
    @pytest.mark.usefixtures("setup_cleanup_content_provider_app")
    @pytest.mark.skipif(
        Settings.is_mediacom() or Settings.is_eastlink(),
        reason="Feature is not applicable for Mediacom and Eastlink MSOs.")
    @pytest.mark.skipif(
        not Settings.is_managed() or Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-11"),
        reason="Feature is for managed devices and hydra-streamer-1-11 or later.")
    def test_13512695_verify_content_provider_app_values(self):
        """
        To verify values from content provider app
        Details could be found in https://jira.tivo.com/browse/IPTV-16328
        :testrail: https://testrail.tivo.com/index.php?/cases/view/13512695
        """
        self.home_page.back_to_home_short()
        state = self.apps_and_games_page.launch_content_provider_app()
        if not state:
            pytest.skip("Unable to start content provider app.")
        self.apps_and_games_assertions.verify_content_provider_app_is_foreground()
        self.apps_and_games_assertions.verify_content_provider_info()

    @pytest.mark.duplicate
    @pytest.mark.wtw_openAPI_impacted
    def test_214969645_launch_ott_source_from_search(self):
        """
        This test case is covered under test_214969644_verify_behaviour_when_ott_app_is_not_installed
        """
        webkit_name = self.apps_and_games_labels.TUBITV_WEBKIT_NAME
        result = self.service_api.check_groups_enabled(webkit_name)
        if not result:
            pytest.skip("Device does not have required webkit. Hence skipping")
        result1 = self.screen.base.is_app_installed(self.apps_and_games_labels.TUBITV_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='TUBITV', feedName="Movies", cnt=4)
        if not program:
            pytest.skip("Program is not available to deeplink. Hence skipping")
        self.my_shows_page.select_strip(self.apps_and_games_labels.LBL_TUBITV_ICON)
        if result1:
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.TUBITV_PACKAGE_NAME, limit=15)
        else:
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                                                              limit=15)

    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-1052")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.notapplicable(Settings.hydra_branch() > Settings.hydra_branch("b-hydra-streamer-1-11"))
    @pytest.mark.usefixtures("cleanup_EAS")
    def test_19778901_trigger_eas_alert_on_ott_app(self):
        """
        :testrail: https://testrail.tivo.com//index.php?/cases/view/19778901
        """
        self.home_page.back_to_home_short()
        self.home_page.launch_app_from_GA(self, self.home_labels.LBL_YOUTUBE)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.home_page.wait_for_EAS_to_dismiss(timeout=90)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")

    @pytest.mark.ott_deeplink2
    @pytest.mark.xray("FRUM-1186")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    def test_214969646_verify_user_able_to_launch_tubitv_from_apps_and_games(self):
        self.home_page.download_game_using_GA(self.apps_and_games_labels.LBL_TUBITV_APP_NAME)
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.TUBITV_PACKAGE_NAME)
        if result:
            self.home_page.back_to_home_short()
            self.apps_and_games_page.go_to_apps_and_games(self)
            self.apps_and_games_assertions.start_ott_application_and_verify_screen(self,
                                                                                   app=self.apps_and_games_labels.
                                                                                   TUBITV_PACKAGE_NAME)
        else:
            pytest.skip("Tubi Tv App is not installed")

    @pytest.mark.ott_deeplink2
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_214989437_verify_launch_tubitv_from_jump_channel(self):
        all_jump_channels = self.api.get_jump_channels_list()
        channel_no = self.apps_and_games_assertions.check_jump_channel_is_available(all_jump_channels,
                                                                                    self.apps_and_games_labels.LBL_TUBITV)
        if not channel_no:
            pytest.skip("Device does not have required jump channel. Hence skipping")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.launch_app_from_guide(channel_no)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.TUBITV_PACKAGE_NAME, limit=15)
        self.screen.base.press_exit_button()

    @pytest.mark.ott_deeplink2
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_214969644_verify_behaviour_when_ott_app_is_not_installed(self):
        webkit_name = self.apps_and_games_labels.TUBITV_WEBKIT_NAME
        result = self.service_api.check_groups_enabled(webkit_name)
        if not result:
            pytest.skip("webkit is not added. Hence skipping")
        result1 = self.screen.base.is_app_installed(self.apps_and_games_labels.TUBITV_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='TUBITV', feedName="Movies", cnt=4)
        if not program:
            pytest.skip("Program is not available to deeplink. Hence skipping")
        self.my_shows_page.select_strip(self.apps_and_games_labels.LBL_TUBITV_ICON)
        if result1:
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.TUBITV_PACKAGE_NAME, limit=15)
        else:
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                                                              limit=15)

    @pytest.mark.stop_streaming
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    def test_12345_verify_stop_streaming_tv_on_off_while_netflix_playback(self):
        """
        Stop Streaming - Stream a recording - TV(HDMI Adapter) Power OFF/ON

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14391789
        """
        channels = self.service_api.get_random_recordable_channel(channel_count=1, filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channels[0][0])
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Netflix', feedName="Movies", cnt=4)
        if not program:
            pytest.skip("Netflix program unavailable on the box")
        self.my_shows_page.select_strip(self.menu_labels.LBL_NETFLIX, matcher_type='in')
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
        self.watchvideo_assertions.verify_video_playback_stopped()
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)
        time.sleep(self.guide_labels.LBL_TEN_SECONDS)
        self.home_assertions.verify_home_title()
        self.watchvideo_assertions.verify_video_playback_started()
        self.watchvideo_page.press_exit_button()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_channel_number(channels[0][0])

    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.longrun
    @pytest.mark.wtw_openAPI_impacted
    def test_21557975_playback_netflix_content_for_longer_duration_and_verify_behavior_by_pressing_home(self):
        """
        Playback netflix content for 1 hours and verify the behavior by pressing home button.
        Home screen should be displayed.
        """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Netflix', feedName="Movies", cnt=4)
        if not program:
            pytest.skip("Program is not available")
        self.my_shows_page.select_strip(self.menu_labels.LBL_NETFLIX, matcher_type='in')
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(60 * 60)
        self.apps_and_games_assertions.press_home_and_verify_screen(self)

    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.p1_regression
    def test_21558701_netflix_screen_saver(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/21558701
        """
        self.driver.set_sleep_timeout(25 * 60 * 1000)
        self.driver.set_screen_saver_timeout(5 * 60 * 1000)
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, "netflix", launch_apps=False)
        self.home_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "netflix")
        self.home_page.wait_for_screen_saver(time=420)
        focused_app = self.driver.driver.get_current_focused_app()
        if self.home_labels.LBL_DREAM not in focused_app[0]:
            pytest.fail("Screen saver did not appear. focussed app: {}".format(focused_app))
        self.home_page.press_home_button()
        time.sleep(15)
        self.home_assertions.verify_home_title()
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, "netflix")
        self.home_page.wait_for_screen_saver(time=420)
        app_focused = self.driver.driver.get_current_focused_app()
        if self.home_labels.LBL_DREAM not in app_focused[0]:
            pytest.fail("Screen saver did not appear.")
        self.watchvideo_page.press_ok_button()
        self.home_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "netflix")
        self.apps_and_games_page.press_up_button()
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_page.press_home_and_verify_screen(self)
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, "netflix")

    @pytest.mark.frumos_15
    @pytest.mark.tivo_plus
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("setup_cleanup_pluto_tv_app")
    @pytest.mark.xray("FRUM-3439")
    def test_21572426_verify_channel_change_in_pluto_tv_app(self):
        """
        testrail: https://testrail.tivo.com//index.php?/cases/view/21572426
        """
        self.home_page.back_to_home_short()
        channels = self.api.get_pluto_tv_channels()
        if not channels:
            pytest.skip("No appropriate channels found.")
        channel_number = channels[0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        self.guide_page.press_ok_button()
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.PLUTO_TV_PACKAGE_NAME)
        self.apps_and_games_page.wait_for_pluto_tv_start_playing()
        self.apps_and_games_assertions.press_channel_button_and_verify_channel_change_in_pluto_tv("channel up")

    @pytest.mark.frumos_15
    @pytest.mark.tivo_plus
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("setup_cleanup_pluto_tv_app")
    @pytest.mark.xray("FRUM-3442")
    def test_21572429_verify_back_button_in_pluto_tv_app(self):
        """
        testrail: https://testrail.tivo.com//index.php?/cases/view/21572429
        """
        self.home_page.back_to_home_short()
        channels = self.api.get_pluto_tv_channels()
        if not channels:
            pytest.skip("No appropriate channels found.")
        channel_number = channels[0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.PLUTO_TV_PACKAGE_NAME)
        self.apps_and_games_page.wait_for_pluto_tv_start_playing()
        self.apps_and_games_page.press_back_button()
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.app_package)
        self.home_assertions.verify_home_title()

    @pytest.mark.frumos_15
    @pytest.mark.tivo_plus
    @pytest.mark.notapplicable(Settings.hydra_branch() != Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               reason="Applicable only for streamer-1-15 release.")
    @pytest.mark.usefixtures("setup_cleanup_pluto_tv_app")
    def test_21572433_verify_pluto_tv_app_starts_from_future_guide_program_cell(self):
        """
        testrail: https://testrail.tivo.com//index.php?/cases/view/21572433
        """
        self.home_page.back_to_home_short()
        channels = self.api.get_pluto_tv_channels()
        if not channels:
            pytest.skip("No appropriate channels found.")
        channel_number = channels[0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        self.guide_page.press_right_button()
        self.guide_page.press_ok_button()
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.PLUTO_TV_PACKAGE_NAME)

    @pytest.mark.frumos_15
    @pytest.mark.tivo_plus
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("setup_cleanup_pluto_tv_app")
    def test_21572494_verify_pluto_tv_app_starts_from_oneline_guide(self):
        """
        testrail: https://testrail.tivo.com//index.php?/cases/view/21572494
        """
        self.home_page.back_to_home_short()
        channels = self.api.get_pluto_tv_channels()
        if not channels:
            pytest.skip("No appropriate channels found.")
        channel_number = channels[0]
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.open_olg()
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True, olg=True)
        self.home_assertions.verify_error_overlay_not_shown()
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.PLUTO_TV_PACKAGE_NAME)

    @pytest.mark.frumos_15
    @pytest.mark.tivo_plus
    @pytest.mark.usefixtures("setup_cleanup_pluto_tv_app")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    def test_21572415_verify_google_play_app_starts_when_pluto_tv_app_not_installed(self):
        """
        testrail: https://testrail.tivo.com//index.php?/cases/view/21572415
        """
        self.driver.uninstall_app(self.apps_and_games_labels.PLUTO_PACKAGE_NAME)
        self.home_page.back_to_home_short()
        channels = self.api.get_pluto_tv_channels()
        if not channels:
            pytest.skip("No appropriate channels found.")
        channel_number = channels[0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        self.guide_page.press_ok_button()
        self.apps_and_games_assertions.verify_app_is_foreground(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME)

    @pytest.mark.xray("FRUM-91268")
    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    def test_frum_91268_launch_netflix_and_verify_source_type(self):
        """
        launch netflix and check the source type matches in the adb log with netflix
        """
        self.home_page.back_to_home_short()
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, "netflix")
        self.program_options_assertions.verify_ott_app_is_foreground(self, "netflix")
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_3)
        self.screen.base.press_exit_button()

    @pytest.mark.netflix_lst_cert_test
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Netflix certification is done only for manged devices")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("skip_old_os_version")
    def test_20959229_launch_netflix_and_verify_lst_type_iid(self):
        """
        Launch netflix from apps and games menu and check the LST iid type matches in the adb log with netflix
        """
        self.home_page.back_to_home_short()
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, "netflix")
        self.program_options_assertions.verify_ott_app_is_foreground(self, "netflix")
        self.apps_and_games_assertions.verify_netflix_app_iid(self.apps_and_games_labels.LBL_NETFLIX_LST_3)

    @pytest.mark.netflix_lst_cert_test
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Netflix certification is done only for manged devices")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("skip_old_os_version")
    def test_21558382_launch_netflix_from_home_shortcut_and_verify_lst_type_iid(self):
        """
         Launch netflix from home shortcut and check the LST iid type matches in the adb log with netflix
        """
        self.home_assertions.select_netflix_shortcut_and_verify_netflix_launch(self)
        self.apps_and_games_assertions.verify_netflix_app_iid(self.apps_and_games_labels.LBL_NETFLIX_LST_2)
        self.home_page.back_to_home_short()

    @pytest.mark.netflix_lst_cert_test
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Netflix certification is done only for manged devices")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("skip_old_os_version")
    def test_20959230_wtw_netflix_originals_and_verify_lst_type_iid(self):
        """
        Launch netflix from Netflix title from What To Watch menu and check the LST iid type matches in the adb log
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.navigate_to_wtw_strip(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER, 'in')
        self.wtw_assertions.verify_current_strip_title(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER)
        self.watchvideo_page.press_ok_button()
        self.home_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, self.apps_and_games.
                                                                     LBL_APPS_AND_GAMES_NETFLIX)
        self.apps_and_games_assertions.verify_netflix_app_iid(self.apps_and_games_labels.LBL_NETFLIX_LST_11)

    @pytest.mark.netflix_lst_cert_test
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Netflix certification is done only for manged devices")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("skip_old_os_version")
    def test_20959231_launch_netflix_from_search_and_verify_lst_type_iid(self):
        """
        Launch netflix from text search and check the LST iid type matches in the adb log
        """
        netflix_strip = self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER
        asset_title = self.service_api.get_assets_titles_from_wtw_strip(netflix_strip, asset_index=1)
        self.text_search_page.go_to_search(self)
        self.text_search_page.input_search_text(asset_title)
        time.sleep(5)
        self.watchvideo_page.press_right_multiple_times(no_of_times=7)
        self.text_search_page.press_ok_button()
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_netflix_app_iid(self.apps_and_games_labels.LBL_NETFLIX_LST_4)

    @pytest.mark.xray("FRUM-63350")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    @pytest.mark.apps_and_games
    def test_t777753846_verify_user_able_to_launch_pandora_from_apps_and_games(self):
        self.home_page.download_game_using_GA(self.apps_and_games_labels.LBL_PANDORA)
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.PANDORA_PACKAGE_NAME)
        if result:
            self.home_page.back_to_home_short()
            self.apps_and_games_page.go_to_apps_and_games(self)
            self.apps_and_games_assertions.start_ott_application_and_verify_screen(self,
                                                                                   app=self.apps_and_games_labels.
                                                                                   PANDORA_PACKAGE_NAME)
        else:
            pytest.skip("Pandora App is not installed")

    @pytest.mark.netflix_lst_cert_test
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Netflix certification is done only for manged devices")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("skip_old_os_version")
    def test_20959236_launch_netflix_from_prediction_bar_and_verify_lst_type_iid(self):
        """
        Launch netflix from prediction bar and check the LST iid type matches in the adb log
        """
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.3455",
                                                                 feed_name="/predictions")
        self.home_page.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME,
                                                                       "NETFLIX")
        self.apps_and_games_assertions.verify_netflix_app_iid(self.apps_and_games_labels.LBL_NETFLIX_LST_21)

    @pytest.mark.netflix_lst_cert_test
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Netflix certification is done only for manged devices")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("skip_old_os_version")
    def test_20959234_launch_netflix_from_jump_channel_and_verify_lst_type_iid(self):
        """
        Launch netflix from direct tune(jump channel) and check the LST iid type matches in the adb log
        """
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels, app=self.menu_labels.LBL_NETFLIX)
        if channel_num is None:
            pytest.skip("Device does not have netflix app")
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.enter_channel_number(channel_num)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_netflix_app_iid(self.apps_and_games_labels.LBL_NETFLIX_LST_18)

    @pytest.mark.netflix_lst_cert_test
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Netflix certification is done only for manged devices")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("skip_old_os_version")
    def test_20959233_launch_netflix_from_gird_guide_and_verify_lst_type_iid(self):
        """
        Browse on grid guide to Netflix cell,launch the app check the LST iid type matches in the adb log
        """
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels, app=self.menu_labels.LBL_NETFLIX)
        if channel_num is None:
            pytest.skip("Device does not have netflix app")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.screen.base.press_enter()
        self.apps_and_games_assertions.verify_ott_or_google_play_shown(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        self.apps_and_games_assertions.verify_netflix_app_iid(self.apps_and_games_labels.LBL_NETFLIX_LST_17)

    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.stability
    def test_FRUM_60240_app_switch(self):
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_assertions.verify_screen_title(self)
        self.apps_and_games_page.launch_all_apps_present_in_apps_and_games_screen(self)

    @pytest.mark.xray("FRUM-89479")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    @pytest.mark.apps_and_games
    def test_t777753996_hbomax_application_launch(self):
        self.home_page.download_game_using_GA(self.apps_and_games_labels.LBL_HBOMAX)
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.HBO_MAX_PACKAGE_NAME)
        if result:
            self.home_page.back_to_home_short()
            self.apps_and_games_page.go_to_apps_and_games(self)
            self.apps_and_games_assertions.start_ott_application_and_verify_screen(self,
                                                                                   app=self.apps_and_games_labels.
                                                                                   LBL_HBOMAX)
        else:
            pytest.skip("HBO MAX App is not installed")

    @pytest.mark.ott_deeplink
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.skipif(not Settings.is_managed(), reason="Apps & Games menu is present on managed streamers only")
    def test_frum_66359_ability_to_launch_and_exit_HBOMAX_app_bail_buttons(self):
        """
        FRUM-66359
        Please ensure HBO Max app has to be installed before using this TC
        Verify Launch and Exit of HBOMAX App with bail buttons
        :return:
        """
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.HBO_MAX_PACKAGE_NAME)
        if not result:
            pytest.skip("HBO Max App is not installed")
        apps = ["HBO MAX"]
        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.verify_bail_buttons_in_ott_app(self, apps, self.apps_and_games_labels.LBL_BAIL_BUTTONS)

    @pytest.mark.ott_deeplink
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.skipif(not Settings.is_managed(), reason="Apps & Games menu is present on managed streamers only")
    def test_frum_68083_ability_to_launch_and_exit_disney_plus_app_bail_buttons(self):
        """
        FRUM-68083
        Verify launch and exit of Disney Plus app with Bail buttons
        :return:
        """
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.DISNEY_PLUS_PACKAGE_NAME)
        if not result:
            pytest.skip("Disney Plus App is not installed")
        apps = ["disney plus"]
        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.verify_bail_buttons_in_ott_app(self, apps, self.apps_and_games_labels.LBL_BAIL_BUTTONS)

    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_76614_verify_netflix_from_guide_and_nav_back(self):
        """
        FRUM-76614
        Verify Netflix launching from Guide and nav back to same place by back button
        :return:
        """
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels, app=self.menu_labels.LBL_NETFLIX)
        if channel_num is None:
            pytest.skip("Device does not have Netflix")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_assertions.verify_ott_or_google_play_shown(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME,
                                                                       limit=30)
        self.screen.base.press_back()
        self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.xray("FRUM-78246")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    @pytest.mark.tivo_plus
    def test_t777753912_verify_user_able_to_launch_pluto_from_apps_and_games(self):
        self.home_page.download_game_using_GA(self.apps_and_games_labels.LBL_PLUTO)
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.PLUTO_PACKAGE_NAME)
        if result:
            self.home_page.back_to_home_short()
            self.apps_and_games_page.go_to_apps_and_games(self)
            self.apps_and_games_assertions.start_ott_application_and_verify_screen(self,
                                                                                   app=self.apps_and_games_labels.
                                                                                   LBL_PLUTO)
        else:
            pytest.skip("Pluto App is not installed")

    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_81060_verify_prime_from_guide_and_nav_back(self):
        """
        FRUM-81060
        Verify Prime Video launching from Jump channel and nav back to same place by back button
        :return:
        """
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels,
                                                              app=self.apps_and_games_labels.LBL_APPS_AND_GAMES_PRIME_VIDEO)
        if channel_num is None:
            pytest.skip("Device does not have Prime Video App")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_assertions.verify_ott_or_google_play_shown(self.apps_and_games_labels.AMAZON_PACKAGE_NAME,
                                                                       limit=30)
        self.screen.base.press_back()
        self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_81544_verify_vudu_from_guide_and_nav_back(self):
        """
        FRUM-81544
        Verify vudu launching from Jump channel and nav back to same place by back button
        :return:
        """
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels, app=self.menu_labels.LBL_VUDU)
        if channel_num is None:
            pytest.skip("Device does not have Vudu app")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_assertions.verify_ott_or_google_play_shown(self.apps_and_games_labels.VUDU_PACKAGE_NAME,
                                                                       limit=30)
        self.screen.base.press_back()
        self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_82449_verify_google_play_from_guide_and_nav_back(self):
        """
        FRUM-82449
        Verify Google Play launching from Jump channel and nav back to same place by back button
        :return:
        """
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels,
                                                              app=self.apps_and_games_labels.LBL_APPS_AND_GAMES_GOOGLE_PLAY)
        if channel_num is None:
            pytest.skip("Device does not have Google Play app")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME2, limit=30)
        self.screen.base.press_back()
        self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.xray("FRUM-84691")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    @pytest.mark.apps_and_games
    def test_c5593954_featured_app_sort_by_recency(self):
        self.apps_and_games_page.go_to_apps_and_games(self)
        section_items = self.apps_and_games_page.get_items_by_section_name(
            self.apps_and_games_labels.LBL_APPS_AND_GAMES_FEATURED_APPS_SECTION_TITLE.lower())
        if len(section_items) == 1:
            pytest.skip("Only one featured app")
        else:
            for items in section_items:
                if section_items.index(items) >= 1:
                    for _ in range(section_items.index(items)):
                        self.press_right()
                    self.press_ok_button()
                    self.home_page.wait_for_screen_ready()
                    if items != self.screen.base.verify_foreground_app(None):
                        pytest.fail("{} app is not the correct opened app".format(items))
                    self.home_page.exit_ott_app_with_back_or_exit_button()
                    self.apps_and_games_assertions.verify_featured_apps_second_item(self, items)

    @pytest.mark.xray("FRUM-63372")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    @pytest.mark.apps_and_games
    def test_t777754006_verify_user_able_to_launch_pbs_kids_from_apps_and_games(self):
        self.home_page.download_game_using_GA(self.apps_and_games_labels.LBL_PBS_KIDS)
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.PBS_KIDS_PACKAGE_NAME)
        if result:
            self.home_page.back_to_home_short()
            self.apps_and_games_page.go_to_apps_and_games(self)
            self.apps_and_games_assertions.start_ott_application_and_verify_screen(self,
                                                                                   app=self.apps_and_games_labels.
                                                                                   PBS_KIDS_PACKAGE_NAME)
        else:
            pytest.skip("PBS Kids App is not installed")

    @pytest.mark.xray("FRUM-87236")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    @pytest.mark.apps_and_games
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    def test_t777753928_verify_user_able_to_launch_youtube_kids_from_apps_and_games(self):
        self.home_page.download_game_using_GA(self.apps_and_games_labels.LBL_YOUTUBE_KIDS)
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.YOUTUBE_KIDS_PACKAGE_NAME)
        if result:
            self.home_page.back_to_home_short()
            self.apps_and_games_page.go_to_apps_and_games(self)
            self.apps_and_games_assertions.start_ott_application_and_verify_screen(self,
                                                                                   app=self.apps_and_games_labels.
                                                                                   LBL_YOUTUBE_KIDS)
        else:
            pytest.skip("Youtube Kids App is not installed")

    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_84386_verify_starz_from_guide_and_nav_back(self):
        """
        FRUM - 84386
        Verify starz launching from Jump channel and nav back to same place by back button
        :return:
        """
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels,
                                                              app=self.apps_and_games_labels.LBL_APPS_AND_GAMES_STARZ)
        if channel_num is None:
            pytest.skip("Device does not have STARZ app")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.apps_and_games_assertions.verify_ott_or_google_play_shown(self.apps_and_games_labels.STARZ_PACKAGE_NAME,
                                                                       limit=30)
        self.screen.base.press_back()
        self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.test_stabilization
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    def test_frum_99598_verify_user_navigate_back_same_place_from_OTT_part1(self):
        """
        FRUM-99598
        Launching OTT apps from various start points and verifying navigates to same place after pressing back
        """
        # Search
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies")
        if not program:
            pytest.skip("OTT not present in search")
        self.program_options_assertions.verify_action_view_mode(self)
        self.screen.base.press_enter()
        self.text_search_assertions.press_select_and_verify_app_is_not_hydra(self, enter=False)
        self.screen.base.press_back()
        self.program_options_assertions.verify_action_view_mode(self)
        # my shows
        bookmark = self.menu_labels.LBL_BOOKMARK
        if self.guide_assertions.verify_bookmark_present(bookmark):
            self.text_search_page.bookmark_from_action_screen(self)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.home_labels.LBL_MOVIES)
            self.my_shows_assertions.verify_category_has_content()
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.screen.base.press_enter()
            self.text_search_assertions.press_select_and_verify_app_is_not_hydra(self, enter=False)
            self.screen.base.press_back()
            self.program_options_assertions.verify_action_view_mode(self)
        # Guide & Jump channels
        channel = self.service_api.get_jump_channels_list()
        channel_num = []
        for ch in channel.keys():
            channel_num.append(ch)
        if channel_num:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(channel_num[0])
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.screen.base.press_enter()
            self.text_search_assertions.press_select_and_verify_app_is_not_hydra(self, enter=False)
            self.screen.base.press_back()
            self.guide_assertions.verify_guide_screen(self)

    @pytest.mark.xray("XTQ-589532")
    @pytest.mark.usefixtures("cleanup_set_sleep_timeout_to_never")
    @pytest.mark.usefixtures("decrease_screen_saver")
    def test_frum_589532_application_playback_screen_saver(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies")
        if not program:
            pytest.skip("OTT not present in search")
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_page.press_ok_button()
        self.driver.set_sleep_timeout(25 * 60 * 1000)
        self.driver.set_screen_saver_timeout(5 * 60 * 1000)
        self.home_page.pause(420, "Wait for screensaver")
        self.home_assertions.verify_foreground_package_name(Settings.screen_saver_package)
        self.home_page.press_home_button()
        self.home_page.wait_for_screen_ready(timeout=15000)
        self.home_assertions.verify_home_title()
        self.watchvideo_assertions.verify_video_playback_started()
        self.watchvideo_page.press_exit_button()
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.xray("FRUM-122789")
    @pytest.mark.skipif(Settings.display_priority_dict is None, reason="prioritydict seems to be empty. Required for testing")
    @pytest.mark.p1_regression
    @pytest.mark.parametrize('ott', Settings.ott_list)
    def test_FRUM_122789_search_ott_priority_check(self, ott):
        self.text_search_page.go_to_search(self)
        ott = ott.replace('_', ' ')
        self.my_shows_page.search_select_program_from_OTT(self, OTT=ott, feedName="Movies", cnt=4, select=False)
        play_options = self.guide_page.get_preview_panel().get('availableOn', None)
        self.apps_and_games_assertions.verify_playback_options_order(play_options=play_options,
                                                                     priority_dict=Settings.display_priority_dict)
        self.home_page.press_info_button()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_INFO_OVERLAY)
        self.screen.refresh()
        self.home_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARD_OPTIONS)
        self.screen.refresh()
        info_play_options = self.apps_and_games_page.get_watch_now_option_images()
        self.apps_and_games_assertions.verify_playback_options_order(play_options=info_play_options,
                                                                     priority_dict=Settings.display_priority_dict)

    @pytest.mark.xray("FRUM-127112")
    @pytest.mark.test_stabilization
    @pytest.mark.notapplicable(Settings.is_fire_tv(), "Fire TV does not have OTTs")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    @pytest.mark.timeout(Settings.timeout_mid)
    def test_frum_127112_switch_between_app_playback_and_standby_multiple_times(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT=None,
                                                                   no_partnerIdCount=False)
            if program:
                break
        if not program:
            pytest.skip("OTT not present in search")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1], select=False)
        self.text_search_page.open_program_screen()
        self.text_search_page.nav_to_menu(self.text_search_labels.LBL_WATCH_NOW)
        strip_list = self.text_search_page.get_strip_list()
        self.text_search_page.check_ott_index_and_select_ott(self, strip_list,
                                                             self.my_shows_labels.LBL_OTT_LIST_ACTION_SCREEN)
        self.program_options_page.press_ok_button(refresh=False)
        for i in range(10):
            self.text_search_assertions.press_select_and_verify_app_is_not_hydra(self, enter=False)
            self.watchvideo_page.watch_video_for(20)
            self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
            self.watchvideo_assertions.verify_video_playback_stopped()
            self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
            self.screen.base.press_enter()
