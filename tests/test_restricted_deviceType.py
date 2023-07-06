import time
import random
import json

import pytest

from set_top_box.test_settings import Settings
import mind_api.middle_mind.field as field
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, HydraBranches, FeaturesList
from set_top_box.client_api.home.conftest import cleanup_package_names_native,\
    preserve_initial_package_state, remove_packages_if_present_before_test, fill_internal_storage_by_installing_apps, \
    free_up_internal_memory_by_uninstalling, restore_mind_availability
from set_top_box.client_api.watchvideo.conftest import setup_liveTv, setup_cleanup_tivo_plus_channels, \
    setup_cleanup_tivo_plus_channels_first_launch, setup_cleanup_inactivity_timeout, reset_bandwidth_rule
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_bind_hsn, setup_cleanup_pluto_tv_app
from set_top_box.client_api.Menu.conftest import disable_parental_controls, setup_enable_closed_captioning
from set_top_box.client_api.Menu.conftest import \
    setup_disable_closed_captioning, setup_cleanup_disable_closed_captioning, disable_video_window
from set_top_box.client_api.Menu.conftest import setup_cleanup_parental_and_purchase_controls, cleanup_favorite_channels, \
    enable_video_providers, setup_cleanup_remove_playback_source
from set_top_box.client_api.guide.conftest import toggle_mind_availability


@pytest.mark.usefixtures("setup_liveTv")
@pytest.mark.usefixtures("is_service_livetv_alive")
@pytest.mark.livetv
@pytest.mark.timeout(Settings.timeout)
class TestRestrictedDeviceType(object):

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_linear_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_31978_linear_playback_restricted_device_type_check_with_mso_true(self):
        """
        Restricted device type check condition
         if (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                Then Playback will be decide based on MOS instructions
                    if no MSO instructions
                        then playback start without any error
                    else:
                        playback will be restricted based on MSO instructions
                            if no mso restrictions
                                then playback will start

        Xray link:https://jira.xperi.com/browse/FRUM-31978

            TODO: checkDevcieTypeWithMso True,  then playback will decide by sessionManager through sessionCreate
            TODO: sessionCreate supporting API needs to create for this test case else
            TODO: Need to put log observer to see the session manager response in adb logs

        """
        channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=True,
            playback_type=field.linear_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.go_to_home_screen(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.press_enter(self)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_linear_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_31980_linear_playback_restricted_device_type_check_with_mso_false(self):
        """
         Restricted device type check condition
          if (restrictedDeviceType True) and  (checkDeviceTypeWithMso False)
                 then playback failed with V414 error
          Xray link: https://jira.xperi.com/browse/FRUM-31980
         """
        channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=False,
            playback_type=field.linear_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.go_to_home_screen(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.press_enter(self)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_linear_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_31983_linear_playback_restricted_device_type_check_with_mso_blank(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
             and (restrictedDeviceType True) and (checkDeviceTypeWithMso False)
                 then playback failed with V414 error
          Xray link: https://jira.xperi.com/browse/FRUM-31983
         """
        channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=None,
            playback_type=field.linear_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.go_to_home_screen(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.press_enter(self)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_linear_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_31995_linear_playback_not_restricted_device_type_check_with_mso_true(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback will start
         Xray link: https://jira.xperi.com/browse/FRUM-31995
         """
        channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=True,
            playback_type=field.linear_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.go_to_home_screen(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.press_enter(self)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_linear_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_31996_linear_playback_not_restricted_device_type_check_with_mso_false(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback start
          Xray link: https://jira.xperi.com/browse/FRUM-31996
         """
        channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=False,
            playback_type=field.linear_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.go_to_home_screen(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.press_enter(self)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_linear_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_31997_linear_playback_not_restricted_device_type_check_with_mso_blank(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
             (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback start
          Xray link: https://jira.xperi.com/browse/FRUM-31997
         """
        channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=None,
            playback_type=field.linear_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.go_to_home_screen(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.press_enter(self)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_start_over_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32065_start_over_playback_restricted_device_type_check_with_mso_true(self):
        """
        Restricted device type check condition
        Start over and catch up has the less restriction rules so if device is restricted and if either of one
        playback(start over or catch up) has checkDeviceTypeWithMso enable so it will check the MSO restrictions instead
        of blocking

        if (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                Then Playback will be decide based on MOS instructions
                    if no MSO instructions
                        then playback start without any error
                    else:
                        playback will be restricted based on MSO instructions
                        playback failed with V414 error

            https://jira.xperi.com/browse/FRUM-32065
            https://jira.xperi.com/browse/FRUM-32066 test case is not covered

            TODO: checkDevcieTypeWithMso True,  then playback will decide by sessionManager through sessionCreate
            TODO: sessionCreate supporting API needs to create for this test case.

        """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=True,
            playback_type=field.start_over_streaming_restrictions)

        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))

        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.go_to_home_screen(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item, playback_check=False)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_start_over_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32067_start_over_playback_restricted_device_type_check_with_mso_false(self):
        """
        Restricted device type check condition
         if
             (restrictedDeviceType True) and (checkDeviceTypeWithMso False)
                then playback failed with V414 error
                https://jira.xperi.com/browse/FRUM-32067
                https://jira.xperi.com/browse/FRUM-32068 test case is not covered
        """

        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=False,
            playback_type=field.start_over_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))

        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item, playback_check=False)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_start_over_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32069_start_over_playback_restricted_device_type_check_with_mso_blank(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback failed with V414 error
                 https://jira.xperi.com/browse/FRUM-32069
                 https://jira.xperi.com/browse/FRUM-32070 test case is not covered
         """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=None,
            playback_type=field.start_over_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item, playback_check=False)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_start_over_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32971_start_over_playback_not_restricted_device_type_check_with_mso_true(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback start
                 https://jira.xperi.com/browse/FRUM-32071
                 https://jira.xperi.com/browse/FRUM-32072 test case is not covered
         """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=True,
            playback_type=field.start_over_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item, playback_check=True)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_start_over_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32073_start_over_playback_not_restricted_device_type_check_with_mso_false(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback start
             https://jira.xperi.com/browse/FRUM-32073
             https://jira.xperi.com/browse/FRUM-32074 test case is not covered
         """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=False,
            playback_type=field.start_over_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item, playback_check=True)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_start_over_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32075_start_over_playback_not_restricted_device_type_check_with_mso_blank(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback start
            https://jira.xperi.com/browse/FRUM-32075
            https://jira.xperi.com/browse/FRUM-32076 test case is not covered
         """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=None,
            playback_type=field.start_over_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item, playback_check=True)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_catch_up_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32977_catch_up_playback_restricted_device_type_check_with_mso_true(self):
        """
        Restricted device type check condition
        Start over and catch up has the less restriction rules so if device is restricted and if either of one
        playback(start over or catch up) has checkDeviceTypeWithMso enable so it will check the MSO restrictions instead
        of blocking

        if (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                Then Playback will be decide based on MOS instructions
                    if no MSO instructions
                        then playback start without any error
                    else:
                        playback will be restricted based on MSO instructions
                        playback failed with V414 error

            https://jira.xperi.com/browse/FRUM-32077
            https://jira.xperi.com/browse/FRUM-32086 test case is not covered

            TODO: checkDevcieTypeWithMso True,  then playback will decide by sessionManager through sessionCreate
            TODO: sessionCreate supporting API needs to create for this test case.

        """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=True,
            playback_type=field.catchup_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_guide_next_page()
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title, playback_check=False)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_catch_up_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32087_catch_up_playback_restricted_device_type_check_with_mso_false(self):
        """
        Restricted device type check condition
         if
             (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                then playback failed with V414 error

        https://jira.xperi.com/browse/FRUM-32087
        https://jira.xperi.com/browse/FRUM-32088 test case is not covered

        """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=False,
            playback_type=field.catchup_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_guide_next_page()
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title, playback_check=False)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_catch_up_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32089_catch_up_playback_restricted_device_type_check_with_mso_blank(self):
        """
        Restricted device type check condition
         if
             (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                then playback failed with V414 error

        https://jira.xperi.com/browse/FRUM-32089
        https://jira.xperi.com/browse/FRUM-32090  test case is not covered

        """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=True, check_device_type_with_mso=None,
            playback_type=field.catchup_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_guide_next_page()
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title, playback_check=False)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_catch_up_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32091_catch_up_playback_not_restricted_device_type_check_with_mso_true(self):
        """
        Restricted device type check condition
         if
             (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                then playback start

        https://jira.xperi.com/browse/FRUM-32091
        https://jira.xperi.com/browse/FRUM-32093 test case is not covered

        """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=True,
            playback_type=field.catchup_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_guide_next_page()
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title, playback_check=False)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_catch_up_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32094_catch_up_playback_not_restricted_device_type_check_with_mso_false(self):
        """
        Restricted device type check condition
         if
             (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                then playback start
        https://jira.xperi.com/browse/FRUM-32094
        https://jira.xperi.com/browse/FRUM-32095 test case is not covered
        """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=False,
            playback_type=field.catchup_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_guide_next_page()
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title, playback_check=True)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_catch_up_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32096_catch_up_playback_not_restricted_device_type_check_with_mso_blank(self):
        """
        Restricted device type check condition
         if
             (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                then playback start

        https://jira.xperi.com/browse/FRUM-32096
        https://jira.xperi.com/browse/FRUM-32097 test case is not covered
        """
        restricted_channels = self.api.get_check_device_type_with_mso_and_restricted_device_type_channel_numbers(
            restricted_device_type=False, check_device_type_with_mso=None,
            playback_type=field.catchup_streaming_restrictions)
        socu_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                   channel_count=100,
                                                                                   filter_channel=True)
        channels = list(set(restricted_channels) & set(socu_channels))
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = channels[0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel_number)
        self.guide_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_guide_next_page()
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title, playback_check=True)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.per_program_device_restrictions_ndvr_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32021_ndvr_playback_restricted_device_type_check_with_mso_true(self):
        """
        Restricted device type check condition
         if (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                Then Playback will be decide based on MOS instructions
                    if no MSO instructions
                        then playback start without any error
                    else:
                        playback will be restricted based on MSO instructions
                            if no mso restrictions
                                then playback will start

        Xray link: https://jira.xperi.com/browse/FRUM-32021

            TODO: checkDevcieTypeWithMso True,  then playback will decide by sessionManager through sessionCreate
            TODO: sessionCreate supporting API needs to create for this test case else
            TODO: Need to put log observer to see the session manager response in adb logs

        """
        channels = self.service_api.get_recordable_channel_with_device_and_mso_restricted_channels(
            restricted_device_type=True, check_device_type_with_mso=True,
            playback_type=field.ndvr_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = random.choice(channels)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.per_program_device_restrictions_ndvr_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32022_ndvr_playback_restricted_device_type_check_with_mso_false(self):
        """

         Restricted device type check condition
          if (restrictedDeviceType True) and  (checkDeviceTypeWithMso False)
                 then playback failed with V414 error
          Xray link: https://jira.xperi.com/browse/FRUM-32022

        """
        channels = self.service_api.get_recordable_channel_with_device_and_mso_restricted_channels(
            restricted_device_type=True, check_device_type_with_mso=False,
            playback_type=field.ndvr_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = random.choice(channels)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.per_program_device_restrictions_ndvr_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32023_ndvr_playback_restricted_device_type_check_with_mso_none(self):
        """

         Restricted device type check condition
          if (restrictedDeviceType True) and  (checkDeviceTypeWithMso False)
                 then playback failed with V414 error
          Xray link: https://jira.xperi.com/browse/FRUM-32023

        """
        channels = self.service_api.get_recordable_channel_with_device_and_mso_restricted_channels(
            restricted_device_type=True, check_device_type_with_mso=None,
            playback_type=field.ndvr_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = random.choice(channels)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.watchvideo_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.per_program_device_restrictions_ndvr_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32026_ndvr_playback_not_restricted_device_type_check_with_mso_true(self):
        """
         Restricted device type check condition
          if (restrictedDeviceType False) and  (checkDeviceTypeWithMso True)
                 then playback start
          Xray link: https://jira.xperi.com/browse/FRUM-32026

        """
        channels = self.service_api.get_recordable_channel_with_device_and_mso_restricted_channels(
            restricted_device_type=False, check_device_type_with_mso=True,
            playback_type=field.ndvr_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = random.choice(channels)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.per_program_device_restrictions_ndvr_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32027_ndvr_playback_not_restricted_device_type_check_with_mso_false(self):
        """
         Restricted device type check condition
          if (restrictedDeviceType False) and  (checkDeviceTypeWithMso False)
                 then playback start
          Xray link: https://jira.xperi.com/browse/FRUM-32027

        """
        channels = self.service_api.get_recordable_channel_with_device_and_mso_restricted_channels(
            restricted_device_type=False, check_device_type_with_mso=False,
            playback_type=field.ndvr_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = random.choice(channels)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.per_program_device_restrictions_ndvr_playback
    @pytest.mark.per_program_device_restrictions
    def test_frum_32041_ndvr_playback_not_restricted_device_type_check_with_mso_none(self):
        """
         Restricted device type check condition
          if (restrictedDeviceType False) and  (checkDeviceTypeWithMso False)
                 then playback start
          Xray link: https://jira.xperi.com/browse/FRUM-32041

        """
        channels = self.service_api.get_recordable_channel_with_device_and_mso_restricted_channels(
            restricted_device_type=False, check_device_type_with_mso=None,
            playback_type=field.ndvr_streaming_restrictions)
        if not channels:
            pytest.skip("Appropriate channel not found.")
        channel_number = random.choice(channels)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.watchvideo_assertions.verify_playback_play()
