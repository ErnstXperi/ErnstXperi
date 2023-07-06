import pytest

from set_top_box.client_api.end2end.conftest import setup_e2e  # noqa: F401
from set_top_box.client_api.Menu.conftest import disable_parental_controls  # noqa: F401
from set_top_box.client_api.vision_tester.conftest import device_wakeup  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings, \
    setup_cleanup_myshows  # noqa: F401, E501
from set_top_box.client_api.vision_tester.conftest import setup_vision_tester, setup_perf_log, \
    vt_precondition  # noqa: F401
from set_top_box.client_api.vision_tester.locators import VTtweaks
from set_top_box.test_settings import Settings
from tools.kpi_calculator import KpiCalculator


@pytest.mark.usefixtures('setup_e2e')
@pytest.mark.usefixtures('device_wakeup')
@pytest.mark.usefixtures('vt_precondition')
@pytest.mark.usefixtures('setup_vision_tester')
@pytest.mark.usefixtures('setup_perf_log')
@pytest.mark.timeout(Settings.timeout)
@pytest.mark.notapplicable(not Settings.is_vision_tester_enabled())
@pytest.mark.vt_performance
class TestPerformance:

    def test_FRUM_84396_wtw_navigate_right_perf(self):
        """
        Measure time between events:
            'press RIGHT button in WHAT TO WATCH screen' and 'transition ends'

        XRay:
            https://jira.tivo.com/browse/FRUM-84396
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.capture_events()
        self.wtw_page.press_right_button()
        self.vision_page.verify_transition(region=VTtweaks.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, timeout=14, stable=5)
        diff = KpiCalculator.calculate_period_between_events(
            self.wtw_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.wtw_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    def test_FRUM_84398_wtw_navigate_down_perf(self):
        """
        Measure time between events:
            'press DOWN button in WHAT TO WATCH screen' and 'transition ends'

        XRay:
            https://jira.tivo.com/browse/FRUM-84398
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.capture_events()
        self.wtw_page.press_down_button()
        self.vision_page.verify_transition(region=VTtweaks.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, timeout=14, stable=5)
        diff = KpiCalculator.calculate_period_between_events(
            self.wtw_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.wtw_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    def test_FRUM_84445_guide_navigate_down_perf(self):
        """
        Measure time between events:
            'press DOWN in GUIDE screen' and 'transition ends'

        XRay:
            https://jira.tivo.com/browse/FRUM-84445
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.go_to_bottom_cell_in_guide()
        self.guide_page.capture_events()
        self.screen.base.press_down()
        self.vision_page.verify_transition(expected=True, region=VTtweaks.NO_PIG_REGION)
        diff = KpiCalculator.calculate_period_between_events(
            self.guide_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.guide_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    def test_FRUM_84452_open_guide_with_button(self):
        """
        Measure time between events:
            'press menu shortcut for GUIDE' and 'GUIDE text displayed on top left of the screen'

        XRay:
            https://jira.tivo.com/browse/FRUM-84452
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.capture_events()
        self.screen.base.press_guide(50)
        self.vision_page.verify_transition(region=VTtweaks.NO_PIG_REGION, timeout=20, stable=5)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        diff = KpiCalculator.calculate_period_between_events(
            self.guide_page.get_all_captured_events(), "KeyPressed", "ScreenReady")
        self.guide_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    def test_FRUM_84461_spinner_removed_in_search(self):
        """
        Measure time between events:
            'press CLR in Tivo Search Screen' and 'transition ends'

        XRay:
            https://jira.tivo.com/browse/FRUM-84461
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_search(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT.upper())
        self.text_search_page.clear_search_text()
        self.home_page.capture_events()
        self.screen.base.press_enter(50)
        self.vision_page.verify_transition(expected=True, region=VTtweaks.NO_PIG_REGION, timeout=10)
        diff = KpiCalculator.calculate_period_between_events(
            self.text_search_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.text_search_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    def test_FRUM_84463_recording_option_overlay_expand(self):
        """
        Measure time between events:
            'press ok/select from RECORDING overlay' and 'RECORDING overlay completely fades out'

        XRay:
            https://jira.tivo.com/browse/FRUM-84463
        """
        if Settings.is_feature_4k():
            channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True)
            if not channel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            channel = self.service_api.get_4k_channel(channel_count=-1, resolution="hd", recordable=True, filter_channel=True)
        if not channel:
            pytest.skip("No channels found")
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.press_right_button()
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready("RecordOverlay")
        self.screen.refresh()
        self.guide_page.select_menu_by_substring(self.guide_labels.LBL_RECORD, confirm=False)
        self.guide_page.capture_events()
        self.screen.base.press_enter(50)
        self.vision_page.verify_transition(expected=True, region=VTtweaks.NO_PIG_REGION, timeout=10, stable=5)
        diff = KpiCalculator.calculate_period_between_events(
            self.guide_page.get_all_captured_events(), "KeyPressed", "VisualisationComplete")
        self.guide_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_84477_whisper_message_for_creation_one_pass(self):
        """
        Measure time between events:
            'press ok/select from CREATE ONE PASS overlay' and 'ONE PASS Whisper overlay displayed'

        XRay:
            https://jira.tivo.com/browse/FRUM-84477
        """
        channel = self.service_api.get_recordable_non_movie_channel()
        if channel is None:
            pytest.skip("Could not find any episodic channel")
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.screen.base.press_info()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_RECORD_OVERLAY)
        self.screen.refresh()
        if not self.guide_page.is_overlay_shown():
            self.screen.base.long_press_enter()
            self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_RECORD_OVERLAY)
            self.screen.refresh()
        self.guide_page.select_menu_by_substring(self.guide_labels.LBL_CREATE)
        self.guide_page.capture_events()
        self.screen.base.press_enter(50)
        self.vision_page.verify_transition(expected=True, region=VTtweaks.NO_PIG_REGION, timeout=6, stable=3)
        diff = KpiCalculator.calculate_period_between_events(
            self.guide_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.guide_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_84484_transition_into_series_screen(self):
        """
        Measure time between events:
            'press ok/select from CREATE ONE PASS overlay' and 'CREATE ONE PASS overlay completely fades out'

        XRay:
            https://jira.tivo.com/browse/FRUM-84484
        """
        channel = self.service_api.get_recordable_non_movie_channel()
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.menu_navigate_left_right(0, 1)
        self.screen.refresh()
        self.my_shows_page.select_menu_by_substring(self.my_shows_page.remove_service_symbols(program), confirm=False)
        self.my_shows_page.capture_events()
        self.screen.base.press_enter(50)
        self.vision_page.verify_transition(region=VTtweaks.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, timeout=20, stable=5)
        diff = KpiCalculator.calculate_period_between_events(
            self.my_shows_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.my_shows_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    def test_FRUM_84485_enter_myshows_screen_perf(self):
        """
        Measure time between events:
            'press menu shortcut for MY SHOWS' and 'MY SHOWS text displayed on top left of the screen'

        XRay:
            https://jira.tivo.com/browse/FRUM-84485
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_MYSHOWS_SHORTCUT, refresh=False)
        self.vision_page.verify_transition(region=VTtweaks.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, timeout=14, stable=7)
        diff = KpiCalculator.calculate_period_between_events(
            self.my_shows_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.my_shows_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.screen.refresh()
        self.menu_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.vt_core_feature
    def test_FRUM_84492_enter_menu_screen_perf(self):
        """
        Measure time between events:
            'press menu shortcut for MENU' and 'MENU text displayed on top left of the screen'

        XRay:
            https://jira.tivo.com/browse/FRUM-84492
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_MENU_SHORTCUT, refresh=False)
        self.vision_page.verify_transition(region=VTtweaks.NO_PIG_REGION, timeout=14, stable=7)
        diff = KpiCalculator.calculate_period_between_events(
            self.menu_page.get_all_captured_events(), "KeyPressed", "VisualisationComplete")
        self.menu_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.screen.refresh()
        self.menu_assertions.verify_overlay_shown(expected=False)
        self.menu_assertions.verify_screen_title(self.home_labels.LBL_MENU_SCREENTITLE)

    def test_FRUM_84493_enter_search_screen_perf(self):
        """
        Measure time between events:
            'press menu shortcut for SEARCH' and 'SEARCH text displayed on top left of the screen'

        XRay:
            https://jira.tivo.com/browse/FRUM-84493
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_SEARCH_SHORTCUT, refresh=False)
        self.vision_page.verify_transition(region=VTtweaks.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, timeout=14, stable=7)
        diff = KpiCalculator.calculate_period_between_events(
            self.text_search_page.get_all_captured_events(), "KeyPressed", "VisualisationComplete")
        self.text_search_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.screen.refresh()
        self.menu_assertions.verify_overlay_shown(expected=False)
        self.menu_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT)

    def test_FRUM_84565_enter_guide_screen_perf(self):
        """
        Measure time between events:
            'press menu shortcut for GUIDE' and 'GUIDE text displayed on top left of the screen'

        XRay:
            https://jira.tivo.com/browse/FRUM-84565
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_GUIDE_SHORTCUT, refresh=False)
        self.vision_page.verify_transition(region=VTtweaks.NO_PIG_REGION, timeout=20, stable=5)
        diff = KpiCalculator.calculate_period_between_events(
            self.guide_page.get_all_captured_events(), "KeyPressed", "ScreenReady")
        self.guide_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.screen.refresh()
        self.menu_assertions.verify_screen_title(self.home_labels.LBL_GUIDE_SHORTCUT)

    def test_FRUM_84566_enter_wtw_screen_perf(self):
        """
        Measure time between events:
            'press menu shortcut for WHAT TO WATCH' and 'WHAT TO WATCH text displayed on top left of the screen'

        XRay:
            https://jira.tivo.com/browse/FRUM-84566
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WHATTOWATCH_SHORTCUT, refresh=False)
        self.vision_page.verify_transition(region=VTtweaks.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, timeout=14, stable=7)
        diff = KpiCalculator.calculate_period_between_events(
            self.wtw_page.get_all_captured_events(), "KeyPressed", "ScreenReady")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.screen.refresh()
        self.wtw_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)

    def test_FRUM_84567_launch_tivo_perf(self):
        """
        Measure time between events:
            'Launch Tivo app by sending select' and 'Home Screen is displayed'

        XRay:
            https://jira.tivo.com/browse/FRUM-84567
        """
        self.system_page.launch_device_settings_screen()
        self.home_page.pause(2)
        app_name = self.home_labels.LBL_APP_NAME_FOR_MSO.get(Settings.mso)
        if not app_name:
            raise AssertionError(f"App name is not defined for mso {Settings.mso}")
        self.system_page.select_device_settings_menu_item("Apps", app_name, "Force stop", "OK")
        self.home_page.capture_events()
        self.home_page.launch_app_through_UI()
        self.home_page.handle_welcome_screen_on_hydra_start()
        self.vision_page.verify_transition(region=VTtweaks.LOWER_SCREEN_REGION, timeout=120, stable=20)
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events, "AppHydraStart", "AppHydra")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        # Test case is failing as it is unable to take latest dump and verify Homescreen. Created CA-20588
        # self.screen.refresh()
        # self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    def test_FRUM_84569_enter_on_demand_screen_perf(self):
        """
        Measure time between events:
            'press menu shortcut for ON DEMAND' and 'ON DEMAND text displayed on top left of the screen'

        XRay:
            https://jira.tivo.com/browse/FRUM-84569
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_ONDEMAND_SHORTCUT, refresh=False)
        self.vision_page.verify_transition(region=VTtweaks.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, timeout=14, stable=7)
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events, "KeyPressed", "ScreenReady")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.screen.refresh()
        self.wtw_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SCREENTITLE)

    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_FRUM_84568_boot_device_perf(self):
        """
        Measure time between events:
            'switch off device' and 'Home Screen is displayed'

        XRay:
            https://jira.tivo.com/browse/FRUM-84568
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.reboot_device()
        self.vision_page.verify_transition(region=VTtweaks.LOWER_SCREEN_REGION, timeout=200, stable=50)
        self.guide_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_91331_show_playback_inprogress_recording_performance(self):
        """
        Measure time between events:
            'open recording program' and 'playback start'

        XRay:
            https://jira.xperi.com/browse/FRUM-91331
        """
        if Settings.is_feature_4k():
            channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True, filter_channel=True)
            if not channel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            channel = self.service_api.get_4k_channel(channel_count=-1, resolution="hd", recordable=True, filter_channel=True)
        if not channel:
            pytest.skip("No channels found")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0], confirm=True)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.open_olg()
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.open_playback_overlay_for_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.pause(10)
        self.my_shows_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.my_shows_page.press_ok_button(refresh=False)
        self.vision_page.measure_playback_starting(black_screen_expected=False)
        self.watchvideo_page.pause(10)
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events, "KeyPressed", "LiveTvPlayback")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.my_shows_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION,
                                                              black_screen_expected=False)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_91332_show_playback_inprogress_recording_5_min_wait_performance(self):
        """
        Measure time between events:
            'open recording program after 5 minutes waiting' and 'playback start'

        XRay:
            https://jira.xperi.com/browse/FRUM-91332
        """
        if Settings.is_feature_4k():
            channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True, filter_channel=True)
            if not channel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            channel = self.service_api.get_4k_channel(channel_count=-1, resolution="hd", recordable=True, filter_channel=True)
        if not channel:
            pytest.skip("No channels found")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0], confirm=True)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.open_olg()
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.watchvideo_page.watch_video_for(270)  # waiting for 5 minutes in total
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.open_playback_overlay_for_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.pause(10)
        self.my_shows_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.my_shows_page.press_ok_button(refresh=False)
        self.vision_page.measure_playback_starting(black_screen_expected=False)
        self.watchvideo_page.pause(10)
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events, "KeyPressed", "LiveTvPlayback")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.my_shows_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION,
                                                              black_screen_expected=False)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_91690_show_playback_complete_recording_performance(self):
        """
        Measure time between events:
            'open complete recording program' and 'playback start'

        XRay:
            https://jira.xperi.com/browse/FRUM-91690
        """
        if Settings.is_feature_4k():
            channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True, filter_channel=True)
            if not channel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            channel = self.service_api.get_4k_channel(channel_count=-1, resolution="hd", recordable=True, filter_channel=True)
        if not channel:
            pytest.skip("No channels found")
        channel_num = self.service_api.map_channel_number_to_currently_airing_offers(
            [channel], self.service_api.channels_with_current_show_start_time(duration=1800, use_cached_grid_row=True))
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num[0][1])
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.open_olg()
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.open_playback_overlay_for_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.pause(10)
        self.my_shows_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.my_shows_page.press_ok_button(refresh=False)
        self.vision_page.measure_playback_starting(black_screen_expected=False)
        self.watchvideo_page.pause(10)
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events, "KeyPressed", "LiveTvPlayback")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.my_shows_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION,
                                                              black_screen_expected=False)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_91789_resume_partially_watched_playback_performance(self):
        """
        Measure time between events:
            'resume_partially_watched_playback' and 'playback start'
        XRay:
            https://jira.xperi.com/browse/FRUM-91789
        """
        if Settings.is_feature_4k():
            channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True, filter_channel=True)
            if not channel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            channel = self.service_api.get_4k_channel(channel_count=-1, resolution="hd", recordable=True, filter_channel=True)
        if not channel:
            pytest.skip("No channels found")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0], confirm=True)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.open_olg()
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.my_shows_page.screen.base.press_back()
        self.my_shows_page.pause(10)
        self.my_shows_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.my_shows_page.press_ok_button(refresh=False)
        self.vision_page.measure_playback_starting(black_screen_expected=False)
        self.watchvideo_page.pause(10)
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events, "KeyPressed", "VideoPlayerStart")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.my_shows_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION,
                                                              black_screen_expected=False)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_93717_ndvr_record_and_playback_recorded_performance(self):
        """
        Measure time between events:
            'resume_partially_watched_playback' and 'playback start'
        XRay:
            https://jira.xperi.com/browse/FRUM-93717
        """
        if Settings.is_feature_4k():
            channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True, filter_channel=True)
            if not channel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            channel = self.service_api.get_4k_channel(channel_count=-1, resolution="hd", recordable=True, filter_channel=True)
        if not channel:
            pytest.skip("No channels found")
        channel_num = self.service_api.map_channel_number_to_currently_airing_offers(
            [channel], self.service_api.channels_with_current_show_start_time(duration=1800, use_cached_grid_row=True))
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num[0][1])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.open_playback_overlay_for_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.pause(10)
        self.my_shows_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.my_shows_page.press_ok_button(refresh=False)
        self.vision_page.measure_playback_starting(black_screen_expected=False)
        self.watchvideo_page.pause(10)
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events, "KeyPressed", "LiveTvPlayback")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.my_shows_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION,
                                                              black_screen_expected=False)

    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_FRUM_94145_direct_tune_hd_channel_performance(self):
        """
        Measure time between events:
            'enter channel' and 'playback start'
        XRay:
            https://jira.xperi.com/browse/FRUM-94145
        """
        if Settings.is_feature_4k():
            hdchannel = self.service_api.get_4k_channel(channel_count=-1, resolution="uhd", filter_channel=True)
            if not hdchannel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            hdchannel = self.service_api.get_random_live_channel_rich_info(channel_count=1, filter_channel=True)
        if not hdchannel:
            pytest.skip("HD channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(hdchannel[0])
        self.guide_page.get_live_program_name(self)
        self.watchvideo_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.my_shows_page.press_ok_button(refresh=False)
        self.vision_page.measure_playback_starting(black_screen_expected=False)
        self.watchvideo_page.pause(10)
        diff = KpiCalculator.calculate_period_between_events(
            self.menu_page.get_all_captured_events(), "KeyPressed", "LiveTvPlayback")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.watchvideo_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION,
                                                              black_screen_expected=False)

    @pytest.mark.vt_core_feature
    def test_FRUM_93944_channel_up_in_livetv_encrypted_channel_performance(self):
        """
        Measure time between events:
            'channel up' and 'playback start'
        XRay:
            https://jira.xperi.com/browse/FRUM-93944
        """
        if Settings.is_feature_4k():
            uhdchannel = self.service_api.get_4k_channel(channel_count=-1, resolution="uhd", filter_channel=True)
            if not uhdchannel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            uhdchannel = self.service_api.get_random_live_channel_rich_info(channel_count=1, filter_channel=True)
        if not uhdchannel:
            pytest.skip("HD channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(uhdchannel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.screen.base.press_channel_up(time=0)
        self.vision_page.measure_playback_starting(black_screen_expected=True, sensitivity_level=3)
        self.watchvideo_page.pause(10)
        diff = KpiCalculator.calculate_period_between_events(
            self.menu_page.get_all_captured_events(), "KeyPressed", "LiveTvPlayback")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.watchvideo_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION)

    def test_FRUM_140041_guide_navigate_right_perf(self):
        """
        Measure time between events:
            'press GUIDE screen' and 'Right in right navigation transition ends'
        Guide navigate right
            1 Go To Tivo Home Screen
            2 Press menu shortcut number for "Guide"
            3 Wait for "Guide" screen to appear & verify the guide screen
            4 Press RIGHT button to navigate next program
            5 Wait until transition animation end
            6 Measure and report duration between step 4 & 5 using VT/ PLOG
        XRay:
          https://jira.xperi.com/browse/CA-22378
        """
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text(
            self.home_labels.LBL_HOME_SCREENTITLE,
            region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.capture_events()
        self.screen.base.press_right()
        self.vision_page.verify_transition(expected=True, region=VTtweaks.NO_PIG_REGION)
        diff = KpiCalculator.calculate_period_between_events(
            self.guide_page.get_all_captured_events(), "KeyPressed", "ContentScreenReady")
        self.guide_page.stop_events_capturing()
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))

    def test_FRUM_95012_vod_playback_performance(self):
        """
        Measure time between events:
            'enter VOD program' and 'playback start'
        XRay:
            https://jira.xperi.com/browse/FRUM-95012
        """
        status, results = self.vod_api.get_offer_playable()
        if results is None:
            pytest.skip("The content is not available on VOD catalog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.capture_events()
        recording_process, recorded_video_path = self.vision_page.background_recording()
        self.vod_page.play_any_playable_vod_content(self, results, confirm=False)
        self.vision_page.measure_playback_starting(black_screen_expected=False)
        diff = KpiCalculator.calculate_period_between_events(
            self.menu_page.get_all_captured_events(), "KeyPressed", "LiveTvPlayback")
        self.vision_page.logger.perf_log("animation_duration_plog", "{:.4f}".format(diff))
        self.watchvideo_page.stop_events_capturing()
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.vision_page.verify_recording_process_succeed(recording_process, recorded_video_path)
        self.vision_page.measure_playback_starting_from_video(recorded_video_path, region=VTtweaks.NO_PIG_REGION,
                                                              black_screen_expected=False)
