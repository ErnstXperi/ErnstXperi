"""
Created on Aug 1, 2017

@author: acernat
"""

import requests
import json
import random
from datetime import timedelta
import time
import re

import pytest

from tools.logger.logger import Logger
from set_top_box.client_api.voice_search.conftest import *
from set_top_box.conf_constants import BodyConfigFeatures, DeviceInfoStoreFeatures, FeaturesList, \
    NotificationSendReqTypes, RemoteCommands
from set_top_box.client_api.home.conftest import setup_cleanup_return_initial_feature_state
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings
from set_top_box.client_api.Menu.conftest import disable_parental_controls, disable_video_providers, \
    enable_video_providers
from pytest_testrail.plugin import pytestrail
from set_top_box.conf_constants import HydraBranches


@pytest.mark.voicesearch
@pytest.mark.notapplicable(Settings.is_devhost(), "There's no Google Assistant on dev host")
@pytest.mark.usefixtures("get_uiautomator_dump")
@pytest.mark.usefixtures("setup_voice_google_assistant")
@pytest.mark.timeout(Settings.timeout)
class TestVoiceSearch(object):
    __log = Logger(__name__)

    @pytest.mark.ibc
    # @pytest.mark.timeout(Settings.timeout)
    def test_329956_voice_search_call(self):
        """
        Make sure voice search URL is responding with status 200
        :return:
        """
        search_text = ["Tom Hanks movies", "James Bond, Sean Connery", "Comedy movies", "Drama", "ESPN", "CNN",
                       "tune to cbs", "tune to abc", "tune to nbc", "Showtime", "HBO",
                       "Tune to ZEETV", "Settings", "Home", "On Demand", "Latest Movies", "Discovery Channel",
                       "Show me Guide",
                       "Show me My Shows", "Starz channel", "Science Channel", "Channel 350", "Tune to channel 305",
                       "Tom Hanks",
                       "Brad Pitt", "Kungfu Panda"]

        # Prod

        for stext in search_text:
            url = "https://janus-prod-nlu.digitalsmiths.net/nlu/tivo-nlu?version=5.1&userId=int:050001E6D37BB673" \
                  "&deviceId=int:0500017608FF3775&locale=en-US&utcOffset=-0700&w=" + stext + "&limit=20"

            # staging
            # url = "https://janus-staging-nlu.digitalsmiths.net/nlu/tivo-nlu?custid=hydra&" \
            #      "version=5.0&userId=int:050001FD77913687&deviceId=int:0500011CD4998106&locale=en-US&utcOffset=-0700&w=What%27s%20on%20TV%20Tonight&limit=20"
            self.__log.info(url)
            resp_json = requests.get(url)
            resp = json.loads(resp_json.content)
            self.__log.info(resp)
            if resp['status'] != "200":
                raise AssertionError('voice search URL is responding with status ' + resp['status'])

    # === C2C - Search Feature - Phase1 ===
    # @pytestrail.case("5590548")
    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_7),
                               "The test is applicable only for Hydra v1.5 and higher")
    @pytest.mark.usefixtures("ga_compact_overlay_check")
    def test_5590548_search_movie_name_search_by_GA_C2C(self):
        """
        Verify record command to GA schedule recording
        testrail: https://testrail.tivo.com//index.php?/cases/view/5590548
        """
        self.home_page.back_to_home_short()
        movies = self.service_api.get_random_live_channel_rich_info(movie=True, channel_count=10, live=False,
                                                                    channel_payload_count=500)
        movie = self.voicesearch_assertions.get_title_recognized_by_ga(titles_list=movies,
                                                                       media_type=self.voicesearch_labels.LBL_VOICE_MOVIE,
                                                                       tester=self)
        title = movie[2]
        year = movie[3]
        self.voicesearch_page.action_command_by_title_with_google_assistant(title=title, year=year,
                                                                            media_type=self.voicesearch_labels.LBL_VOICE_MOVIE)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(tester=self, open_cta=True, play_cta=False,
                                                             record_cta=False)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())

    # @pytestrail.case("5590550")
    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.xray("FRUM-726")
    @pytest.mark.msofocused
    @pytest.mark.C2C_Phase1
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_7),
                               "The test is applicable only for Hydra v1.5 and higher")
    def test_5590550_search_series_name_search_by_GA_C2C(self):
        """
        Search series name with GA
        xray: https://jira.xperi.com/browse/FRUM-726
        """
        self.home_page.back_to_home_short()
        series = self.service_api.get_random_live_channel_rich_info(movie=False, channel_count=5, live=False,
                                                                    episodic=True, channel_payload_count=200)
        show = self.voicesearch_assertions.get_title_recognized_by_ga(titles_list=series, tester=self)
        title = show[2]
        self.voicesearch_page.action_command_by_title_with_google_assistant(title=title)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(tester=self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())

    # @pytest.mark.p1_regression
    # @pytestrail.case("5590551")
    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_7),
                               "The test is applicable only for Hydra v1.5 and higher")
    @pytest.mark.usefixtures("ga_compact_overlay_check")
    def test_5590551_genre_search_series_search_by_GA_C2C(self):
        """
        Verify that the MSO logo appears in GA overlay when general search is made
        testrail: https://testrail.tivo.com//index.php?/cases/view/5590551
        """
        self.home_page.back_to_home_short()
        search_content = self.voicesearch_labels.LBL_VOICE_GENRE_COMEDY + self.voicesearch_labels.LBL_VOICE_SHOWS
        self.voicesearch_page.general_search_with_google_assistant(search_content=search_content)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_general_search_results_overlay(self)
        title = self.voicesearch_assertions.get_selected_item_details(self)
        self.voicesearch_page.open_selected_search_item()
        self.voicesearch_assertions.wait_ga_entity_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_5),
                               "The test is applicable only for Hydra v1.5 and higher")
    @pytest.mark.usefixtures("ga_compact_overlay_check")
    def test_665044556_movie_decade_temporal_search_by_GA_C2C(self):
        """
        Verify that movie search can be filtered by decade
        testrail: https://testrail.tivo.com//index.php?/tests/view/665044556
        """
        self.home_page.back_to_home_short()
        utterance = self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_TIME_DECADE
        self.voicesearch_page.general_search_with_google_assistant(
            search_action=self.voicesearch_labels.LBL_VOICE_SEARCH_CMD,
            search_content=utterance)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_general_search_results_overlay(self)
        title = self.voicesearch_assertions.get_selected_item_details(self)
        self.voicesearch_page.open_selected_search_item()
        self.voicesearch_assertions.wait_ga_entity_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
        screen_title = self.guide_assertions.get_screen_title()
        year = self.voicesearch_page.get_year(screen_title)
        self.voicesearch_assertions.verify_year_in_decade(year, 1990)

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_5),
                               "The test is applicable only for Hydra v1.5 and higher")
    @pytest.mark.usefixtures("ga_compact_overlay_check")
    def test_665044553_character_search_by_GA_C2C(self):
        """
        Verify that search by character name returns valid MSO content
        testrail: https://testrail.tivo.com//index.php?/tests/view/665044553
        """
        self.home_page.back_to_home_short()
        character = self.voicesearch_assertions.get_filter_search_recognized_by_ga(
            filter_list=self.voicesearch_labels.LBL_VOICE_CHARACTERS, tester=self,
            media_type=self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_WITH)
        utterance = self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_WITH + character
        self.voicesearch_page.general_search_with_google_assistant(search_content=utterance)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_general_search_results_overlay(self)
        title = self.voicesearch_assertions.get_selected_item_details(self)
        self.voicesearch_page.open_selected_search_item()
        self.voicesearch_assertions.wait_ga_entity_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.xray("FRUM-931")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_5),
                               "The test is applicable only for Hydra v1.5 and higher")
    @pytest.mark.usefixtures("ga_compact_overlay_check")
    def test_5590556_actor_search_by_GA_C2C(self):
        """
        Verify that search actor returns valid MSO content
        testrail: https://testrail.tivo.com//index.php?/cases/view/5590556
        """
        self.home_page.back_to_home_short()
        # getting a list of actors
        actor_list = self.service_api.get_person_with_role(tsn=Settings.tsn, **{"note": ["contentGroupForPersonId"]},
                                                           **{"levelOfDetail": "high"}, role="actor")
        # chosing actor recognized by GA as being mso specific
        actor = self.voicesearch_assertions.get_filter_search_recognized_by_ga(
            filter_list=actor_list, tester=self,
            media_type=self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_WITH)
        # building the utterance to be tested
        utterance = self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_WITH + actor
        self.voicesearch_page.general_search_with_google_assistant(search_content=utterance)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_general_search_results_overlay(self)
        title = self.voicesearch_assertions.get_selected_item_details(self)
        self.voicesearch_page.open_selected_search_item()
        self.voicesearch_assertions.wait_ga_entity_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_7),
                               "The test is applicable only for Hydra v1.5 and higher")
    @pytest.mark.usefixtures("ga_compact_overlay_check")
    def test_5590559_negative_filters_by_GA_C2C(self):
        """
        Verify that content can be filtered by taking out specific characters
        testrail: https://testrail.tivo.com//index.php?/cases/view/5590559
        """
        self.home_page.back_to_home_short()
        # getting a list of actors
        actor_list = self.service_api.get_person_with_role(tsn=Settings.tsn, **{"note": ["contentGroupForPersonId"]},
                                                           **{"levelOfDetail": "high"}, role="actor")
        # chosing actor recognized by GA as being mso specific
        actor = self.voicesearch_assertions.get_filter_search_recognized_by_ga(
            filter_list=actor_list, tester=self,
            media_type=self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_WITH)
        utterance = self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_WITHOUT + actor
        self.voicesearch_page.general_search_with_google_assistant(search_content=utterance)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_general_search_results_overlay(self)
        title = self.voicesearch_assertions.get_selected_item_details(self)
        self.voicesearch_page.open_selected_search_item()
        self.voicesearch_assertions.wait_ga_entity_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_7),
                               "The test is applicable only for Hydra v1.5 and higher")
    @pytest.mark.usefixtures("ga_compact_overlay_check")
    def test_5590554_crew_search_by_GA_C2C(self):
        """
        Verify that content can be filtered by crew role(director)
        testrail: https://testrail.tivo.com//index.php?/cases/view/5590554
        """
        self.home_page.back_to_home_short()
        # getting a list of directors
        director_list = self.service_api.get_person_with_role(tsn=Settings.tsn, **{"note": ["contentGroupForPersonId"]},
                                                              **{"levelOfDetail": "high"}, role="director")
        # chosing director recognized by GA as being mso specific
        director = self.voicesearch_assertions.get_filter_search_recognized_by_ga(
            filter_list=director_list, tester=self,
            media_type=self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_DIRECTED_BY)
        utterance = self.voicesearch_labels.LBL_VOICE_MOVIES + self.voicesearch_labels.LBL_VOICE_DIRECTED_BY + director
        self.voicesearch_page.general_search_with_google_assistant(search_content=utterance)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_general_search_results_overlay(self)
        title = self.voicesearch_assertions.get_selected_item_details(self)
        self.voicesearch_page.open_selected_search_item()
        self.voicesearch_assertions.wait_ga_entity_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())

    # === C2C - Switch to channel name- Phase 1 ===
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.xray("FRUM-771")
    @pytest.mark.C2C_Phase1
    @pytestrail.case("5590563")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_5),
                               "The test is applicable only for Hydra v1.5 and higher")
    def test_5590563_go_to_channel_name_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide with focus on specified channel by name
        testrail: https://testrail.tivo.com/index.php?/cases/view/5590563
        """
        # first verifying that live channel is not LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.home_page.back_to_home_short()
        # TODO: Update test to use channel_name once light channel ingestion to google is made
        self.voicesearch_page.switch_to_channel_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_GO_TO_CHANNEL,
            channel=self.voicesearch_labels.LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME[Settings.test_environment]["alias"])
        self.voicesearch_page.wait_for_screen_ready(timeout=30000)
        self.watchvideo_assertions.verify_channel_callsign(
            self.voicesearch_labels.LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME[Settings.test_environment]["callsign"])

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_5),
                               "The test is applicable only for Hydra v1.5 and higher")
    def test_5590562_switch_to_channel_name_by_GA_C2C(self):
        """
        C2C - Verify that user is redirected to specified channel by Channel Name
        Say "Switch to channel Fox"
        https://testrail.tivo.com//index.php?/cases/view/5590562
        """
        # first verifying that live channel is not LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.home_page.back_to_home_short()
        # TODO: Update test to use channel_name once light channel ingestion to google is made
        self.voicesearch_page.switch_to_channel_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_SWITCH_CHANNEL,
            channel=self.voicesearch_labels.LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME[Settings.test_environment]["alias"])
        self.voicesearch_page.wait_for_screen_ready(timeout=30000)
        self.watchvideo_assertions.verify_channel_callsign(
            self.voicesearch_labels.LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME[Settings.test_environment]["callsign"])

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase1
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_5),
                               "The test is applicable only for Hydra v1.5 and higher")
    def test_5590560_watch_channel_name_by_GA_C2C(self):
        """
            C2C - Verify that user is redirected to specified channel by Channel Name
            Say "Watch channel Fox"
            https://testrail.tivo.com//index.php?/cases/view/5590560
        """
        # first verifying that live channel is not LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.home_page.back_to_home_short()
        # TODO: Update test to use channel_name once light channel ingestion to google is made
        self.voicesearch_page.switch_to_channel_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_GO_TO_CHANNEL,
            channel=self.voicesearch_labels.LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME[Settings.test_environment]["alias"])
        self.voicesearch_page.wait_for_screen_ready(timeout=30000)
        self.watchvideo_assertions.verify_channel_callsign(
            self.voicesearch_labels.LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME[Settings.test_environment]["callsign"])

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.xray("FRUM-728")
    @pytest.mark.msofocused
    @pytest.mark.C2C_Phase1
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_5),
                               "The test is applicable only for Hydra v1.5 and higher")
    def test_C5590561_tune_to_channel_name_by_GA_C2C(self):
        """
        C2C - Verify that user is redirected to specified channel by Channel Name
        Say "Tune to channel Fox"
        xray: https://jira.xperi.com/browse/FRUM-728
        """
        # first verifying that live channel is not LBL_VOICE_COMMON_CHANNEL_ALIAS_NAME
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        current_call_sign = self.guide_page.get_channel_call_sign()
        self.home_page.back_to_home_short()
        self.voicesearch_page.switch_to_channel_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_TUNE_TO_CHANNEL,
            channel=current_call_sign)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_channel_callsign(current_call_sign)

    # === C2C - Navigation feature - Phase 2 ===
    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.C2C_smoke
    @pytestrail.case("C5603249")
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603249_go_to_guide_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide page when he sends the voice command "Guide"
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603249
        """
        self.home_page.back_to_home_short()
        # GA command to go to Guide
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.home_labels.LBL_GUIDE_SCREENTITLE)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_GUIDE_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_GUIDE_SCREENTITLE)

    # @pytest.mark.test_stabilization
    # @pytest.mark.e2e
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_10196880_apps_and_games_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to Apps and Games page when he sends the voice command "My Apps"
        testrail: https://testrail.tivo.com//index.php?/cases/view/10196880
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_APPS)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_APPSANDGAME_SHORTCUT, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_APPSANDGAME_SHORTCUT)

    # @pytest.mark.test_stabilization
    # @pytest.mark.e2e
    # @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5604137_go_to_home_screen_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to home screen when he sends the voice command "Go to Home Screen"
        testrail: https://testrail.tivo.com//index.php?/cases/view/5604137
        """
        #   Test affected by google bug
        self.home_page.go_to_guide(self)
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.voicesearch_labels.LBL_VOICE_HOMESCREEN)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    # @pytest.mark.test_stabilization
    # @pytest.mark.e2e
    # @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603247_go_home_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to home screen when he sends the voice command "Go Home"
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603247
        """
        # Test affected by Google bug
        self.home_page.go_to_guide(self)
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO,
            screen_title=self.home_labels.LBL_HOME_SCREENTITLE)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603241_go_to_my_recordings_myshows_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "Go to my recordings"
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603241
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_RECORDINGS)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_MYSHOWS_SHORTCUT, timeout=20000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_7),
                               "The test is applicable only for Hydra v1.7 and higher")
    def test_14381055_show_my_recordings_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "Show my recordings"
        testrail: https://testrail.tivo.com//index.php?/cases/view/14381055
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_SHOW,
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_RECORDINGS)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_MYSHOWS_SHORTCUT, timeout=20000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.xray('FRUM-864')
    @pytest.mark.msofocused
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603240_go_to_my_library_myshows_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "Go to My library"
        xray: https://jira.xperi.com/browse/FRUM-864
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_LIBRARY)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_MYSHOWS_SHORTCUT, timeout=5000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603242_go_to_my_library_myshows_from_OTT_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "Go to My library" from
        Youtube
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603242
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_OPEN,
            screen_title=self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.programs_options_assertions.verify_ott_app_is_foreground(
            self, self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_LIBRARY)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_MYSHOWS_SHORTCUT, timeout=8000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.xray("FRUM-841")
    @pytest.mark.C2C_Phase2
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603246_go_to_guide_from_OTT_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide screen when he sends the voice command "Go to Guide" from
        Youtube
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603246
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_OPEN,
            screen_title=self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.programs_options_assertions.verify_ott_app_is_foreground(
            self, self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.home_labels.LBL_GUIDE_SCREENTITLE)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_GUIDE_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_GUIDE_SCREENTITLE)

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603244_go_home_from_OTT_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "Home" from
        Youtube
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603244
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_OPEN,
            screen_title=self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.programs_options_assertions.verify_ott_app_is_foreground(
            self, self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_GO_TO,
            screen_title=self.home_labels.LBL_HOME_SCREENTITLE)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603245_go_to_my_apps_from_OTT_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "Go to my apps" from
        Youtube
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603245
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_OPEN,
            screen_title=self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.programs_options_assertions.verify_ott_app_is_foreground(
            self, self.apps_and_games_labels.LBL_APPS_AND_GAMES_YOUTUBE)
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_SHOW,
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_APPS)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_APPSANDGAME_SHORTCUT, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_APPSANDGAME_SHORTCUT)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5604756_open_my_library_myshows_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "Open My library"
        testrail: https://testrail.tivo.com//index.php?/cases/view/5604756
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_OPEN,
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_LIBRARY)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_MYSHOWS_SHORTCUT, timeout=8000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.GA
    @pytest.mark.C2C_smoke
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603235_my_recordings_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "My recordings"
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603235
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_RECORDINGS)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_MYSHOWS_SHORTCUT, timeout=8000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_5603214_my_library_navigate_by_GA_C2C(self):
        """
        Verify that the user is redirected to My shows screen when he sends the voice command "My library"
        testrail: https://testrail.tivo.com//index.php?/cases/view/5603214
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            screen_title=self.voicesearch_labels.LBL_VOICE_MY_LIBRARY)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_MYSHOWS_SHORTCUT, timeout=8000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_7),
                               "The test is applicable only for Hydra v1.7 and higher")
    def test_9914332_settings_by_GA_C2C(self):
        """
        Verify that the user is redirected to Settings screen when he sends the voice command "Settings"
        testrail: https://testrail.tivo.com//index.php?/cases/view/9914332
        """
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            screen_title=self.apps_and_games_labels.LBL_SETTINGS)
        self.voicesearch_page.wait_ga_to_be_dismissed(self)
        self.programs_options_assertions.verify_ott_app_is_foreground(self, self.apps_and_games_labels.LBL_SETTINGS)

    @pytestrail.case("C10838903")
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_10838903_switch_channel_by_number_by_GA_C2C(self):
        """
        Verify that the user is redirected to specified channel by voice command"

        testrail: https://testrail.tivo.com//index.php?/cases/view/10838903
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True)[0]
        self.voicesearch_page.switch_to_channel_with_google_assistant(self.voicesearch_labels.LBL_VOICE_SWITCH_CHANNEL,
                                                                      channel_number)
        self.watchvideo_assertions.verify_channel_number(channel_number)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.7 and higher")
    def test_10838901_watch_channel_number_by_GA_C2C(self):
        """
        Verify that the user is redirected to specified channel by voice command"

        testrail: https://testrail.tivo.com//index.php?/cases/view/10838901
        """
        self.home_page.go_to_guide(self)
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.voicesearch_page.switch_to_channel_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_NAVIGATION_WATCH_CHANNEL, channel_number)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_GUIDE_SCREENTITLE, timeout=30000)
        self.watchvideo_assertions.verify_channel_number(channel_number)

    @pytest.mark.test_stabilization
    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.7 and higher")
    def test_12790362_movies_on_now_by_GA_C2C(self):
        """
        Verify that the user can filter movies by current time"

        testrail: https://testrail.tivo.com//index.php?/cases/view/12790362
        """
        self.home_page.go_to_guide(self)
        self.home_page.back_to_home_short()
        # test will be skipped if live channel method does not return any Live movies
        self.service_api.get_random_live_channel_rich_info(channel_count=-1, live=True, movie=True,
                                                           adult=False, channel_payload_count=200)
        utterance = self.voicesearch_labels.LBL_VOICE_ON + self.voicesearch_labels.LBL_VOICE_TIME_NOW
        self.voicesearch_page.general_search_with_google_assistant(
            search_action=self.voicesearch_labels.LBL_VOICE_MOVIES,
            search_content=utterance)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_general_search_results_overlay(self)
        title = self.voicesearch_assertions.get_selected_item_details(self)
        self.voicesearch_page.open_selected_search_item()
        self.voicesearch_assertions.wait_ga_entity_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
        self.menu_assertions.verify_item_option_focus("Live TV")

    @pytest.mark.C2C_smoke
    @pytest.mark.xray('FRUM-335')
    @pytest.mark.msofocused
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_10201523_verify_play_mode_in_LiveTV_by_GA_C2C(self):
        """
        Verify that voice command Play starts playing paused LiveTV
        xray: https://jira.xperi.com/browse/FRUM-335
        """
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True)[0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.guide_page.pause_show(self)
        self.voicesearch_page.sent_media_command_with_google_assistant(self.voicesearch_labels.LBL_VOICE_MEDIA_PLAY)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytestrail.case("C10202028")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_10202028_verify_resume_mode_in_LiveTV_by_GA_C2C(self):
        """
        Verify that voice command Resume starts playing paused LiveTV
        testrail: https://testrail.tivo.com//index.php?/cases/view/10202028
        """
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True)[0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.guide_page.pause_show(self)
        self.voicesearch_page.sent_media_command_with_google_assistant(self.voicesearch_labels.LBL_VOICE_MEDIA_RESUME)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytestrail.case("C10202053")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_10202053_verify_pause_mode_in_LiveTV_by_GA_C2C(self):
        """
        Verify that voice command Pause pauses playing LiveTV
        testrail: https://testrail.tivo.com//index.php?/cases/view/10202053
        """
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True)[0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.voicesearch_page.sent_media_command_with_google_assistant(self.voicesearch_labels.LBL_VOICE_MEDIA_PAUSE)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytestrail.case("C10202075")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_10202075_verify_stop_mode_in_LiveTV_by_GA_C2C(self):
        """
        Verify that voice command Stop pauses playing LiveTV
        testrail: https://testrail.tivo.com//index.php?/cases/view/10202075
        """
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True)[0]
        self.home_page.goto_livetv_short(self)
        self.guide_page.enter_channel_number(channel_number)
        self.voicesearch_page.sent_media_command_with_google_assistant(self.voicesearch_labels.LBL_VOICE_MEDIA_STOP)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase3
    @pytestrail.case("C11121754")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11121754_view_guide_now_tv_guide_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide screen when he sends the voice command "What'on now"
        testrail: https://testrail.tivo.com//index.php?/cases/view/11121754
        """
        self.home_page.go_to_guide(self)
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_NAVIGATION_WHATS_ON,
            time_interval=self.voicesearch_labels.LBL_VOICE_TIME_NOW)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_GUIDE_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_GUIDE_SCREENTITLE)
        data = self.guide_page.screen.get_json()
        self.guide_assertions.verify_in_current_guide(data)

    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase3
    @pytestrail.case("C11121757")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11121757_channel_number_tv_guide_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide with focus on specified channel by number
        testrail: https://testrail.tivo.com//index.php?/cases/view/11121757
        """
        self.home_page.go_to_guide(self)
        self.home_page.back_to_home_short()
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_NAVIGATION_WHATS_ON_CHANNEL, channel=channel_number)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_GUIDE_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_GUIDE_SCREENTITLE)
        data = self.guide_page.screen.get_json()
        self.guide_assertions.verify_in_current_guide(data)
        self.guide_assertions.verify_channel_of_highlighted_program_cell(channel_number, data)

    @pytest.mark.C2C_smoke
    @pytest.mark.xray('FRUM-686')
    @pytest.mark.msofocused
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase3
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_11121760_tv_guide_view_guide_channel_number_now_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide with focus on specified channel by number at current time
        xray: https://jira.xperi.com/browse/FRUM-686
        """
        channel_details = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                             adult=False, filter_channel=True)
        if channel_details is None:
            pytest.skip("Could not find any channel")
        channel_number = channel_details[0][0]
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_NAVIGATION_WHATS_ON_CHANNEL, channel=channel_number,
            time_interval=self.voicesearch_labels.LBL_VOICE_TIME_NOW)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_GUIDE_SCREENTITLE)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_channel_number_in_guide(channel_number, refresh=True)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase3
    @pytest.mark.xray("FRUM-743")
    @pytest.mark.msofocused
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11121756_channel_name_tv_guide_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide with focus on specified channel by name
        xray: https://jira.xperi.com/browse/FRUM-743
        """
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.wait_for_guide_next_page()
        current_call_sign = self.guide_page.get_channel_call_sign()
        self.home_page.back_to_home_short()
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_NAVIGATION_WHATS_ON_CHANNEL,
            channel=current_call_sign)
        self.voicesearch_page.wait_for_screen_ready()
        self.voicesearch_page.screen.refresh()
        data = self.guide_page.screen.get_json()
        self.guide_assertions.verify_channel_name_of_highlighted_program_cell(
            current_call_sign, data)

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase3
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_9),
                               "The test is applicable only for Hydra v1.9 and higher")
    def test_11121761_channel_number_and_time_tv_guide_by_GA_C2C(self):
        """
        Verify that the user is redirected to Guide with focus on specified channel by number at specified time
        testrail: https://testrail.tivo.com//index.php?/cases/view/11121761
        """
        self.home_page.go_to_guide(self)
        # fetching grid for current time
        grid_time_snapshot = self.guide_page.get_grid_time_snapshot(guide_screen=self.screen.get_json())
        # creating new time to set the guide to
        newtime = grid_time_snapshot["current_window"][0] + timedelta(hours=3)
        # formatting time to be used with GA utterance e.g. "at 10:30 pm"
        time_interval = " " + self.voicesearch_labels.LBL_VOICE_AT + newtime.strftime("%I:%M %p")
        # getting random entitled channel number
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                            adult=False, filter_channel=True)[0][0]
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_NAVIGATION_WHATS_ON_CHANNEL, channel=channel_number,
            time_interval=time_interval)
        self.voicesearch_page.wait_for_screen_ready(self.home_labels.LBL_GUIDE_SCREENTITLE, timeout=30000)
        self.voicesearch_page.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_GUIDE_SCREENTITLE)
        screen = self.guide_page.screen.get_json()
        self.guide_assertions.verify_guide_start_interval(screen_dump=screen, date_time=newtime)
        self.guide_assertions.verify_channel_of_highlighted_program_cell(channel_number, screen)

    # C2C recording feature tests Phase 4
    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase4
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14385607_record_movie_recording_by_GA_C2C(self):
        """
        Verify record command to GA schedule recording
        testrail: https://testrail.tivo.com//index.php?/cases/view/14385607
        """
        self.home_page.back_to_home_short()
        movies = self.service_api.get_random_recordable_movie_channel(movie_count=5, live=False,
                                                                      channel_payload_count=200)
        movie = self.voicesearch_assertions.get_title_recognized_by_ga(
            titles_list=movies, media_type=self.voicesearch_labels.LBL_VOICE_MOVIE, tester=self)
        title = movie[2]
        year = movie[3]
        self.voicesearch_page.action_command_by_title_with_google_assistant(
            action=self.voicesearch_labels.LBL_VOICE_RECORD_CMD, title=title, year=year,
            media_type=self.voicesearch_labels.LBL_VOICE_MOVIE)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_RECORDING_OPTIONS, timeout=50000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
        self.voicesearch_page.select_menu(self.guide_labels.LBL_RECORD_THIS_MOVIE)
        self.guide_assertions.verify_whisper_shown(self.guide_labels.LBL_RECORD_SUCCESS_WHISPER_MOVIE)

    @pytest.mark.msofocused
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase4
    @pytest.mark.xray('FRUM-1056')
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14385615_search_and_record_movie_recording_by_GA_C2C(self):
        """
        Verify record command to GA schedule recording
        xray: https://jira.xperi.com/browse/FRUM-1056
        """
        self.home_page.back_to_home_short()
        movies = self.service_api.get_random_recordable_movie_channel(movie_count=5, live=False,
                                                                      channel_payload_count=200)
        movie = self.voicesearch_assertions.get_title_recognized_by_ga(
            titles_list=movies, media_type=self.voicesearch_labels.LBL_VOICE_MOVIE, tester=self)
        title = movie[2]
        year = movie[3]
        self.voicesearch_page.action_command_by_title_with_google_assistant(
            title=title, year=year, media_type=self.voicesearch_labels.LBL_VOICE_MOVIE)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(tester=self, open_cta=True, play_cta=False,
                                                             record_cta=True)
        self.voicesearch_assertions.click_on_record_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_RECORDING_OPTIONS, timeout=50000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
        self.voicesearch_page.select_menu(self.guide_labels.LBL_RECORD_THIS_MOVIE)
        self.guide_assertions.verify_whisper_shown(self.guide_labels.LBL_RECORD_SUCCESS_WHISPER_MOVIE)

    @pytest.mark.C2C_smoke
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase4
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14385607_record_series_recording_by_GA_C2C(self):
        """
        Verify record series creates Onepass
        testrail: https://testrail.tivo.com//index.php?/cases/view/14381061
        """
        self.home_page.back_to_home_short()
        series = self.service_api.get_random_live_channel_rich_info(movie=False, channel_count=-1, live=False,
                                                                    episodic=True, channel_payload_count=200)
        show = self.voicesearch_assertions.get_title_recognized_by_ga(titles_list=series, tester=self)
        title = show[2]
        self.voicesearch_page.action_command_by_title_with_google_assistant(
            action=self.voicesearch_labels.LBL_VOICE_RECORD_CMD, title=title)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_ONE_PASS_OPTIONS, timeout=50000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
        self.voicesearch_page.select_menu(self.guide_labels.LBL_CREATE_ONEPASS_WITH_THIS_OPTIONS)
        self.guide_assertions.verify_whisper_shown(self.guide_labels.LBL_ONEPASS_WHISPER_TEXT)

    @pytestrail.case("14382896")
    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase4
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14382896_search_and_record_series_recording_by_GA_C2C(self):
        """
        Verify record series creates Onepass
        testrail: https://testrail.tivo.com//index.php?/cases/view/14382896
        """
        self.home_page.back_to_home_short()
        series = self.service_api.get_random_live_channel_rich_info(movie=False, channel_count=-1, live=False,
                                                                    episodic=True, channel_payload_count=200)
        show = self.voicesearch_assertions.get_title_recognized_by_ga(titles_list=series, tester=self)
        title = show[2]
        self.voicesearch_page.action_command_by_title_with_google_assistant(title=title)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(tester=self, open_cta=True, create_onepass_cta=True)
        self.voicesearch_assertions.click_on_create_onepass_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_ONE_PASS_OPTIONS, timeout=50000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
        self.voicesearch_page.select_menu(self.guide_labels.LBL_CREATE_ONEPASS_WITH_THIS_OPTIONS)
        self.guide_assertions.verify_whisper_shown(self.guide_labels.LBL_ONEPASS_WHISPER_TEXT)

    @pytest.mark.GA
    # @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    # @pytest.mark.skipif(not Settings.is_voice(), reason="Valid for only for arris with voice apk")
    # this behavior is not C2C voice, is OnDevice voice
    def test_312517_verify_series_screen(self):
        channel = self.service_api.get_recordable_non_movie_channel()
        if not channel:
            pytest.fail("Test requires recordable channels")
        self.guide_page.go_to_live_tv(self)
        self.watchvideo_assertions.verify_playback_play()
        try:
            self.home_page.launch_series_voice_strip_tile(channel[0][2])
            self.guide_page.wait_for_search_results()
            self.screen.base.press_up()
            self.voicesearch_assertions.verify_mso_open_cta(self)
            self.screen.base.press_enter()
        except Exception:
            self.home_page.launch_series_voice_strip_tile(channel[0][2])
            self.guide_page.wait_for_search_results()
            self.screen.base.press_up()
            self.voicesearch_assertions.verify_mso_open_cta(self)
            self.screen.base.press_enter()
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=30000)
        self.my_shows_assertions.verify_series_screen(self)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685252")
    @pytest.mark.e2e
    @pytest.mark.GA
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device does not have Video Providers")
    def test_74179073_verify_voice_empty_response(self):
        """
        To verify TiVo voice empty response times out.
        """
        # Press voice button on Home Screen and utter nothing
        self.home_page.back_to_home_short()
        self.voicesearch_page.send_empty_voice()
        self.voicesearch_assertions.verify_availability_of_text("")
        self.screen.base.press_back()  # Dismiss voice response strip
        # Press voice button on LiveTV and utter nothing
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.voicesearch_page.send_empty_voice()
        self.voicesearch_assertions.verify_availability_of_text("")
        self.screen.base.press_back()  # Dismiss voice response strip
        self.watchvideo_assertions.verify_livetv_mode()
        # Launch Netflix, press voice button and utter nothing
        self.watchvideo_assertions.press_netflix_and_verify_screen(self)
        time.sleep(30)  # Delay added for the app screen to settle down
        self.voicesearch_page.send_empty_voice()
        self.voicesearch_assertions.verify_availability_of_text("")
        self.screen.base.press_back()  # Dismiss voice response strip

    @pytest.mark.GA
    # @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    # @pytest.mark.skipif(not Settings.is_voice(), reason="Valid for only for arris with voice apk")
    # this behavior is not C2C voice or OnDevice voice.
    def test_351608_episode_movie_in_result_strip_GA(self):
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, movie=False)
        channel = channel[0][0]
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.home_page.launch_series_voice_strip_tile(program)
        self.voicesearch_page.wait_ga_compact_overlay(self)
        expected_text = self.voicesearch_page.get_available_text(self)
        self.home_page.launch_series_voice_strip_tile(program)
        self.voicesearch_assertions.verify_availability_of_text(expected_text)

    # @pytest.mark.p1_regression
    @pytest.mark.GA
    @pytest.mark.bc_to_fss
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.VOICE)])
    @pytest.mark.parametrize("body_config_feature", [(BodyConfigFeatures.VOICE)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.VOICE)])
    @pytest.mark.parametrize("req_type", ["NO_REQ"])
    @pytest.mark.parametrize("bc_state, fs_state", [(False, False), (False, True), (True, False), (True, True)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.is_devhost(), reason="Does not support reboot")
    @pytest.mark.notapplicable(not Settings.is_internal_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.notapplicable(not Settings.is_managed(), "GA feature works correctly only on Managed boxes")
    def test_10464414_voice_from_body_config_to_feature_status(self, request, feature_status_feature,
                                                               device_info_store_feature, body_config_feature,
                                                               req_type, bc_state, fs_state):
        """
        Verify MSO logo in voice search results for a movie.
        Only feature state in featureStatus should affect feature enabling/disabling.
        bc_state = feature state in bodyConfig, fs_state = feature state in featureStatus.

        Xray:
            https://jira.tivo.com/browse/FRUM-1006
            https://jira.tivo.com/browse/FRUM-954
            https://jira.tivo.com/browse/FRUM-853
            https://jira.tivo.com/browse/FRUM-662

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/10464415
            https://testrail.tivo.com//index.php?/cases/view/10464414
            https://testrail.tivo.com//index.php?/cases/view/11124437
            https://testrail.tivo.com//index.php?/cases/view/11124436
        """
        request.config.cache.set("is_relaunch_needed", True)
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, fs_state)
        self.service_api.update_features_in_body_config(body_config_feature, is_add=bc_state)
        self.voicesearch_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.service_api.check_feature_with_body_search(body_config_feature, expected=bc_state)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=fs_state)
        self.voicesearch_page.sent_media_command_with_google_assistant("movies")
        self.voicesearch_assertions.verify_if_voice_feature_is_on(self, "movies", expected=fs_state)

    # @pytest.mark.p1_regression
    @pytest.mark.GA
    @pytest.mark.fast_fs_update
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.VOICE)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.VOICE)])
    @pytest.mark.parametrize("req_type,enable", [
        (NotificationSendReqTypes.FCM, True), (NotificationSendReqTypes.FCM, False),
        (NotificationSendReqTypes.NSR, True), (NotificationSendReqTypes.NSR, False)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(not Settings.is_internal_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.notapplicable(not Settings.is_managed(), "GA feature works correctly only on Managed boxes")
    def test_20959886_voice_fast_feature_status_update(self, request, feature_status_feature,
                                                       device_info_store_feature, req_type, enable):
        """
        Fast featureStatus Update.
        Feature Enabling: Set VOICE = TRUE in featureStatusSearch.
        Precondition = initial feature state, it should be inverted value of 'enable' variable.
        'enable' variable represents feature state we are going to check.

        Xray:
            https://jira.tivo.com/browse/FRUM-1437
            https://jira.tivo.com/browse/FRUM-1361

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20959886
            https://testrail.tivo.com/index.php?/cases/view/20959887
        """
        request.config.cache.set("is_relaunch_needed", False)
        # Preconditions
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, not enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=not enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.back_to_home_short()
        self.voicesearch_page.sent_media_command_with_google_assistant("movies")
        self.voicesearch_assertions.verify_if_voice_feature_is_on(self, "movies", expected=not enable)
        # Steps
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.back_to_home_short()
        self.voicesearch_page.sent_media_command_with_google_assistant("movies")
        self.voicesearch_assertions.verify_if_voice_feature_is_on(self, "movies", expected=enable)

    # @pytest.mark.test_stabilization
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    def test_5590560_watch_channel_name(self):
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        channel_details = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                             adult=False, filter_channel=True)
        if channel_details is None:
            pytest.skip("Could not find any channel")
        channel_number = channel_details[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        self.screen.base.press_left()
        channel_logo = self.guide_page.get_channellogo_from_guide(self, refresh=True)
        channel_name = self.guide_page.get_channelname_from_guide(self, refresh=True)
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_NAVIGATION_WATCH_CHANNEL, channel_name)
        self.voicesearch_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_logo_of_info_baner_header(channel_logo)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.notapplicable(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("disable_video_providers")
    @pytest.mark.usefixtures("enable_video_providers")
    def test_c11124067_voice_feature_play_livetv_movie(self):
        """
        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/11124067
        """
        # Verify if Voice feature is ON
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        channel = self.service_api.get_random_live_channel_rich_info(movie=True, live=True)
        if channel is None:
            pytest.skip("Could not find any movie channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.voicesearch_page.sent_media_command_with_google_assistant(self.voicesearch_labels.
                                                                       LBL_VOICE_MEDIA_PLAY + " " + re.escape(program[:-6]))
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_amino())
    @pytest.mark.timeout(Settings.timeout)
    def test_11121754_guide_view_by_time(self):
        """
        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/11121754
        """
        # Verify if Voice feature is ON
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        self.home_page.back_to_home_short()
        self.guide_page.go_to_live_tv(self)
        channel_number = self.watchvideo_assertions.get_channel_number()
        self.voicesearch_page.sent_media_command_with_google_assistant("What'\'’s on now")
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_default_channel_is_highlighted(self, channel_number)
        self.guide_assertions.verify_focus_on_channel_airing_now_program(self, channel_number)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    def test_5590563_go_to_channel_name(self):
        """
        C2C - Go to Channel Name
        Say "Go to channel CBS"
        """
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        channel_details = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                             adult=False, filter_channel=True)
        if channel_details is None:
            pytest.skip("Could not find any channel")
        channel_number = channel_details[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        self.screen.base.press_left()
        channel_logo = self.guide_page.get_channellogo_from_guide(self, refresh=True)
        channel_name = self.guide_page.get_channelname_from_guide(self, refresh=True)
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_GO_TO_CHANNEL, channel_name)
        self.voicesearch_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_logo_of_info_baner_header(channel_logo)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    def test_5590562_switch_to_channel_name(self):
        """
        C2C - Switch to Channel Name
        Say "Switch to channel CBS"
        """
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        channel_details = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                             adult=False, filter_channel=True)
        if channel_details is None:
            pytest.skip("Could not find any channel")
        channel_number = channel_details[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        self.screen.base.press_left()
        channel_logo = self.guide_page.get_channellogo_from_guide(self, refresh=True)
        channel_name = self.guide_page.get_channelname_from_guide(self, refresh=True)
        self.voicesearch_page.navigate_in_guide_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_SWITCH_CHANNEL, channel_name)
        self.voicesearch_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_logo_of_info_baner_header(channel_logo)

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    def test_5590556_c2c_search_actor(self):
        """
        C2C - Search actor

        https://testrail.tivo.com//index.php?/cases/view/5590556
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SIDE_PANEL, 30000)
        self.menu_page.select_menu_items(self.home_labels.LBL_MOVIES)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 50000)
        self.home_page.press_info_button()
        if Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-11"):
            self.home_page.select_menu_item("More Info")
        else:
            self.home_page.select_menu_item("Options")
            self.home_page.select_menu_item("See More Info")
        self.my_shows_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_ACTION_SCREEN_VIEWMODE)
        cast_name = self.movie_cdp_page.get_cast_name()
        self.home_page.back_to_home_short()
        self.home_page.launch_series_voice_strip_tile(cast_name)
        self.guide_page.wait_for_search_results()
        self.screen.base.press_up()
        self.screen.base.press_enter()
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_FRAMELAYOUT, timeout=5000)
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_OPEN, 5000)
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.vod_assertions.verify_vod_series_or_action_screen_view_mode()

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    def test_5590558_C2C_keyword_search(self):
        """
        C2C - Keyword Search

        https://testrail.tivo.com//index.php?/cases/view/5590558
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SIDE_PANEL, 30000)
        self.menu_page.select_menu_items(self.home_labels.LBL_MOVIES)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 50000)
        self.home_page.press_info_button()
        if Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-11"):
            self.home_page.select_menu_item("More Info")
        else:
            self.home_page.select_menu_item("Options")
            self.home_page.select_menu_item("See More Info")
        self.my_shows_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_ACTION_SCREEN_VIEWMODE)
        genre = self.watchvideo_page.get_genre_details(refresh=True)
        movie_on_genre = self.voicesearch_labels.LBL_MOVIE + genre
        self.home_page.back_to_home_short()
        self.home_page.launch_series_voice_strip_tile(movie_on_genre)
        self.guide_page.wait_for_search_results()
        self.screen.base.press_up()
        self.screen.base.press_enter()
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_FRAMELAYOUT, timeout=5000)
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_OPEN, 5000)
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_ACTION_SCREEN_VIEWMODE)

    @pytest.mark.GA
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_amino())
    @pytest.mark.timeout(Settings.timeout)
    def test_c11124064_c5590550_c2c_search_episodic_content(self):
        """
        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/11124064
            https://testrail.tivo.com//index.php?/cases/view/5590550
        """
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        channel = self.service_api.get_random_live_channel_rich_info(movie=False, live=False, episodic=True)
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.voicesearch_page.sent_media_command_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_SEARCH_CMD + " " + program)
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_OPEN, 2000)
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=12000)
        self.my_shows_assertions.verify_series_screen(self)

    @pytest.mark.GA
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_amino())
    @pytest.mark.timeout(Settings.timeout)
    def test_c5590564_kids_genre(self):
        """
        Testrail:
        https://testrail.tivo.com//index.php?/cases/view/5590564
        """
        # Verify if Voice feature is ON
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        self.voicesearch_page.sent_media_command_with_google_assistant("Find me shows for kids")
        self.guide_page.wait_for_search_results()
        self.voicesearch_assertions.verify_availability_of_row_content()
        self.screen.base.press_enter()
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_FRAMELAYOUT, timeout=5000)
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_OPEN, 5000)
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_series_screen(self)

    @pytest.mark.GA
    @pytest.mark.xray("FRUM-886")
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_amino())
    @pytest.mark.timeout(Settings.timeout)
    def test_5590551_search_comedy_genre(self):
        """
        Verify that the user is able to search comedy shows and able to view content screen through GA"
        testrail: https://testrail.tivo.com/index.php?/cases/view/5590551
        """
        # Verify if Voice feature is ON
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        self.voicesearch_page.sent_media_command_with_google_assistant("Search Comedy Shows")
        self.guide_page.wait_for_search_results()
        self.voicesearch_assertions.verify_availability_of_row_content()
        self.screen.base.press_enter()  # Highlight is on first tile of strip
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_FRAMELAYOUT, timeout=5000)
        self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_OPEN, 5000)
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_series_screen(self)

    @pytest.mark.GA
    @pytest.mark.notapplicable(Settings.is_amino())
    def test_19779075_send_ga_on_eas_screen(self):
        """
        testrail: https://testrail.tivo.com//index.php?/cases/view/19779075
        """
        self.home_page.back_to_home_short()
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.voicesearch_page.sent_media_command_with_google_assistant("back")
        time.sleep(10)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_amino())
    @pytest.mark.timeout(Settings.timeout)
    def test_c5590554_movie_director(self):
        """
        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/5590554
        """
        # Verify if Voice feature is ON
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        results = self.service_api.get_person_with_role(tsn=Settings.tsn, **{"note": ["contentGroupForPersonId"]},
                                                        **{"levelOfDetail": "high"}, role="director")
        for person in results:
            self.home_page.back_to_home_short()
            self.voicesearch_page.sent_media_command_with_google_assistant("Movies directed by" + " " + person)
            self.guide_page.wait_for_search_results()
            self.screen.base.press_up()  # In case highlight not on content tile
            self.screen.base.press_enter()
            self.screen.base.wait_ui_element_appear(self.voicesearch_labels.LBL_OPEN, 3000)
            self.screen.base.press_enter()
            state = self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 12000)
            if state:
                break
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_ACTION_SCREEN_VIEWMODE)

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    def test_11124068_search_free_vod(self):
        """
        https://testrail.tivo.com//index.php?/cases/view/11124068
        """
        if Settings.is_cc3():
            status, result = self.vod_api.getOffer_fvod()
            if result is None:
                title = self.voicesearch_labels.LBL_VOICE_SEARCH_CMD + " " + self.voicesearch_labels.LBL_FVOD_CC3
            else:
                program = self.vod_page.extract_title(result)
                self.home_page.back_to_home_short()
        else:
            status, result = self.vod_api.getOffer_tvod_movie_entitledRented()
            if result is None:
                status, result = self.vod_api.getOffer_tvod_movie()
                if result is None:
                    pytest.skip("The content is not available on VOD catlog.")
                else:
                    self.home_page.back_to_home_short()
                    self.vod_page.goto_vodoffer_program_screen(self, result)
                    self.vod_page.play_confirmrented_content(self, result)
                    self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
            program = self.vod_page.extract_title(result)
            self.home_page.back_to_home_short()
            title = self.voicesearch_labels.LBL_VOICE_SEARCH_CMD + " " + program
        self.home_page.launch_series_voice_strip_tile(title)
        self.guide_page.wait_for_search_results()
        self.screen.base.press_up()
        self.voicesearch_assertions.verify_mso_open_cta(self)
        self.voicesearch_assertions.verify_mso_play_cta(self)
        self.screen.base.press_right()
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    # @pytest.mark.test_stabilization
    @pytest.mark.GA
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.skipif(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_11124060_search_movie_recording(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/11124060

        Product Bug : https://jira.tivo.com/browse/BZSTREAM-8306
        """
        self.home_page.back_to_home_short()
        movies = self.service_api.get_random_recordable_movie_channel(movie_count=5, live=True,
                                                                      channel_payload_count=200)
        if movies is None:
            pytest.skip("Recordable movie channel is not available")
        movie = self.voicesearch_assertions.get_title_recognized_by_ga(titles_list=movies,
                                                                       media_type=self.voicesearch_labels.LBL_VOICE_MOVIE,
                                                                       tester=self)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(movie[0])
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_content_in_category(program)
        self.home_page.back_to_home_short()
        title = self.voicesearch_labels.LBL_SEARCH_MOVIE + " " + movie[2] + " " + movie[3]
        self.home_page.launch_series_voice_strip_tile(title)
        self.guide_page.wait_for_search_results()
        self.screen.base.press_up()
        self.voicesearch_assertions.verify_mso_open_cta(self)
        self.voicesearch_assertions.verify_mso_play_cta(self)
        self.screen.base.press_right()
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.my_shows_page.get_watch_or_video_recording_view_mode(self))
        self.my_shows_assertions.verify_recording_playback(self)

    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_amino())
    @pytest.mark.C2C
    @pytest.mark.GA
    @pytest.mark.vod
    @pytest.mark.timeout(Settings.timeout)
    def test_c11121857_play_vod_movie(self):
        """
        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/11121857
        """
        # Verify if Voice feature is ON
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        status, result = self.vod_api.getOffer_fvod_movie()
        if result is None:
            pytest.skip("FVOD movies are not available on VOD catlog.")
        else:
            program = self.vod_page.extract_title(result)
            self.home_page.back_to_home_short()
            self.voicesearch_page.action_command_with_google_assistant(action=self.voicesearch_labels.LBL_VOICE_PLAY_CMD,
                                                                       title=re.escape(program[:-6]))
            self.guide_page.wait_for_screen_ready()
            self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.notapplicable(Settings.is_amino())
    @pytest.mark.C2C
    @pytest.mark.GA
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("disable_video_providers")
    @pytest.mark.usefixtures("enable_video_providers")
    def test_c11124063_c2c_search_non_episodic_content(self):
        """
        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/11124063
        """
        # Verify if Voice feature is ON
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        channel = self.service_api.get_random_live_channel_rich_info(movie=True, live=True)
        if channel is None:
            pytest.skip("Could not find any movie channel")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.voicesearch_page.action_command_with_google_assistant(action=self.voicesearch_labels.LBL_VOICE_SEARCH_CMD,
                                                                   title=re.escape(program[:-6]))
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.voicesearch_assertions.verify_entity_ga_overlay(tester=self, play_cta=True)
        self.voicesearch_assertions.click_on_play_cta(self)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.GA
    def test_T486395020_voice_search_over_youtube_video(self):
        """
        Voice search over Video playback - YouTube
        testrail: https://testrail.tivo.com//index.php?/tests/view/486395020
        """
        self.home_page.back_to_home_short()
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, "youtube")
        self.programs_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.apps_and_games_assertions.verify_app_content_playing()
        self.voicesearch_page.sent_media_command_with_google_assistant("Search for Kids shows")
        self.guide_page.wait_for_search_results()
        self.apps_and_games_page.press_back_button()
        self.programs_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_assertions.verify_app_content_playing()
        self.voicesearch_page.sent_media_command_with_google_assistant("Search for Action Movies")
        self.guide_page.wait_for_search_results()
        self.voicesearch_page.sent_media_command_with_google_assistant("Play the third one")
        self.guide_page.wait_for_search_results()
        self.apps_and_games_assertions.verify_app_content_playing()

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase2
    @pytest.mark.xray("FRUM-104439")
    @pytest.mark.msofocused
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="C2C voice solution is only for Managed streamers")
    @pytest.mark.notapplicable(Settings.is_amino(), reason="C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_open_app_by_GA_C2C(self):
        """
        Verify that the called app is opened
        xray: https://jira.xperi.com/browse/FRUM-104439
        """
        self.menu_page.go_to_video_providers(self)
        app_name = self.voicesearch_page.get_current_focused_item()
        self.voicesearch_page.navigate_to_screen_with_google_assistant(
            nav_cmd=self.voicesearch_labels.LBL_VOICE_NAVIGATION_OPEN,
            screen_title=app_name)
        self.voicesearch_page.pause(10, "Waiting till voice search overlay disappears")
        self.programs_options_assertions.verify_ott_app_is_foreground(
            self, app_name)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.C2C_Phase4
    @pytest.mark.xray("FRUM-76095")
    @pytest.mark.msofocused
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "C2C voice solution is only for Managed streamers")
    @pytest.mark.notapplicable(Settings.is_amino(), "C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_76095_onepass_record_series_available_live_in_future_by_GA_C2C(self):
        """
        Verify that OnePass - Record series available on Live TV in the future
        xray: https://jira.xperi.com/browse/FRUM-76095
        """
        offer = self.service_api.get_offer_with_parameters(collection_type='series', is_live=False, with_ott=True,
                                                           is_recordable=True)
        if not offer:
            pytest.skip("Test requires OTT program.")
        title = offer.title
        self.voicesearch_page.action_command_by_title_with_google_assistant(
            action=self.voicesearch_labels.LBL_VOICE_RECORD_CMD, title=title)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_ONE_PASS_OPTIONS, timeout=50000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
        self.voicesearch_page.select_menu(self.guide_labels.LBL_CREATE_ONEPASS_WITH_THIS_OPTIONS)
        self.guide_assertions.verify_whisper_shown(self.guide_labels.LBL_ONEPASS_WHISPER_TEXT)
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(title)

    @pytest.mark.GA
    @pytest.mark.C2C
    @pytest.mark.xray("FRUM-128331")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "C2C voice solution is only for Managed streamers")
    @pytest.mark.notapplicable(Settings.is_amino(), "C2C is not supported by Amino boxes")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_frum_128331_voice_search_sports_team(self):
        """
        Voice search sports team from What to watch
        """
        self.service_api.check_feature_with_body_search(BodyConfigFeatures.VOICE, expected=True)
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_SPORTS)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_SPORTS)
        title = self.my_shows_page.get_title_from_pane()
        self.voicesearch_page.sent_media_command_with_google_assistant(
            self.voicesearch_labels.LBL_VOICE_SEARCH_CMD + " " + title)
        self.voicesearch_assertions.wait_ga_compact_overlay(self)
        self.screen.base.press_enter()
        self.voicesearch_page.pause(10, "Waiting till voice search overlay disappears")
        self.voicesearch_assertions.verify_entity_ga_overlay(self, open_cta=True)
        self.voicesearch_assertions.click_on_open_cta(self)
        self.voicesearch_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=30000)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(title.upper())
