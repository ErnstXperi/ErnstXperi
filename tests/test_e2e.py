"""
    @author: artur.kovalenko@tivo.com
    @created: Feb-14-2020
"""

import random
import time

import pytest

from set_top_box.test_settings import Settings
from set_top_box.conf_constants import HydraBranches, NotificationSendReqTypes, RemoteCommands
from set_top_box.client_api.end2end.conftest import setup_e2e, switch_off_show_only_favorite_channels_in_guide  # noqa: F401
from set_top_box.client_api.end2end.conftest import decrease_screen_saver, set_screen_saver_default_value  # noqa: F401
from set_top_box.client_api.home.conftest import restore_mind_availability  # noqa: F401
from set_top_box.client_api.Menu.conftest import disable_parental_controls, enable_netflix, disable_video_window  # noqa: F401
from set_top_box.client_api.Menu.conftest import setup_lock_parental_and_purchase_controls  # noqa: F401
from set_top_box.client_api.Menu.conftest import enable_video_providers  # noga: F401
from set_top_box.client_api.Menu.conftest import disable_video_providers  # noga: F401
from set_top_box.client_api.Menu.conftest import setup_parental_controls_and_always_require_pin
from set_top_box.client_api.Menu.conftest import setup_disable_closed_captioning, setup_parental_control, \
    setup_cleanup_parental_and_purchase_controls
from set_top_box.client_api.home.conftest import launch_hydra_app_when_script_is_on_ott
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings, setup_delete_book_marks, \
    setup_adhoc_OTT_provider_and_functionality, setup_myshows_schedule_recording   # noqa: F401
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_start_tivo_app, pluto_tv_app_install  # noqa: F401
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions
from set_top_box.client_api.guide.conftest import setup_cleanup_list_favorite_channels_in_guide
from set_top_box.client_api.TTS.conftest import stop_tts_log
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.guide.conftest import toggle_mind_availability  # noqa: F401


@pytest.mark.usefixtures('setup_e2e')
@pytest.mark.notapplicable(Settings.is_devhost())
@pytest.mark.e2e
@pytest.mark.timeout(Settings.timeout)
class TestEnd2End(object):
    TIMEOUT_FAST = 600
    TIMEOUT_MID = 1200
    TIMEOUT_LONG = 3600

    @pytestrail.case("C11684188")
    @pytest.mark.parental_control
    @pytest.mark.longrun
    @pytest.mark.menu
    def test_74063254_verify_lock_channels_menu_not_listed_in_parental_controls(self):
        """
        Description:
        To verify that 'Lock Channels' item does not shown in Parental Controls Menu.
        """
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        parental_control_title = parental_control.upper()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_assertions.verify_screen_title(parental_control_title)
        self.menu_assertions.verify_menu_item(self.menu_labels.LBL_LOCK_CHANNELS, expected=False)

    @pytest.mark.stress
    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_stress_testing_001_verify_stress_scenario_with_ott_exit(self):
        """
        Description:
        Verify stress scenario with OTT exit
        """
        KEYPRESS_STRESS_COUNT_MAX = 100
        KEYPRESS_STRESS_COUNT_MED = 30
        KEYPRESS_STRESS_COUNT_MIN = 50
        KEYPRESS_STRESS_OK_BUTTON = 3
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_GUIDE_SHORTCUT)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.wait_for_screen_ready()
        for key_press in range(KEYPRESS_STRESS_COUNT_MAX):
            self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.press_netflix_and_verify_screen(self)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_page.press_back_button()
        for key_press in range(KEYPRESS_STRESS_OK_BUTTON):
            self.watchvideo_page.press_ok_button()
        # Forwarding the video
        for key_press in range(KEYPRESS_STRESS_COUNT_MED):
            self.watchvideo_page.press_right_button()
        self.watchvideo_page.press_home_button()
        self.home_assertions.verify_home_title()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_GUIDE_SHORTCUT)
        self.watchvideo_page.press_ok_button()
        for key_press in range(KEYPRESS_STRESS_COUNT_MIN):
            self.watchvideo_page.press_channel_down_button()
        if self.watchvideo_page.is_overlay_shown() or self.watchvideo_page.osd_shown():
            self.watchvideo_page.press_ok_button()
        else:
            self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_home_button()

    @pytest.mark.e2e1_15
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-22073")
    # @pytest.mark.notapplicable(Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.usefixtures("setup_myshows_schedule_recording")
    @pytest.mark.usefixtures("restore_mind_availability")
    def test_22073_resiliency_mode_ndvr_socu_vod(self):
        playbacks = ["ndvr", "vod", "socu"]
        for x in playbacks:
            if x == "vod":
                status, result = self.vod_api.get_offer_playable()
                if result is None:
                    pytest.skip("The content is not available on VOD catlog.")
                self.home_page.back_to_home_short()
                self.vod_page.goto_vodoffer_program_screen(self, result)
                self.vod_page.play_vod_entitled_content(self, result)
                self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
                self.home_page.toggle_mind_availability()
                self.home_assertions.verify_connected_disconnected_state_happened(is_select=False)
                self.home_page.toggle_mind_availability()
                self.home_page.back_to_home_short()
                self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)
            if x == "socu":
                channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                                   filter_socu=True,
                                                                                   restrict=False)
                if not channel:
                    pytest.skip("Could not find any SOCU channel")
                channel_number = (channel[0][0])
                self.home_page.go_to_guide(self)
                self.guide_page.enter_channel_number(channel_number)
                focused_item = self.guide_page.get_live_program_name(self)
                self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
                self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
                self.home_page.toggle_mind_availability()
                self.home_assertions.verify_connected_disconnected_state_happened(is_select=False)
                self.home_page.toggle_mind_availability()
                self.home_page.back_to_home_short()
                self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)
            if x == "ndvr":
                self.my_shows_page.navigate_to_recordings_filter(self)
                self.watchvideo_page.press_ok_button()
                self.watchvideo_page.press_ok_button()
                self.watchvideo_page.press_ok_button()
                self.watchvideo_assertions.verify_view_mode(
                    self.my_shows_page.get_watch_or_video_recording_view_mode(self))
                self.my_shows_assertions.verify_recording_playback(self)
                self.home_page.toggle_mind_availability()
                self.home_assertions.verify_connected_disconnected_state_happened()
                self.home_page.toggle_mind_availability()
                self.home_page.back_to_home_short()
                self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False)

    @pytestrail.case("C11684202")
    @pytest.mark.menu
    @pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_disable_closed_captioning")
    def test_74104163_verify_changes_in_accessibility_reflect_in_live_tv_and_vod(self):
        """
        Description:
        To Verify Changes made in accessibility options and reflected in Live TV/VOD
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_on_cc(self, ON=True)
        self.menu_page.go_to_accessibility(self)
        self.menu_assertions.verify_accessibility_screen_title(self)
        self.menu_page.go_to_closed_captioning(self)
        self.menu_assertions.verify_cc_state(self, ON=True)
        self.menu_assertions.select_menu(self.menu_labels.LBL_OFF)
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.turn_on_cc(self, ON=True)
        self.watchvideo_page.turn_on_cc(self, ON=False)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11685232")
    @pytest.mark.menu
    @pytest.mark.infobanner
    @pytest.mark.usefixtures("stop_tts_log")
    def test_74569488_verify_changes_in_accessibility_reflect_in_live_tv(self):
        """
        Description:
        T74569488
        To Verify Changes made in accessibility options and reflected in Live TV
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        # self.watchvideo_assertions.verify_playback_play()
        if Settings.is_managed():
            self.watchvideo_page.show_accessibility_menu()
            self.watchvideo_assertions.verify_accessibility_strip()
            self.watchvideo_page.press_back_button()
        self.watchvideo_page.turn_on_cc(self, ON=True, consume_error=True)
        if Settings.is_managed():
            self.watchvideo_page.show_accessibility_menu()
            self.vod_assertions.verify_closed_captioning(self.vod_labels.LBL_CLOSED_CAPTIONING_CC_OFF)
        self.menu_page.go_to_accessibility(self)
        self.menu_assertions.verify_accessibility_screen_title(self)
        self.menu_page.go_to_closed_captioning(self)
        self.menu_assertions.verify_cc_state(self, ON=True)
        self.menu_assertions.select_menu(self.menu_labels.LBL_OFF)
        if Settings.is_managed():
            self.watchvideo_page.show_accessibility_menu()
            self.vod_assertions.verify_closed_captioning(self.vod_labels.LBL_CLOSED_CAPTIONING_CC_ON)

    @pytestrail.case("C11685183")
    @pytest.mark.home
    @pytest.mark.longrun
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.skipif(("amino" not in Settings.platform.lower() and "puck" not in Settings.platform.lower()),
                        reason="Valid for amino and puck only")
    def test_74171929_verify_any_remote_key_wake_up(self):
        """
        Description:
        To be able to wake up the box from screensaver by any Remote key.
        """
        home = self.home_page
        home.back_to_home_short()
        src = self.home_page.screen.base
        buttons = [  # monkey doesn't wake up device
            # home.press_netflix_and_verify_screen,
            # home.press_youtube_and_verify_screen,
            home.press_apps_and_verify_screen,
            home.press_vod_and_verify_screen,
            home.press_home_and_verify_screen,
            home.press_guide_and_verify_screen,
            src.press_advance, src.press_playpause,
            src.press_fast_forward,
            src.press_replay,
            src.press_rewind,
            src.press_right,
            src.press_left,
            src.press_up,
            src.press_down]
        counter = 0
        for button in buttons:
            home.pause(80)
            button() if counter > 3 else button(self)
            home.pause(15)
            with pytest.raises(Exception):
                self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
            counter += 1

    @pytestrail.case("C11684193")
    @pytest.mark.vod
    # @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_74074769_1_verify_smooth_transition_trickplay_vod(self):
        """
        Description:
        https://testrail.tivo.com//index.php?/cases/view/8880107
        74074769
        To Verify smooth transitions between the trickplay
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        self.home_page.back_to_home_short()
        durationRange = range(2000, 3000)
        requests = {}
        for i in range(len(durationRange)):
            request = 'request' + str(i)
            requests.update({request: {"offer": {"packageType": "fvod", "filterValues": "trickplayRestriction",
                                                 "duration": durationRange[i]}}})
        status, result = self.vod_api._searchVODMixes(requests)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_page.press_ff(times=3)
        self.watchvideo_page.open_olg()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        self.watchvideo_page.pause(15)
        self.watchvideo_page.press_ff(times=3)
        self.watchvideo_page.press_playpause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        self.watchvideo_page.press_rewind(times=3)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel(refresh=False)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.pause(15)
        self.watchvideo_page.press_playpause_button()
        if Settings.hydra_branch("b-hydra-streamer-1-7") == Settings.hydra_branch():
            timeout = ((5 * 60 + 30) * 1000)
        else:
            timeout = ((10 * 60 + 30) * 1000)
        self.watchvideo_page.wait_for_screen_ready(self.vod_labels.LBL_TIMEOUT_OVERLAY, timeout=timeout)
        self.watchvideo_assertions.verify_overlay_shown()

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685236")
    @pytest.mark.livetv
    @pytest.mark.skipif(Settings.is_technicolor(), reason="No cache")
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_74074769_2_verify_smooth_transition_trickplay_live_tv(self):
        """
        Description:
        https://testrail.tivo.com//index.php?/cases/view/8880107
        74074769
        To Verify smooth transitions between the trickplay
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        channel = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.vod_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_start_of_video()
        self.watchvideo_page.press_ff(times=3)
        self.watchvideo_page.open_olg()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        self.watchvideo_page.pause(15)
        self.watchvideo_page.press_ff(times=3)
        self.watchvideo_page.press_playpause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        self.watchvideo_page.press_rewind(times=3)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytestrail.case("C11685244")
    @pytest.mark.vod
    @pytest.mark.menu
    @pytest.mark.infobanner
    @pytest.mark.not_devhost  # livetv button is not implemented for devhost
    @pytest.mark.usefixtures("setup_disable_closed_captioning")
    def test_10840631_verify_changes_cc_across_app(self):
        """
        To verify closed captioning ON/OFF are common across the app.

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/10840631
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_on_cc(self, ON=True)
        self.menu_page.go_to_accessibility(self)
        self.menu_assertions.verify_accessibility_screen_title(self)
        self.menu_page.go_to_closed_captioning(self)
        self.menu_assertions.verify_cc_state(self, ON=True)
        self.menu_assertions.select_menu(self.menu_labels.LBL_OFF)
        self.home_page.back_to_home_short()
        durationRange = range(2000, 3000)  # to eliminate short show
        requests = {}
        for i in range(len(durationRange)):
            request = 'request' + str(i)
            requests.update({request: {"offer": {"packageType": "fvod", "duration": durationRange[i]}}})
        status, result = self.vod_api._searchVODMixes(requests)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_on_cc(self, ON=True)
        self.menu_page.go_to_accessibility(self)
        self.menu_assertions.verify_accessibility_screen_title(self)
        self.menu_page.go_to_closed_captioning(self)
        self.menu_assertions.verify_cc_state(self, ON=True)
        self.menu_assertions.select_menu(self.menu_labels.LBL_OFF)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685184")
    @pytest.mark.ndvr
    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74200415_verify_nDvr_recording_with_commercial(self):
        """
        74200415
        Description:
        Verify playing a nDVR recording with commercials, fast forwarding during commercials, and playing until the end
        """
        # TODO: to be refactored channel source once cloud recordings will contain commercial
        channels = self.service_api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True)
        recording = self.service_api.schedule_single_recording(channels=channels)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        recorded_content = self.my_shows_page.convert_special_chars(recording[0][0])
        self.my_shows_page.select_menu_by_substring(recorded_content)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_start_of_video()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete(True)

    @pytestrail.case("C11684194")
    @pytest.mark.livetv
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="Remote should contain advance an replay keys")
    def test_74077072_verify_advance_and_replay(self):
        """
        74077072
        Description:
        Press and release trickplay buttons like Advance & Replay for n times.
        """
        restrictions = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True,
                                                                                           entitled=True)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(restrictions[0], confirm=True)
        # We do not need program name from a Guide Cell at this point, so no rasing errors if no text on the cell
        self.guide_page.get_live_program_name(self, raise_error_if_no_text=False)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.build_cache(9)
        self.watchvideo_page.navigate_to_start_of_video()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_right_multiple_times(no_of_times=2)
        self.watchvideo_assertions.is_advance_focused(self)
        start_pos = self.watchvideo_page.get_trickplay_current_position()
        self.guide_page.press_enter_multiple_times(20)
        self.watchvideo_assertions.verify_playback_play()
        current_pos = self.watchvideo_page.get_trickplay_current_position()
        self.home_page.log.info(f"start_pos: {start_pos} and current_pos: {current_pos}")
        self.watchvideo_assertions.verify_playback_streaming_for(start_pos, current_pos)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_left_multiple_times(no_of_times=2)
        self.watchvideo_assertions.is_replay_focused(self)
        self.guide_page.press_enter_multiple_times(20)
        latest_pos = self.watchvideo_page.get_trickplay_current_position()
        self.home_page.log.info(f"current_pos: {current_pos} and latest_pos: {latest_pos}")
        self.watchvideo_assertions.verify_playback_streaming_for(latest_pos, current_pos)

    @pytestrail.case("C11684205")
    @pytest.mark.vod
    @pytest.mark.not_devhost
    @pytest.mark.usefixtures("set_screen_saver_default_value")
    def test_74122764_VOD_playback_after_screen_saver(self):
        """
        Description:
        To verify VOD playback after waking up from screen saver and sleep
        """
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.select_menu(self.menu_labels.LBL_VIDEO_BACKGROUND)
        self.menu_page.nav_to_menu(self.menu_labels.LBL_DISPLAY_VIDEO)
        self.menu_page.nav_to_item_option(self.menu_labels.LBL_YES)
        durationRange = range(2000, 3000)  # to eliminate short show
        requests = {}
        for i in range(len(durationRange)):
            request = 'request' + str(i)
            requests.update({request: {"offer": {"packageType": "fvod", "duration": durationRange[i]}}})
        status, result = self.vod_api._searchVODMixes(requests)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_assertions.verify_playback_play()
        last = self.watchvideo_page.get_trickplay_current_position()
        self.home_page.back_to_home_short()
        self.watchvideo_page.pause(4 * 60)
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_assertions.verify_playback_play()
        current = self.watchvideo_page.get_trickplay_current_position()
        self.watchvideo_assertions.verify_playback_streaming_for(last, current, delta=3)

        # self.watchvideo_page.pause(6 * 60)  # current player fallback behaviour may cause failure
        # self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        # self.home_page.back_to_home_short()
        # self.home_page.select_menu_shortcut(self.home_labels.LBL_ONDEMAND_SHORTCUT)
        # self.vod_assertions.verify_screen_title(self.vod_labels.LBL_ON_DEMAND)
        # self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        # self.vod_page.select_vod(self, collectionID, contentID, title)
        # self.vod_page.play_content(self, resume=True)
        # self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        # self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        # self.watchvideo_assertions.verify_playback_play()
        # current = self.watchvideo_page.get_trickplay_current_position()
        # self.watchvideo_assertions.verify_playback_streaming_for(last, current, delta=4)

    @pytestrail.case("C11684192")
    @pytest.mark.vod
    @pytest.mark.not_devhost
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74072466_create_bookmarks_pc_locked(self):
        """
        Description:
        To be able to create onepass/bookmarks when PC is locked
        """
        self.home_page.back_to_home_short()
        # requests = {'request1': {"offer": {"packageType": "fvod", 'episodic': 1}}}
        # Get any entited episodic content instead of checking only free vod
        status, result = self.vod_api.getOffer_mapped_svod_entitledSubscribed_series()
        self.vod_page.extract_entryPoint(result)
        if result is None:
            pytest.skip("Test requires mapped offer to validate onepass")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_assertions.verify_playback_play()
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_set_rating_limit(self)
        self.menu_page.set_rating_limits(self.menu_labels.LBL_BLOCK_ALL_RATED, self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         self.menu_labels.LBL_BLOCK_ALL_UNRATED, self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS_MENUITEM)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        try:
            self.program_options_assertions.verify_series_screen()
            self.menu_page.menu_navigate_left_right(0, 1)
            self.program_options_assertions.verify_go_to_episode_screen_icon_focused()
            self.program_options_page.press_ok_button()
            self.program_options_assertions.verify_action_view_mode(self)
        except Exception:
            self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.create_one_pass(self)
        self.program_options_assertions.verify_one_pass_created()

    @pytestrail.case("C11685176")
    @pytest.mark.menu
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.skipif(Settings.is_apple_tv(), reason="CA-20471-Reboot not implemented")
    def test_74134299_user_pref_retained_after_reboot(self):
        """
        T74134299
        To verify changes made in User Preference are retained after reboot of device.
        :return:
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.menu_page.go_to_video_providers(self)
        self.menu_page.unchecked_option(self.menu_labels.LBL_NETFLIX)
        self.menu_page.menu_press_back()
        self.menu_assertions.verify_user_pref_screen_title()
        self.menu_page.go_to_favorite_channels()
        self.menu_assertions.verify_favorite_channels_screen_title()
        channel = self.service_api.get_channel_search()[4].channel_number
        self.menu_page.enter_channel_number(channel)
        self.menu_page.checkbox_option_in_focus(self)
        self.menu_page.menu_press_back()
        self.menu_page.go_to_autoplay_next_episode()
        self.menu_assertions.select_menu(self.menu_labels.LBL_OFF)
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME, reboot=True, wait_reboot=200)
        self.menu_page.go_to_video_providers(self)
        self.menu_assertions.verify_item_unchecked(self.menu_labels.LBL_NETFLIX, self)
        self.menu_page.menu_press_back()
        self.menu_assertions.verify_user_pref_screen_title()
        self.menu_page.go_to_favorite_channels()
        self.menu_assertions.verify_favorite_channels_screen_title()
        self.menu_page.enter_channel_number(channel)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_item_checked(channel, self)
        self.menu_page.menu_press_back()
        self.menu_page.go_to_autoplay_next_episode()
        self.menu_assertions.verify_item_checked(self.menu_labels.LBL_OFF, self)

    @pytestrail.case("C11685221")
    @pytest.mark.menu
    def test_74458831_verify_jump_channels_names_in_user_pref(self):
        """
        74458831
        To verify that jump channel names are displayed under favorite channels screen
        :return:
        """
        jump_channels = self.service_api.get_jump_channels_list()
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_user_pref_screen_title()
        self.menu_page.go_to_favorite_channels()
        self.menu_assertions.verify_favorite_channels_screen_title()
        for channel in jump_channels:
            self.menu_page.enter_channel_number(channel)
            self.menu_assertions.verify_favorite_channels_list_item()

    @pytestrail.case("C11685219")
    @pytest.mark.livetv
    def test_74454141_verify_loading_indicator_OSD(self):
        """
        74454141
        To verify the time taken for the loading indicator OSD to display on channel change using Up-Down or OLG
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        # Getting cached response since get_grid_row_search() was called above
        channels = self.service_api.extract_offer_id(
            self.service_api.channels_with_current_show_start_time(transportType="stream", use_cached_grid_row=True),
            genre='series', count=1)
        self.watchvideo_page.enter_channel_number(channels[0][3])
        self.watchvideo_page.pause(3)
        try:
            self.watchvideo_page.verify_osd_text(self.watchvideo_labels.LBL_LOADING_VIDEO_OSD)
        except KeyError:
            self.watchvideo_assertions.verify_playback_play(refresh=False)

    @pytestrail.case("C11685227")
    def test_74487072_pc_block_alternating_audio_track(self):
        """
        74487072
        Verify an alternate audio track.
        :return:
        """
        row = self.service_api.channels_with_current_show_start_time(duration=1800)
        channels = self.service_api.get_random_encrypted_unencrypted_channels(encrypted=True,
                                                                              grid_row=row, channel_count=-1,
                                                                              filter_channel=True)

        if len(channels) < 4:
            channels.extend(self.service_api.get_random_encrypted_unencrypted_channels(encrypted=False,
                                                                                       grid_row=row, channel_count=3,
                                                                                       filter_channel=True))
        msg = ""
        for channel in channels:
            try:
                self.home_page.go_to_guide(self)
                self.watchvideo_page.enter_channel_number(channel[0], confirm=True)
                self.watchvideo_page.press_ok_button()
                self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
                self.watchvideo_assertions.verify_playback_play()
                self.watchvideo_page.show_info_banner()
                self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_AUDIO_TRACK, refresh=False)
                self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_AUDIO_TRACK_OVERLAY_TITLE)
                track = self.watchvideo_page.get_audio_track()
                self.watchvideo_page.select_menu(track)
                break
            except Exception as err:
                msg += "{} \n".format(err)
        else:
            pytest.skip("Couldn't find channels. \n {}".format(msg))

        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_AUDIO_TRACK, refresh=False)
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_AUDIO_TRACK_OVERLAY_TITLE)
        self.watchvideo_assertions.verify_audio_track_selected(track)

    @pytestrail.case("C11685192")
    @pytest.mark.guide
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74334382_verify_launching_an_app_from_the_guide(self):
        """
        74334382
         Verify launching an app from the Guide screen is successful and pressing the Exit button returns to Guide
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.home_page.press_guide_button()
        self.guide_assertions.verify_guide_title()
        self.guide_assertions.press_netflix_and_verify_screen(self)
        self.guide_page.press_exit_button()
        self.guide_assertions.verify_guide_title()

    @pytestrail.case("C11685180")
    @pytest.mark.guide
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74160107_verify_creating_one_pass_from_future_airing(self):
        """
        74160107
         Verify creating a OnePass from a future airing,
         available and entitled nDVR show in Guide displays the OnePass in My Shows and OnePass Manager.
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready('GridGuide')
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.build_cache(180)
        # Let's call cached get_grid_row_search() since it's already called above
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, use_cached_grid_row=True),
            self.service_api.channels_with_current_show_start_time(
                transportType="stream", duration=5400, use_cached_grid_row=True),
            genre="series", count=1, future=1, filter_channel=True)
        if not channel:
            pytest.skip("No recordable channel with series found")
        self.home_assertions.press_guide_and_verify_screen(self)
        self.guide_page.enter_channel_number(channel[0][1])
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        self.menu_page.menu_navigate_left_right(0, 1)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.guide_assertions.verify_onepass_icon()
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_assertions.verify_one_pass_exists(program)

    @pytestrail.case("C11685190")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74230822_press_apps_button_lead_to_apps_and_games_screen(self):
        """
        T74230822
        Verify pressing the Apps button from Home goes to the Apps & Games screen, and launching an app is successful
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.home_page.press_apps_and_verify_screen(self)
        self.apps_and_games_assertions.start_netflix_and_verify_screen(self)

    @pytestrail.case("C11685187")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.search_ccu
    # @pytest.mark.test_stabilization
    @pytest.mark.notapplicable(Settings.is_fire_tv() or Settings.is_apple_tv() or Settings.is_ruby() or Settings.is_jade())
    def test_74221466_launch_app_from_app_screen(self):
        """
        T74221466
        Verify launching an app from the Apps screen is successful and pressing the Back button returns to the Apps screen.
        :return:
        """
        feed_name = self.wtw_page.get_feed_name(feedtype="On TV Today")[0]
        program = self.service_api.get_show_available_from_OTT(verbose=True, feedName=feed_name,
                                                               update_tivo_pt=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.home_page.back_to_home_short()
        if Settings.is_managed():
            self.home_assertions.verify_menu_item_available(self.home_labels.LBL_APPSANDGAME_SHORTCUT)
            self.home_page.select_menu_shortcut(self.home_labels.LBL_APPSANDGAME_SHORTCUT)
            self.apps_and_games_assertions.verify_screen_title(self)
            self.apps_and_games_assertions.start_netflix_and_verify_screen(self)
            self.apps_and_games_page.press_back_button()
            self.apps_and_games_assertions.verify_screen_title(self)
        self.text_search_page.go_to_search(self)
        self.text_search_assertions.verify_search_screen_title()
        self.text_search_page.search_and_select(f'{program[0][1]}', [program[0][0], f"{program[0][1]}"])
        self.program_options_assertions.verify_action_view_mode()
        self.program_options_assertions.verify_biaxial_screen()
        OTT = self.my_shows_page.OTT_from_ca_screen(self)
        self.my_shows_page.select_strip(OTT)
        self.home_page.verify_OTT_screen(Settings.app_package)
        self.apps_and_games_page.press_back_button()
        self.program_options_assertions.verify_action_view_mode()
        self.program_options_assertions.verify_biaxial_screen()

    @pytestrail.case("C11685210")
    @pytest.mark.home
    @pytest.mark.wtw_openAPI_impacted
    def test_74419161_show_removed_from_predictions_when_its_not_live(self, request):
        """
        TT74419161
        To Verify program is removed from predictions when its no more currently airing in Live TV.
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.home_page.back_to_home_short()
        show_name = self.service_api.get_shortest_show_from()[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        try:
            self.home_page.nav_to_show_on_prediction_strip(show_name)
        except Exception:
            pytest.skip("Show Not Found in Prediction Bar")
        self.watchvideo_assertions.is_watch_video_mode(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.guide_page.wait_for_current_show_to_finish()
        self.home_page.go_to_guide(self)
        self.home_page.pause(60)  # wait for show rotation
        request.getfixturevalue("setup_myshows_delete_recordings")
        self.home_page.pause(30)  # wait for show rotation
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        with pytest.raises(Exception):
            self.home_page.nav_to_show_on_prediction_strip(show_name)

    @pytestrail.case("C11685181")
    @pytest.mark.ndvr
    def test_74162446_watch_nDvr_entitled_show_from_olg(self):
        """
        T74162446
        Verify displaying One Line Guide, selecting an airing available and entitled nDVR show tunes to show,
        and watching the show until the end
        :return:
        """
        api = self.service_api
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(2.5 * 60)
        self.watchvideo_assertions.verify_playback_play()
        to_watch = self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=5)
        source = api.map_channel_number_to_currently_airing_offers(api.get_random_recordable_channel(channel_count=-1),
                                                                   api.get_grid_row_search(),
                                                                   transportType="stream")
        show = api.get_shortest_show_from(source=source)
        self.watchvideo_page.open_olg()
        self.watchvideo_page.enter_channel_number(show[0][1], confirm=True)
        self.watchvideo_page.press_playpause_button()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_assertions.verify_channel_number(show[0][1])
        self.watchvideo_assertions.verify_show_title(title=show[0][0])
        up_next = self.watchvideo_page.get_up_next_show()
        self.watchvideo_page.watch_video_for(to_watch * 60)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.watchvideo_assertions.verify_channel_number(show[0][1])
        if show[0][0] == up_next:
            self.watchvideo_assertions.verify_show_title(title=show[0][0])
        else:
            with pytest.raises(Exception):
                self.watchvideo_assertions.verify_show_title(title=show[0][0])

    @pytestrail.case("C11685179")
    @pytest.mark.ndvr
    def test_74155429_tune_to_nDvr(self):
        """
        T74155429
        Verify tuning to an airing available and entitled nDVR show in Guide and watching until the end.
        :return:
        """
        api = self.service_api
        channel = api.map_channel_number_to_currently_airing_offers(api.get_random_recordable_channel(channel_count=-1,
                                                                    filter_channel=True),
                                                                    api.get_grid_row_search(is_preview_offer_needed=True),
                                                                    genre='series', transportType="stream", count=1)
        self.home_page.goto_live_tv(channel[0][1])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(2.5 * 60)
        to_watch = self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=5)
        # Let's get cached get_grid_row_search() since it's already called above
        source = api.map_channel_number_to_currently_airing_offers(
            api.get_random_recordable_channel(channel_count=-1, filter_channel=True, use_cached_grid_row=True),
            api.channels_with_current_show_start_time(use_cached_grid_row=True), transportType="stream")
        show = api.get_shortest_show_from(source=source)
        self.home_page.goto_live_tv(show[0][1])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_view_mode()
        show_title = self.watchvideo_page.get_show_title()
        up_next = self.watchvideo_page.get_up_next_show()
        self.watchvideo_assertions.verify_channel_number(show[0][1])
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_page.watch_video_for((to_watch + 3) * 60)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.watchvideo_assertions.verify_channel_number(show[0][1])
        if show_title == up_next:
            self.watchvideo_assertions.verify_show_title(title=show_title)
        else:
            with pytest.raises(Exception):
                self.watchvideo_assertions.verify_show_title(title=show_title)

    @pytestrail.case("C11685195")
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74343754_record_future_show_from_guide(self):
        """
        T74343754
        Verify creating a recording from a future available show that is entitled for nDVR in the Guide
        displays the recording in the To Do List
        :return:
        """
        api = self.service_api
        channel = api.map_channel_number_to_currently_airing_offers(
            api.get_random_recordable_channel(channel_count=-1, is_preview_offer_needed=True),
            api.channels_with_current_show_start_time(duration=5400, use_cached_grid_row=True),
            future=1, genre='series', count=1)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][1])
        self.guide_page.press_right_button()
        self.guide_page.select_and_record_program(self)
        self.menu_page.go_to_to_do_list(self)
        with pytest.raises(Exception):
            self.menu_assertions.verify_toDo_list_empty(self)

    @pytestrail.case("C11685201")
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74348567_add_record_from_olg(self):
        """
        T74348567
        Verify displaying One Line Guide, selecting a future available and entitled nDVR show, and creating a recording
        displayed in the To Do List.
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, filter_channel=True, use_cached_grid_row=True),
            self.service_api.get_grid_row_search(use_cached_grid_row=True),
            genre='series', transportType="stream", count=1)
        self.watchvideo_page.open_olg()
        self.watchvideo_page.enter_channel_number(channel[0][1], olg=True)
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.schedule_upcoming_rec_from_olg()
        self.menu_page.go_to_to_do_list(self)
        with pytest.raises(Exception):
            self.menu_assertions.verify_toDo_list_empty(self)

    @pytestrail.case("C11685182")
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74164912_add_one_pass_from_olg(self):
        """
        T74164912
        Verify displaying One Line Guide, selecting a future available and entitled nDVR show, and creating a OnePass
        displays the OnePass in My Shows and OnePass Manager.
        :return:
        """
        api = self.service_api
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        icm_ch, ccm_ch = self.service_api.get_CCM_or_ICM_channel(channel_count=-1, is_preview_offer_needed=True)
        # Let's use cached get_grid_row_search() since it's already called above
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            [icm_ch], self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True), count=1)
        self.home_page.goto_live_tv(channel[0][1])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        channel = api.map_channel_number_to_currently_airing_offers(
            api.get_random_recordable_channel(channel_count=-1, use_cached_grid_row=True),
            api.get_grid_row_search(use_cached_response=True), genre="series", future=1, count=1, transportType="stream")
        self.watchvideo_page.open_olg()
        self.watchvideo_page.enter_channel_number(channel[0][1], confirm=True)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.schedule_upcoming_rec_from_olg(one_pass=True)
        self.menu_page.go_to_one_pass_manager(self)
        with pytest.raises(Exception):
            self.menu_assertions.verify_onepass_manager_empty_screen(self)

    @pytestrail.case("C11684201")
    @pytest.mark.livetv
    def test_74101856_check_full_info_banner_liveTV(self):
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_page.wait_for_infobanner(status='dismissed')
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        self.watchvideo_page.show_info_banner()
        more_info = self.menu_page.get_more_info_name(self, vod_labels=True)
        self.watchvideo_page.select_strip(more_info)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_ACTION_SCREEN_VIEWMODE)
        self.watchvideo_page.press_back_button()
        self.watchvideo_page.wait_for_infobanner(status='dismissed')
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        if not Settings.is_apple_tv():
            self.watchvideo_page.show_info_banner()
            self.watchvideo_assertions.verify_full_info_banner_is_shown()
            self.watchvideo_assertions.show_full_infobanner_and_verify_button_do_nothing('press up')
            self.watchvideo_page.close_info_banner()
            self.watchvideo_page.show_info_banner()
            self.watchvideo_assertions.verify_full_info_banner_is_shown()
            self.watchvideo_assertions.show_full_infobanner_and_verify_button_do_nothing('press down')
            self.watchvideo_page.close_info_banner()
            if Settings.is_managed():
                self.watchvideo_page.show_info_banner()
                self.watchvideo_assertions.verify_full_info_banner_is_shown()
                self.watchvideo_assertions.show_full_infobanner_and_verify_channel_change_button('channel up')
                self.watchvideo_page.close_info_banner()
                self.watchvideo_page.show_info_banner()
                self.watchvideo_assertions.verify_full_info_banner_is_shown()
                self.watchvideo_assertions.show_full_infobanner_and_verify_channel_change_button('channel down')
                self.watchvideo_page.close_info_banner()

    @pytestrail.case("C11685226")
    @pytest.mark.parental_control
    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74484727_validate_pc_osd_on_upcoming(self, request):
        """
        T74484727
        To Verify able to create parental control pin for rating validated programs
        :return:
        """
        to_wait = self.watchvideo_page.calc_end_time_for_30_m_show(self)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(
            grid_row=self.service_api.channels_with_current_show_start_time(duration=1800), filter_channel=True)
        request.getfixturevalue('setup_lock_parental_and_purchase_controls')
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_page.watch_video_for(to_wait * 60)
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_assertions.verify_osd()

    @pytestrail.case("C11685216")
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.parametrize('fixture', [None])
    def test_74447106_validate_unentitled_display_V56(self, fixture, request):
        """
        T74447106
         To verify that pressing Ok/clear/exit when tuned to a unentitled channel continues to display V56
         Channel requires subscription OSD irrespective with PC state(locked/unlocked)
        :return:
        """
        if fixture:
            request.getfixturevalue(fixture)
        status = self.api.get_show_entitled_channels_status(tsn=Settings.tsn)
        if status:
            pytest.skip("Device does not have unentitled channels")
        else:
            channel = self.service_api.get_unentitled_channels()
            if not channel:
                pytest.skip("Couldn't find any unentitled channel")
        ch = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(ch)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.enter_channel_number(channel[0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")

    @pytestrail.case("C11685238")
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74447106_validate_unentitled_display_V56_setup_lock_parental_and_purchase_controls(self, request):
        """
        T74447106
         To verify that pressing Ok/clear/exit when tuned to a unentitled channel continues to display V56
         Channel requires subscription OSD irrespective with PC state(locked/unlocked)
        :return:
        """
        status = self.api.get_show_entitled_channels_status(tsn=Settings.tsn)
        if status:
            pytest.skip("Device does not have unentitled channels")
        else:
            channel = self.service_api.get_unentitled_channels()
            if not channel:
                pytest.skip("Couldn't find any unentitled channel")
        ch = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(ch)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        request.getfixturevalue('setup_lock_parental_and_purchase_controls')
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.enter_channel_number(channel[0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")

    @pytestrail.case("C11684189")
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74065557_verify_adult_title_hidden(self, request):
        """
        T74065557
        Parental Controls - MY_SHOWS_TITLE- PC ON, and HAC ON
        :return:
        """
        channels = self.service_api.get_past_grid_row(delta=120)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1,
                                                                             encrypted=True, adult=True, bookmark=True,
                                                                             grid_row=channels, filter_channel=True)
        request.getfixturevalue('setup_lock_parental_and_purchase_controls')
        self.service_api.bookmark_show(*channel[0][2])
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        menu = list(map(lambda x: x.lower(), self.my_shows_page.extract_content_from_menu()))
        if self.my_shows_labels.LBL_TITLE_HIDDEN.lower() not in menu:
            try:
                folder = self.my_shows_labels.LBL_MY_SHOWS_STREAMING_MOVIES
                self.my_shows_assertions.verify_content_in_category(folder)
            except Exception:
                folder = self.my_shows_labels.LBL_MY_SHOWS_NOT_CURRENTLY_AVAILABLE_FOLDER
                self.my_shows_assertions.verify_content_in_category(folder)
            self.my_shows_page.select_show(folder)
            self.my_shows_page.verify_screen_title(folder.upper())
            self.my_shows_assertions.verify_content_in_category(self.my_shows_labels.LBL_TITLE_HIDDEN)

    @pytestrail.case("C11685191")
    @pytest.mark.home
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74332039_home_button_return_to_home(self):
        '''
        T74332039
        Verify launching an app from the Guide screen is successful and pressing the TiVo/Home button returns to Home.
        :return:
        '''
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.press_guide_button()
        self.guide_assertions.verify_guide_title()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.guide_page.press_home_button()
        self.home_assertions.verify_home_title()

    @pytestrail.case("C11684187")
    @pytest.mark.parental_control
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74060824_verify_pc_with_incorrect_pin(self):
        """
        T74060824
        Verifying Parental Control with incorrect PIN
        :return:
        """
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_assertions.verify_screen_title(parental_control.upper())
        self.menu_page.select_menu(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.menu_press_back()
        self.menu_assertions.verify_menu_screen_title()
        self.menu_page.select_menu_items(self.menu_labels.LBL_SETTINGS_SHORTCUT)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.enter_wrong_pc_password(self)
        self.menu_assertions.verify_wrong_PIN_overlay()

    @pytestrail.case("C11685189")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74228483_press_apps_button_from_live_tv(self):
        """
        T74228483
        Verify pressing the Apps button from live TV goes to the Apps & Games screen, and launching an app is successful.
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 3)
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_assertions.verify_currentPos_not_initial()
        self.home_page.press_apps_and_verify_screen(self)
        self.apps_and_games_assertions.start_netflix_and_verify_screen(self)

    @pytestrail.case("C11684204")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74118150_launch_ott_app_with_hotkey_and_exit_with_exit_button(self):
        '''
        :description:
            Verify launching an app when watching an airing and pressing the Exit button returns to Live TV
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/tests/view/74118150
        '''
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.home_assertions.press_home_and_verify_screen(self)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.watchvideo_assertions.press_exit_and_verify_screen(self)
        self.apps_and_games_assertions.press_youtube_and_verify_screen(self)
        self.watchvideo_assertions.press_exit_and_verify_screen(self)

    @pytestrail.case("C11684203")
    @pytest.mark.apps_and_games
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74115843_launch_ott_app_with_hotkey_and_exit_with_home_button(self):
        '''
        :description:
            Verify launching an app when watching an airing, available and pressing the TiVo/Home button returns to Home
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/tests/view/74115843
        '''
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.apps_and_games_assertions.press_home_and_verify_screen(self)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.press_netflix_and_verify_screen(self)
        self.apps_and_games_assertions.press_home_and_verify_screen(self)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.press_youtube_and_verify_screen(self)
        self.apps_and_games_assertions.press_home_and_verify_screen(self)

    @pytestrail.case("C11685208")
    @pytest.mark.guide
    def test_74409781_verify_able_to_plays_live_tv_when_exit_button_is_pressed(self):
        """
        74409781
        Verify able to plays Live TV when exit button is pressed.
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        channels = self.service_api.channels_with_current_show_start_time(duration=5400)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1, encrypted=True,
                                                                             grid_row=channels, transportType="stream",
                                                                             filter_channel=True)
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.menu_page.go_to_video_background_settings(self)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_VIDEO_WINDOW_and_BACKGROUND)
        self.menu_page.apply_option(self.menu_labels.LBL_DISPLAY_VIDEO, self.menu_labels.LBL_NO)
        self.menu_assertions.verify_option(self.menu_labels.LBL_DISPLAY_VIDEO, self.menu_labels.LBL_NO)
        if not Settings.is_apple_tv():
            self.watchvideo_assertions.press_exit_and_verify_streaming(self)
            self.home_page.back_to_home_short()
            self.watchvideo_assertions.press_exit_and_verify_streaming(self)

    @pytestrail.case("C11685193")
    @pytest.mark.guide
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74336725_back_return_to_guide(self):
        '''
        T74336725
        Verify launching an app from the Guide screen is successful and pressing the Back button returns to Guide.
        :return:
        '''
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.press_guide_button()
        self.guide_assertions.verify_guide_title()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.guide_page.press_back_button()
        self.guide_assertions.verify_guide_title()

    @pytestrail.case("C11684190")
    @pytest.mark.guide
    @pytest.mark.socu
    def test_74067860_check_source_icons_for_socu_and_socu_non_OTT_part1(self):
        """
        T74067860
        To check source icons displayed in Past Grid Guide header for assets available from Catchup feature.
        OTT_count= 1 means socu+any OTT
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        channels = self.service_api.get_past_grid_row(align=True, delta=30)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1, socu=True, duration=1800,
                                                                             grid_row=channels, encrypted=True,
                                                                             OTT_count=1)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_assertions.verify_socu_icon_in_guide_header(self, channel[0][1])

    @pytestrail.case("C11685235")
    @pytest.mark.guide
    @pytest.mark.socu
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74067860_check_source_icons_for_socu_and_socu_non_OTT_part2(self):
        """
        T74067860
        To check source icons displayed in Past Grid Guide header for assets available from Catchup feature.
        OTT_count= 2 means OTT only.
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        channels = self.service_api.get_past_grid_row(align=True, delta=30)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1, socu=True, duration=1800,
                                                                             grid_row=channels, encrypted=True,
                                                                             OTT_count=2)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_assertions.verify_socu_icon_in_guide_header(self, channel[0][1])

    @pytestrail.case("C11685205")
    @pytest.mark.iplinear
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74381641_add_partial_record_from_olg(self):
        """
        T74381641
        Verify watching an airing live show, going to One Line Guide, creating a partial nDVR recording, and playing the
        partial recording from My Shows
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=10)
        icm_ch, ccm_ch = self.service_api.get_CCM_or_ICM_channel(channel_count=-1)
        # Let's get cached get_grid_row_search() since it's already called above
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            [icm_ch], self.service_api.channels_with_current_show_start_time(multiple_by=1, use_cached_grid_row=True), count=1,
            error_msg="Stating No ICM channels are available and test requires ICM channel to create partial recording")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.enter_channel_number(channel[0][1])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.schedule_upcoming_rec_from_olg(current=True)
        self.watchvideo_page.pause(50)  # hang in livetv cuz recording don't start immediately
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(channel[0][0])
        self.screen.refresh()
        if self.screen.get_screen_dump_item('viewMode') == self.my_shows_labels.LBL_SERIES_SCREEN_VIEW:
            self.my_shows_assertions.verify_view_mode(self.my_shows_labels.LBL_SERIES_SCREEN_VIEW)
        else:
            self.vod_assertions.verify_view_mode(self.my_shows_labels.LBL_ACTION_SCREEN_VIEW)
        self.my_shows_page.go_to_cached_action_screen(self)
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.select_play_option()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11685204")
    @pytest.mark.iplinear
    @pytest.mark.ndvr
    @pytest.mark.e2e
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74372261_create_partial_rec_from_guide(self):
        """
        T74372261
        Verify watching live TV, going to Guide, creating a partial nDVR recording, and playing the partial recording
        from My Shows
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=10)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        icm_ch, ccm_ch = self.service_api.get_CCM_or_ICM_channel(channel_count=-1)
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            [icm_ch], self.service_api.channels_with_current_show_start_time(multiple_by=1, use_cached_grid_row=True), count=1,
            error_msg="Stating No ICM channels are available and test requires ICM channel to create partial recording",
            transport_type="stream")
        self.guide_page.enter_channel_number(channel[0][1])
        self.guide_page.choose_show_by_name(channel[0][0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.pause(90)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.pause(20)  # timeout trickplay
        self.guide_page.press_back_button(refresh=True)
        self.guide_assertions.verify_guide_title()
        self.guide_page.select_and_record_program(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(channel[0][0])
        self.screen.refresh()
        if self.screen.get_screen_dump_item('viewMode') == self.my_shows_labels.LBL_SERIES_SCREEN_VIEW:
            self.my_shows_assertions.verify_view_mode(self.my_shows_labels.LBL_SERIES_SCREEN_VIEW)
        else:
            self.vod_assertions.verify_view_mode(self.my_shows_labels.LBL_ACTION_SCREEN_VIEW)
        self.my_shows_page.go_to_cached_action_screen(self)
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.select_play_option()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11684197")
    @pytest.mark.socu
    @pytest.mark.iplinear
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74086544_to_be_able_play_same_show_multiple_sources(self):
        """
        T74086544
        To be able to playback same show from multiple sources.
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=12)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        api = self.service_api
        channel = api.map_channel_number_to_currently_airing_offers(
            api.get_random_recordable_channel(channel_count=-1, is_preview_offer_needed=True),
            api.channels_with_current_show_start_time(use_cached_grid_row=True),
            genre="series", count=1, socu=True)
        self.guide_page.enter_channel_number(channel[0][1])
        self.guide_page.select_and_record_program(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.validate_channel_number(channel[0][1])
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(90)
        self.watchvideo_assertions.verify_playback_play()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(channel[0][0])
        self.my_shows_page.select_show(channel[0][0])
        self.guide_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_assertions.verify_view_mode(self.my_shows_labels.LBL_SERIES_SCREEN_VIEW)
        self.my_shows_page.go_to_cached_action_screen(self)
        self.guide_page.wait_for_screen_ready()
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.select_play_option()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_back_to_navigate_to_action_screen()
        self.guide_page.wait_for_screen_ready()
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.my_shows_page.go_to_cached_action_screen(self)
            self.guide_page.wait_for_screen_ready()
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.select_play_from_socu(socu=self.home_labels.LBL_WTW_SOCU_ICON)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60)
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11684191")
    @pytest.mark.guide
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74070163_check_record_overlay_for_socu_and_OTT_offer(self):
        """
        T74070163
        Verify "Watch" actions in Record overlay for a show that is available
        from OTT and SOCU catalog and is in progress now on LiveTV
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        channels = self.service_api.channels_with_current_show_start_time()
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1,
                                                                             socu=True, grid_row=channels,
                                                                             encrypted=True, OTT_count=2)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.open_record_overlay()
        catchup_name = self.guide_page.get_watch_now_catchup_name(self)
        self.guide_assertions.verify_text_image_from_screen(catchup_name,
                                                            self.guide_labels.LBL_RECORD_OVERLAY_CATCHUP_ICON)
        self.guide_assertions.verify_watch_now_option_on_record_overlay()
        self.guide_assertions.verify_more_info_option_on_record_overlay(self)

    @pytestrail.case("C11685223")
    @pytest.mark.guide
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74477692_verify_creating_one_pass_from_currently_airing(self):
        """
        74477692
         Verify creating a OnePass from a currently airing,
         available and entitled nDVR show in Guide displays the OnePass in My Shows and OnePass Manager.
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=10)
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(
                channel_count=-1, filter_channel=True, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True),
            transportType="stream", genre="series", count=1, OTT_count=-1)
        if not channel:
            pytest.skip("No recordable airing show found for the test")
        program = channel[0][0]
        self.home_page.goto_live_tv(channel[0][1])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(150)
        self.home_page.press_guide_button()
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_default_channel_is_highlighted(self, channel[0][1])
        self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.menu_page.menu_navigate_left_right(0, 1)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_recording_now_icon()
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_assertions.verify_one_pass_exists(program)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)

    @pytestrail.case("C11685209")
    @pytest.mark.myshows
    @pytest.mark.ndvr
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures('setup_myshows_delete_recordings')
    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74412126_user_able_playback_and_delete_bookmark(self):
        """
        T74412126
        To verify user is able to playback and delete onepass/bookmarks from my shows.
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)  # Tune to playable live channel
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=4)
        channels = self.service_api.get_live_channels_with_OTT_available(verbose=True, count=3, collectionType="series")
        if not channels:
            pytest.skip("Test requires OTT program.")
        self.watchvideo_page.tune_to_channel(channels[0][0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.open_olg()
        program = self.guide_page.create_one_pass_on_record_overlay(self, new_only=True)
        if len(channels) > 1:
            self.watchvideo_page.tune_to_channel(channels[1][0])
            self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
            self.watchvideo_assertions.verify_playback_play()
            self.watchvideo_page.open_olg()
            program1 = self.guide_page.create_one_pass_on_record_overlay(self, new_only=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.go_to_cached_action_screen(self)
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        OTT = self.my_shows_page.OTT_from_ca_screen(self)
        self.my_shows_page.select_strip(OTT, refresh=False)
        self.home_page.verify_OTT_screen(Settings.app_package)
        self.home_page.launch_hydra_when_script_is_on_ott()
        if len(channels) > 1:
            self.home_page.go_to_my_shows(self)
            self.my_shows_assertions.verify_my_shows_title()
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
            self.my_shows_page.select_show(program1, matcher_type="partial_match")
            self.my_shows_page.go_to_cached_action_screen(self)
            self.program_options_assertions.verify_action_view_mode(self)
            self.program_options_assertions.verify_biaxial_screen()
            OTT = self.my_shows_page.OTT_from_ca_screen(self)
            self.my_shows_page.select_strip(OTT, refresh=False)
            self.home_page.verify_OTT_screen(Settings.app_package)
            self.home_page.launch_hydra_when_script_is_on_ott()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_assertions.verify_view_mode(self.my_shows_labels.LBL_SERIES_SCREEN_VIEW)
        self.screen.base.press_left(time=5000)
        self.my_shows_page.cancel_one_pass(self)
        self.program_options_page.press_back_button()
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_assertions.verify_content_not_in_category(self, program)

    @pytestrail.case("C11685202")
    @pytest.mark.guide
    def test_74350910_verify_creating_one_pass_from_past_available_and_entitled_ndvr_show_in_one_line_guide(self):
        """
        74350910
         Verify creating a OnePass from a past available and entitled nDVR show in Guide displays
         the OnePass in My Shows and OnePass Manager
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=5)
        channels = self.service_api.get_past_grid_row(align=True, delta=30, is_preview_offer_needed=True)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1,
                                                                             grid_row=channels, transportType="stream",
                                                                             encrypted=True,
                                                                             genre="series", socu=True, filter_channel=True)
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_page.open_olg()
        self.menu_page.menu_navigate_left_right(2, 0)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.menu_page.go_to_one_pass_manager(self)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        # verify_content_in_category fails because of bugs BZDM-11029 BZDM-11030
        self.my_shows_assertions.verify_content_in_category(program)

    @pytestrail.case("C11685194")
    @pytest.mark.textsearch
    @pytest.mark.not_devhost
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.search_ccu
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74341411_verify_searching_episode_OTT(self):
        """
        74341411
        Verify searching for an episode available from an app and playing that episode.
        :return:
        """
        feed_name = self.wtw_page.get_feed_name(feedtype="On TV Today")[0]
        program = self.service_api.get_show_available_from_OTT(verbose=True, feedName=feed_name,
                                                               update_tivo_pt=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_assertions.verify_search_screen_title()
        self.text_search_page.search_and_select(f'{program[0][1]}', [program[0][0], f"{program[0][1]}"])
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        OTT = self.my_shows_page.OTT_from_ca_screen(self)
        self.my_shows_page.select_strip(OTT, refresh=False)
        self.home_page.verify_OTT_screen(Settings.app_package)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685215")
    @pytest.mark.livetv
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.search_ccu
    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_74440071_verify_live_tv_with_sequence_keypress(self):
        """
        https://testrail.tivo.com//index.php?/cases/view/8880414
        74440071
        To Verify Live TV playback is successful, when a sequence of keypress is repeated multiple times.
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")[0][0]
        # Tune to playable live channel
        self.home_page.goto_live_tv(channel)
        self.menu_page.go_to_video_providers(self)
        self.menu_page.checked_option(self.menu_labels.LBL_NETFLIX)
        for _ in range(4):
            self.home_page.screen.base.press_youtube()
            self.home_page.press_home_button()
            self.screen.wait_for_screen_ready("HomeMainScreen", timeout=200000)
            self.home_page.goto_livetv_short(self)
            self.watchvideo_assertions.verify_playback_play()
        self.home_page.relaunch_hydra_app(reboot=True)
        for _ in range(4):
            self.home_page.screen.base.press_netflix(keycode=True)
            self.home_page.screen.base.press_youtube()
            self.home_page.press_home_button()
            self.screen.wait_for_screen_ready("HomeMainScreen", timeout=200000)
            self.home_page.goto_livetv_short(self)
            self.watchvideo_assertions.verify_playback_play()
        self.home_page.relaunch_hydra_app(reboot=True)
        try:
            program = self.service_api.get_assets_titles_from_wtw_strip("Netflix Exclusives", asset_index=1)
        except ValueError:
            return
        self.text_search_page.go_to_search(self)
        self.text_search_assertions.verify_search_screen_title()
        self.text_search_page.search_and_select(program, program)
        self.text_search_page.watch_on_netflix()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "netflix")
        self.home_page.press_exit_button()
        for _ in range(4):
            self.home_page.screen.base.press_netflix(keycode=True)
            self.home_page.screen.base.press_youtube()
            self.home_page.press_home_button()
            self.screen.wait_for_screen_ready("HomeMainScreen", timeout=200000)
            self.home_page.goto_livetv_short(self)
            self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11685207")
    @pytest.mark.wtw
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_8880250_search_OTT_and_linear_from_WTW(self):
        """
        Search for shows from OTT apps, Linear content from WTW

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/8880250
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=6)
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        for feed in feed_list:
            self.log.info("feed : {}".format(feed))
            if feed is not None:
                program = self.service_api.get_show_available_from_OTT(feedName=feed, count=-1,
                                                                       raw=True, update_tivo_pt=False)
                if len(program) > 0:
                    break
        if not program:
            pytest.skip("Test requires OTT program.")
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY)
        try:
            if not self.wtw_page.check_carousel_focused(self.wtw_labels.LBL_ON_NOW_TV_SHOWS):
                self.wtw_page.quick_update_wtw()
            show = self.wtw_page.nav_to_show_on_strip(program)
        except Exception:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode():
            self.my_shows_page.select_first_item_in_live_and_upcoming()
        self.program_options_assertions.verify_action_view_mode()
        self.program_options_assertions.verify_biaxial_screen()
        OTT = self.my_shows_page.OTT_from_ca_screen(self)
        self.my_shows_page.select_strip(OTT)
        self.home_page.verify_OTT_screen(Settings.app_package)
        self.menu_page.go_to_video_providers(self)
        self.menu_page.check_or_uncheck_all_menu_items(uncheck=True)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY)
        if not self.wtw_page.check_carousel_focused(self.wtw_labels.LBL_ON_NOW_TV_SHOWS):
            self.wtw_page.quick_update_wtw()
        self.wtw_page.nav_to_show_on_strip(show)
        if self.my_shows_page.is_series_screen_view_mode():
            self.my_shows_page.select_first_item_in_live_and_upcoming()
        self.program_options_assertions.verify_action_view_mode()
        self.program_options_assertions.verify_biaxial_screen()
        with pytest.raises(Exception):
            self.my_shows_page.select_strip(OTT)

    @pytestrail.case("C11684196")
    @pytest.mark.favorite_channels
    @pytest.mark.livetv
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.usefixtures("switch_off_show_only_favorite_channels_in_guide")
    def test_74084161_change_channels_with_empty_favorite_channels_list(self):
        """
        Description: https://testrail.corporate.local/index.php?/tests/view/74084161
        To be able to change the channel in Live TV when the favorite channel list is empty in guide
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        # Precondition steps to avoid jump channels during test execution, could be moved to fixtures
        channels = self.service_api.get_random_encrypted_unencrypted_channels(
            filter_channel=True, encrypted=True, transportType="stream")
        if not channels:
            pytest.skip("There are no applicable channels for this test were found.")
        channel = channels[0][0]
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.enter_channel_number(channel)
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_playback_play()
        # End of precondition steps
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_assertions.verify_empty_favorite_channels_list_in_guide()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        if Settings.is_managed():
            self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel up')
            self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel down')
            # One more time to verify Channel Down tunes to different channel with a lower channel number
            self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel down')

    @pytestrail.case("C11685178")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74143527_verify_launching_an_app_from_the_apps_screen(self):
        '''
        :description:
            Verify launching an app from the Apps screen is successful and pressing the Exit button returns to Home
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/tests/view/74143527
        '''
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.home_page.press_apps_and_verify_screen(self)
        self.apps_and_games_assertions.start_netflix_and_verify_screen(self)
        self.apps_and_games_page.press_exit_button()
        self.apps_and_games_assertions.verify_screen_title(self)

    @pytestrail.case("C11685224")
    @pytest.mark.livetv
    def test_74480037_to_verify_able_to_navigate_first_to_last_channels(self):
        """
        To Verify able to navigate first to last channels

        Testrail:
            https://testrail.corporate.local/index.php?/tests/view/74480037
        """
        if Settings.mso.lower() == "bluestream":
            channel_list = self.api.get_channel_search(omit=False, isHidden=True, entitled=True,
                                                       includeUnavailableChannels=True, includeAdultChannels=True)
        elif Settings.mso.lower() == "cableco11":
            channel_list = self.api.get_channel_search(is_received=None, omit=False, isHidden=True,
                                                       includeUnavailableChannels=True, includeAdultChannels=True)
        else:
            channel_list = self.api.get_channel_search(omit=False, isHidden=True, entitled=True,
                                                       includeUnavailableChannels=True, includeAdultChannels=True)
        first_channel = channel_list[0].channel_number
        last_channel = channel_list[-1].channel_number
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")[0][0]
        # Tune to playable live channel
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.open_olg()
        self.watchvideo_page.enter_channel_number(channel=first_channel, confirm=False, olg=True, dump=False)
        self.guide_assertions.verify_highligted_and_next_highlighted_channel_in_one_line_guide(first_channel,
                                                                                               last_channel, False)

    @pytestrail.case("C11684186")
    @pytest.mark.menu
    @pytest.mark.parental_control
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74058521_parental_controls_in_settings_submenus(self):
        """
        Description:
        https://testrail.corporate.local/index.php?/tests/view/74058521
        To Verify User should be able to setup parental controls from the Settings submenus
        """
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_page.select_menu(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.turn_parental_control(self, turn='On - Locked')
        self.menu_page.go_to_settings(self)
        self.menu_assertions.verify_PIN_overlay_in_settings_submenus(parental='On - Locked')
        self.menu_page.select_menu(self.menu_labels.LBL_ACCESSIBILITY)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)  # switches parental to 'On - Unlocked'
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_ACCESSIBILITY.upper())
        self.menu_page.menu_press_back()
        self.menu_assertions.verify_PIN_overlay_in_settings_submenus(parental='On - Unlocked')

    @pytestrail.case("C11685211")
    @pytest.mark.menu
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74421506_verify_pin_challenge_in_settings_submenus(self):
        """
        Description:
        https://testrail.corporate.local/index.php?/tests/view/74421506
        To verify PIN challenge on all menu items in Settings
        """
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_page.select_menu(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.turn_parental_control(self, turn='On - Locked')
        self.menu_page.go_to_settings(self)
        self.menu_assertions.verify_PIN_overlay_in_settings_submenus(parental='On - Locked')

    @pytestrail.case("C11684206")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.usefixtures("enable_netflix")
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74125071_verify_ability_launch_netflix_with_the_NETFLIX_button_before_and_after_unchecking(self):
        """
        :description:
            Verify ability o launch Netflix with the NETFLIX button before and after unchecking it
            from the Video Provider List (VPL)
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/tests/view/74125071
        """

        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.apps_and_games_assertions.press_youtube_and_verify_screen(self)
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.home_page.back_to_home_short()
        self.menu_page.go_to_video_providers(self)
        self.menu_page.unchecked_option(self.menu_labels.LBL_NETFLIX)
        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.apps_and_games_assertions.press_youtube_and_verify_screen(self)
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.home_page.back_to_home_short()

    @pytestrail.case("C11685185")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    @pytest.mark.usefixtures("setup_parental_control")
    @pytest.mark.usefixtures("setup_adhoc_OTT_provider_and_functionality")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74216788_Verify_launching_an_App_from_Home(self):
        '''
        :description:
            Verify launching an App from Home is successful and pressing the TiVo/Home button returns to Home
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/tests/view/74216788
        '''
        if Settings.is_managed():
            self.home_page.back_to_home_short()
            self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
            self.apps_and_games_assertions.press_home_and_verify_screen(self)
        else:
            self.home_page.back_to_home_short()
            self.home_page.go_to_search(self)
            program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies", update_tivo_pt=True)
            if not program:
                pytest.skip("Test requires OTT program.")
            OTT = self.my_shows_page.OTT_from_ca_screen(self)
            self.my_shows_page.select_strip(OTT, refresh=False)
            self.my_shows_page.pause(20)
            fg_pkg = self.screen.base.get_foreground_package()
            self.home_page.log.info(f"current app package: {fg_pkg}")
            if fg_pkg == Settings.app_package:
                pytest.fail("OTT App did not launch.")

    @pytestrail.case("C11685186")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74219127_verify_launching_an_app_from_home_and_pressing_the_exit(self):
        '''
        :description:
            Verify launching an App from Home is successful and pressing the Exit button
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/tests/view/74219127
        '''

        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.press_youtube_and_verify_screen(self)
        self.home_page.press_exit_button()
        self.home_assertions.verify_home_title()

    @pytestrail.case("C11684198")
    @pytest.mark.livetv
    @pytest.mark.vod
    @pytest.mark.usefixtures("disable_video_window")
    def test_74092628_verify_video_reverts_to_livetv_after_vod_playback_complete(self):
        """
        Description: https://testrail.corporate.local/index.php?/tests/view/74092628
        To Verify that full screen video reverts to Live TV once VOD playback completes
        when the video window is turned off
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")[0][0]
        # Tune to playable live channel
        self.home_page.goto_live_tv(channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        status, result = self.vod_api.getOffer_playable_rating_movie()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete(self)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, 200000)
        self.home_assertions.verify_home_title()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.watchvideo_assertions.verify_livetv_mode()

    @pytestrail.case("C11685175")
    @pytest.mark.vod
    def test_74129685_play_next_episode_from_playnext_overlay(self):
        """
        Description: https://testrail.corporate.local/index.php?/tests/view/74129685
        Able to play next episode from View next overlay
        """
        status, result = self.vod_api.getOffer_svod_entitledSubscribed_series(1500, 10800, count=1000)
        ep = self.vod_page.extract_entryPoint(result)
        mixID = self.vod_page.extract_mixID(result)
        contentID = self.vod_page.extract_contentId(result)
        collectionID = self.vod_page.extract_collectionId(result)
        title = self.vod_page.extract_title(result)
        self.vod_page.go_to_vod(self)
        self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        episode_list = self.vod_page.get_episode_list_from_screen()
        if len(episode_list) < 2:
            self.home_page.log.warning(f"Two or more episodes needed, but have '{len(episode_list)}' - '{episode_list}'")
            return
        first_episode_title = episode_list[0][0]
        first_episode = episode_list[0][1]
        next_episode = episode_list[1][1]
        self.vod_page.check_next_episode_available(next_episode)
        self.vod_page.play_free_vod_content(subtitle=first_episode_title)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_assertions.verify_currently_playing_episode(first_episode)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.vod_page.press_right_button()
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.vod_page.press_ok()
        self.vod_page.pause(20)
        value0 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value, value0, 3)
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.guide_assertions.verify_play_normal()
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.vod_page.pause(3)
        value11 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value1, value11, 3)
        self.vod_page.press_right_button()
        self.vod_page.press_ok()
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete(False)
        self.watchvideo_page.select_option_in_playnext_banner(self.liveTv_labels.LBL_ON_DEMAND)
        self.watchvideo_assertions.verify_currently_playing_episode(next_episode)
        value2 = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.vod_page.press_right_button()
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.vod_page.press_ok()
        self.vod_page.pause(20)
        value22 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value2, value22, 3)
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.guide_assertions.verify_play_normal()
        value3 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.vod_page.pause(3)
        value33 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value3, value33, 3)
        self.vod_page.press_right_button()
        self.vod_page.press_ok()

    @pytestrail.case("C11685177")
    @pytest.mark.textsearch
    @pytest.mark.not_devhost
    @pytest.mark.search_ccu
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74138913_verify_onepass_modify_on_various_screens(self):
        """
          74138913
          To verify after OnePass created, modify onepass options displayed on various screens
          :return:
        """
        # Tune to playable live channel
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.text_search_page.go_to_search(self)
        self.text_search_assertions.verify_search_screen_title()
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=10)
        # Let's get cached get_grid_row_search() since it's already called above
        program = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, use_cached_grid_row=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True),
            subtitle=True, genre="series", socu=True, count=1)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(program[0][1])
        show_name = self.guide_page.get_live_program_name(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(show_name, show_name)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.my_shows_page.go_to_cached_action_screen(self)
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.create_one_pass(self)
        self.program_options_assertions.verify_one_pass_created()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.enter_channel_number(program[0][1])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_info_banner()
        more_info = self.menu_page.get_more_info_name(self, vod_labels=True)
        self.watchvideo_page.select_strip(more_info)
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_assertions.verify_one_pass_created()

    @pytestrail.case("C11685233")
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.vod
    @pytest.mark.search_ccu
    # @pytest.mark.test_stabilization
    def test_74571840_verify_live_tv_after_launching_OTT_VOD(self):
        """
        74571840
        https://testrail.tivo.com//index.php?/cases/view/8880470
        To verify Live TV playback after launching OTT+VOD and exiting immediately by pressing exit button
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.screen.base.press_youtube()
        self.screen.base.press_vod_button()
        self.watchvideo_assertions.press_exit_and_verify_streaming(self)
        channel = self.service_api.get_random_recordable_channel(channel_count=2, filter_channel=True)
        self.watchvideo_page.enter_channel_number(channel[0][0], confirm=True)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.text_search_page.go_to_search(self)
        self.text_search_assertions.verify_search_screen_title()
        self.home_page.goto_livetv_short(self)
        self.screen.base.press_netflix(keycode=True)
        self.watchvideo_assertions.press_exit_and_verify_streaming(self)
        self.watchvideo_page.enter_channel_number(channel[1][0], confirm=True)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.screen.base.press_google_voice()
        self.screen.base.press_vod_button()
        self.watchvideo_assertions.press_exit_and_verify_streaming(self)

    @pytestrail.case("C11685228")
    @pytest.mark.guide
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74489417_verify_live_tv_is_played_after_deleting_the_onepass(self):
        """
        74489417
            To verify Live TV is played after deleting the OnePass recorded program.
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=5)
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, filter_channel=True,
                                                           is_preview_offer_needed=True),
            self.service_api.get_grid_row_search(use_cached_grid_row=True), genre="series")
        if not channel:
            pytest.skip("No recordable channel with series found")
        self.home_page.goto_live_tv(channel[0][1])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.open_olg()
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.vod_assertions.verify_video_streaming()
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_page.cancel_one_pass(program)
        self.menu_assertions.verify_onepass_manager_empty_screen()
        if not Settings.is_apple_tv():
            self.watchvideo_assertions.press_exit_and_verify_streaming(self)

    @pytestrail.case("C11685229")
    @pytest.mark.guide
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74491762_verify_live_tv_is_played_after_deleting_from_to_do_list(self):
        """
        74491762
            To verify Live TV is played after deleting the OnePass recorded program.
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=5)
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, filter_channel=True,
                                                           is_preview_offer_needed=True),
            self.service_api.get_grid_row_search(use_cached_grid_row=True), genre="series")
        if not channel:
            pytest.skip("No recordable channel with series found")
        self.home_page.goto_live_tv(channel[0][1])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.open_olg()
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.log.debug("create_one_pass_on_record_overlay_program: {}".format(program))
        self.watchvideo_page.watch_video_for(180)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.menu_page.go_to_to_do_list(self)
        self.my_shows_page.select_show(program)
        self.my_shows_page.cancel_one_pass(self)
        self.menu_page.go_to_to_do_list(self)
        self.menu_assertions.verify_toDo_list_empty(self)
        self.watchvideo_assertions.press_exit_and_verify_streaming(self)

    @pytestrail.case("C11684200")
    @pytest.mark.guide
    @pytest.mark.ndvr
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_delete_book_marks")
    def test_74099549_verify_all_one_pass_bookmarks_created_are_placed_under_my_shows1(self):
        """
        74099549
        verify all onepass bookmarks created are placed under My shows.
        Part1
        :return:
        """
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_screen_title(self.my_shows_labels.LBL_MY_SHOWS)
        self.my_shows_assertions.verify_body_text_in_category(self, self.my_shows_labels.LBL_TV_SERIES,
                                                              self.my_shows_labels.LBL_EMPTY_TEXT_TV_SERIES)
        self.my_shows_assertions.verify_body_text_in_category(self, self.my_shows_labels.LBL_MOVIES,
                                                              self.my_shows_labels.LBL_EMPTY_TEXT_MOVIES)
        self.my_shows_assertions.verify_body_text_in_category(self, self.my_shows_labels.LBL_KIDS,
                                                              self.my_shows_labels.LBL_EMPTY_TEXT_KIDS)
        self.my_shows_assertions.verify_body_text_in_category(self, self.my_shows_labels.LBL_SPORTS,
                                                              self.my_shows_labels.LBL_EMPTY_TEXT_SPORTS)
        self.watchvideo_page.calc_end_time_for_30_m_show(self)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True),
            genre="series", socu=True, count=1, OTT_count=1)
        self.guide_page.enter_channel_number(channel[0][1])
        program = self.guide_page.create_one_pass_on_record_overlay(self, streaming_only=True)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_TV_SERIES)
        self.my_shows_page.select_show(program)
        self.my_shows_page.go_to_cached_action_screen(self)
        self.program_options_page.select_play_from_socu(socu=self.home_labels.LBL_WTW_SOCU_ICON)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11685237")
    @pytest.mark.guide
    @pytest.mark.ndvr
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74099549_verify_all_one_pass_bookmarks_created_are_placed_under_my_shows2(self):
        """
        74099549
        verify all onepass bookmarks created are placed under My shows.
        Part2
        :return:
        """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies", update_tivo_pt=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.create_bookmark_from_movie_screen(self)
        try:
            self.text_search_page.select_folder_from_myshows(self, self.my_shows_labels.LBL_MY_SHOWS_STREAMING_MOVIES)
            self.text_search_assertions.verify_program_availablity_under_myshows_folder(self, program,
                                                                                        self.my_shows_labels.
                                                                                        LBL_MY_SHOWS_STREAMING_MOVIES)
        except Exception:
            self.text_search_page.select_folder_from_myshows(self, self.my_shows_labels.
                                                             LBL_MY_SHOWS_NOT_CURRENTLY_AVAILABLE_FOLDER)
            folder_values = self.my_shows_labels.LBL_MY_SHOWS_NOT_CURRENTLY_AVAILABLE_FOLDER
            self.text_search_assertions.verify_program_availablity_under_myshows_folder(self, program, folder_values)

    @pytestrail.case("C11685242")
    @pytest.mark.guide
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_delete_book_marks")
    def test_74099549_verify_all_one_pass_bookmarks_created_are_placed_under_my_shows3(self):
        """
        74099549
        verify all onepass bookmarks created are placed under My shows.
        This script is enhanced to delete the bookmarked show and verify show is not present catogory
        Part3
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self)
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            [[channel] for channel in self.service_api.get_current_guide_line_up()],
            self.service_api.channels_with_current_show_start_time(is_preview_offer_needed=True),
            genre="special", transportType="stream", linear_only=True, count=1)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][1])
        program = self.guide_page.select_and_bookmark(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(self.my_shows_labels.LBL_MY_SHOWS_NOT_CURRENTLY_AVAILABLE_FOLDER)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.delete_content_bookmark(self, program)
        self.my_shows_assertions.verify_content_not_in_category(self, program)

    @pytestrail.case("C11685188")
    @pytest.mark.apps_and_games
    @pytest.mark.not_devhost
    @pytest.mark.notapplicable(Settings.is_apple_tv() or Settings.is_fire_tv())
    def test_74223805_launch_youtube_from_home_and_pressing_back_returns_to_home(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74223805
         Verify launching YouTube from Home is successful and pressing the Back button returns to Home
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.open_youtube()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.exit_ott_app_with_back_button()
        self.home_assertions.verify_home_title()

    @pytestrail.case("C11685222")
    @pytest.mark.vod
    @pytest.mark.timeout(TIMEOUT_MID)
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74461176_verify_tv_ma_rated_vod_asset_is_playing(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74461176
         To verify that Parental Controls does not block a TV-MA rated VOD offer when set to Allow all ratings.
        :return:
        """
        status, result = self.vod_api.get_asset_with_tv_rating_ma()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.menu_page.go_to_settings(self)
        self.menu_page.select_menu_items(self.menu_page.get_parental_controls_menu_item_label())
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.enter_default_parental_control_password(self)  # to confirm
        self.menu_page.toggle_hide_adult_content(ON=False)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SET_RATING_LIMITS)
        self.menu_page.set_rating_limits(
            rated_movie=self.menu_page.get_movie_rating(),
            rated_tv_show=self.menu_page.get_tv_rating(),
            unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
            unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)
        self.menu_page.press_back_button(refresh=True)
        self.menu_page.turn_parental_control(self, turn='On - Locked')
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)

    @pytestrail.case("C11685213")
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74426196_verify_options_under_preview_area_on_highlight_modify_onepass(self):
        """
          74426196
          To verify the options displayed under preview area on highlighting Modify/Cancel One Pass
          under One Pass Options from series/episode screen.
          :return:
          """
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True), genre="series", count=1)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][1])
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ONEPASS_OPTIONS)
        self.my_shows_page.nav_to_menu(self.my_shows_labels.LBL_MODIFY_ONEPASS)
        self.my_shows_assertions.verify_modify_onepass_preview_area()

    @pytestrail.case("C11685220")
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_74456486_cancel_onepass_for_in_progress_recording(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74456486
        To verify that cancelling a One Pass is successful for an in-progress recording.
        """
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True), genre="series", count=1)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][1])
        self.guide_page.get_live_program_name(self)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ONEPASS_OPTIONS)
        self.my_shows_page.select_menu(self.my_shows_labels.LBL_CANCEL_ONEPASS)
        self.my_shows_page.select_menu(self.my_shows_labels.LBL_CONFIRM_CANCEL_ONEPASS)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.delete_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_not_in_category(self, program)

    @pytestrail.case("C11685212")
    @pytest.mark.ndvr
    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74423851_socu_and_ndvr_both_work(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74423851
        To Verify SOCU and nDVR playback both work as expected for a program available through both options.
        """
        channels = self.service_api.get_available_channels_with_socu_offer()
        program = self.service_api.schedule_single_recording(channels=channels)
        show = program[0][0]
        channel = program[0][1]
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.wait_for_header_rendering()
        self.guide_assertions.verify_show_title(show, "guide_cell")
        self.guide_page.watch_now_from(self, self.guide_labels.LBL_MY_SHOWS)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_back_button(refresh=True)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.wait_for_header_rendering()
        self.guide_assertions.verify_show_title(show, "guide_cell")
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        self.guide_assertions.press_select_verify_watch_screen(self, show)

    @pytestrail.case("C11685203")
    @pytest.mark.ndvr
    @pytest.mark.e2e
    @pytest.mark.livetv
    @pytest.mark.cloud_core_watch_Recording
    def test_74355596_verify_watching_live_tv_playing_the_partial_recording_from_my_shows(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74355596
        Verify watching live TV, creating a partial nDVR recording, and playing the partial recording from My Shows
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=6)
        channel = self.text_search_page.get_filtered_program_from_grid_row(self,
                                                                           is_recordable_channel=True,
                                                                           genre="series",
                                                                           with_ott=False,
                                                                           not_ppv=True,
                                                                           live_filter=True,
                                                                           filter_live_only=True,
                                                                           channels_count=1)
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.goto_live_tv(channel[0]['channel_item'].channel_number)
        self.watchvideo_assertions.verify_livetv_mode()
        self.guide_page.build_cache(180)
        self.watchvideo_page.open_olg()
        self.guide_page.create_live_recording()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_title()
        self.guide_assertions.verify_recording_now_icon()
        program = self.guide_page.get_grid_focus_details()["program_name_in_cell"]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.play_recording(program)
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11685206")
    @pytest.mark.ndvr
    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74398056_verify_deleting_ndvr_recording_from_my_shows(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74398056
        Verify deleting a nDVR recording from My Shows' episode list,
        undeleting recording from Recently Deleted Recordings,
        and then playing the undeleted recording until the end.
        """
        show = self.service_api.schedule_single_recording()[0][0]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.delete_recording_in_my_show(show)
        self.my_shows_page.select_show(self.my_shows_labels.LBL_RECENTLY_DELETED)
        self.my_shows_page.undelete_recording_in_my_show(self, show)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(show)
        self.my_shows_page.select_show(show)
        self.my_shows_page.select_and_wait_for_playback_play()
        self.guide_page.wait_and_watch_until_end_of_program(self)

    @pytestrail.case("C11685230")
    @pytest.mark.apps_and_games
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.search_ccu
    @pytest.mark.notapplicable(not Settings.is_managed())
    def test_74496452_verify_transitions_when_switching_ott_apps(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74496452
         To verify that UI transitions between different apps
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        self.watchvideo_assertions.press_youtube_and_verify_screen(self)
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.watchvideo_assertions.press_exit_button()
        self.home_assertions.verify_home_title()
        self.home_page.back_to_home_short()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.guide_page.press_home_button()
        self.home_assertions.verify_home_title()
        self.home_page.press_right_button()
        self.home_page.press_left_button()
        self.home_page.press_down_button()
        self.home_page.press_up_button()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.apps_and_games_assertions.press_guide_and_verify_screen(self, key_press='inputkeyevent')
        self.guide_page.wait_for_screen_ready()
        self.text_search_page.go_to_search(self)
        self.text_search_assertions.verify_search_screen_title()
        self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
        self.guide_page.press_home_button()
        self.home_assertions.verify_home_title()
        self.home_page.go_to_what_to_watch(self)
        self.wtw_assertions.verify_wtw_screen_title()
        self.home_page.back_to_home_short()

    @pytestrail.case("C11685231")
    @pytest.mark.home
    @pytest.mark.voicesearch
    @pytest.mark.GA
    @pytest.mark.usefixtures("set_screen_saver_default_value")
    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_74498797_exit_screensaver_wakeup_with_voicesearch(self):
        """
        Description:
        To verify exiting screensaver and waking up the device is successful using Tivo Voice
        """
        self.home_page.back_to_home_short()
        self.watchvideo_page.pause(5 * 60)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.wake_up_device_voice_search()
        self.home_assertions.verify_home_title()

    @pytestrail.case("C11684195")
    @pytest.mark.GA
    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_74081805_live_playback_validation_using_GA(self):
        show = self.service_api.extract_offer_id(self.service_api.get_grid_row_search(is_preview_offer_needed=True),
                                                 genre='movie', count=1)
        collectionId = show[0][1]
        self.guide_page.open_youtube()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.home_page.back_to_home_short()
        self.guide_page.launch_action_screen_using_GA(collectionId)
        self.program_options_assertions.verify_action_view_mode()
        self.program_options_page.select_play_from_liveTv()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C11685225")
    @pytest.mark.textsearch
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_74482382_search_currently_airing_entitled_channel(self):
        """
        74482382
        Verify ability to search for currently airing entitled/unentitled and PC blocked program, channel name and call sign.
        :return:
        """
        self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=5)
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel:
            pytest.skip("Recordable episodic channels are not found.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.my_shows_page.go_to_cached_action_screen(self)
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.select_play_from_liveTv()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.my_shows_page.go_to_cached_action_screen(self)
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.text_search_page.go_to_search(self)
        self.text_search_page.move_focus_to_textpad()
        channel = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=True, filter_channel=True)
        call_sign_name = channel[0][4]
        if '-' in call_sign_name:
            index = call_sign_name.index('-')
            channel[0][4] = call_sign_name[:index]
        channel_callsign = (channel[0][0] + " " + channel[0][4])
        self.home_page.log.info("channel_callsign ={}".format(channel_callsign))
        self.text_search_page.search_and_select(f'{channel[0][4]}', f"{channel_callsign}", select=False)
        self.screen.base.press_enter(time=5000)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode()

    @pytestrail.case("C11684185")
    @pytest.mark.GA
    @pytest.mark.skipif(Settings.is_fire_tv(), reason="Not valid for Fire TV")
    def test_351614_launch_person_screen_using_GA(self):
        person = self.service_api.get_random_person(Settings.tsn, **{"first": "Dwayne"})
        self.home_page.back_to_home_short()
        self.guide_page.launch_action_screen_using_GA(person[0][2])
        self.program_options_assertions.verify_person_screen_title(person)
        self.program_options_assertions.verify_person_screen_strip()

    @pytestrail.case("C11685243")
    @pytest.mark.vod
    @pytest.mark.notapplicable(not Settings.is_unmanaged(), reason="Valid only for unmanaged")
    def test_74451796_verify_vod_launch_stability_unmanaged_devices(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74451796
         To verify that VOD launch and browse is stable even after multiple launches of different VOD asset.
        :return:
        """

        # navigating to asset and Click OK
        status, result = self.vod_api.getOffer_fvod()
        status, results = self.vod_api.getOffer_svod_entitledSubscribed()
        if result is None and results is None:
            pytest.skip("Assets are not available")
        self.vod_page.navigate_to_vod_show(self, result)
        self.vod_page.navigate_to_vod_show(self, results)
        self.vod_page.check_vod_launch_browse_stability_unmanaged_devices(self, result, results)

    @pytestrail.case("C11685200")
    @pytest.mark.onepass
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74346224_verify_creating_onepass_from_past_available(self):
        """
        74346224
         Verify creating a OnePass from a past available
         and entitled nDVR show in Guide displays the OnePass in My Shows and OnePass Manager.
        :return:
        """
        channels = self.service_api.get_past_grid_row(align=True, delta=30, is_preview_offer_needed=True)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1, duration=1800,
                                                                             grid_row=channels, encrypted=True,
                                                                             genre="series", filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.wait_for_screen_ready()
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_screen_ready()
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_assertions.verify_one_pass_exists(program)

    @pytestrail.case("C11685218")
    @pytest.mark.vod
    # @pytest.mark.test_stabilization
    @pytest.mark.notapplicable(("amino" not in Settings.platform.lower() and "puck" not in Settings.platform.lower()),
                               reason="Valid for amino only")
    def test_74451796_verify_vod_launch_stability(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74451796
         To verify that VOD launch and browse is stable even after multiple launches of different VOD assets.
        :return:
        """

        # navigating to asset and Click OK
        status, result = self.vod_api.getOffer_fvod()
        status, results = self.vod_api.getOffer_svod_entitledSubscribed()
        if result is None and results is None:
            pytest.skip("Assets are not available")
        self.vod_page.navigate_to_vod_show(self, result)
        self.vod_page.navigate_to_vod_show(self, results)
        self.vod_page.check_vod_launch_browse_stability_managed_specific_devices(self, result, results)

    @pytestrail.case("C11685239")
    @pytest.mark.vod
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Valid only for managed")
    def test_74451796_verify_vod_launch_stability_managed_devices(self):
        """
        https://testrail.corporate.local/index.php?/tests/view/74451796
         To verify that VOD launch and browse is stable even after multiple launches of different VOD assets.
        :return:
        """

        # navigating to asset and Click OK
        status, result = self.vod_api.getOffer_fvod()
        status, results = self.vod_api.getOffer_svod_entitledSubscribed()
        if result is None and results is None:
            pytest.skip("Assets are not available")
        self.vod_page.navigate_to_vod_show(self, result)
        self.vod_page.navigate_to_vod_show(self, results)
        self.vod_page.check_vod_launch_browse_stability_managed_devices(self, result, results)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685214")
    @pytest.mark.GA
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.skipif(Settings.is_fire_tv(), reason="Not valid for Fire TV")
    def test_e2e_74430886_launch_device_settings_using_GA(self):
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_device_settings(self)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "settings")
        screen_title = self.system_page.get_device_settings_screen_title()
        self.menu_assertions.verify_device_settings_screen_title(self, screen_title)
        self.home_page.back_to_home_short()
        self.home_page.open_device_setting(self.home_labels.LBL_DEVICE_SETTINGS_TITLE)
        self.menu_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "settings")
        self.home_page.back_to_home_short()

    @pytestrail.case("C11685217")
    @pytest.mark.home
    @pytest.mark.longrun
    @pytest.mark.usefixtures("decrease_screen_saver")
    def test_74449451_verify_device_wake_up_gracefully(self):
        """
        Description:
        To be able to wake up the box from screensaver by any Remote key.
        """
        self.menu_page.go_to_settings(self)
        self.home_page.wait_for_screen_saver(time=80)
        self.home_page.verify_key_press_to_wake_up_device(self)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685199")
    @pytest.mark.GA
    @pytest.mark.skipif(Settings.is_fire_tv(), reason="Not valid for Fire TV")
    def test_e2e_74127378_launch_device_settings_from_both_with_and_without_TiVo_app(self):
        """
        74127378
        Verify device settings launch both from within TiVo app and from within an OTT app.
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.open_device_setting(self.home_labels.LBL_DEVICE_SETTINGS_TITLE)
        self.menu_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "settings")
        self.home_page.launch_app_from_GA(self, self.home_labels.LBL_YOUTUBE)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.home_page.open_device_setting(self.home_labels.LBL_DEVICE_SETTINGS_TITLE)
        self.menu_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "settings")
        self.home_page.launch_app_from_GA(self, self.home_labels.LBL_NETFLIX)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.home_page.open_device_setting(self.home_labels.LBL_DEVICE_SETTINGS_TITLE)
        self.menu_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "settings")

    @pytestrail.case("C11685234")
    @pytest.mark.tts
    @pytest.mark.longrun
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("stop_tts_log")
    @pytest.mark.usefixtures("setup_disable_closed_captioning")
    def test_74574192_green_box_verification(self):
        """
        Description:
        TC - 74574192 - verifying greenbox visibility on different screens when TTS is enabled
        """
        self.home_page.back_to_home_short()
        dump, channel = self.home_page.dump_without_TTS_ON(self, myshows=True)
        dump_with_tts_on = self.home_page.dump_with_TTS_ON(self, channel, myshows=True)
        self.home_assertions.check_and_validate_green_box_status(dump, dump_with_tts_on)
        dump, channel = self.home_page.dump_without_TTS_ON(self, guide=True)
        dump_with_tts_on = self.home_page.dump_with_TTS_ON(self, channel, guide=True)
        self.home_assertions.check_and_validate_green_box_status(dump, dump_with_tts_on)
        dump, channel = self.home_page.dump_without_TTS_ON(self, live=True)
        dump_with_tts_on = self.home_page.dump_with_TTS_ON(self, channel, live=True)
        self.home_assertions.check_and_validate_green_box_status(dump, dump_with_tts_on)
        dump, channel = self.home_page.dump_without_TTS_ON(self, olg=True)
        dump_with_tts_on = self.home_page.dump_with_TTS_ON(self, channel, olg=True)
        self.home_assertions.check_and_validate_green_box_status(dump, dump_with_tts_on)
        self.home_page.dump_without_TTS_ON(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.textsearch
    @pytest.mark.search_ccu
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.usefixtures("disable_video_providers")
    def test_e2e_74482382_search_for_currently_airing_unentitled_program(self):
        """
        74482382
        Verify ability to search for currently airing unentitled program.
        :return:
        """
        status = self.api.get_show_entitled_channels_status(tsn=Settings.tsn)
        if status:
            pytest.skip("Device does not have unentitled channels")
        else:
            channel = self.service_api.get_unentitled_channels()
            if not channel:
                pytest.skip("Couldn't find any unentitled channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.input_search_text(program)
        self.text_search_assertions.verify_search_result(self.menu_labels.LBL_EMPTY_RESULT)

    # Same test is in test_apps_and_games.py and not specific only to managed device and running in GA feature
    # @pytest.mark.test_stabilization
    # @pytestrail.case("C11684199")
    # @pytest.mark.apps_and_games
    # @pytest.mark.skipif(not Settings.is_managed(), reason="Valid for managed only")
    # def test_74094935_verify_smooth_transition_between_apps(self):
    #    """
    #    74094935
    #    To verify smooth transition when switching between the apps
    #    :return:
    #    """
    #    self.apps_and_games_page.go_to_apps_and_games(self)
    #    self.apps_and_games_assertions.verify_screen_title(self)
    #    self.apps_and_games_assertions.start_google_play_and_verify_screen(self)
    #    self.home_page.back_to_home_short()
    #    self.apps_and_games_assertions.press_netflix_and_verify_screen(self)
    #    self.apps_and_games_assertions.pause(5 * 60)
    #    self.apps_and_games_assertions.verify_ott_app_is_foreground(self, "netflix")
    #    self.apps_and_games_page.press_exit_button()
    #    self.home_page.goto_livetv_short(self)
    #    self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
    #    self.watchvideo_assertions.verify_playback_play()
    #    show = self.service_api.get_random_recordable_channel()
    #    self.watchvideo_page.open_olg()
    #    self.watchvideo_page.enter_channel_number(show[0][0], confirm=True)
    #    self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
    #    self.watchvideo_assertions.verify_playback_play()
    #    self.watchvideo_assertions.verify_view_mode()
    #    self.watchvideo_assertions.verify_channel_number(show[0][0])
    #    self.watchvideo_page.watch_video_for(5 * 60)
    #    self.watchvideo_assertions.verify_view_mode()
    #    self.watchvideo_assertions.verify_channel_number(show[0][0])
    #    self.apps_and_games_assertions.press_youtube_and_verify_screen(self)
    #    self.apps_and_games_assertions.pause(5 * 60)
    #    self.apps_and_games_assertions.verify_ott_app_is_foreground(self, "youtube")
    #    self.apps_and_games_page.press_exit_button()
    #    self.home_page.goto_livetv_short(self)
    #    self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
    #    self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.livetv
    @pytest.mark.usefixtures("stop_tts_log")
    def test_e2e_74501142_device_respond_for_info_and_accessibility_button(self):
        """
        74501142
        Verify the device responds properly to info+accessibility+accessibility button press
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        if Settings.is_managed():
            self.watchvideo_page.show_accessibility_menu()
            self.watchvideo_assertions.verify_option_in_accessibility_strip(self.home_labels.TURN_SCREEN_READER_ON)
            self.watchvideo_page.press_back_button()
            self.home_assertions.verify_highlighter_on_prediction_strip()
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.watchvideo_page.press_back_button()
        self.watchvideo_page.press_back_button()

    @pytestrail.case("C11685198")
    @pytest.mark.livetv
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_e2e_74113536_verify_toggling_between_livetv_channels(self):
        channel = self.service_api.get_random_encrypted_unencrypted_channels(transportType="stream",
                                                                             filter_channel=True)
        if channel is None:
            pytest.skip("Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.back_to_home_short()
        self.home_assertions.select_live_channel_from_prediction(self)
        self.home_page.channel_change_in_olg(self)
        self.guide_page.goto_one_line_guide_from_live(self, channel=channel[0][0])
        self.guide_page.check_for_overlay_watchnow_or_watchlive()
        self.guide_assertions.wait_for_LiveTVPlayback("PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_LIVETV_VIEWMODE)

    @pytest.mark.vod
    @pytest.mark.onepass
    @pytest.mark.wtw_openAPI_impacted
    def test_74169590_create_delete_onepass(self):
        self.vod_page.get_content_available_from_both_vod_and_ott(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Valid for managed devices only")
    def test_11124681_remote_setup_help(self):
        """
        :testopia: https://testrail.tivo.com//index.php?/cases/view/11124681
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_MENU_TITLE)
        self.menu_page.select_menu_items(self.menu_labels.LBL_HELP)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_HELP_SCREENTITLE)
        self.menu_page.select_menu_items(self.menu_labels.LBL_REMOTE_AND_NAVIGATION)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_REMOTE_AND_NAVIGATION_SCREETITLE)
        self.menu_page.select_menu_items(self.menu_labels.LBL_REMOTE_SETUP)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_REMOTE_SETUP_SCREENTITLE)
        self.menu_assertions.verify_remote_type()
        self.menu_assertions.verify_remote_setup_preview()

    @pytest.mark.xray("FRUM-108012")
    @pytest.mark.xray("FRUM-108013")
    @pytest.mark.xray("FRUM-108014")
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.stability
    @pytest.mark.notapplicable(Settings.is_ruby() or Settings.is_jade())
    def test_108012_108013_108014_black_screen_issue(self):
        """
        Test Case 1:
        Play Live TV for someitme and press TiVo Home button 50 times
        FRUM-108012

        Test Case 2:
        Open Netflix, play for sometime and press TiVo Home button 50 times
        FRUM-108013

        Test Case 3:
        Relaunch Hydra app and press TiVo Home button 50 times
        FRUM-108014

        """
        self.home_page.back_to_home_short()
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if channel is None:
            self.log.info("No healthy channels found.")
        else:
            self.home_page.goto_live_tv(channel[0])
            self.log.info("Pressing TiVo Home button 50 times")
            for i in range(50):
                self.screen.base.press_home()
            self.home_assertions.verify_home_title()
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, self.apps_and_games_labels.
                                                                               LBL_APPS_AND_GAMES_NETFLIX)
        self.program_options_assertions.verify_ott_app_is_foreground(self,
                                                                     self.apps_and_games_labels.LBL_APPS_AND_GAMES_NETFLIX)
        self.log.info("Pressing TiVo Home button 50 times")
        for i in range(50):
            self.screen.base.press_home()
        self.home_assertions.verify_home_title()
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.log.info("Pressing TiVo Home button 50 times")
        for i in range(50):
            self.screen.base.press_home()
        self.home_assertions.verify_home_title()

    @pytest.mark.xray("FRUM-19028")
    @pytest.mark.e2e
    @pytest.mark.e2e1_15
    @pytest.mark.notapplicable(Settings.is_prod())
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.FCM, NotificationSendReqTypes.NSR])
    def test_19028_Send_ServiceCall_and_trigger_EAS(self, req_type):
        """
        This TC to test Send service Call First And then send EAS
        FRUM-19028

        """
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL)
        self.home_page.press_back_button()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.home_page.wait_for_EAS_to_dismiss(timeout=90)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_RESTART_NOW)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.home_assertions.verify_home_title()

    @pytest.mark.tivo_plus
    @pytest.mark.e2e
    @pytest.mark.e2e1_15
    @pytest.mark.usefixtures("toggle_mind_availability")
    @pytest.mark.xray("FRUM-11216")
    def test_11216_resiliency_mode_tivo_plus(self):
        channel = self.api.get_tivo_plus_channels()[0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.tune_to_tivo_plus_channel(self, channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)

    @pytest.mark.xray('FRUM-70751')
    @pytest.mark.e2e
    @pytest.mark.longrun
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_apple_tv())
    @pytest.mark.e2e1_16
    def test_stop_streaming_four_hours_continuous_playback(self):
        """
        Verify Stop streaming while setting screen save to Never
        """
        status = self.system_page.change_screensaver_time(self.watchvideo_labels.LBL_SCREENSAVER_TEXT_NEVER)
        if not status:
            pytest.skip("Never option not available in screensaver settings")
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREENTITLE)
        channel = self.api.get_random_encrypted_unencrypted_channels(transportType="stream", filter_channel=True)
        if not channel:
            pytest.skip("No appropriate channels found.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.verify_long_hours_playback(self, no_of_hrs=4)
        self.watchvideo_page.wait_for_osd_text(self.watchvideo_labels.LBL_INACTIVITY_TIME_OSD_TEXT)
        self.watchvideo_page.pause(300)
        self.watchvideo_page.wait_for_osd_text(self.watchvideo_labels.LBL_AREYOUSTILL_THERE_OSD_TEXT)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()

    @pytest.mark.e2e1_15
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-10950")
    @pytest.mark.usefixtures("toggle_mind_availability")
    @pytest.mark.usefixtures("set_screen_saver_default_value")
    @pytest.mark.notapplicable(Settings.is_ruby() or Settings.is_jade(), reason="Netflix is not supported")
    def test_frum_10950_resiliency_mode_screensaver_netflix(self):
        channels = self.service_api.get_live_channels_with_OTT_available(count=1)[0]
        if not channels:
            pytest.skip("Test requires OTT program.")
        self.home_page.back_to_home_short()
        self.driver.set_screen_saver_timeout(5 * 60)
        self.home_page.wait_for_screen_saver(time=420)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.select_and_watch_program(self)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.xray("FRUM-10947")
    @pytest.mark.usefixtures("toggle_mind_availability")
    def test_frum_10947_resiliency_mode_jump_channel_from_guide_olg(self):
        channel_num = list(self.api.get_jump_channels_list().keys())[0]
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.screen.base.press_enter()
        self.guide_assertions.verify_jump_channel_launch(Settings.app_package)
        self.watchvideo_page.open_olg()
        self.watchvideo_assertions.verify_one_line_guide()
        self.guide_page.enter_channel_number(channel_num, confirm=True, dump=True, olg=True)
        self.guide_assertions.verify_jump_channel_launch(Settings.app_package, enter=False)

    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.xray("FRUM-12044")
    @pytest.mark.e2e1_15
    @pytest.mark.e2e
    @pytest.mark.tivo_plus
    def test_12044_get_pluto_tv_channel_create_bookmark_play_from_myshows(self):
        channels = self.api.get_pluto_tv_channels_with_ott_offers()
        if not channels:
            pytest.skip("MSO has not configured any Pluto TV channels")
        self.home_page.back_to_home_short()
        channel_number = random.choice(channels)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_get_more_info(self)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.guide_page.select_menu_by_substring(self.menu_labels.LBL_BOOKMARK)
        self.wtw_page.verify_whisper(self.menu_labels.LBL_BOOKMARK_COMMON_WHISPER)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_content_in_any_category(self, program)
        self.my_shows_page.select_show(program)
        self.guide_page.press_ok_button()
        self.apps_and_games_assertions.wait_fo_app_launch(Settings.PLUTO_TV_PACKAGE_NAME, limit=15)

    @pytest.mark.xray("FRUM-19033")
    @pytest.mark.e2e1_15
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.FCM])
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "C2C voice solution is only for Managed streamers")
    @pytest.mark.notapplicable(Settings.is_prod())
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    def test_19028_Send_ServiceCall_and_trigger_C2C(self, req_type):
        """
        This TC to test Send service Call First And then send C2C
        FRUM-19033

        """
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL)
        self.home_page.press_back_button()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.voicesearch_page.send_empty_voice()
        self.voicesearch_assertions.verify_availability_of_text("")
        self.screen.base.press_back()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_RESTART_NOW)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.home_assertions.verify_home_title(label=self.home_labels.LBL_HOME_SCREENTITLE)
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_OPEN,
            screen_title=self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL)
        self.screen.base.press_home()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_RESTART_NOW)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.home_assertions.verify_home_title(label=self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.e2e1_16
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-72511")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    @pytest.mark.parametrize("req_type", ["FCM", "NSR"])
    def test_72511_service_call_when_tivo_background(self, req_type):
        self.home_page.back_to_home_short()
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type="serviceCall")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.home_page.press_home_button()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_REMIND_ME_LATER_OPTION)
        self.vod_page.go_to_vod(self)
        self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)
        self.home_page.press_home_button()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.watchvideo_assertions.press_netflix_and_verify_screen(self)
        self.home_page.press_home_button()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_RESTART_NOW)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package)
        self.watchvideo_assertions.press_netflix_and_verify_screen(self)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type="serviceCall")
        self.home_page.press_home_button()
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(self.home_labels.LBL_RESTART_NOW)
        self.watchvideo_page.press_back_button()
        self.home_page.handling_hydra_app_after_exit(Settings.app_package)
        self.home_assertions.press_home_and_verify_screen(self)

    @pytest.mark.tivo_plus
    @pytest.mark.e2e1_15
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-11232")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("pluto_tv_app_install")
    @pytest.mark.usefixtures("toggle_mind_availability")
    def test_11232_pluto_tv_service_down(self):
        channels = self.api.get_pluto_tv_channels()
        if not channels:
            pytest.skip("MSO has not configured any Pluto TV channels")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0])
        self.guide_page.press_ok_button()
        self.apps_and_games_assertions.wait_fo_app_launch(Settings.PLUTO_TV_PACKAGE_NAME, limit=20)
        self.apps_and_games_page.wait_for_pluto_tv_start_playing()
        self.apps_and_games_assertions.press_channel_button_and_verify_channel_change_in_pluto_tv("channel up")
        self.apps_and_games_page.press_back_button()
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.app_package)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.press_exit_button()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.goto_one_line_guide_from_live(self, channel=channels[0])
        self.guide_page.press_ok_button()
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.PLUTO_TV_PACKAGE_NAME)
        self.apps_and_games_page.wait_for_pluto_tv_start_playing()
        self.apps_and_games_page.press_back_button()
        self.apps_and_games_assertions.verify_app_is_foreground(Settings.app_package)

    @pytest.mark.e2e1_15
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-10954", "FRUM-18614")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("setup_parental_controls_and_always_require_pin")
    def test_10954_18614_pc_behaviour_when_tivo_services_down(self):
        self.home_page.back_to_home_short()
        self.home_page.toggle_mind_availability()
        self.home_page.press_ok_button()
        self.home_assertions.verify_predictions_error_message(self, self.home_labels.LBL_ERROR_CODE_C219)
        channel = self.service_api.get_channels_with_no_trickplay_restrictions(self)
        if not channel:
            pytest.skip("No channels with trickplay found.")
        for i in range(2):
            self.home_page.goto_live_tv(random.choice(channel))
            self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
            self.watchvideo_assertions.verify_osd()
            self.screen.base.press_enter()
            self.watchvideo_assertions.verify_PIN_challenge_overlay()
            self.vod_page.enter_pin_in_overlay(self)
            self.guide_page.wait_for_screen_ready()
            self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
            self.watchvideo_assertions.verify_no_osd_on_screen()
        self.my_shows_page.validate_trickplay_actions(self, Settings.platform)
        self.guide_page.change_audio(self)
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_page.turn_on_cc(self)
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_page.turn_on_cc(self, ON=False)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        info_banner = [self.liveTv_labels.LBL_BOOKMARK, self.liveTv_labels.LBL_CREATE_ONEPASS,
                       self.liveTv_labels.LBL_RECORD]
        for item in info_banner:
            self.watchvideo_assertions.verify_target_option_not_present_in_info_banner(item)
        self.home_page.back_to_home_short()
        self.home_page.toggle_mind_availability()
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=False)

    @pytest.mark.e2e1_16
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-64781")
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.usefixtures("set_screen_saver_default_value")
    def test_64781_guide_button_on_screen_saver(self):
        self.home_page.back_to_home_short()
        self.vod_page.go_to_vod(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SCREENTITLE)
        self.home_page.wait_for_screen_saver(time=300)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.home_page.press_guide_button(key_press='inputkeyevent')
        self.home_page.wait_for_screen_ready("GridGuide", timeout=10000)
        self.screen.refresh()
        self.guide_assertions.verify_guide_title()

    @pytest.mark.e2e1_16
    @pytest.mark.xray("FRUM-64771")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_fire_tv() or Settings.is_apple_tv())
    def test_64771_global_ads_and_user_preference(self):
        privacy_optin = self.api.branding_ui(field="privacy_opt_in_config")
        if not privacy_optin:
            pytest.skip("Privacy opt in not supported by the MSO")
        global_ads_enabled = self.system_page.launch_global_ads_from_device_settings()
        if global_ads_enabled:
            self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME, reboot=True)
            self.menu_page.go_to_user_preferences(self)
            self.menu_assertions.verify_personalized_ads_enabled(status=False)
        else:
            self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME, reboot=True)
            self.menu_page.go_to_user_preferences(self)
            self.menu_page.set_personalized_ads_status(enable=True)
            self.menu_assertions.verify_personalized_ads_enabled(status=True)

    @pytest.mark.longevity
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_longevity_watch_youtube_long_hours_navigate_to_tivo_livetv(self):
        """
            Verify launching Youtube form GA and playing content from Youtube OTT for longer durations and pressing
            TiVo home button and playing live tv for another hour
            Xray:https://jira.xperi.com/browse/FRUM-131408
        """
        self.home_page.back_to_home_short()
        self.apps_and_games_page.play_youtube_content_for_3hours()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.pause(10800, reason="Waiting fot Youtube video to get completed")
        self.home_page.back_to_home_short()
        self.menu_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.e2e1_17
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-111085")
    @pytest.mark.notapplicable(not Settings.is_cc5())
    def test_111085_web_vtt_and_vod(self):
        self.home_page.back_to_home_short()
        self.menu_page.go_to_accessibility(self)
        self.menu_assertions.verify_accessibility_screen_title(self)
        self.menu_page.go_to_closed_captioning(self)
        self.menu_assertions.select_menu(self.menu_labels.LBL_ON)
        self.home_page.back_to_home_short()
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.menu_page.turn_parental_control(self, turn='On - Locked')
        self.home_page.back_to_home_short()
        program = self.vod_labels.LBL_SUBTITLE_VOD_PROGRAM_NEW
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program, select=True)
        self.my_shows_page.select_strip(self.vod_labels.LBL_VP15_ON_DEMAND)
        self.vod_page.manage_launched_playback(self, availability_type="fvod")
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.guide_page.wait_for_screen_ready()
        if self.screen.get_screen_dump_item('viewMode') == self.guide_labels.LBL_RESUME_OVERLAY:
            self.log.step("Overlay detected, trying to select resume/startover")
            self.watchvideo_page.select_menu(self.guide_labels.LBL_STARTOVER)
        else:
            self.log.step("Overlay is not shown, video is already playing.")
        self.vod_assertions.verify_vod_playback(self)
        self.screen.base.press_info()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.menu_page.select_menu_items(self.menu_labels.LBL_SPANISH)
        self.screen.base.press_info()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_language_with_blue_tick(self.menu_labels.LBL_SPANISH)
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")

    @pytest.mark.usefixtures("setup_lock_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.longrun
    @pytest.mark.e2e1_16
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-70751")
    def test_70751_screensaver_never_pc_e2e_case(self):
        """
            Verify the plaback after setting screensaver to Never and locking the PC with Block all
        """
        status = self.system_page.change_screensaver_time(self.watchvideo_labels.LBL_SCREENSAVER_TEXT_NEVER)
        if not status:
            pytest.skip("Never option not available in screensaver settings")
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREENTITLE)
        channel = self.guide_page.get_streamable_rating_content(self)
        if len(channel) < 2:
            pytest.skip("could not find rating channel")
        self.home_page.goto_live_tv(channel[0])
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.verify_long_hours_playback(self, no_of_hrs=4)
        self.watchvideo_page.wait_for_osd_text(self.watchvideo_labels.LBL_INACTIVITY_TIME_OSD_TEXT)
        self.watchvideo_page.pause(300)
        self.watchvideo_page.wait_for_osd_text(self.watchvideo_labels.LBL_AREYOUSTILL_THERE_OSD_TEXT)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(15)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=True)
