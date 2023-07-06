import os
import time
import random
import pytest

from set_top_box.client_api.voice_search.conftest import setup_voice_search  # noqa: F401
from set_top_box.client_api.end2end.conftest import set_screen_saver_default_value  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings  # noqa: F401
from set_top_box.client_api.watchvideo.conftest import ensure_livetv_on_realtime  # noqa: F401
from set_top_box.client_api.vision_tester.conftest import setup_vision_tester, vt_precondition, device_wakeup, \
    check_hdmi_adb_connected_to_same_device  # noqa: F401
from set_top_box.client_api.end2end.conftest import setup_e2e  # noqa: F401
from set_top_box.client_api.Menu.conftest import disable_parental_controls, disable_video_window, exit_OTT, \
    setup_enable_closed_captioning, setup_cleanup_disable_closed_captioning  # noqa:F401
from set_top_box.client_api.home.conftest import preserve_initial_package_state, remove_packages_if_present_before_test, \
    enable_canadian_eas_by_override, enable_floating_eas_by_override  # noqa: F401
from set_top_box.client_api.Menu.conftest import setup_enable_video_window, setup_enable_full_screen_video_on_home  # noqa:F401
from set_top_box.client_api.Menu.conftest import setup_lock_parental_and_purchase_controls  # noqa:F401
from set_top_box.client_api.Menu.conftest import setup_cleanup_parental_and_purchase_controls  # noqa:F401
from set_top_box.client_api.Menu.conftest import setup_enable_top_right_video_window_on_home  # noqa:F401
from set_top_box.client_api.Menu.conftest import setup_enable_atmospheric_home_background  # noqa:F401
from set_top_box.client_api.Menu.conftest import enable_tts  # noqa:F401
from set_top_box.client_api.Menu.conftest import setup_cleanup_remove_playback_source  # noqa:F401
from set_top_box.conftest import get_and_restore_tcdui_test_conf  # noqa:F401
from set_top_box.test_settings import Settings
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, HydraBranches, FeaturesList, \
    LongevityConstants
from pytest_testrail.plugin import pytestrail


@pytest.mark.usefixtures('setup_e2e')
@pytest.mark.timeout(Settings.timeout)
@pytest.mark.notapplicable(not Settings.is_vision_tester_enabled())
@pytest.mark.vision_tester
@pytest.mark.usefixtures('device_wakeup')
@pytest.mark.usefixtures('vt_precondition')
@pytest.mark.usefixtures('setup_vision_tester')
class TestVisionTester:

    @pytest.mark.mandatory_test
    @pytest.mark.usefixtures('check_hdmi_adb_connected_to_same_device')
    def test_mandatory_test_vision_tester(self):
        self.home_page.back_to_home_short()
        self.vision_page.verify_screen_contains_text("GUIDE")

    @pytest.mark.player
    @pytest.mark.watchvideo
    @pytest.mark.usefixtures('set_screen_saver_default_value')
    def test_8880255_livetv_indefinite_time(self):
        """
        C8880255
        Go to Menu->Settings->Device settings->Screen saver
        Navigate to Live TV.
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(300)
        self.vision_page.verify_av_playback()

    @pytest.mark.eas
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               reason="This test is applicable only for builds streamer-1-15 or later.")
    def test_9390559_trigger_canadian_eas_alert(self,
                                                get_and_restore_tcdui_test_conf,  # noqa: F811
                                                enable_canadian_eas_by_override,  # noqa: F811
                                                ):
        """
        C9390559
        Verify that following text "ALERTE D'URGENCE" is displayed on the bottom of the screen
        """
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_EAS_screen(eas="canadian")
        self.vision_page.verify_audio_state(time_to_verify=10)
        self.vision_page.verify_screen_contains_text(self.home_labels.LBL_EMERGENCY_ALERT_FRENCH, lang='fra')
        self.screen.base.press_back()

    @pytest.mark.socu
    @pytest.mark.ndvr
    @pytest.mark.player
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74423851_socu_and_ndvr_both_work(self):
        """
        https://testrail.tivo.com/index.php?/tests/view/74423851
        To Verify SOCU and nDVR playback both work as expected for a program available through both options.
        """
        channels = self.service_api.get_available_channels_with_socu_offer()
        if not channels:
            pytest.skip("Channels not available. Hence skipping.")
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
        self.guide_page.watch_now_from(self, source=self.home_labels.LBL_WATCH_FROM_CATCH_UP)
        self.watchvideo_assertions.verify_playback_play()
        self.vision_page.verify_av_playback()
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
        self.vision_page.verify_av_playback()

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.player
    @pytest.mark.vod
    @pytest.mark.vt_core_feature
    @pytest.mark.usefixtures('setup_enable_top_right_video_window_on_home')
    def test_309966_12792175_watch_streaming_video_GUIDE_button_PIG_enabled(self):
        """
        318398/C12792175
         Verify a VOD offer continues to play in the video window when pressing GUIDE while watching the VOD offer.
        :return:
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(40)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.screen.base.press_guide()
        self.vod_page.wait_for_screen_ready()
        self.vod_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_pig_video_playback()

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures('disable_video_window')
    def test_309966_12792175_watch_streaming_video_GUIDE_button_PIG_disabled(self):
        """
        318398/C12792175
         Verify a VOD offer continues to play in the video window when pressing GUIDE while watching the VOD offer.
        :return:
        """
        status, result = self.vod_api.get_entitled_HD_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.screen.base.press_guide()
        self.vod_page.wait_for_screen_ready()
        self.vod_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)
        self.vision_page.verify_pig_video_playback(expected=False)

    @pytest.mark.e2e
    @pytest.mark.player
    @pytest.mark.vt_core_feature
    @pytest.mark.skipif(not Settings.is_advance_available(), reason="Device doesn`t have the ADVANCE button.")
    def test_8880426_airing_show_resumes_playing_after_pausing(self):
        channel = self.api.get_channels_with_no_trickplay_restrictions()[0]
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.enter_channel_number(channel)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.watch_video_for(120)
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.watch_video_for(120)
        self.vision_page.verify_av_playback(expected=False)
        self.watchvideo_page.press_advance_button()
        self.vision_page.verify_av_playback()

    @pytest.mark.player
    @pytest.mark.watchvideo
    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_8880429_airing_continue_playing_after_reboot(self):
        channel = self.api.get_channels_with_no_trickplay_restrictions()[0]
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.enter_channel_number(channel)
        self.watchvideo_page.watch_video_for(120)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.vision_page.check_and_dismiss_pair_remote_overlay()
        self.home_page.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()

    def test_9643005_verify_jump_channel_overlay_is_dismissed_using_back_button(self):
        """
        Verify behavior for BACK button in "Leaving Live TV" overlay.
        """
        jump_channel_number = self.service_api.get_channel_with_jump_channel_near(jump_channel_near=True,
                                                                                  nextprev='next')[0]
        if not jump_channel_number:
            pytest.skip("Channel with jump channel near is not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.enter_channel_number(jump_channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.press_back_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()
        self.vision_page.verify_screen_contains_text(str(jump_channel_number),
                                                     region=self.vision_page.locators.LIVE_TV_CHANNEL_REGION)
        self.watchvideo_assertions.verify_channel_number(jump_channel_number)

    @pytest.mark.skipif(not (Settings.is_puck() or Settings.is_amino()), reason="Valid for amino only")
    def test_9643005_verify_jump_channel_overlay_is_dismissed_using_clear_button(self):
        """
        Verify behavior for Clear button in "Leaving Live TV" overlay.
        """
        jump_channel_number = self.service_api.get_channel_with_jump_channel_near(jump_channel_near=True,
                                                                                  nextprev='next')[0]
        if not jump_channel_number:
            pytest.skip("Channel with jump channel near is not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.enter_channel_number(jump_channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()
        self.vision_page.verify_screen_contains_text(str(jump_channel_number),
                                                     region=self.vision_page.locators.LIVE_TV_CHANNEL_REGION)
        self.watchvideo_assertions.verify_channel_number(jump_channel_number)

    @pytest.mark.eas
    @pytest.mark.vt_core_feature
    def test_9390558_trigger_us_EAS_alert(self):
        """
        C9390558
        Verify that following text "EMERGENCY ALERT" is displayed on the top of the screen
        :return:
        """
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_EAS_screen()
        frame = self.vision_page.get_current_frame()
        self.vision_page.verify_audio_state(time_to_verify=10)
        self.vision_page.verify_screen_contains_text(self.home_labels.LBL_EMERGENCY_ALERT_ENG_US,
                                                     region=self.vision_page.locators.EAS_US_REGION,
                                                     frame=frame)
        self.screen.base.press_back()

    @pytest.mark.eas
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               reason="This test is applicable only for builds streamer-1-15 or later.")
    def test_9390469_verify_canadian_EAS_text_is_white(self,
                                                       get_and_restore_tcdui_test_conf,  # noqa: F811
                                                       enable_canadian_eas_by_override,  # noqa: F811
                                                       ):
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_EAS_screen(eas='canadian')
        self.vision_page.verify_screen_contains_text(self.home_labels.LBL_EMERGENCY_ALERT_FRENCH, lang='fra')
        self.vision_page.verify_screen_contains_text_by_color(
            self.home_labels.LBL_EMERGENCY_ALERT_FRENCH, self.vision_page.colors_range.WHITE_COLOR, lang='fra')
        self.screen.base.press_back()

    @pytest.mark.eas
    def test_9390526_trigger_us_EAS_alert_and_verify_text_crawls_left_to_right(self):
        """
        C9390526
        Verify that EAS text crawls from right to left
        :return:
        """
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.vision_page.is_text_crawls_left(text=self.home_labels.LBL_EAS_MESSAGE_CRAWLING_ANCHOR_CHILD, iterations=2)
        self.screen.base.press_back()

    @pytest.mark.eas
    @pytest.mark.vt_core_feature
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               reason="This test is applicable only for builds streamer-1-15 or later.")
    def test_9390460_trigger_canadian_EAS_alert_full_screen(self,
                                                            get_and_restore_tcdui_test_conf,  # noqa: F811
                                                            enable_canadian_eas_by_override,  # noqa: F811
                                                            ):
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.api.get_EAS(Settings.tsn, self.home_labels.LBL_EAS_MESSAGE)
        self.home_assertions.verify_EAS_screen(eas='canadian')
        self.vision_page.verify_screen_contains_text(self.home_labels.LBL_EMERGENCY_ALERT_FRENCH, lang='fra')
        self.vision_page.verify_eas_full_screen(self.vision_page.colors_range.START_RED_COLOR_RANGE,
                                                self.vision_page.colors_range.END_RED_COLOR_RANGE)

    @pytest.mark.eas
    @pytest.mark.vt_core_feature
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               reason="This test is applicable only for builds streamer-1-15 or later.")
    def test_96673_trigger_floating_EAS_alert_and_verify_text_crawls_twice(self,
                                                                           get_and_restore_tcdui_test_conf,  # noqa: F811
                                                                           enable_floating_eas_by_override,  # noqa: F811
                                                                           ):
        """
        FRUM-96673
        Verify that FLOATING EAS banner text only scrolls twice on the bottom part of screen, then disappear leaving the
        alternative EAS video playing
        :return:
        """
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.api.get_EAS(tsn=Settings.tsn, text=self.home_labels.LBL_FLOATING_EAS_MESSAGE,
                         mediaurl=self.home_labels.LBL_FLOAT_EAS_LIVE_VIDEO_URL)
        self.home_assertions.verify_EAS_screen(eas='floating')
        self.vision_page.verify_eas_bottom_part_of_screen(self.home_labels.LBL_FLOATING_EAS_MESSAGE_ANCHOR)
        self.vision_page.verify_av_playback(url=self.home_labels.LBL_FLOAT_EAS_LIVE_VIDEO_URL, audio_check=True)
        self.home_page.wait_for_EAS_to_dismiss(timeout=35)
        self.vision_page.verify_eas_bottom_part_of_screen(self.home_labels.LBL_FLOATING_EAS_MESSAGE_ANCHOR,
                                                          presented_on_screen=False)
        self.screen.base.press_back()

    @pytest.mark.vt_core_feature
    @pytest.mark.usefixtures("setup_enable_video_window")
    @pytest.mark.usefixtures("setup_enable_full_screen_video_on_home")
    def test_4863386_video_on_home_yes_full_screen(self):
        channel = self.guide_page.guide_streaming_channel_number(self)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(10)
        self.home_page.back_to_home_short()
        self.vision_page.verify_low_contrast_playback()

    @pytest.mark.vt_core_feature
    @pytest.mark.usefixtures("setup_enable_top_right_video_window_on_home")
    def test_4863386_video_on_home_yes_PIG_mode(self):
        channel = self.guide_page.guide_streaming_channel_number(self)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(10)
        self.home_page.back_to_home_short()
        self.vision_page.verify_video_playbak_in_area(
            area=self.vision_page.locators.HOME_PAGE_PIG_PLAYBACK_REGION)
        self.vision_page.verify_video_playbak_in_area(
            area=self.vision_page.locators.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, expected=False)

    @pytest.mark.vt_core_feature
    def test_audio_feature(self):
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel:
            pytest.skip("Did not find good channel. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.select_and_watch_program(self)
        self.vision_page.verify_av_playback()
        self.screen.base.press_left()
        self.watchvideo_page.verify_next_or_previous_channel_is_good_channel(self, channel_num=channel[0][0])
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_audio_state(time_to_verify=15)
        self.home_page.log.info("Verifying audio feature for previous channel")
        self.screen.base.press_channel_down()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()
        self.watchvideo_page.verify_next_or_previous_channel_is_good_channel(self, channel_num=channel[0][0],
                                                                             channel="channel down")
        self.vision_page.verify_av_playback()
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_audio_state(time_to_verify=15)

    @pytest.mark.usefixtures('disable_video_window')
    def test_4863386_video_off_background_black_on_home(self):
        channel = self.guide_page.guide_streaming_channel_number(self)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(10)
        self.home_page.back_to_home_short()
        self.vision_page.verify_video_playbak_in_area(
            area=self.vision_page.locators.HOME_PAGE_PIG_PLAYBACK_REGION, expected=False)
        self.vision_page.verify_video_playbak_in_area(
            area=self.vision_page.locators.HOME_PAGE_FULL_SCREEN_PLAYBACK_REGION, expected=False)

    @pytest.mark.player
    @pytest.mark.witbe_e2ecase
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.test_stabilization
    def test_74157768_ndvr_record_and_playback_recorded(self):
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()

    @pytest.mark.player
    @pytest.mark.usefixtures('setup_enable_atmospheric_home_background')
    def test_4863386_video_off_background_atmospheric(self):
        image_path = self.vision_page.templates.HYDRA_BACKGROUND
        channel = self.guide_page.guide_streaming_channel_number(self)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(10)
        self.home_page.back_to_home_short()
        self.vision_page.verify_av_playback(expected=False)
        self.vision_page.match_template(f'{image_path}', 0.2)

    @pytest.mark.watchvideo
    @pytest.mark.player
    @pytest.mark.notapplicable(Settings.is_fire_tv() or Settings.is_apple_tv())
    def test_8880237_vod_watching_exit_playback(self):
        status, results = self.vod_api.get_offer_playable()
        if results is None:
            pytest.skip("The content is not available on VOD catlog.")
        channel = self.guide_page.guide_streaming_channel_number(self)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(40)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.watchvideo_page.watch_video_for(60)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.press_exit_button()
        self.watchvideo_page.watch_video_for(40)
        self.vision_page.verify_av_playback()

    def test_verify_carousel_contains_image(self):
        self.home_page.back_to_home_short()
        self.home_page.go_to_what_to_watch(self)
        images = self.wtw_page.get_images_in_focused_strip()
        template = self.api.get_download_image(images[2]['imagename'], Settings.log_path)
        self.vision_page.match_template(template)

    @pytest.mark.vt_core_feature
    def test_verify_carousel_works_wtw(self):
        self.home_page.back_to_home_short()
        self.home_page.go_to_what_to_watch(self)
        images = self.wtw_page.get_images_in_focused_strip()
        template = self.api.get_download_image(images[1]['imagename'], Settings.log_path)
        start_pos = self.vision_page.match_template(template)
        self.driver.base.press_right()
        self.watchvideo_page.watch_video_for(5)
        end_pos = self.vision_page.match_template(template)
        self.vision_page.verify_carousel_images_moves(end_pos[3][0], start_pos[3][0])

    def test_bootup_logo(self):
        image = self.vision_page.templates.BOOT_LOGO
        self.home_page.back_to_home_short()
        self.screen.base.reboot_device()
        self.vision_page.match_bootup_logo(image)
        self.watchvideo_page.watch_video_for(120)
        self.home_page.back_to_home_short()

    @pytest.mark.player
    @pytest.mark.skipif(not Settings.is_prod(), reason='Works only on prod devices')
    def test_11124067_voice_play_live_tv(self):
        channel_number = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True)[0]
        if not channel_number:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.guide_page.pause_show(self)
        self.voicesearch_page.sent_media_command_with_google_assistant(self.voicesearch_labels.LBL_VOICE_MEDIA_RESUME)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()

    @pytest.mark.player
    @pytest.mark.skipif(not Settings.is_prod(), reason='Works only on prod devices')
    def test_11121857_vod_play_voice(self):
        self.home_page.back_to_home_short()
        self.voicesearch_page.action_command_by_title_with_google_assistant(action="Play", title="Frozen", year="2019")
        self.watchvideo_page.watch_video_for(29)
        self.vision_page.verify_av_playback()

    @pytest.mark.player
    @pytest.mark.skipif(not Settings.is_prod(), reason='Works only on prod devices')
    def test_10201997_vod_actions_voice_c2c(self):
        status, results = self.vod_api.get_offer_playable()
        if results is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.guide_page.pause_show(self)
        self.voicesearch_page.sent_media_command_with_google_assistant(self.voicesearch_labels.LBL_VOICE_MEDIA_RESUME)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()

    @pytest.mark.vtp
    @pytest.mark.test_stabilization
    def test_29417801_vtp_press_right_motion_live_tv(self):
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_right_button()
        self.vod_page.press_ok()
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=False)
        self.vision_page.verify_av_playback()

    @pytest.mark.vtp
    @pytest.mark.test_stabilization
    def test_29417742_vtp_rewind_press_left_live_tv(self):
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.watch_video_for(300)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.screen.base.press_rewind()
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX1)
        self.home_page.screen.base.press_right()
        self.vod_page.press_ok()
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=True)
        self.vision_page.verify_av_playback()

    @pytest.mark.vtp
    @pytest.mark.test_stabilization
    def test_29417749_vtp_rewind_press_left_vod(self):
        status, result = self.vod_api.getOffer_vod_without_trickplay_restrictions()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.watch_video_for(250)
        self.vod_assertions.verify_vod_playback(self)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.screen.base.press_rewind()
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX1)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=True)
        self.vision_page.verify_av_playback()

    @pytest.mark.vtp
    @pytest.mark.test_stabilization
    def test_29417749_vtp_forward_press_right_vod(self):
        status, result = self.vod_api.getOffer_vod_without_trickplay_restrictions()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.watch_video_for(20)
        self.vod_assertions.verify_vod_playback(self)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_right_button()
        self.screen.base.ok()
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=False)
        self.vision_page.verify_av_playback()

    @pytest.mark.usefixtures('setup_lock_parental_and_purchase_controls')
    @pytest.mark.usefixtures('setup_cleanup_parental_and_purchase_controls')
    @pytest.mark.usefixtures("setup_enable_video_window")
    def test_4864181_parental_control_on_home_video_on(self):
        adult = self.guide_page.get_streamable_adult_content(self)
        if not adult:
            pytest.skip("Couldn't find an adult channel. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(adult[0])
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(10)
        self.vod_page.press_ok()
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_page.watch_video_for(10)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.back_to_home_short()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_pig_video_playback()
        self.menu_page.go_to_parental_controls(self)
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.menu_page.screen.refresh()
        self.menu_page.turn_parental_control(self, "On - Locked")
        self.home_page.back_to_home_short()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_pig_video_playback(expected=False)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(adult[0])
        self.guide_page.select_and_watch_program(self)
        self.vod_page.press_ok()
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()

    @pytest.mark.test_stabilization
    @pytest.mark.ott_deeplink
    def test_8880425_home_button_from_ott_netflix(self):
        self.home_page.back_to_home_short()
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select('Amar', "Amar (2017)", watch_now=True)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback(audio_check=False, timeout=10)
        self.screen.base.press_home()
        self.home_page.wait_for_screen_ready()
        self.vision_page.verify_screen_contains_text(self.home_labels.LBL_HOME_SCREENTITLE,
                                                     region=self.vision_page.locators.HOME_PAGE_TITLE_REGION)

    @pytest.mark.vt_tts
    @pytest.mark.usefixtures('enable_tts')
    @pytest.mark.usefixtures('disable_video_window')
    def test_74097242_talk_back_in_menu(self):
        self.home_page.back_to_home_short()
        self.home_page.screen.base.press_right(time=0)
        self.vision_page.verify_audio_state()

    @pytest.mark.vt_core_feature
    @pytest.mark.vt_tts
    @pytest.mark.usefixtures('enable_tts')
    @pytest.mark.usefixtures('disable_video_window')
    def test_355617_talk_back_speech_recognition(self):
        self.home_page.back_to_home_short()
        self.home_page.screen.base.press_right(time=0)
        tts_speech = self.vision_page.recognize_speech()
        assert self.home_labels.LBL_TTS_NAVIGATION in tts_speech

    @pytest.mark.test_stabilization
    @pytest.mark.compliance
    @pytest.mark.eas
    def test_312064623_interrupt_EAS_message(self):
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.home_page.back_to_home_short()
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.vision_page.verify_audio_state(time_to_verify=15)
        self.watchvideo_assertions.press_exit_button()
        self.vision_page.verify_screen_contains_text(self.home_labels.LBL_EMERGENCY_ALERT_ENG_US,
                                                     region=self.vision_page.locators.EAS_US_REGION)
        self.vision_page.is_text_crawls_left(text=self.home_labels.LBL_EAS_MESSAGE_CRAWLING_ANCHOR_CHILD, iterations=1)
        self.home_page.wait_for_EAS_to_dismiss(timeout=45)
        self.home_assertions.verify_home_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.skipif("blackmagic" in Settings.vision_tester_hardware(), reason="cannot validate video quality check")
    def test_FRUM_24_switch_between_UHD_channels(self, record_property):
        channel = self.service_api.get_4k_channel(channel_count=2)
        if not channel:
            pytest.skip("None of the channels were found. Hence Skipping")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
        playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
        vqt_score = self.vision_page.get_mixed_video_quality_score(
            channel_details=channel_details, time_offset=playback_duration, duration=30, sync_window=5, model_type="4K")
        record_property("vmaf_score1", vqt_score)
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])
        if channel[1]:
            self.watchvideo_page.tune_to_channel(channel[1])
            record_property("channel_number", channel[1])
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
            channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
            playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
            vqt_score = self.vision_page.get_mixed_video_quality_score(
                channel_details=channel_details, time_offset=playback_duration, duration=30, sync_window=5,
                model_type="4K")
            record_property("vmaf_score2", vqt_score)
            self.watchvideo_assertions.verify_screen_resolution(self)
            self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[1])
            self.watchvideo_page.tune_to_channel(channel[0])
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
            channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
            playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
            vqt_score = self.vision_page.get_mixed_video_quality_score(
                channel_details=channel_details, time_offset=playback_duration, duration=30, sync_window=5,
                model_type="4K")
            record_property("vmaf_score3", vqt_score)
            self.watchvideo_assertions.verify_screen_resolution(self)
            self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])
            self.vision_page.verify_video_quality_score(vqt_score)

    @pytest.mark.vt_quality_demo
    @pytest.mark.vt_core_feature
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_get_vmaf_score(self, record_property):
        channel_number = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not bool(channel_number):
            pytest.skip("Appropriate channel not found.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(10)
        channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
        playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
        path_to_video = self.vision_page.prepare_videos_full_reference_video_quality_score(
            channel_details, duration=30, time_offset=playback_duration, quality="fullhd_or_less")
        vqt_score = self.vision_page.get_full_reference_video_quality_score(
            path_to_video, sync_window=20, model_type="4K")
        record_property("vqt_score", vqt_score)
        self.vision_page.verify_video_quality_score(vqt_score)

    @pytest.mark.vt_quality_demo
    @pytest.mark.vt_core_feature
    def test_get_vqm_score(self, record_property):
        channel_numbers = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True)
        if bool(channel_numbers) is False:
            pytest.skip("Appropriate channel not found.")
        channel_number = channel_numbers[0][0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(10)
        path_to_video = self.vision_page.prepare_videos_non_reference_video_quality_score(duration=30)
        vqt_score = self.vision_page.get_non_reference_video_quality_score(path_to_video)
        record_property("vqt_score", vqt_score)
        self.vision_page.verify_video_quality_score(vqt_score, vqt_type='mitsu')

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_10_switch_between_UHD_HD_channel(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        hdchannel = self.service_api.get_4k_channel(resolution="hd")
        if not hdchannel:
            pytest.skip("HD channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.tune_to_channel(hdchannel[0])
        record_property("channel_number", hdchannel[0])
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_page.tune_to_channel(channel[0])
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_428_switch_between_UHD_SD_channel(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        sdchannel = self.service_api.get_4k_channel(resolution="sd")
        if not sdchannel:
            pytest.skip("SD channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.tune_to_channel(sdchannel[0])
        record_property("channel_number", sdchannel[0])
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_page.tune_to_channel(channel[0])
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_enable_closed_captioning", "setup_cleanup_disable_closed_captioning")
    def test_FRUM_12_closed_caption_on_4k_channel(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.turn_on_cc(self, ON=False)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_13_switch_audio_track(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_AUDIO_TRACK_CH_NO_10120
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        record_property("channel_number", channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_AUDIO_TRACK, refresh=False)
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_AUDIO_TRACK_OVERLAY_TITLE)
        self.watchvideo_page.select_menu_by_substring(self.menu_labels.LBL_SPANISH)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for managed devices")
    def test_FRUM_4355_switch_between_youtube_UHD_channel(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("UHD channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(180)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.home_page.launch_app_from_GA_from_any_screen(self, self.home_labels.LBL_YOUTUBE)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.voicesearch_page.sent_media_command_with_google_assistant("4k video")
        self.guide_page.wait_for_search_results()
        self.voicesearch_page.sent_media_command_with_google_assistant("Play this video")
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.vision_page.verify_av_playback()
        self.home_page.exit_ott_app_with_back_or_exit_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.watch_video_for(180)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytestrail.case("C13531298")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize(
        "feature, package_type", [(FeAlacarteFeatureList.LINEAR, FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C13531298_IPLinear_widevine_no_audio_during_trickplay(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/13531298
        """
        encrpyted_channellist = self.api.get_encrypted_channel_list()
        no_trickplay_restriction_channellist = self.api.get_channels_with_no_trickplay_restrictions()
        intersection = set(encrpyted_channellist).intersection(no_trickplay_restriction_channellist)
        channel_list = list(intersection)
        if not channel_list:
            pytest.skip("No encrptyed channel found with trickplay")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_IPLINEAR_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(
            self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_NATIVE, feature, FeAlacartePackageTypeList.NATIVE)
        channel_number = random.choice(channel_list)
        self.guide_page.verify_channel(self, channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.vision_page.verify_av_playback()
        self.watchvideo_page.watch_video_for(500)
        self.guide_page.rewind_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)
        self.screen.base.press_playpause()
        self.vision_page.verify_av_playback()
        self.vision_page.verify_audio_state(expected=True)
        self.guide_page.fast_forward_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)

    @pytestrail.case("C13531302")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize(
        "feature, package_type", [(FeAlacarteFeatureList.SOCU, FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C13531302_SoCu_widevine_no_audio_during_trickplay(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/13531302
        """
        socu_channellist = self.api.fetch_good_socu_channels()
        no_trickplay_restriction_channellist = self.api.get_channels_with_no_trickplay_restrictions()
        intersection = set(socu_channellist).intersection(no_trickplay_restriction_channellist)
        channel_list = list(intersection)
        if not channel_list:
            pytest.skip("No SoCu content available with trickplay")
        request.getfixturevalue(self.home_labels.LBL_DRM_PRESERVE_PACKAGE)
        request.getfixturevalue(self.home_labels.LBL_DRM_REMOVE_PACKAGE)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE)
        self.home_assertions.verify_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE)
        self.home_page.relaunch_hydra_app()
        channel_number = random.choice(channel_list)
        self.guide_page.verify_channel(self, channel_number)
        self.guide_page.select_and_watch_program(self, socu=True, open_rec_overlay=False)
        self.watchvideo_assertions.verify_playback_play()
        self.vision_page.verify_av_playback()
        self.watchvideo_page.watch_video_for(500)
        self.guide_page.rewind_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)
        self.screen.base.press_playpause()
        self.vision_page.verify_av_playback()
        self.vision_page.verify_audio_state(expected=True)
        self.guide_page.fast_forward_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)

    @pytestrail.case("C13531303")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize(
        "feature, package_type", [(Settings.mdrm_ndvr_feature(), FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C13531303_nDVR_widevine_no_audio_during_trickplay(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/13531303
        """
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_NDVR_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(
            self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_NATIVE, feature, FeAlacartePackageTypeList.NATIVE)
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.watch_video_for(500)
        self.guide_page.rewind_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)
        self.screen.base.press_playpause()
        self.vision_page.verify_av_playback()
        self.vision_page.verify_audio_state(expected=True)
        self.guide_page.fast_forward_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)

    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize(
        "feature, package_type", [(FeAlacarteFeatureList.VOD, FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C13531311_VOD_widevine_no_audio_during_trickplay(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/13531311
        """
        status, result = self.vod_api.getOffer_vod_without_trickplay_restrictions()
        if result is None:
            pytest.skip("Content without trickplay restriction is not available on VOD catalog.")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_VOD_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(
            self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_NATIVE, feature, FeAlacartePackageTypeList.NATIVE)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.watch_video_for(500)
        self.guide_page.rewind_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)
        self.screen.base.press_playpause()
        self.vision_page.verify_av_playback()
        self.vision_page.verify_audio_state(expected=True)
        self.guide_page.fast_forward_show(self, 2)
        self.vision_page.verify_audio_state(expected=False)

    @pytest.mark.skipif(not Settings.is_cc3(), reason="Audio only feature is supported only on CC3")
    @pytest.mark.vt_core_feature
    def test_12782653_audio_only_channel(self):
        """
        :description:
            Verify audioonly channel
        :testrail:
            https://testrail.tivo.com//index.php?/cases/view/12782653
            https://testrail.tivo.com//index.php?/cases/view/12782654
            https://testrail.tivo.com//index.php?/cases/view/12782649
        """
        audio_only_channel = self.service_api.get_random_audioonly_channel()
        if not audio_only_channel:
            pytest.skip("Audio Only channel is not available")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.enter_channel_number(audio_only_channel[0], confirm=True)
        self.vision_page.verify_playback_area_is_black(expected=True)
        self.vision_page.verify_audio_state(expected=True)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_16_create_onepass_4kcontent(self, record_property):
        channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True, is_preview_offer_needed=True)
        if not channel:
            pytest.skip("Failed to get UHD channels")
        channel_num = self.service_api.map_channel_number_to_currently_airing_offers(
            [channel], self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True), subtitle=True)
        if not channel_num:
            pytest.skip("Failed to get currently airling series")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num[random.randint(0, len(channel_num) - 1)][1])
        self.guide_page.get_live_program_name(self)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0][1])
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0][1])

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_14_trickplay_action_on_4k_content(self, record_property):
        channel_4k = self.service_api.get_4k_channel(socu=True)
        no_trickplay_restriction_channellist = self.api.get_channels_with_no_trickplay_restrictions()
        intersection = set(channel_4k).intersection(no_trickplay_restriction_channellist)
        channel = list(intersection)
        if not channel:
            pytest.skip("No 4k content available without  trickplay restrictions")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])
        # to verify rewind mode
        self.watchvideo_page.watch_video_for(60 * 10)  # build cache for REW modes verification
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.press_ok()  # REW2 mode
        self.vod_page.press_ok()  # REW3 mode
        # trickplay shown
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX3)
        self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])
        # to verify play
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_page.fast_forward_show(self, 3)
        self.guide_page.rewind_show(self, 3)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        # to verify fast forward
        self.watchvideo_page.navigate_to_start_of_video()
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_page.press_ok()  # FF3 mode
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX3)
        self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])
        # to verify play
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete(False)
        self.guide_page.rewind_show(self, 3)
        self.guide_page.fast_forward_show(self, 3)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        # to verify replay
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_replay(self, current_position, key_press=15)
        # to verify advance
        self.watchvideo_page.watch_video_for(10)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_advance_move(self, current_position)
        # to verify go to end
        self.my_shows_page.navigate_to_gotoend_icon(self)
        self.vod_page.press_ok()  # Press 'Go to End' button
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_30seconds_to_end_of_video(value1)
        # to verify start over
        self.my_shows_page.navigate_to_start_over_icon(self)
        self.vod_page.press_ok()  # Press 'Start Over' button
        value2 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_startover_of_the_video(value2)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.skipif("blackmagic" in Settings.vision_tester_hardware(), reason="cannot validate video quality check")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_33_inprogress_4k_recording(self, record_property):
        channel = self.service_api.get_4k_channel(recordable=True)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
        playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
        vqt_score = self.vision_page.get_mixed_video_quality_score(
            channel_details=channel_details, time_offset=playback_duration, duration=30, sync_window=5, model_type="4K")
        record_property("vmaf_score", vqt_score)
        self.vision_page.verify_video_quality_score(vqt_score)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.skipif("blackmagic" in Settings.vision_tester_hardware(), reason="cannot validate video quality check")
    def test_FRUM_17_playback_completed_4k_recording(self, record_property):
        channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True)
        if not channel:
            pytest.skip("Failed to get UHD channels")
        channel_num = self.service_api.map_channel_number_to_currently_airing_offers(
            [channel], self.service_api.channels_with_current_show_start_time(duration=1800, use_cached_grid_row=True))
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num[0][1])
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel_num[0][1])
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0][1])
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0][1])
        channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
        playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
        vqt_score = self.vision_page.get_mixed_video_quality_score(
            channel_details, time_offset=playback_duration, duration=30, sync_window=5, model_type="4K"
        )
        record_property("vmaf_score", vqt_score)
        self.vision_page.verify_video_quality_score(vqt_score)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.skipif("blackmagic" in Settings.vision_tester_hardware(), reason="cannot validate video quality check")
    def test_FRUM_423_playback_4k_FVOD(self, record_property):
        status, result = self.vod_api.get_UHD_entitled_vod_with_duration(type="fvod", minDuration=1200)
        if result is None:
            pytest.skip("4k fvod content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(60)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.watch_video_for(600)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
        playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
        vqt_score = self.vision_page.get_mixed_video_quality_score(
            channel_details=channel_details, time_offset=playback_duration, duration=30, sync_window=5, model_type="4K")
        record_property("vmaf_score", vqt_score)
        self.vision_page.verify_video_quality_score(vqt_score)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_424_playback_4k_SVOD(self):
        status, result = self.vod_api.get_UHD_entitled_vod_with_duration(type="svod", minDuration=1200)
        if result is None:
            pytest.skip("4k svod content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(60)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.watch_video_for(600)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_426_playback_4k_VOD_long_duration(self):
        status, result1 = self.vod_api.get_UHD_entitled_vod_with_duration(type="svod", minDuration=3000)
        status, result2 = self.vod_api.get_UHD_entitled_vod_with_duration(type="fvod", minDuration=3000)
        status, result3 = self.vod_api.get_UHD_entitled_vod_with_duration(type="tvod", minDuration=3000)
        if all(val is None for val in [result1, result2, result3]):
            pytest.skip("4k long duration content is not available on VOD catlog.")
        results = [result1, result2, result3]
        for result in results:
            if result:
                self.home_page.back_to_home_short()
                self.vod_page.goto_vodoffer_program_screen(self, result)
                self.vod_page.play_any_playable_vod_content(self, result)
                self.watchvideo_page.watch_video_for(60)
                self.vod_assertions.verify_vod_playback(self)
                self.vision_page.verify_av_playback()
                self.watchvideo_assertions.verify_screen_resolution(self)
                self.watchvideo_page.watch_video_for(1800)
                self.vod_assertions.verify_vod_playback(self)
                self.vision_page.verify_av_playback()
                self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_30012_toggle_4k_and_non4k_recording(self, record_property):
        uhdchannel = self.service_api.get_4k_channel(recordable=True)
        if not uhdchannel:
            pytest.skip("UHD channel not available. Hence skipping.")
        hdchannel = self.service_api.get_4k_channel(resolution="hd", recordable=True)
        if not hdchannel:
            pytest.skip("HD channel not available. hence skipping.")
        uhd_show = self.api.record_currently_airing_shows(1, includeChannelNumbers=uhdchannel)[0][0]
        hd_show = self.api.record_currently_airing_shows(1, includeChannelNumbers=hdchannel)[0][0]
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(uhd_show)
        self.my_shows_page.select_show(uhd_show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(hd_show)
        self.my_shows_page.select_show(hd_show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution_not_uhd(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(uhd_show)
        self.my_shows_page.select_show(uhd_show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_28_validate_UHD_resolution_with_required_bandwidth(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_page.show_network_osd()
        self.watchvideo_assertions.verify_uhd_streaming_bandwidth(self)
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_25_toggle_4k_inprogress_recording_and_vod(self, record_property):
        channel = self.service_api.get_4k_channel(recordable=True)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        status, result = self.vod_api.get_UHD_entitled_vod_with_duration()
        if result is None:
            pytest.skip("4k vod content is not available on VOD catlog.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(60)
        self.watchvideo_page.open_olg()
        self.guide_page.create_live_recording()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(60)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.skipif("blackmagic" in Settings.vision_tester_hardware(), reason="cannot validate video quality check")
    def test_FRUM_6_4k_socu_playback(self, record_property):
        channel = self.service_api.get_4k_channel(socu=True)
        if not channel:
            pytest.skip("UHD channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        record_property("channel_number", channel[0])
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.home_assertions.verify_socu_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])
        channel_details = self.watchvideo_page.get_playback_screen_channel_streaming_url_drm_details()
        playback_duration = self.guide_page.get_trickplay_current_position_in_sec()
        vqt_score = self.vision_page.get_mixed_video_quality_score(
            channel_details=channel_details, time_offset=playback_duration, duration=30, sync_window=5, model_type="4K")
        record_property("vmaf_score", vqt_score)
        self.vision_page.verify_video_quality_score(vqt_score)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.vt_core_feature
    @pytest.mark.usefixtures('setup_enable_top_right_video_window_on_home')
    def test_FRUM_11_4k_video_window_playback(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.home_page.back_to_home_short()
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_pig_video_playback()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_31_verify_60_frames_on_livetv_playback(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_60_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_frame_rate(self, self.watchvideo_labels.LBL_FRAME_RATE_60)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_35_pause_resume_4k_playback(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback(expected=False)
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_7_playback_4k_VOD(self):
        status, result = self.vod_api.get_UHD_entitled_vod_with_duration()
        if result is None:
            pytest.skip("4k vod content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(60)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_22_verify_24_frames_on_livetv_playback(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_24_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(60)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_frame_rate(self, self.watchvideo_labels.LBL_FRAME_RATE_24)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_421_toggle_4k_live_and_vod(self, record_property):
        channel = self.service_api.get_4k_channel()
        status, result = self.vod_api.get_UHD_entitled_vod_with_duration()
        if result is None:
            pytest.skip("4k vod content is not available on VOD catlog.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_422_toggle_4k_live_and_recording(self, record_property):
        uhdchannel = self.service_api.get_4k_channel(recordable=True)
        if not uhdchannel:
            pytest.skip("UHD channel not available. Hence skipping.")
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(uhdchannel[0])
        uhd_show = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel[0])
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(uhd_show)
        self.my_shows_page.select_show(uhd_show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_FRUM_29_verify_30_frames_on_livetv_playback(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_30_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_frame_rate(self, self.watchvideo_labels.LBL_FRAME_RATE_30)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_14_trickplay_action_on_4k_ndvr_content(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_30_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        # to verify rewind mode
        self.watchvideo_page.watch_video_for(60 * 30)  # build cache for REW modes verification
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.press_ok()  # REW2 mode
        self.vod_page.press_ok()  # REW3 mode
        # trickplay shown
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX3)
        playback_status = self.watchvideo_page.get_playback_status()
        if playback_status != self.vod_labels.LBL_PLAY:
            self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TWENTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        # to verify play
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_page.fast_forward_show(self, 3)
        self.guide_page.rewind_show(self, 3)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        # to verify fast forward
        self.watchvideo_page.navigate_to_start_of_video()
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_page.press_ok()  # FF3 mode
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX3)
        self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TWENTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        # to verify replay
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_replay(self, current_position, key_press=15)
        # to verify advance
        self.watchvideo_page.watch_video_for(10)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_advance_move(self, current_position)
        # to verify go to end
        self.my_shows_page.navigate_to_gotoend_icon(self, exact_icon_match=True)
        self.vod_page.press_ok()  # Press 'Go to End' button
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_30seconds_to_end_of_video(value1)
        # to verify play
        self.guide_page.rewind_show(self, 3)
        self.guide_page.fast_forward_show(self, 3)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        # to verify start over
        self.my_shows_page.navigate_to_start_over_icon(self)
        self.vod_page.press_ok()  # Press 'Start Over' button
        value2 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_startover_of_the_video(value2)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_FRUM_14_trickplay_action_on_4k_socu_content(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_30_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(30)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        # to verify rewind mode
        self.watchvideo_page.watch_video_for(60 * 30)  # build cache for REW modes verification
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.press_ok()  # REW2 mode
        self.vod_page.press_ok()  # REW3 mode
        # trickplay shown
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX3)
        playback_status = self.watchvideo_page.get_playback_status()
        if playback_status != self.vod_labels.LBL_PLAY:
            self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TWENTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        # to verify play
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_page.fast_forward_show(self, 3)
        self.guide_page.rewind_show(self, 3)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        # to verify fast forward
        self.watchvideo_page.navigate_to_start_of_video()
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_page.press_ok()  # FF3 mode
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX3)
        self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TWENTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        # to verify replay
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_replay(self, current_position, key_press=15)
        # to verify advance
        self.watchvideo_page.watch_video_for(10)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_advance_move(self, current_position)
        # to verify go to end
        self.my_shows_page.navigate_to_gotoend_icon(self, exact_icon_match=True)
        self.vod_page.press_ok()  # Press 'Go to End' button
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_30seconds_to_end_of_video(value1)
        # to verify play
        self.guide_page.rewind_show(self, 3)
        self.guide_page.fast_forward_show(self, 3)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        # to verify start over
        self.my_shows_page.navigate_to_start_over_icon(self)
        self.vod_page.press_ok()  # Press 'Start Over' button
        value2 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_startover_of_the_video(value2)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.skipif(not Settings.is_cc5(), reason="VOD CC/subtitle with different language available only for cc5 MSO")
    @pytest.mark.usefixtures("setup_enable_closed_captioning", "setup_cleanup_disable_closed_captioning")
    def test_FRUM_9_switch_different_closedcaption_on_4kcontent(self):
        offerId = self.vod_labels.LBL_VTP_VOD_OFFERID
        self.home_page.back_to_home_short()
        self.vod_api.navigate_to_vod_offer(offerId)
        self.guide_page.wait_for_screen_ready()
        self.vod_page.select_watch_now(self)
        self.watchvideo_page.watch_video_for(60)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.navigate_by_strip(self.watchvideo_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.menu_page.select_menu_items(self.vod_labels.LBL_CC_ENGLISH)
        self.watchvideo_page.watch_video_for(10)
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.navigate_by_strip(self.watchvideo_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.menu_page.select_menu_items(self.vod_labels.LBL_CC_FRENCH)
        self.watchvideo_page.watch_video_for(10)
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.vt_quality_demo
    @pytest.mark.vt_core_feature
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_live_vqat(self, record_property):
        channel_numbers = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True)
        if not channel_numbers:
            pytest.skip("No workable live channel(mind)")
        channel_number = channel_numbers[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel_number)
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.live_stream_video_assessment(vqat_session_duration=600)

    @pytest.mark.frumos_18
    @pytest.mark.longevity_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_4k_live_long_streaming_vqat(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_AUDIO_TRACK_CH_NO_10120
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel)
        self.vision_page.live_stream_video_assessment(vqat_session_duration=10800, test_chunk_duration=30)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel)

    @pytest.mark.frumos_18
    @pytest.mark.longevity_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_long_duration_audio_video_playback(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_30_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.live_stream_video_assessment(vqat_session_duration=3600 * 6)

    @pytest.mark.frumos_18
    @pytest.mark.longevity_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.parametrize(
        "counter", [LongevityConstants.MED_COUNTER])
    def test_4k_live_longevity_temperature(self, counter, record_property):
        channel = self.watchvideo_labels.LBL_4K_30_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", channel)
        for count in range(counter):
            self.watchvideo_page.watch_video_for(30)
            self.vision_page.verify_av_playback()
            self.watchvideo_assertions.verify_screen_resolution(self)
            self.watchvideo_page.watch_video_for(60 * 30)
            self.watchvideo_page.navigate_to_start_of_video()
            self.guide_page.fast_forward_show(self, 3)
            self.guide_page.rewind_show(self, 3)
            self.guide_assertions.verify_play_normal()
            self.watchvideo_page.watch_video_for(10)
            self.vision_page.verify_av_playback()
            # to verify replay
            current_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.my_shows_page.validate_replay(self, current_position, key_press=15)
            # to verify advance
            self.watchvideo_page.watch_video_for(10)
            current_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.my_shows_page.validate_advance_move(self, current_position)
            # to verify go to end
            self.my_shows_page.navigate_to_gotoend_icon(self, exact_icon_match=True)
            self.vod_page.press_ok()  # Press 'Go to End' button
            value1 = self.guide_page.get_trickplay_current_position_in_sec()
            self.vod_assertions.verify_30seconds_to_end_of_video(value1)
            # to verify start over
            self.my_shows_page.navigate_to_start_over_icon(self)
            self.vod_page.press_ok()  # Press 'Start Over' button
            value2 = self.guide_page.get_trickplay_current_position_in_sec()
            self.vod_assertions.verify_startover_of_the_video(value2)
            self.system_page.validate_temperature()

    @pytest.mark.frumos_18
    @pytest.mark.longevity_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_4k_socu_long_streaming_vqat(self, record_property):
        channel = self.service_api.get_4k_channel(channel_count=-1, socu=True)
        if not channel:
            pytest.skip("No UHD channels found")
        channel_num = self.service_api.map_channel_number_to_currently_airing_offers(
            [channel], self.service_api.channels_with_current_show_start_time(duration=10800, use_cached_grid_row=True))
        if not channel_num:
            pytest.skip("Channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel_num[0][1])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        record_property("channel_number", channel_num[0][1])
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0])
        self.vision_page.live_stream_video_assessment(vqat_session_duration=9000, test_chunk_duration=30)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0])

    @pytest.mark.frumos_18
    @pytest.mark.longevity_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_4k_ndvr_long_streaming_vqat(self, record_property):
        channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True)
        if not channel:
            pytest.skip("No UHD channels found")
        channel_num = self.service_api.map_channel_number_to_currently_airing_offers(
            [channel], self.service_api.channels_with_current_show_start_time(duration=10800, use_cached_grid_row=True))
        if not channel_num:
            pytest.skip("Channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num[0][1])
        record_property("channel_number", channel_num[0][1])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0][1])
        self.vision_page.live_stream_video_assessment(vqat_session_duration=9000, test_chunk_duration=30)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_num[0][1])

    @pytest.mark.frumos_18
    @pytest.mark.longevity_4k
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_4k_vod_long_streaming_vqat(self):
        status, result = self.vod_api.get_UHD_entitled_vod_with_duration(type="fvod", minDuration=3600)
        if result is None:
            pytest.skip("4k fvod long duration content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vod_assertions.verify_vod_playback(self)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.vision_page.live_stream_video_assessment(vqat_session_duration=3600, test_chunk_duration=30)

    @pytest.mark.e2e
    @pytest.mark.witbe_e2ecase
    @pytest.mark.timeout(Settings.timeout_mid)
    def test_74379296_verify_livetv_for_two_airing_shows(self):
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True)
        if channel is None:
            pytest.skip("Working channel is not available")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.wait_for_screen_ready()
        # watch to the end first show
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.guide_page.wait_and_watch_until_end_of_program_livetv(self)
        # verify if the second show has started playing
        self.guide_page.verify_episode_panel_and_playback_of_upcoming_episode(self)
        self.vision_page.verify_av_playback()
        # watch to the end second show
        self.guide_page.wait_and_watch_until_end_of_program_livetv(self)

    @pytest.mark.witbe_e2ecase
    @pytest.mark.e2e
    @pytest.mark.usefixtures("ensure_livetv_on_realtime")
    def test_74209771_verify_rewind_mode_for_livetv_show(self):
        self.vision_page.verify_av_playback()
        self.watchvideo_page.watch_video_for(300)
        initial_position = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.navigate_to_start_of_video()
        new_position = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(initial_position, new_position, rewind=True)
        self.vision_page.verify_av_playback()

    @pytest.mark.e2e
    @pytest.mark.witbe_e2ecase
    @pytest.mark.usefixtures("ensure_livetv_on_realtime")
    def test_74362881_verify_pause_fastforward_modes_for_livetv_show(self):
        self.vision_page.verify_av_playback()
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_page.press_pause_in_visual_trickplay()
        playback_status = self.watchvideo_page.get_playback_status()
        assert playback_status == "PAUSE", f"Playback status expected PAUSE, actual {playback_status}"
        self.watchvideo_page.watch_video_for(300)
        initial_position = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.navigate_to_end_of_video()
        new_position = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(initial_position, new_position, rewind=False)
        self.vision_page.verify_av_playback()

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.witbe_e2ecase
    def test_74395711_create_onepass_for_ndvr_program(self):
        """
        TC 74395711 - create onepass for nDVR program and watch till end
        """
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(
                channel_count=-1, filter_channel=True, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True),
            genre="series", linear_only=True, count=1)
        if not channel:
            pytest.skip("Recordable episodic channels are not found.")
        self.home_page.back_to_home_short()
        # goto Guide and verify that nDVR series actually airing
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][1])
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        # go to Search, find airing program and create OnePass
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program)
        self.vod_page.check_onepass_SVOD(self, record=self.guide_labels.LBL_EVERYTHING)
        # go to MyShows, find and play recorded program
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        # watch to the end and complete watching
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.my_shows_assertions.wait_and_verify_delete_recording_overlay()
        self.my_shows_page.select_keep_option(self)

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.witbe_e2ecase
    @pytest.mark.e2e
    def test_verify_youtube_launch_and_livetv_background_test(self):
        """
        https://jira.xperi.com/browse/FRUM-108271
        To verify ability to playback an Youtube
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.open_youtube()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.vision_page.verify_av_playback()
        self.home_page.back_to_home_short()
        self.menu_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.xray("FRUM-108470")
    @pytest.mark.e2e
    def test_e2e_358263_verify_trickplay_modes_for_socu_offer(self):
        channel_number = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)[0]
        if not channel_number:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut(self.home_labels.LBL_GUIDE_SHORTCUT)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 10)
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_page.playback_and_verify_trickplay_action(self, forward=True, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, forward=True, speed=2, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, forward=True, speed=3, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, playpause=True, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, rewind=True, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, rewind=True, speed=2, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, rewind=True, speed=3, socu=False)

    @pytest.mark.e2e
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_74367571_verify_rewind_fastforward_modes_for_ndvr_recording(self):
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(180)
        self.vision_page.verify_av_playback()
        initial_position = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.navigate_to_start_of_video()
        new_position = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(initial_position, new_position, rewind=True)
        self.vision_page.verify_av_playback()
        initial_position = self.guide_page.get_trickplay_current_position_in_sec()
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        self.watchvideo_page.watch_video_for(5)
        self.vod_page.press_play_pause_button()
        new_position = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(initial_position, new_position, rewind=False)
        self.vision_page.verify_av_playback()

    @pytest.mark.yukon
    @pytest.mark.notapplicable(Settings.yukon_server == "localhost")
    @pytest.mark.usefixtures("setup_cleanup_remove_playback_source")
    def test_x99999_demo_yukon_vt(self, record_property):
        """
        Demo VT isolated env based on Yukon Server
        """
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        if not channel_number:
            pytest.skip("Channel not available. Hence skipping.")
        self.home_page.go_to_guide(self)
        # video_request = {"purpose": "no_throttling", "asset": "asset1"}
        yukon_url = self.watchvideo_page.get_yukon_url(purpose="no_throttling", asset="asset1")
        self.guide_page.set_playback_source(yukon_url)
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        path_to_video = self.vision_page.prepare_videos_full_reference_vqa_m3u8(yukon_url, duration=30)
        vqt_score = self.vision_page.get_full_reference_video_quality_score(path_to_video,
                                                                            sync_window=20,
                                                                            model_type="4K",
                                                                            )
        record_property("vqt_score", vqt_score)
        self.vision_page.verify_video_quality_score(vqt_score)

    @pytest.mark.frumos_19
    @pytest.mark.acceptance_4k
    def test_FRUM_121928_switch_between_HDR10_non_HDR10_channel(self, record_property):
        """
        FRUM_121928: Switch between HDR10 and non-HDR10 assets.
        This case has been developed specifically for HDR10 Testing.
        """
        hdr10_channel = self.watchvideo_labels.LBL_4K_HDR10_CH_NO
        non_hdr10_channel = self.watchvideo_labels.LBL_4K_60_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(hdr10_channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        record_property("channel_number", hdr10_channel)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.tune_to_channel(non_hdr10_channel)
        record_property("channel_number", non_hdr10_channel)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.watchvideo_page.tune_to_channel(hdr10_channel)
        record_property("channel_number", hdr10_channel)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_19
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_121928_toggle_HDR10_non_HDR10_recording(self, record_property):
        """
        FRUM_121928: Switch between HDR10 and non-HDR10 assets.
        This case has been developed specifically for HDR10 Testing.
        """
        hdr10_channel = self.watchvideo_labels.LBL_4K_HDR10_CH_NO
        non_hdr10_channel = self.watchvideo_labels.LBL_4K_60_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(hdr10_channel)
        hdr10_show = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.enter_channel_number(non_hdr10_channel)
        non_hdr10_show = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(hdr10_show)
        self.my_shows_page.select_show(hdr10_show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(non_hdr10_show)
        self.my_shows_page.select_show(non_hdr10_show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(hdr10_show)
        self.my_shows_page.select_show(hdr10_show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_19
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_22_verify_24_frames_on_ndvr_playback(self, record_property):
        """
        FRUM_22_ndvr: To verify 24fps recording playback
        """
        channel = self.watchvideo_labels.LBL_4K_24_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        record_property("channel_number", channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_frame_rate(self, self.watchvideo_labels.LBL_FRAME_RATE_24)

    @pytest.mark.frumos_19
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_31_verify_60_frames_on_ndvr_playback(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_60_FPS_CH_NO
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        record_property("channel_number", channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_frame_rate(self, self.watchvideo_labels.LBL_FRAME_RATE_60)

    @pytest.mark.frumos_19
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_35_pause_resume_on_ndvr_4k_playback(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        record_property("channel_number", channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback(expected=False)
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.watch_video_for(10)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_19
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_enable_closed_captioning", "setup_cleanup_disable_closed_captioning")
    def test_FRUM_12_closed_caption_on_ndvr_4k_channel(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        record_property("channel_number", channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.turn_on_cc(self, ON=False)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel[0])

    @pytest.mark.frumos_19
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_144992_switch_audio_track_in_ndvr(self, record_property):
        channel = self.watchvideo_labels.LBL_4K_AUDIO_TRACK_CH_NO_10120
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel)
        record_property("channel_number", channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_AUDIO_TRACK, refresh=False)
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_AUDIO_TRACK_OVERLAY_TITLE)
        self.watchvideo_page.select_menu_by_substring(self.menu_labels.LBL_SPANISH)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.frumos_19
    @pytest.mark.acceptance_4k
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures('setup_enable_top_right_video_window_on_home')
    def test_FRUM_144993_ndvr_4k_video_window_playback(self, record_property):
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("4K channel not available. hence skipping.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        program = self.guide_page.get_live_program_name(self)
        record_property("channel_number", channel[0])
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.home_page.back_to_home_short()
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_pig_video_playback()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.vision_page.verify_av_playback()
        self.watchvideo_assertions.verify_screen_resolution(self)
