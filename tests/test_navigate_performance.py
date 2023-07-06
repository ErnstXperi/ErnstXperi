import os
import pytest

from set_top_box.test_settings import Settings
from set_top_box.conftest import setup_perf_log  # noqa: F401
from set_top_box.client_api.end2end.conftest import setup_e2e  # noqa: F401
from set_top_box.client_api.Menu.conftest import disable_parental_controls  # noqa: F401
from set_top_box.client_api.home.conftest import clear_client_cache  # noqa: F401
from tools.kpi_calculator import KpiCalculator


@pytest.mark.usefixtures('setup_e2e')
@pytest.mark.usefixtures('setup_perf_log')
@pytest.mark.usefixtures('clear_client_cache')
@pytest.mark.timeout(600)
@pytest.mark.perf_navigation
class TestNavigatePerformance:

    def pytest_generate_tests(self, metafunc):
        """
        Hook to setup number of test repetition.
        """
        repeat_number = int(os.getenv("TEST_REPEAT_NUMBER", 1))
        if repeat_number > 1:
            metafunc.fixturenames.append('repeat_cnt')
            metafunc.parametrize("repeat_cnt", range(repeat_number))

    def test_open_guide(self):
        self.home_page.back_to_home_short()
        self.home_page.capture_events()
        self.screen.base.press_guide()
        self.guide_page.wait_for_screen_ready()
        events = self.text_search_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events,
                                                             "KeyPressed",
                                                             "VisualisationComplete")
        self.perf_logger.perf_log("animation_duration", "{:.4f}".format(diff))
        self.guide_assertions.verify_guide_screen(self)
        self.home_assertions.verify_overlay_shown(expected=False)

    @pytest.mark.perf_TE4
    def test_open_w2w(self):
        self.home_page.back_to_home_short()
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WHATTOWATCH_SHORTCUT)
        self.wtw_page.pause(3)
        self.wtw_page.wait_for_screen_ready('WhatToWatch', 60000)
        events = self.text_search_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events,
                                                             "KeyPressed",
                                                             "VisualisationComplete")
        self.perf_logger.perf_log("animation_duration", "{:.4f}".format(diff))
        self.home_assertions.verify_screen_title(self.home_labels.LBL_WHATTOWATCH_SHORTCUT)
        self.home_assertions.verify_overlay_shown(expected=False)

    def test_open_search(self):
        self.home_page.back_to_home_short()
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_SEARCH_SHORTCUT)
        self.text_search_page.pause(5)
        self.text_search_page.wait_for_screen_ready('SearchMainScreen', 60000)
        events = self.text_search_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events,
                                                             "KeyPressed",
                                                             "VisualisationComplete")
        self.perf_logger.perf_log("animation_duration", "{:.4f}".format(diff))
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT)
        self.home_assertions.verify_overlay_shown(expected=False)

    def test_open_menu_screen(self):
        self.home_page.back_to_home_short()
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_MENU_SHORTCUT)
        self.home_page.pause(1)
        self.menu_page.wait_for_screen_ready()
        events = self.menu_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events,
                                                             "KeyPressed",
                                                             "VisualisationComplete")
        self.perf_logger.perf_log("animation_duration", "{:.4f}".format(diff))
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MENU_SCREENTITLE)
        self.home_assertions.verify_overlay_shown(expected=False)

    def test_open_my_shows(self):
        self.home_page.back_to_home_short()
        self.home_page.capture_events()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.home_page.pause(5)
        self.my_shows_page.wait_for_screen_ready('MyShowsMainScreen', 60000)
        events = self.my_shows_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events,
                                                             "KeyPressed",
                                                             "VisualisationComplete")
        self.perf_logger.perf_log("animation_duration", "{:.4f}".format(diff))
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.home_assertions.verify_overlay_shown(expected=False)

    def test_open_vod(self):
        self.home_page.back_to_home_short()
        self.home_page.capture_events()
        self.home_page.pause(1)
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_ONDEMAND_SHORTCUT)
        self.vod_page.pause(5)
        self.vod_page.wait_for_screen_ready('VodBrowseMainScreen', 60000)
        events = self.vod_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events,
                                                             "KeyPressed",
                                                             "VisualisationComplete")
        self.perf_logger.perf_log("animation_duration", "{:.4f}".format(diff))
        self.home_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)
        self.home_assertions.verify_overlay_shown(expected=False)

    @pytest.mark.perf_TE4
    def test_frum_79155_back_to_home(self):
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_SEARCH_SHORTCUT)
        self.home_page.capture_events()
        self.screen.base.press_back()
        self.home_page.pause(5)
        self.wtw_page.wait_for_screen_ready('HomeMainScreen', 60000)
        events = self.text_search_page.get_all_captured_events()
        diff = KpiCalculator.calculate_period_between_events(events,
                                                             "KeyPressed",
                                                             "VisualisationComplete")
        self.perf_logger.perf_log("animation_duration", "{:.4f}".format(diff))
        self.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_assertions.verify_overlay_shown(expected=False)
