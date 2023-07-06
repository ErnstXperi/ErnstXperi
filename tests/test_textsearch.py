"""
Created on Aug 1, 2017

@author: sghosh
"""

import time

import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.text_search.conftest import setup_text_search  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings  # noqa: F401
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions  # noqa: F401
from pytest_testrail.plugin import pytestrail
from set_top_box.conf_constants import HydraBranches
from set_top_box.client_api.Menu.conftest import enable_netflix, disable_parental_controls
from set_top_box.client_api.Menu.conftest import enable_video_providers, disable_video_providers
from set_top_box.client_api.apps_and_games.conftest import enable_app
from set_top_box.client_api.home.conftest import launch_hydra_app_when_script_is_on_ott
from mind_api.middle_mind.field import socu_partner_id
from set_top_box.client_api.ott_deeplinking.conftest import enabling_video_providers


@pytest.mark.usefixtures("setup_text_search")
# Removing the check due to service timeout CA-10523
# @pytest.mark.usefixtures("is_service_search_alive")
@pytest.mark.textsearch
class TestTextSearch(object):

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_324770_text_alphabetical_search(self):
        """
        User should be able to do  Alphabetical Search
        :return:
        """
        self.text_search_page.go_to_search(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT.upper())
        self.text_search_page.input_search_text("ARNOLD SCHWARZENEGGER")
        self.text_search_assertions.verify_search_text_entry("ARNOLD SCHWARZENEGGER")
        self.text_search_assertions.verify_search_result("Arnold Schwarzenegger")

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_324771_text_numeric_search(self):
        """
        User should be able to do  numeric search
        :return:
        """
        self.text_search_page.go_to_search(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT.upper())
        self.text_search_page.input_search_text("4")
        self.text_search_assertions.verify_search_text_entry("4")
        time.sleep(5)
        self.text_search_assertions.verify_search_result("4")

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_324772_text_delete_reenter(self):
        """
        User should be able to delete and reenter the text
        :return:
        """
        self.text_search_page.go_to_search(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT.upper())
        self.text_search_page.input_search_text("ARNOLD SCHWARZENEGGER")
        self.text_search_assertions.verify_search_text_entry("ARNOLD SCHWARZENEGGER")
        self.text_search_page.delete_reenter()
        self.text_search_assertions.verify_search_text_entry("ARNOLD SCHWARZENEGGER")
        self.text_search_assertions.verify_search_result("Arnold Schwarzenegger")

    @pytestrail.case("C10838513")
    @pytest.mark.xray('FRUM-38')
    @pytest.mark.devhost
    @pytest.mark.sanity
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_109383_search_and_verify_movie_title(self):
        """
        109383
        verify the matching movie title appears in the search result list on entering the search query.
        :return:
        """
        self.text_search_page.go_to_search(self)
        movie = self.text_search_page.searchMovie(self.service_api)
        if not movie:
            pytest.fail("Test requires movie name to get a search results.")
        self.text_search_assertions.verify_search_result(movie)

    @pytestrail.case('C11123867')
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_393710_search_and_record_part1(self):
        """
        393710
        Verify explicit recording from Search
        :return:
        """
        self.text_search_page.go_to_search(self)
        movie, movie_year = self.text_search_page.get_movie(self.service_api)
        if movie_year:
            self.text_search_page.search_and_select(movie, movie, year=movie_year)
        else:
            self.text_search_page.search_and_select(movie, movie)
        self.text_search_assertions.verify_movie_screen(self)
        self.text_search_page.record_from_movie_screen(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.home_labels.LBL_MOVIES)
        if movie_year:
            self.my_shows_assertions.verify_content_in_category(movie + " (" + str(movie_year) + ")")
        else:
            self.my_shows_assertions.verify_content_in_category(movie)

    @pytestrail.case("C12792780")
    # @pytest.mark.devhost
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_113913_search_person_item(self):
        """
        113913
        Verify the behavior when selecting a person item in search results.

        :return:
        """
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select("Tom Hanks", "Tom Hanks")
        self.text_search_page.verify_person_screen(self, "Tom Hanks")

    @pytestrail.case("C12792794")
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.timeout(Settings.timeout)
    def test_271847_person_screen_strip_order(self):
        """
        271847
        Verify Person Screen strip order.
        """
        person = self.service_api.get_random_person(Settings.tsn, **{"first": "Alan"})
        if person is None:
            pytest.fail("Failed to fetch persons")
        person = f"{person[0][0]} {person[0][1]}"
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_person(person)
        self.text_search_assertions.verify_person_titlescreen(person)
        self.program_options_assertions.verify_person_screen_strip()
        self.program_options_assertions.verify_biaxial_screen()
        self.text_search_assertions.verify_preview_pane()

    @pytestrail.case("C12792168")
    @pytest.mark.p1_regression
    @pytest.mark.deeplink
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_231329_deep_linking_search(self):
        self.text_search_page.go_to_search(self)
        self.my_shows_page.search_select_program_from_OTT(self, OTT=None, feedName="Movies",
                                                          cnt=4, update_tivo_pt=False)
        self.text_search_page.select_app_strip()
        self.home_page.verify_OTT_screen(Settings.app_package)

    @pytest.mark.test_stabilization
    @pytestrail.case('C11123868')
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_393710_explicit_recording_from_search_series_part2(self):
        """
        393710
        To schedule and verify explicit recording from search
        :return:
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel:
            pytest.skip("Failed to get channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        selected_option = self.text_search_page.explicit_recording_from_search(self, program)
        self.text_search_assertions.verify_explicit_recording_from_search(self, program, selected_option)

    @pytestrail.case('C11123946')
    @pytest.mark.bat
    @pytest.mark.devhost
    @pytest.mark.socu
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_363174_watch_socu_from_search(self):
        """
        363174
        Watch SoCu offer from Search Screen
        :return:
        """
        api = self.service_api
        channel = api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True, filter_socu=True)
        if not channel:
            pytest.skip("SOCU channels not found. Hence skipping")
        self.home_page.go_to_guide(self)
        self.menu_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.text_search_page.go_to_search(self)
        self.text_search_assertions.verify_search_screen_title()
        self.text_search_page.search_and_select(program, program, select=False)
        self.my_shows_page.search_and_select_ott(self, program, self.home_labels.LBL_SOCU_ICON)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.home_page.select_first_item_in_live_and_upcoming()
        self.program_options_assertions.verify_action_view_mode(self)
        self.program_options_assertions.verify_biaxial_screen()
        self.program_options_page.select_play_from_socu(socu=self.home_labels.LBL_WTW_SOCU_ICON)
        self.home_assertions.verify_socu_playback(self)

    @pytestrail.case("C12792784")
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_339659_verify_onepass_overlay(self):
        """
        339659
        Verify Pressing OK Create ONE_PASS_NAME action from Get This Show strip displays OnePass Options overlay.
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program)
        self.my_shows_assertions.verify_onepass_options_overlay(self)

    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.longrun
    @pytest.mark.timeout(Settings.timeout)
    def test_331774_search_content_validation(self):
        """
        TC 331774 - Search - content list verification
        """
        channel, program = self.text_search_page.get_episodic_program(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program, select=False)
        channel_expected = channel[0][0] + " " + channel[0][4]
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(channel[0][4], channel_expected, select=False)
        program = self.text_search_page.get_non_episodic_program(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program, select=False)
        movie, movie_year = self.text_search_page.get_movie(self.service_api)
        self.text_search_page.go_to_search(self)
        if movie_year:
            self.text_search_page.search_and_select(movie, movie, year=movie_year, select=False)
        else:
            self.text_search_page.search_and_select(movie, movie, select=False)
        person = self.service_api.get_random_person(Settings.tsn, **{"first": "Alan"})
        if person is None:
            raise AssertionError("could not find a person")
        person = f"{person[0][0]} {person[0][1]}"
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(person, person, select=False)
        show = self.service_api.extract_offer_id(self.service_api.get_grid_row_search(is_preview_offer_needed=True),
                                                 genre='movie', count=1)
        if show is None:
            raise AssertionError("Could not find any collection")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(show[0][0], show[0][0], select=False)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685250")
    @pytest.mark.e2e
    @pytest.mark.myshows
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    def test_74120457_bookmark_ott_programs_and_verify_in_myshows(self):
        vod_partner_id = self.vod_api._getVodPartnerId()[1]
        offer = self.service_api.get_offer_with_parameters(collection_type='movie', is_recordable=False, with_ott=True,
                                                           is_live=False, exclude_socu=True,
                                                           vod_partner_id=vod_partner_id, without_vod=True)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(offer.title, offer.title, year=offer.movie_year)
        self.guide_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN)
        self.text_search_page.create_bookmark_from_movie_screen(self)
        self.text_search_page.select_folder_from_myshows(self, self.my_shows_labels.LBL_MY_SHOWS_STREAMING_MOVIES)
        self.my_shows_assertions.verify_category_has_content()
        self.menu_page.go_to_video_providers(self)
        self.menu_page.check_or_uncheck_all_menu_items(uncheck=True)
        self.text_search_page.select_folder_from_myshows(self,
                                                         self.my_shows_labels.LBL_MY_SHOWS_NOT_CURRENTLY_AVAILABLE_FOLDER)
        self.my_shows_assertions.verify_category_has_content()
        self.menu_page.go_to_video_providers(self)
        self.menu_page.check_or_uncheck_all_menu_items()
        self.text_search_page.select_folder_from_myshows(self, self.my_shows_labels.LBL_MY_SHOWS_STREAMING_MOVIES)
        self.my_shows_assertions.verify_category_has_content()

    @pytest.mark.ipppv
    @pytest.mark.search_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_C9649054_PPV_Search_AdultContent(self):
        """
        TC C9649054
        Verify searching an adult content in the search returns empty search result.
        :return:
        """
        program = self.service_api.get_random_encrypted_unencrypted_channels(encrypted=True,
                                                                             ppv=True,
                                                                             adult=True,
                                                                             )
        self.text_search_page.go_to_search(self)
        self.text_search_page.input_search_text(program[0][1])
        self.text_search_assertions.verify_empty_search_result_on_search_screen()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_11
    @pytest.mark.direct_play_from_search
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    @pytest.mark.timeout(Settings.timeout)
    def test_12793359_direct_play_from_search_live_tv_show(self):
        """
        Direct Play from Search - verify Live TV show is successfully streaming

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/12793359
        """
        program = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1, adult=False,
                                                                             subtitle=True, encrypted=None,
                                                                             filter_channel=True)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(f'{program[0][2]}', f"{program[0][1]}: {program[0][2]}",
                                                select=False)
        self.watchvideo_assertions.press_select_and_verify_streaming(self)

    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.direct_play_from_search
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    @pytest.mark.timeout(Settings.timeout)
    def test_12793365_direct_play_from_search_show_without_sources(self):
        """
        Direct Play from Search - verify navigating to the Program screen when there are no sources

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/12793365
        """
        api = self.service_api
        show = api.map_channel_number_to_currently_airing_offers(
            channel_source=None,
            grid_row=api.get_grid_row_search(is_preview_offer_needed=True),
            genre="series", subtitle=True, with_ott=False, future=2, count=1)
        title = show[0][0]
        subtitle = show[0][2]
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(subtitle, f"{title}: {subtitle}", select=False)
        self.text_search_page.press_ok_button()
        self.text_search_assertions.verify_view_mode(self.watchvideo_labels.LBL_ACTION_SCREEN_VIEWMODE)

    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.direct_play_from_search
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.is_fire_tv(), "Fire TV does not have OTTs")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    def test_12793361_direct_play_from_search_ott_show(self):
        """
        Direct Play OTT from Search - verify transition to OTT from Search on single press

        This test gets show on OTT partner, does its Search and expects
        to either launch corresponding app or play market (proposing to install it)

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/12793361
        """
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT=None,
                                                                   no_partnerIdCount=False,
                                                                   count=-1)
        if not program:
            pytest.skip("OTT not present in search")
        self.text_search_page.log.info("program list: {}".format(program))
        self.text_search_page.go_to_search(self)
        for pgm in program:
            self.text_search_page.search_and_select(pgm[0], pgm[0], year=pgm[1], select=False)
            play_options = self.guide_page.get_preview_panel().get('availableOn', None)
            if not play_options:
                self.text_search_page.log.info("No playback options displayed in preview")
                continue
            if not self.text_search_page.check_playback_options_are_not_tivo(play_options):
                self.text_search_assertions.press_select_and_verify_app_is_not_hydra(self)
                break

    @pytest.mark.p1_regression
    @pytest.mark.frumos_11
    @pytest.mark.apps_and_games
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.usefixtures("disable_video_providers")
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_12785342_netflix_program_screen_shown_on_netflix_series_asset(self):
        """
            Verify that Netflix program screen shown after long key press on netflix series asset in search results.
            Not applicable for fire tv.

            Testrail:
                https://testrail.tivo.com/index.php?/cases/view/12785342
        """
        self.menu_page.go_to_video_providers(self)
        self.menu_page.checked_option(self.menu_labels.LBL_NETFLIX)
        self.text_search_page.go_to_search(self)
        feed_name = self.wtw_page.get_feed_name("On TV Today")[5]
        program = self.service_api.get_show_available_from_OTT(OTT='Netflix', feedName=feed_name,
                                                               update_tivo_pt=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        year = self.my_shows_page.check_program_if_year_exists(program[0])
        self.my_shows_page.search_deeplink_ott_program(self, program[0], year)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider_by_ui(self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.wtw_page.wait_for_screen_ready()
        self.screen.refresh()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)

    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.direct_play_from_search
    @pytest.mark.vod
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    @pytest.mark.notapplicable(Settings.is_external_mso(), "There's no working VOD playback on external MSOs like RCN etc.")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.usefixtures("disable_video_providers")
    def test_12793363_direct_play_from_search_vod_show(self):
        """
        Direct Play from Search - verify VOD show playback started

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/12793363
        """
        status, result = self.vod_api.getOffer_playable_rating_movie()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        title = self.vod_page.extract_title(result)
        movieYear = self.vod_page.extract_movie_year(result)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(title, title, year=movieYear, select=True)
        self.my_shows_page.select_strip(self.vod_labels.LBL_ON_DEMAND)
        self.vod_page.manage_launched_playback(self, availability_type="fvod")
        self.vod_assertions.verify_vod_playback(self)

    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.socu
    @pytest.mark.direct_play_from_search
    @pytest.mark.vod
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    @pytest.mark.timeout(Settings.timeout)
    def test_12793361_direct_play_from_search_socu_show(self):
        """
        Direct Play OTT from Search - verify transition to SOCU from Search on single press

        This test finds SOCU show, enters its name in Search, selects and expects its playback.

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/12793362
        """
        api = self.service_api
        random_past_socu_offer = api.find_random_past_socu_offer(no_live=True,
                                                                 no_recording=True,
                                                                 subtitle=True,
                                                                 is_preview_offer_needed=True)
        title = random_past_socu_offer.title
        subtitle = random_past_socu_offer.subtitle
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(subtitle, f"{title}: {subtitle}", select=False)
        self.text_search_page.press_ok_button(refresh=False)
        self.vod_page.manage_launched_playback(self, availability_type="svod")
        self.watchvideo_assertions.verify_socu_playback_started()

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.direct_play_from_search
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-13"),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_13530089_direct_play_from_search_recording_no_providers_live(self):
        """
        Search - Direct Play - Series - Press SELECT - Recording, no providers, live
        https://testrail.tivo.com//index.php?/cases/view/13530089
        """
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        channel = self.text_search_page.get_filtered_program_from_grid_row(self, is_recordable_channel=True, genre="series",
                                                                           with_ott=False, not_ppv=True, live_filter=True,
                                                                           filter_live_only=True, future=0, channels_count=1)
        self.guide_page.enter_channel_number(channel[0]['channel_item'].channel_number)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program, select=False)
        self.watchvideo_assertions.press_select_and_verify_recording_is_played(self)

    @pytest.mark.p1_regression
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.ndvr
    @pytest.mark.direct_play_from_search
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14377497_direct_play_from_search_episode_recording_providers_live(self):
        """
        Search - Direct Play - Episode - Press SELECT - Recording, providers, live
        https://testrail.tivo.com/index.php?/cases/view/14377497
        """
        offer = self.service_api.get_offer_with_parameters(collection_type='series')
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_guide_next_page()
        self.guide_page.enter_channel_number(offer.channel_field.channel_number)
        self.home_page.wait_for_screen_ready()
        title = self.guide_page.get_live_program_name(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.select_and_record_program(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(title, title, select=False)
        self.watchvideo_assertions.press_select_and_verify_recording_is_played(self)

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.direct_play_from_search
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("disable_video_providers")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_14378054_direct_play_from_search_movie_recording_no_providers_live(self):
        """
        Search - Direct Play - Movie - Press SELECT - Recording, no providers, live
        https://testrail.tivo.com/index.php?/cases/view/14378054
        """
        offer = self.service_api.get_offer_with_parameters(collection_type='movie', with_ott=False)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_guide_next_page()
        self.guide_page.enter_channel_number(offer.channel_field.channel_number)
        self.guide_page.select_and_record_program(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(offer.title, offer.title, year=offer.movie_year, select=False)
        self.watchvideo_assertions.press_select_and_verify_recording_is_played(self)

    @pytest.mark.p1_regression
    @pytest.mark.direct_play_from_search
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("enabling_video_providers")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    def test_13530094_direct_play_from_search_series_no_recording_providers_not_live(self):
        """
        Search - Direct Play - Series - Press SELECT - No recording, providers, not live
        https://testrail.tivo.com//index.php?/cases/view/13530094
        """
        feed_list = self.wtw_page.get_feed_name(feedtype="TV")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT=None,
                                                                   no_partnerIdCount=False)
            if program:
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], select=False)
        self.text_search_assertions.press_select_and_verify_app_is_not_hydra(self)

    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.longrun
    def test_21570241_verify_asset_is_played_in_order_part_1(self):
        '''
        https://testrail.tivo.com/index.php?/cases/view/21570241

        Live & VOD
        '''
        vod_partner_id = self.vod_api._getVodPartnerId()[1]
        content_list = self.service_api.get_content_list_for_partner_id(partner_id=vod_partner_id,
                                                                        collection_type="movie",
                                                                        assert_if_not_found=False)
        good_for_search_content_list = self.text_search_page.filter_good_for_search_content_list(content_list)
        asset = self.vod_api.get_vod_random_filtered_vod_content(good_for_search_content_list,
                                                                 package_type="fvod", no_live=True,
                                                                 no_recording=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select_by_content(asset, select=False)
        title = asset['title']
        for i in range(2):
            self.my_shows_page.play_vod_asset_multiple_times_from_search(self, asset_name=asset, count=30)
            self.home_page.back_to_home_short()
            self.home_page.wait_for_screen_ready()
            self.home_page.goto_prediction()
            self.home_page.wait_for_screen_ready()
            self.home_assertions.verify_highlighter_on_prediction_strip()
            shows = self.home_page.get_prediction_bar_shows(self)
            status = self.home_assertions.is_content_available_in_prediction(self, title, shows)
            if status:
                self.home_page.nav_to_show_on_prediction_strip(title)
                self.watchvideo_assertions.press_select_and_verify_streaming(self)
            else:
                if i == 0:
                    self.text_search_page.go_to_search(self)
                    self.text_search_page.search_and_select_by_content(asset, select=False)
                    continue
                else:
                    pytest.skip("VOD asset  not found in prediction bar")

    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.direct_play_from_search
    @pytest.mark.usefixtures("disable_video_providers")
    @pytestrail.case("C12940203")
    def test_12940203_bail_button_on_netfix_series_search(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/12940203
        Verify BAIL buttons behaviour during request
        """
        self.menu_page.go_to_video_providers(self)
        self.menu_page.checked_option(self.menu_labels.LBL_NETFLIX)
        feed_name = self.wtw_page.get_feed_name("On TV Today")[5]
        program = self.service_api.get_show_available_from_OTT(OTT='Netflix', feedName=feed_name, update_tivo_pt=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        year = self.my_shows_page.check_program_if_year_exists(program[0])
        button_search = {
            self.screen.base.press_home: self.home_labels.LBL_HOME_SCREENTITLE,
            self.screen.base.press_vod_button: self.home_labels.LBL_ONDEMAND_SCREENTITLE,
            "guide": self.guide_labels.LBL_SCREENTITLE,
            "exit": self.watchvideo_labels.LBL_ACTION_SCREEN_VIEWMODE
        }
        for (key, screen) in button_search.items():
            self.text_search_page.go_to_search(self)
            self.home_page.wait_for_screen_ready()
            self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT.upper())
            self.home_page.log.info('Finding netflix series asset and focusing it in search results.')
            self.my_shows_page.search_deeplink_ott_program(self, program[0], year)
            self.home_page.nav_to_all_episodes_listview()
            self.ott_deeplinking_page.search_ott_provider_by_ui(self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
            self.ott_deeplinking_page.nav_to_more_option()
            self.wtw_page.wait_for_screen_ready()
            self.screen.refresh()
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
            if key == "guide":
                self.screen.base.press_guide(key_press="inputkeyevent")
                self.guide_assertions.verify_guide_title()
            elif key == "exit":
                self.screen.base.press_exit_button()
                time.sleep(15)
                self.screen.refresh()
                self.text_search_assertions.verify_view_mode(screen)
            else:
                self.text_search_page.press_bail_button_verify_screen(key=key, screen=screen)

    @pytestrail.case("C12940199")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.usefixtures("enable_video_providers")
    def test_12940199_series_sccreen_nextflix_launch_fail(self):
        """
        We removed ott_deeplink marker because, Netflix_originals feature is
        removed https://jira.xperi.com/browse/PARTDEFECT-11254
        """
        MOD_DATA = {"QUERY_RESPONSE_FAILURE_PROPERTIES": "exclusiveProviderObjectSearch",
                    "QUERY_FAILURE_TYPE_RANGES": "1,300"}
        self.home_page.screen.base.driver.modify_tcdui_conf(retain_original=False, **MOD_DATA)
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        netflix_strip = self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER
        asset_title = self.service_api.get_assets_titles_from_wtw_strip(netflix_strip, asset_index=1)
        self.text_search_page.go_to_search(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT.upper())
        self.home_page.log.info('Finding netflix series asset and focusing it in search results.')
        self.text_search_page.search_and_select(asset_title, asset_title, 2, select=False, watch_now=False)
        self.text_search_page.press_ok_button()
        self.my_shows_assertions.verify_series_screen(self)

    @pytest.mark.xray("FRUM-91306")
    @pytest.mark.test_stabilization
    @pytest.mark.wtw_openAPI_impacted
    def test_frum_91306_verify_netflix_source_type_from_search(self):
        netflix_strip = self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER
        asset_title = self.service_api.get_assets_titles_from_wtw_strip(netflix_strip, asset_index=1)
        self.text_search_page.go_to_search(self)
        self.text_search_page.input_search_text(asset_title)
        time.sleep(5)
        self.watchvideo_page.press_right_multiple_times(no_of_times=7)
        self.text_search_page.press_ok_button()
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_4)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM18_verify_4kcontent_search_result_streamlive(self):
        """
        https://jira.tivo.com/browse/FRUM-18
        """
        channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True, is_preview_offer_needed=True)
        if not channel:
            pytest.skip("Failed to get channel")
        channel_num = self.service_api.map_channel_number_to_currently_airing_offers(
            [channel], self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True), subtitle=True,
            genre="series")
        if not channel_num:
            pytest.skip("Failed to get channel")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel_num[0][1])
        program = self.guide_page.get_live_program_name(self)
        self.text_search_page.explicit_recording_from_search(self, program)
        self.home_page.nav_to_top_menuitem_in_list()
        self.program_options_page.select_play_from_liveTv()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_page.watch_video_for(60)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.search_ccu
    @pytest.mark.notapplicable(Settings.is_fire_tv() or Settings.is_apple_tv())
    @pytest.mark.usefixtures("enable_app")
    def test_t389366360_appbehaviour_onsearching_netflixmovie_while_netflix_disabled(self):
        """
        Verify Hydra app behaviour after selecting Netflix Exclusive content when Netflix app is disabled in Android settings.
        https://testrail.tivo.com//index.php?/tests/view/389366360:
        """
        self.screen.base.disable_app(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        self.home_page.log.info('Finding netflix movie in Netflix Originals strip on what to watch screen.')
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_screen_ready()
        self.wtw_assertions.verify_wtw_screen_title()
        self.wtw_page.nav_to_wtw_movies(self)
        asset_title = self.service_api.get_assets_titles_from_wtw_strip(self.wtw_labels.LBL_WTW_NETFLIX_MOVIE,
                                                                        feed_name="/screens/movies", asset_index=1)
        self.text_search_page.go_to_search(self)
        self.home_page.wait_for_screen_ready()
        self.text_search_assertions.verify_search_screen_title()
        self.home_page.log.info('Finding netflix movie asset and focusing it in search results.')
        self.text_search_page.search_and_select(asset_title, asset_title, 2, False)
        self.screen.base.press_enter(time=2500)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_SEARCH_SHORTCUT.upper())
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_ERROR_MSG_276)

    @pytest.mark.xray("FRUM-136521")
    @pytest.mark.frumos_19
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/vodOttActionDetails/content/ is supported since Hydra v1.19")
    def test_frum_136521_verify_socu_playback_starts_from_streaming_options_overlay(self, request, content_type):
        """
        Verifying that SOCU is started from Streaming Options Overlay
        /v1/vodOttActionDetails/content/ (OpenAPI requests).

        Xray:
            https://jira.xperi.com/browse/FRUM-121923 (Streaming Options overlay view - SOCU)
            https://jira.xperi.com/browse/FRUM-136521 (Search - InfoCard - All Streaming Options overlay - SOCU)
        """
        params = {"content_type": content_type, "find_appropriate": True, "is_startover": True, "is_subtitle": True}
        params["count"] = None
        channel_show = self.service_api.get_random_channel_from_guide_rows(**params)
        params["count"] = 1
        channel_show = self.service_api.get_random_filtered_channels_by_preview_offer(channel_show, **params)
        socu_provider_name = self.service_api.partner_info_search(
            socu_partner_id[Settings.mso], use_cached_response=True).get("partnerInfo")[0].get("vodAppName")
        self.home_page.go_to_search(self)
        self.text_search_page.search_and_select(channel_show[0][4].episode_title,
                                                f"{channel_show[0][1].title}: {channel_show[0][4].episode_title}")
        self.menu_page.select_strip(self.menu_labels.LBL_STREAMING_OPTIONS)
        self.menu_assertions.verify_all_streaming_options_overlay()
        self.menu_assertions.verify_all_streaming_options_overlay_items_view_compare_with_api(
            channel_show[0][1].content_id, _screen="other")
        self.menu_page.select_provider_on_all_streaming_options_overlay(
            channel_show[0][1].content_id, socu_partner_id[Settings.mso], self.menu_labels.LBL_STREAMING_OPTIONS_SUBSCR,
            socu_provider_name)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.watchvideo_assertions.verify_channel_number(channel_show[0][0])
        self.watchvideo_assertions.verify_show_title(channel_show[0][1].title)

    @pytest.mark.xray("FRUM-142679")
    @pytest.mark.frumos_19
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/vodOttActionDetails/content/ is supported since Hydra v1.19")
    def test_frum_142679_verify_vod_playback_starts_from_streaming_options_overlay(self, request, content_type):
        """
        Verifying that VOD is started from Streaming Options Overlay
        /v1/vodOttActionDetails/content/ (OpenAPI requests).

        Xray:
            https://jira.xperi.com/browse/FRUM-122685 (Streaming Options overlay view - VOD)
            https://jira.xperi.com/browse/FRUM-142679 (Search - InfoCard - All Streaming Options overlay - VOD)
        """
        status, result = self.vod_api.getOffer_playable_rating_movie()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        # VOD label needs to be retrieved
        self.service_api.partner_info_search(
            socu_partner_id[Settings.mso], use_cached_response=True).get("partnerInfo")[0].get("vodAppName")
        self.home_page.go_to_search(self)
        self.text_search_page.search_and_select(result.get("offer").title, result.get("offer").title,
                                                year=result.get("offer").movie_year)
        self.menu_page.select_strip(self.menu_labels.LBL_STREAMING_OPTIONS)
        self.menu_assertions.verify_all_streaming_options_overlay()
        self.menu_assertions.verify_all_streaming_options_overlay_items_view_compare_with_api(
            result.get("offer").content_id, _screen="other")
        self.menu_page.select_provider_on_all_streaming_options_overlay(
            result.get("offer").content_id, result.get("offer").content_id)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.watchvideo_assertions.verify_show_title(result.get("offer").title)

    @pytest.mark.xray('FRUM-141149')
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19))
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_141149_may_also_like_open_api_response_ui_response_comparison(self):
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(self.text_search_labels.LBL_SEARCH_TEXT_STRING,
                                                self.text_search_labels.LBL_EXPECTED_SEARCH_STRING)
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        self.text_search_assertions.verify_ui_and_open_api_response_match_for_may_also_like()

    @pytest.mark.xray('FRUM-141627')
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_141627_may_also_like_info_card(self):
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(self.text_search_labels.LBL_SEARCH_TEXT_STRING,
                                                self.text_search_labels.LBL_EXPECTED_SEARCH_STRING)
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        self.screen.base.long_press_enter()
        self.home_assertions.verify_infocard_on_long_key_press()
