import time
import pytest
from set_top_box.client_api.ott_deeplinking.conftest import setup_ott_deeplinking, enabling_video_providers
from set_top_box.client_api.vision_tester.conftest import setup_vision_tester
from set_top_box.client_api.my_shows.conftest import setup_adhoc_OTT_provider_and_functionality
from pytest_testrail.plugin import pytestrail
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger
from set_top_box.conf_constants import HydraBranches


@pytest.mark.usefixtures("enabling_video_providers")
@pytest.mark.usefixtures("setup_ott_deeplinking")
@pytest.mark.usefixtures('setup_vision_tester')
@pytest.mark.notapplicable(not Settings.is_vision_tester_enabled())
class Test_OTT_Deeplinking(object):
    log = Logger(__name__)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.platform_cert_smoke_test
    def test_launch_vudu_check_foreground_pkg(self):
        """Sample testcase to verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='VUDU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.VUDU_PACKAGE_NAME,
                                                                       "VUDU")

    @pytestrail.case("C12932396")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12932396_vudu_deeplinking_av_playback_movie(self):
        """Deeplink vudu app for movie, check audio/video motion and verify video title on the asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='VUDU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.VUDU_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        self.ott_deeplinking_page.verify_watch_button()
        self.watchvideo_page.watch_video_for(20)
        self.screen.base.press_enter()
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.platform_cert_smoke_test
    def test_launch_starz_check_foreground_pkg(self):
        """Sample testcase to verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='STARZ', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.STARZ_PACKAGE_NAME,
                                                                       "STARZ")

    @pytestrail.case("C12938881")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12938881_starz_deeplinking_av_playback_movie(self):
        """Deeplink starz app for movie check audio/video motion and verify video title on the asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='STARZ', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("BRAVEHEART", "Braveheart (1995)")
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.STARZ_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_resume_button()
        self.watchvideo_page.watch_video_for(20)
        self.screen.base.press_enter()
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.platform_cert_smoke_test
    def test_launch_googleplay_check_foreground_pkg(self):
        """Sample testcase to verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='GooglePlay', feedName='Movies', cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       GOOGLE_PLAY_PACKAGE_NAME2, "Google Play")

    @pytestrail.case("C14391657")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_14391657_googleplay_deeplinking_av_playback_movie(self):
        """Deeplink googleplay app for a movie, check audio/video motion and verify video title on the asset detail
        screen """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='GooglePlay', feedName='Movies', cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("D DAY", "D-Day (2019)")
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME2,
                                                          limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        self.ott_deeplinking_page.verify_play_trailer_button()
        self.watchvideo_page.watch_video_for(20)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.platform_cert_smoke_test
    def test_launch_netflix_check_foreground_pkg(self):
        """Sample testcase to verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Netflix', feedName='Movies', cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME,
                                                                       "Netflix")

    @pytestrail.case("C12932391")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12932391_netflix_deeplinking_av_playback_movie(self):
        """Deeplink Netflix app for movie and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Netflix', feedName='Movies', cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
        screentitle = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screentitle)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=20000)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_NETFLIX)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.platform_cert_smoke_test
    def test_launch_amazon_check_foreground_pkg(self):
        """Sample testcase to verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='amazonPrimeCS', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_AMAZON_PRIME_NEW)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.AMAZON_PACKAGE_NAME,
                                                                       "Prime Membership")

    @pytestrail.case("C12934354")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12934354_amazon_deeplinking_av_playback_movie(self):
        """Deeplink amazon app for movie, check audio/video motion and verify video title on the asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='amazonPrimeCS', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_AMAZON_PRIME_NEW)
        if not program:
            self.text_search_page.search_and_select("ABOUT ALEX", "About Alex (2014)")
        screentitle = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.replace_character(screentitle, ampersand=True)
        self.ott_deeplinking_page.select_amazon_option(self.my_shows_labels.LBL_PRIME_MEMBERSHIP,
                                                       self.my_shows_labels.LBL_AMAZON,
                                                       self.my_shows_labels.LBL_AMAZON_ICON,
                                                       self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.AMAZON_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_AMAZON_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_RENT_MOVIE in current_screen.upper():
            pytest.skip("Test requires Watch button to stream video")
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=10000)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_AMAZON)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.test_stabilization
    def test_launch_hulu_check_foreground_pkg(self):
        """Sample testcase to verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='HULU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.HULU_PACKAGE_NAME,
                                                                       "HULU")

    @pytestrail.case("C12932393")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    def test_12932393_hulu_shallowlinking_av_playback_movie(self):
        """Shallow-link hulu app for movie check audio/video motion and verify video title on the asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='HULU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("THE HERO", "Hero, The (2017)")
        screentitle = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screentitle)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.HULU_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_HULU_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
            current_screen_2 = self.vision_page.get_screen_text()
            if self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen_2.upper():
                pytest.skip("Test lands on the app home page - Shallowlink")
        elif self.ott_deeplinking_labels.LBL_HULU_RESUME_BUTTON in current_screen.upper() \
                or self.ott_deeplinking_labels.LBL_HULU_START_WATCHING in current_screen.upper():
            pytest.skip("Test lands on the previously deep-linked screen app home page")
        elif self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen.upper():
            pytest.skip("Test lands on the app home page - Shallowlink")
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback(timeout=10)
        self.ott_deeplinking_page.press_pause_button()
        time.sleep(5)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_HULU)

    @pytestrail.case("C12932392")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12932392_netflix_deeplinking_av_playback_series(self):
        """Deeplink Netflix app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Netflix', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("HOUSE OF CARDS", "House of Cards")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.screen.get_screen_dump_item('screentitle')
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback(timeout=10)
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=30000)
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_NETFLIX)

    @pytestrail.case("C12938093")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12938093_vudu_deeplinking_av_playback_series(self):
        """Deeplink vudu app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='VUDU', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("SHADOWS OF DEATH", "Shadows of Death, The")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.VUDU_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        if self.ott_deeplinking_page.verify_watch_button():
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytestrail.case("C12932394")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    def test_12932394_hulu_shallowlinking_av_playback_series(self):
        """Deeplink hulu app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='HULU', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("FAMILY GUY", "Family Guy")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.screen.get_screen_dump_item('screentitle')
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.HULU_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_HULU_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
            current_screen_2 = self.vision_page.get_screen_text()
            if self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen_2.upper():
                self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
        elif self.ott_deeplinking_labels.LBL_HULU_RESUME_BUTTON in current_screen.upper() \
                or self.ott_deeplinking_labels.LBL_HULU_START_WATCHING in current_screen.upper():
            self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
        elif self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen.upper():
            self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        time.sleep(5)
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_HULU)

    @pytestrail.case("C12934355")
    def test_12934355_amazon_deeplinking_av_playback_series(self):
        """Deeplink amazon app for series and check audio/video motion
           Removed marker for this TC due to Rent/purchase as asset
        """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='amazonCS', feedName="TV",
                                                                    cnt=4, select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_AMAZON_PRIME_NEW)
        if not program:
            self.text_search_page.search_and_select("LITTLE WOMEN", "Little Women: NY")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_AMAZON_ICON_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.screen.get_screen_dump_item('screentitle')
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        self.ott_deeplinking_page.select_amazon_option(self.my_shows_labels.LBL_PRIME_MEMBERSHIP,
                                                       self.my_shows_labels.LBL_AMAZON,
                                                       self.my_shows_labels.LBL_AMAZON_ICON,
                                                       self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.AMAZON_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_AMAZON_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_AMAZON)

    @pytestrail.case("C12830312")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12830312_googleplay_deeplinking_av_playback_series(self):
        """Deeplink googleplay app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='GooglePlay', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("NORTH AND SOUTH", "North and South")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME2,
                                                          limit=15)
        if self.ott_deeplinking_page.verify_play_trailer_button():
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytestrail.case("C12938882")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_12938882_starz_deeplinking_av_playback_series(self):
        """Deeplink starz app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='STARZ', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("BMF", "BMF")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.screen.get_screen_dump_item('screentitle')
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.STARZ_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_resume_button()
        self.watchvideo_page.watch_video_for(20)
        self.screen.base.press_enter()
        self.ott_deeplinking_page.verify_screen_title(episode_screen_title)

    @pytestrail.case("C12934353")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.may_also_like_ccu
    def test_12934353_deeplink_vudu_from_may_also_like_screen(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='VUDU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        ott = self.ott_deeplinking_assertions.verify_ott_icon_existence(self.home_labels.
                                                                        LBL_WHAT_TO_WATCH_VUDU_FANDANGO_ICON)
        if ott:
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.VUDU_PACKAGE_NAME, limit=15)
            self.ott_deeplinking_page.verify_watch_button()
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_assertions.verify_gallery_screen(self)

    @pytestrail.case("C20933933")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.may_also_like_ccu
    def test_20933933_deeplink_netflix_from_may_also_like_screen(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Netflix', feedName='Movies', cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        ott = self.ott_deeplinking_assertions.verify_ott_icon_existence(self.home_labels.LBL_WHAT_TO_WATCH_NETFLIX_ICON)
        if ott:
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_assertions.verify_gallery_screen(self)

    @pytestrail.case("C20933936")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.may_also_like_ccu
    def test_20933936_deeplink_amazon_from_may_also_like_screen(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='amazonPrimeCS', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_AMAZON_PRIME_NEW)
        if not program:
            self.text_search_page.search_and_select("ABOUT ALEX", "About Alex (2014)")
        screentitle = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.replace_character(screentitle, ampersand=True)
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        ott = self.ott_deeplinking_assertions.verify_ott_icon_existence(self.home_labels.LBL_WHAT_TO_WATCH_AMAZON_ICON)
        if ott:
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_AMAZON_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.AMAZON_PACKAGE_NAME, limit=15)
            current_screen = self.vision_page.get_screen_text()
            if self.ott_deeplinking_labels.LBL_AMAZON_PROFILE_PAGE in current_screen.upper():
                self.screen.base.press_enter()
            if not self.watchvideo_page.watch_video_for(20):
                self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
            else:
                self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_assertions.verify_gallery_screen(self)

    @pytestrail.case("C12938091")
    def test_12938091_wtw_netflix_originals(self):
        """
        Verifies that "Netflix Original" strip is displayed and check, Netflix provider is available for select asset
        Netflix_originals feature is removed https://jira.xperi.com/browse/PARTDEFECT-11254
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.navigate_to_wtw_strip(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER, 'in')
        self.wtw_assertions.verify_current_strip_title(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER)
        self.wtw_assertions.verify_netflix_icon_on_wtw_screen()
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME,
                                                                       "Netflix")

    @pytestrail.case("C20933935")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    @pytest.mark.may_also_like_ccu
    def test_20933935_deeplink_hulu_from_may_also_like_screen(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='HULU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("THE HERO", "Hero, The (2017)")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        ott = self.ott_deeplinking_assertions.verify_ott_icon_existence(self.home_labels.LBL_WHAT_TO_WATCH_HULU_ICON)
        if ott:
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.HULU_PACKAGE_NAME, limit=15)
            current_screen = self.vision_page.get_screen_text()
            if self.ott_deeplinking_labels.LBL_HULU_PROFILE_PAGE in current_screen.upper():
                self.screen.base.press_enter()
                current_screen_2 = self.vision_page.get_screen_text()
                if self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen_2.upper():
                    self.ott_deeplinking_assertions.verify_hulu_screen(self,
                                                                       self.apps_and_games_labels.HULU_PACKAGE_NAME)
            elif self.ott_deeplinking_labels.LBL_HULU_RESUME_BUTTON in current_screen.upper() \
                    or self.ott_deeplinking_labels.LBL_HULU_START_WATCHING in current_screen.upper():
                self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
            elif self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen.upper():
                self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_assertions.verify_gallery_screen(self)

    @pytestrail.case("C20933934")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.may_also_like_ccu
    def test_20933934_deeplink_starz_from_may_also_like_screen(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='STARZ', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("BRAVEHEART", "Braveheart (1995)")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        ott = self.ott_deeplinking_assertions.verify_ott_icon_existence(self.home_labels.LBL_WHAT_TO_WATCH_STARZ_ICON)
        if ott:
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
            self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.STARZ_PACKAGE_NAME, limit=15)
            self.ott_deeplinking_page.verify_resume_button()
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_assertions.verify_gallery_screen(self)

    @pytestrail.case("C20933937")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.may_also_like_ccu
    def test_20933937_deeplink_google_play_from_may_also_like_screen(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='GooglePlay', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("D DAY", "D-Day 360 (2014)")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        ott = self.ott_deeplinking_assertions.verify_ott_icon_existence(self.home_labels.LBL_WTW_GOOGLE_PLAY_ICON)
        if ott:
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
            self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME2,
                                                              limit=15)
            self.ott_deeplinking_page.verify_play_trailer_button()
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_assertions.verify_gallery_screen(self)

    @pytestrail.case("C20941216")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_20941216_verify_hulu_app_is_not_installed(self):
        """To verify HULU application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.HULU_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='HULU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("THE HERO", "Hero, The (2017)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           HULU_PACKAGE_NAME, "HULU")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           GOOGLE_PLAY_PACKAGE_NAME, "GooglePlay")
            self.ott_deeplinking_page.verify_install_button()

    @pytestrail.case("C20942227")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    def test_20942227_verify_starz_app_is_not_installed(self):
        """To verify STARZ application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.STARZ_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='STARZ', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("BRAVEHEART", "Braveheart (1995)")
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           STARZ_PACKAGE_NAME, "STARZ")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           GOOGLE_PLAY_PACKAGE_NAME, "GooglePlay")
            self.ott_deeplinking_page.verify_install_button()

    @pytestrail.case("C20943730")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    def test_20943730_verify_vudu_app_is_not_installed(self):
        """To verify VUDU application is not installed on the device"""
        webkit_name = self.apps_and_games_labels.VUDU_WEBKIT_NAME
        result = self.service_api.check_groups_enabled(webkit_name)
        if not result:
            pytest.skip("webkit is not added. Hence skipping")
        result1 = self.screen.base.is_app_installed(self.apps_and_games_labels.VUDU_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='VUDU', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        if result1:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           VUDU_PACKAGE_NAME, "VUDU")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           GOOGLE_PLAY_PACKAGE_NAME, "GooglePlay")
            self.ott_deeplinking_page.verify_install_button()

    @pytestrail.case("C20943732")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    def test_20943732_verify_netflix_app_is_not_installed(self):
        webkit_name = self.ott_deeplinking_labels.NETFLIX_WEBKIT_NAME
        result = self.service_api.check_groups_enabled(webkit_name)
        if not result:
            pytest.skip("webkit is not added. Hence skipping")
        result1 = self.screen.base.is_app_installed(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Netflix', feedName='Movies', cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        if result1:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           NETFLIX_PACKAGE_NAME, "Netflix")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           GOOGLE_PLAY_PACKAGE_NAME, "GooglePlay")
            self.ott_deeplinking_page.verify_install_button()

    @pytestrail.case("C20943733")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.xray("FRUM-1299")
    @pytest.mark.test_stabilization
    def test_20943733_verify_amazon_app_is_not_installed(self):
        webkit_name = self.ott_deeplinking_labels.AMAZON_WEBKIT_NAME
        result = self.service_api.check_groups_enabled(webkit_name)
        if not result:
            pytest.skip("webkit is not added. Hence skipping")
        result1 = self.screen.base.is_app_installed(self.apps_and_games_labels.AMAZON_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Amazon', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_AMAZON_ICON_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT ALEX", "About Alex (2014)")
        self.ott_deeplinking_page.select_amazon_option(self.my_shows_labels.LBL_PRIME_MEMBERSHIP,
                                                       self.my_shows_labels.LBL_AMAZON,
                                                       self.my_shows_labels.LBL_AMAZON_ICON,
                                                       self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        if result1:
            try:
                self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                               AMAZON_PACKAGE_NAME, "Prime video")
            except Exception:
                self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                               AMAZON_PACKAGE_NAME, "Prime Membership")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           GOOGLE_PLAY_PACKAGE_NAME, "GooglePlay")
            self.ott_deeplinking_page.verify_install_button()

    @pytestrail.case("C20949043")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_20949043_uncheck_vudu_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='VUDU', no_partnerIdCount=False)
            if program:
                break
        if program:
            self.menu_page.check_uncheck_app(self, ["Vudu"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Vudu", self.my_shows_labels.LBL_VUDU_ICON)
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            self.menu_page.check_uncheck_app(self, ["Vudu"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select("ABOUT ALEX", "About Alex (2014)")
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Vudu", self.my_shows_labels.LBL_VUDU_ICON)

    @pytestrail.case("C12938092")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_12938092_uncheck_netflix_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Netflix',
                                                                   no_partnerIdCount=False)
            if program:
                break
        if program:
            self.menu_page.check_uncheck_app(self, ["Netflix"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Netflix",
                                                                         self.my_shows_labels.LBL_NETFLIX_ICON)
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            self.menu_page.check_uncheck_app(self, ["Netflix"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Netflix",
                                                                         self.my_shows_labels.LBL_NETFLIX_ICON)

    @pytestrail.case("C20949865")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_20949865_uncheck_hulu_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='HULU', no_partnerIdCount=False)
            if program:
                break
        if program:
            self.menu_page.check_uncheck_app(self, ["Hulu"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Hulu", self.my_shows_labels.LBL_HULU_ICON)
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            self.menu_page.check_uncheck_app(self, ["Hulu"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select("THE HERO", "Hero, The (2017)")
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Hulu", self.my_shows_labels.LBL_HULU_ICON)

    @pytestrail.case("C20950947")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_20950947_uncheck_starz_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='STARZ', no_partnerIdCount=False)
            if program:
                break
        if program:
            self.menu_page.check_uncheck_app(self, ["STARZ"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("starz", self.ott_deeplinking_labels.
                                                                         LBL_STARZ_ICON)
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            self.menu_page.check_uncheck_app(self, ["STARZ"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select("BRAVEHEART", "Braveheart (1995)")
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("starz", self.ott_deeplinking_labels.
                                                                         LBL_STARZ_ICON)

    @pytestrail.case("C20950948")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_20950948_uncheck_googleplay_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='GooglePlay',
                                                                   no_partnerIdCount=False)
            if program:
                break
        if program:
            self.menu_page.check_uncheck_app(self, ["Google Play Movies and TV"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
            self.ott_deeplinking_assertions. \
                verify_app_provider_in_strip("Google Play Movies and TV",
                                             self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            self.menu_page.check_uncheck_app(self, ["Google Play Movies and TV"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select("D DAY", "D-Day 360 (2014)")
            self.ott_deeplinking_assertions. \
                verify_app_provider_in_strip("Google Play Movies and TV",
                                             self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)

    @pytestrail.case("C20950946")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_20950946_uncheck_amazon_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='amazonPrimeCS',
                                                                   no_partnerIdCount=False)
            if program:
                break
        if program:
            self.menu_page.check_uncheck_app(self, ["Prime Membership", "Prime Video"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Prime Membership", "Prime Video",
                                                                         self.my_shows_labels.LBL_AMAZON_ICON,
                                                                         self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            self.menu_page.check_uncheck_app(self, ["Prime Membership", "Prime Video"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select("ABOUT ALEX", "About Alex (2014)")
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Prime Membership", "Prime Video",
                                                                         self.my_shows_labels.LBL_AMAZON_ICON,
                                                                         self.my_shows_labels.LBL_AMAZON_PRIME_ICON)

    @pytestrail.case("C20951058")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_20951058_search_vudu_live_and_upcoming(self):
        """To verify Vudu app can be launched from "Upcoming/Live & Upcoming" option"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='VUDU', feedName="On TV Today", cnt=4)
        if not program:
            pytest.skip("Test requires OTT program.")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Vudu")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_VUDU_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       VUDU_PACKAGE_NAME, "VUDU")

    @pytestrail.case("C20951059")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20951059_search_netflix_live_and_upcoming(self):
        """To verify Netflix app can be launched from "Upcoming/Live & Upcoming" option"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Netflix', feedName="On TV Today", cnt=4)
        if not program:
            pytest.skip("Test requires OTT program.")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Netflix")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       NETFLIX_PACKAGE_NAME, "Netflix")

    @pytestrail.case("C20951081")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20951081_search_googleplay_live_and_upcoming(self):
        """To verify GooglePlay app can be launched from "Upcoming/Live & Upcoming" option"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='GooglePlay', feedName="On TV Today",
                                                                    cnt=4)
        if not program:
            pytest.skip("Test requires OTT program.")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Google Play Movies and TV")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       GOOGLE_PLAY_PACKAGE_NAME2, "GooglePlay")

    @pytestrail.case("C20951385")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20951385_search_hulu_live_and_upcoming(self):
        """To verify HUlu app can be launched from "Upcoming/Live & Upcoming" option"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='HULU', feedName="On TV Today",
                                                                    cnt=4)
        if not program:
            pytest.skip("Test requires OTT program.")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Hulu")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_HULU_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.HULU_PACKAGE_NAME,
                                                                       "HUlu")

    @pytestrail.case("C20951913")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20951913_search_amazon_live_and_upcoming(self):
        """To verify Amazon app can be launched from "Upcoming/Live & Upcoming" option"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='amazonCS', feedName="On TV Today",
                                                                    cnt=4)
        if not program:
            pytest.skip("Test requires OTT program.")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_AMAZON_ICON_PREVIEW_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Prime Video")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.ott_deeplinking_page.verify_and_nav_prime_video_or_membership_in_strip(self.my_shows_labels.
                                                                                        LBL_AMAZON_ICON,
                                                                                        self.my_shows_labels.
                                                                                        LBL_AMAZON_PRIME_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.ott_deeplinking_page.select_amazon_image_strip()
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.AMAZON_PACKAGE_NAME,
                                                                       "Amazon")

    @pytestrail.case("C20952463")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20952463_search_starz_live_and_upcoming(self):
        """To verify HUlu app can be launched from "Upcoming/Live & Upcoming" option"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='starz', feedName="On TV Today",
                                                                    cnt=4)
        if not program:
            pytest.skip("Test requires OTT program.")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False)
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.STARZ_PACKAGE_NAME,
                                                                       "Starz")

    @pytestrail.case("C12938094")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12938094_vudu_deeplinking_episode(self):
        """Deeplink vudu app for episode and check audio/video motion"""
        program = self.service_api.get_show_with_ott(ott_partner_id="tivo:pt.4576", episodic=True, movie=False,
                                                     live=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(f"{program[0][7]}", f"{program[0][2]}: {program[0][7]}")
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.VUDU_PACKAGE_NAME, limit=15)
        episode_screen_title = program[0][2]
        if self.ott_deeplinking_page.check_trailer_button_exists():
            self.screen.base.press_enter()
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
            self.ott_deeplinking_page.press_pause_button()
            self.wtw_page.wait_for_screen_ready(timeout=30000)
            self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                         region=self.vision_page.locators.SCREEN_TITLE_OF_VUDU)
        else:
            self.ott_deeplinking_page.verify_screen_title(episode_screen_title)

    @pytestrail.case("C12934352")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12934352_deeplink_vudu_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.4576",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON)
        self.log.info("Navigating to more option")
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.VUDU_PACKAGE_NAME,
                                                                       "VUDU")

    @pytestrail.case("C20957934")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20957934_deeplink_netflix_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.3455",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME,
                                                                       "NETFLIX")

    @pytestrail.case("C20957938")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20957938_deeplink_googleplay_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1006173",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       GOOGLE_PLAY_PACKAGE_NAME2, "GooglePlay")

    @pytestrail.case("C19783974")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_19783974_googleplay_deeplinking_episode(self):
        """Deeplink GooglePlay app for episode and check audio/video motion"""
        program = self.service_api.get_show_with_ott(ott_partner_id="tivo:pt.1006173", episodic=True, movie=False,
                                                     live=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(f"{program[0][7]}", f"{program[0][2]}: {program[0][7]}")
        episode_screen_title = program[0][2]
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME2,
                                                          limit=15)
        if self.ott_deeplinking_page.check_trailer_button_exists():
            self.screen.base.press_enter()
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
            self.ott_deeplinking_page.press_pause_button()
            self.wtw_page.wait_for_screen_ready(timeout=30000)
            self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                         region=self.vision_page.locators.SCREEN_TITLE_OF_GOOGLE_PLAY)
        else:
            self.ott_deeplinking_page.verify_screen_title(episode_screen_title)

    @pytestrail.case("C12932395")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12932395_hulu_shallowing_episode(self):
        """Deeplink Hulu app for episode and verify screen title"""
        program = self.service_api.get_show_with_ott(ott_partner_id="tivo:pt.3820", episodic=True, movie=False,
                                                     live=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(f"{program[0][7]}", f"{program[0][2]}: {program[0][7]}")
        episode_screen_title = program[0][2]
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.HULU_PACKAGE_NAME,
                                                          limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_HULU_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
            current_screen_2 = self.vision_page.get_screen_text()
            if self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen_2.upper():
                self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
        elif self.ott_deeplinking_labels.LBL_HULU_RESUME_BUTTON in current_screen.upper() \
                or self.ott_deeplinking_labels.LBL_HULU_START_WATCHING in current_screen.upper():
            self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
        elif self.ott_deeplinking_labels.LBL_HULU_HOME_PAGE in current_screen.upper():
            self.ott_deeplinking_assertions.verify_hulu_screen(self, self.apps_and_games_labels.HULU_PACKAGE_NAME)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_HULU)

    @pytestrail.case("C12932388")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12932388_netflix_deeplinking_av_playback_episode(self):
        """Deeplink Netflix app for episode and check audio/video motion"""
        program = self.service_api.get_show_with_ott(ott_partner_id="tivo:pt.3455", episodic=True, movie=False,
                                                     live=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(f"{program[0][7]}", f"{program[0][2]}: {program[0][7]}")
        episode_screen_title = program[0][2]
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=30000)
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_NETFLIX)

    @pytestrail.case("C12934356")
    @pytest.mark.test_stabilization
    def test_12934356_amazon_deeplinking_av_playback_episode(self):
        """Deeplink Amazon app for episode and check audio/video motion
           Removed marker for this TC due to Rent/purchase as asset
        """
        program = self.service_api.get_show_with_ott(ott_partner_id="tivo:pt.1006010", episodic=True, movie=False,
                                                     live=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(f"{program[0][7]}", f"{program[0][2]}: {program[0][7]}")
        episode_screen_title = program[0][2]
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_AMAZON_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.AMAZON_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_AMAZON_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_AMAZON)

    @pytestrail.case("C12938883")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12938883_starz_deeplinking_av_playback_episode(self):
        """Deeplink Starz app for episode and check audio/video motion"""
        program = self.service_api.get_show_with_ott(ott_partner_id="tivo:pt.1005006", episodic=True, movie=False,
                                                     live=False)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(f"{program[0][7]}", f"{program[0][2]}: {program[0][7]}")
        episode_screen_title = program[0][2]
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.STARZ_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_resume_button()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.screen.base.press_enter()
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_STARZ)

    @pytestrail.case("C20957933")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20957933_deeplink_hulu_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.3820",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.HULU_PACKAGE_NAME,
                                                                       "HULU")

    @pytestrail.case("C20957935")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20957935_deeplink_amazon_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1006010",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_AMAZON_ICON_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.ott_deeplinking_page.select_amazon_option(self.my_shows_labels.LBL_PRIME_MEMBERSHIP,
                                                       self.my_shows_labels.LBL_AMAZON,
                                                       self.my_shows_labels.LBL_AMAZON_ICON,
                                                       self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.AMAZON_PACKAGE_NAME,
                                                                       "Prime video")

    @pytestrail.case("C20957936")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20957936_deeplink_starz_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1005006",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.STARZ_PACKAGE_NAME,
                                                                       "STARZ")

    @pytestrail.case("C20959521")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959521_deeplink_netflix_from_upcoming_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.3455",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Netflix")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       NETFLIX_PACKAGE_NAME, "Netflix")

    @pytestrail.case("C12938251")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12938251_deeplink_vudu_from_upcoming_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.4576",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Vudu")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_VUDU_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.VUDU_PACKAGE_NAME,
                                                                       "VUDU")

    @pytestrail.case("C20959525")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959525_deeplink_googleplay_from_upcoming_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1006173",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Google Play Movies and TV")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       GOOGLE_PLAY_PACKAGE_NAME2, "GooglePlay")

    @pytestrail.case("C20959524")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959524_deeplink_hulu_from_upcoming_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.3820",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Hulu")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_HULU_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.HULU_PACKAGE_NAME,
                                                                       "HULU")

    @pytestrail.case("C20959522")
    @pytest.mark.test_stabilization
    @pytest.mark.ott_deeplink_4
    def test_20959522_deeplink_amazon_from_upcoming_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1006010",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_AMAZON_ICON_PREVIEW_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Prime Video")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.ott_deeplinking_page.select_amazon_option(self.my_shows_labels.LBL_PRIME_MEMBERSHIP,
                                                       self.my_shows_labels.LBL_AMAZON,
                                                       self.my_shows_labels.LBL_AMAZON_ICON,
                                                       self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.AMAZON_PACKAGE_NAME,
                                                                       "Prime video")

    @pytestrail.case("C20959523")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959523_deeplink_starz_from_upcoming_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1005006",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="STARZ")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.STARZ_PACKAGE_NAME,
                                                                       "STARZ")

    @pytestrail.case("C20959527")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959527_search_and_nav_vudu_wtw_upcoming(self):
        """Deeplink Vudu app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='VUDU', count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_VUDU_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Vudu")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_VUDU_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_VUDU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       VUDU_PACKAGE_NAME, "VUDU")

    @pytestrail.case("C12938252")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12938252_search_and_nav_googleplay_wtw_upcoming(self):
        """Deeplink GooglePlay app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='GooglePlay', count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode():
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Google Play Movies and TV")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_GOOGLE_PLAY_NEW_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       GOOGLE_PLAY_PACKAGE_NAME2, "GooglePlay")

    @pytestrail.case("C20959526")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959526_search_and_nav_amazon_wtw_upcoming(self):
        """Deeplink Amazon app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        program = False
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='amazonCS',
                                                                   count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_AMAZON_ICON_PREVIEW_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Prime Video")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_AMAZON_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.ott_deeplinking_page.select_amazon_option(self.my_shows_labels.LBL_PRIME_MEMBERSHIP,
                                                       self.my_shows_labels.LBL_AMAZON,
                                                       self.my_shows_labels.LBL_AMAZON_ICON,
                                                       self.my_shows_labels.LBL_AMAZON_PRIME_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       AMAZON_PACKAGE_NAME, "Prime Video")

    @pytestrail.case("C20959529")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959529_search_and_nav_netflix_wtw_upcoming(self):
        """Deeplink Netflix app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        program = False
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Netflix',
                                                                   count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_NETFLIX_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Netflix")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       NETFLIX_PACKAGE_NAME, "Netflix")

    @pytestrail.case("C12932389")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_12932389_search_and_nav_starz_wtw_upcoming(self):
        """Deeplink Starz app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        program = False
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='STARZ',
                                                                   count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.ott_deeplinking_labels.LBL_STARZ_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="STARZ")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.my_shows_page.select_strip(self.ott_deeplinking_labels.LBL_STARZ_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       STARZ_PACKAGE_NAME, "STARZ")

    @pytestrail.case("C20959530")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_20959530_search_and_nav_hulu_wtw_upcoming(self):
        """Deeplink Hulu app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        program = False
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='HULU',
                                                                   count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_HULU_PREVIEW_IMAGE_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Hulu")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_HULU_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HULU_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       HULU_PACKAGE_NAME, "HULU")

    @pytest.mark.vt_core_feature
    @pytest.mark.xray("FRUM-1316")
    def test_20959739_verify_playback_status_after_returning_from_other_apps(self):
        """
        We removed ott_deeplink marker, as this test case is not belongs to ott_deeplinking
        https://jira.xperi.com/browse/BZSTREAM-9787
        """
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.verify_screen_title(self)
        self.apps_and_games_assertions.start_google_play_movies_and_tv_app(self)
        self.ott_deeplinking_page.select_any_asset()
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LOC_PLAYER_TRAILER_BUTTON in current_screen.upper():
            self.ott_deeplinking_page.verify_play_trailer_button()
        else:
            self.screen.base.press_back()
            self.ott_deeplinking_page.search_for_asset_nav_right(self.ott_deeplinking_labels.LOC_PLAYER_TRAILER_BUTTON,
                                                                 iter_num=10)
        self.watchvideo_page.watch_video_for(20)
        self.screen.base.press_home()
        self.apps_and_games_page.go_to_apps_and_games(self)
        self.apps_and_games_assertions.verify_screen_title(self)
        self.apps_and_games_assertions.start_google_play_movies_and_tv_app(self)
        self.vision_page.verify_playback_status_after_returning_from_other_apps()

    @pytest.mark.ott_deeplink
    @pytest.mark.xray("FRUM-84183")
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.ott_deeplink_3
    def test_84183_launch_tubi_check_foreground_pkg(self):
        """To verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Tubi', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.apps_and_games_labels.LBL_TUBITV_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.apps_and_games_labels.LBL_TUBITV_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.TUBITV_PACKAGE_NAME,
                                                                       "TUBITV")

    @pytest.mark.xray("FRUM-57599")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_57599_tubi_deeplinking_av_playback_movie(self):
        """Deeplink Tubi TV app for movie, check audio/video motion and verify video title on the asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Tubi', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.apps_and_games_labels.LBL_TUBITV_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("ABOUT TIME", "About Time (2013)")
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.apps_and_games_labels.LBL_TUBITV_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.TUBITV_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        self.ott_deeplinking_page.verify_watch_button()
        self.watchvideo_page.watch_video_for(20)
        self.screen.base.press_enter()
        time.sleep(5)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-57604")
    def test_57604_Tubi_deeplinking_av_playback_series(self):
        """Deeplink tubi TV app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Tubi', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.apps_and_games_labels.LBL_TUBITV_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("ONE-PUNCH MAN", "One-Punch Man")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.apps_and_games_labels.LBL_TUBITV_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        preview_pane_text = self.screen.get_screen_dump_item('previewPane')
        epi_title = preview_pane_text["episodeTitle"].split(";")[-1]
        episode_screen_title = epi_title.strip()
        self.log.info("Episode screen tittle is:{}".format(episode_screen_title))
        self.my_shows_page.select_strip(self.apps_and_games_labels.LBL_TUBITV_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.TUBITV_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback(timeout=10)
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=30000)
        self.vision_page.verify_screen_contains_text(episode_screen_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_TUBI)

    @pytest.mark.xray("FRUM-84212")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.platform_cert_smoke_test
    def test_84212_launch_disneyPlus_check_foreground_pkg(self):
        """To verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Disney+', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(
            self.apps_and_games_labels.DISNEYPLUS_PACKAGE_NAME,
            "Disney+")

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-57613")
    @pytest.mark.test_stabilization
    def test_57613_verify_tubi_app_is_not_installed(self):
        """To verify Tubi TV application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.TUBITV_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Tubi', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.apps_and_games_labels.LBL_TUBITV_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("HONEYDRIPPER", "Honeydripper (2007)")
        self.my_shows_page.select_strip(self.apps_and_games_labels.LBL_TUBITV_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           TUBITV_PACKAGE_NAME, "TUBITV")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           GOOGLE_PLAY_PACKAGE_NAME, "GooglePlay")
            self.ott_deeplinking_page.verify_install_button()

    @pytest.mark.xray("FRUM-59957")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_59957_verify_disneyPlus_app_is_not_installed(self):
        """To verify disneyPlus application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.DISNEYPLUS_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Disney+', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("HIDDEN FIGURES", "Hidden Figures (2016)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           DISNEYPLUS_PACKAGE_NAME, "Disney+")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                           GOOGLE_PLAY_PACKAGE_NAME, "GooglePlay")
            self.ott_deeplinking_page.verify_install_button()

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-57622")
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_57622_uncheck_tubi_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='TUBITV', no_partnerIdCount=False)
            if program:
                break
            else:
                self.log.info(" Program not found using service api hence hardcoding it.")
                program = [("Beast Mode", 2020)]

        self.menu_page.check_uncheck_app(self, ["Tubi"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("TUBITV",
                                                                     self.apps_and_games_labels.LBL_TUBITV_ICON)

    @pytest.mark.xray("FRUM-59963")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_59963_deeplink_disneyPlus_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1006247",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(
            self.apps_and_games_labels.DISNEYPLUS_PACKAGE_NAME,
            "Disney+")

    @pytest.mark.xray("FRUM-59967")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_59967_uncheck_disneyPlus_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Disney+',
                                                                   no_partnerIdCount=False)
            if program:
                break
        if program:
            self.menu_page.check_uncheck_app(self, ["Disney+"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Disney+",
                                                                         self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            self.menu_page.check_uncheck_app(self, ["Disney+"], check=False)
            self.text_search_page.go_to_search(self)
            self.text_search_page.search_and_select("BRAVEHEART", "Braveheart (1995)")
            self.ott_deeplinking_assertions.verify_app_provider_in_strip("Disney+",
                                                                         self.my_shows_labels.LBL_DISNEYPLUS_ICON)

    @pytest.mark.xray("FRUM-59968")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_59968_deeplink_disneyPlus_from_upcoming_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1006247",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Disney+")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       DISNEYPLUS_PACKAGE_NAME, "Disney+")

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.xray("FRUM-59953")
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_59953_disneyplus_deeplinking_av_playback_movie(self):
        """Deeplink DisneyPlus app for movie, check audio/video motion and verify video title on the asset detail
        screen """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Disney+', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("WHO FRAMED ROGER RABBIT", "Who Framed Roger Rabbit (1988)")
        screenTitle = self.guide_page.get_screen_title()
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screenTitle)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.DISNEYPLUS_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_DISNEYPLUS_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=10000)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_DISNEYPLUS)

    @pytest.mark.xray("FRUM-59956")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    def test_59956_disneyPlus_deeplinking_av_playback_series(self):
        """Deeplink disneyPlus app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Disney+', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("JESSIE", "Jessie")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.ott_deeplinking_page.screen_title()
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        episode_title = episode_screen_title.title()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.DISNEYPLUS_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_DISNEYPLUS_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=20000)
        self.vision_page.verify_screen_contains_text(episode_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_SERIES_DISNEYPLUS)

    @pytest.mark.xray("FRUM-59962")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_59962_search_and_nav_disney_plus_wtw_upcoming(self):
        """Deeplink Disney Plus app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Disney+', count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_DISNEYPLUS_PREVIEW_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Disney+")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISNEYPLUS_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       DISNEYPLUS_PACKAGE_NAME, "Disney+")

    @pytest.mark.xray("FRUM-84225")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.platform_cert_smoke_test
    def test_84225_launch_mgm_plus_check_foreground_pkg(self):
        """To verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='MGM_PLUS', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_MGM_PLUS_PREVIEW_IMAGE_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_MGM_PLUS_ICON_NEW)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.MGM_PLUS_PACKAGE_NAME,
                                                                       "MGM_PLUS")

    @pytest.mark.xray("FRUM-84229")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.platform_cert_smoke_test
    def test_launch_peacock_check_foreground_pkg(self):
        """Sample testcase to verify Peacock OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Peacock', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.PEACOCK_PACKAGE_NAME,
                                                                       "Peacock")

    @pytest.mark.xray("FRUM-57997")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_57997_deeplink_Peacock_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.1006270",
                                                                 feed_name="/predictions",
                                                                 record=False,
                                                                 is_pfrc=True)
        self.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.PEACOCK_PACKAGE_NAME,
                                                                       "Peacock")

    @pytest.mark.xray("FRUM-59972")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_59972_mgm_plus_deeplinking_av_playback_movie(self):
        """Deeplink mgm+ app for movie, check audio/video motion and verify video title on the asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='MGM_PLUS', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_MGM_PLUS_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("WRATH OF MAN", "Wrath of man, (2020)")
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_MGM_PLUS_ICON_NEW)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.MGM_PLUS_PACKAGE_NAME, limit=15)
        if self.ott_deeplinking_page.verify_watch_button():
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytest.mark.xray("FRUM-57988")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_57988_peacock_deeplinking_av_playback_series(self):
        """Deeplink peacock app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Peacock', feedName="TV",
                                                                    cnt=4, skip=False, select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("ONE-PUNCH MAN", "One-Punch Man")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.ott_deeplinking_page.screen_title()
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        episode_title = episode_screen_title.title()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.PEACOCK_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_DISNEYPLUS_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.screen.base.press_right()
        self.vision_page.verify_screen_contains_text(episode_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_SERIES_PECOCK)

    @pytest.mark.xray("FRUM-57985")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_57985_Peacock_deeplinking_av_playback_movie(self):
        """Deeplink Peacock app for movie, check audio/video motion and verify video title on the asset detail
        screen """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Peacock', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("Beast mode", "Beast Mode (2020)")
        screenTitle = self.guide_page.get_screen_title()
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screenTitle)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.PEACOCK_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_DISNEYPLUS_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(170)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.screen.base.press_right()
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_PEACOCK)

    @pytest.mark.xray("FRUM-58003")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_4
    @pytest.mark.test_stabilization
    @pytest.mark.may_also_like_ccu
    def test_58003_deeplink_peacock_from_may_also_like_screen(self):
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Peacock', feedName="Movies", cnt=4,
                                                                    skip=False, select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("Beast mode", "Beast Mode (2020)")
        screentitle = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.replace_character(screentitle, ampersand=True)
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.ott_deeplinking_assertions.verify_gallery_screen(self)
        ott = self.ott_deeplinking_assertions.verify_ott_icon_existence(self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        if ott:
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.PEACOCK_PACKAGE_NAME, limit=15)
            current_screen = self.vision_page.get_screen_text()
            if self.ott_deeplinking_labels.LBL_DISNEYPLUS_PROFILE_PAGE in current_screen.upper():
                self.screen.base.press_enter()
            self.watchvideo_page.watch_video_for(170)
            self.vision_page.verify_av_playback()
            self.ott_deeplinking_page.press_pause_button()
            self.screen.base.press_right()
            self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                         region=self.vision_page.locators.SCREEN_TITLE_OF_PEACOCK)
        else:
            self.ott_deeplinking_assertions.verify_gallery_screen(self)

    @pytest.mark.xray("FRUM-57994")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_57994_verify_Peacock_app_is_not_installed(self):
        """To verify Peacock application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.PEACOCK_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Peacock', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("PUPPET MASTER", "Puppet Master (1989)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.PEACOCK_PACKAGE_NAME,
                "Peacock")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.xray("FRUM-57992")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_skip
    @pytest.mark.test_stabilization
    def test_57992_search_and_nav_peacock_wtw_upcoming(self):
        """Deeplink Peacock app from WTW "Upcoming/Live & Upcoming" option"""
        feed_list = self.wtw_page.get_feed_name(feedtype="On TV Today")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Peacock', count=-1, raw=True)
            if program:
                carousel = feed
                break
        if not program:
            pytest.skip("Test requires OTT program.")
        carousel_caption = self.wtw_page.get_carousel_caption(carousel)
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_ON_TV_TODAY, check=True)
        self.wtw_page.navigate_to_carousel(self, carousel_caption)
        if not self.wtw_page.check_carousel_focused(carousel_caption):
            self.wtw_page.quick_update_wtw()
        if self.wtw_page.check_carousel_focused(carousel_caption):
            self.ott_deeplinking_page.nav_to_show_on_wtw_strip(program, use_preview_panel=True)
        else:
            pytest.skip("No live OTT show available")
        if self.my_shows_page.is_series_screen_view_mode(refresh=True):
            self.ott_deeplinking_page.select_live_and_upcoming()
            self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_PEACOCK_PREVIEW_ICON,
                                                          jumpSeason_option=False, strip_to_check="Upcoming",
                                                          provider="Peacock")
            self.screen.base.press_enter()
        else:
            self.my_shows_page.is_action_screen_view_mode()
            self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
            strip = self.guide_assertions.verify_upcoming_menu_episode_screen(self)
            self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0], select_view_all=True)
            self.wtw_page.nav_to_info_card_action_mode(self)
            self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.program_options_assertions.verify_action_view_mode()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PEACOCK_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       PEACOCK_PACKAGE_NAME, "Peacock")

    @pytest.mark.xray("FRUM-58006")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_58006_uncheck_Peacock_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Peacock',
                                                                   no_partnerIdCount=False)
            if program:
                break
            else:
                self.log.info(" Program not found using service api hence hardcoding it.")
                program = [("Beast Mode", 2020)]
        self.menu_page.check_uncheck_app(self, ["Peacock (free)"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("Peacock (free)",
                                                                     self.my_shows_labels.LBL_PEACOCK_ICON)

    @pytest.mark.xray("FRUM-59976")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_59976_verify_mgm_plus_app_is_not_installed(self):
        """To verify mgm+ application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.MGM_PLUS_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='MGM_PLUS', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_MGM_PLUS_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("WRATH OF MAN", "Wrath of man, (2020)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_MGM_PLUS_ICON_NEW)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.MGM_PLUS_PACKAGE_NAME,
                "MGM_PLUS")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-59980")
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_59980_uncheck_mgm_plus_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='MGM_PLUS', no_partnerIdCount=False)
            if program:
                break
            else:
                self.log.info(" Program not found using service api hence hardcoding it.")
                program = [("Wrath of Man", 2020)]

        self.menu_page.check_uncheck_app(self, ["MGM+"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("MGM+", self.my_shows_labels.LBL_MGM_PLUS_ICON_NEW)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-59975")
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_59975_mgm_plus_deeplinking_av_playback_series(self):
        """Deeplink mgm+ app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='MGM_PLUS', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_MGM_PLUS_PREVIEW_IMAGE_ICON)
        if not program:
            self.text_search_page.search_and_select("CONDOR", "CONDOR")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_MGM_PLUS_PREVIEW_IMAGE_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.screen.get_screen_dump_item('screentitle')
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_MGM_PLUS_ICON_NEW)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.MGM_PLUS_PACKAGE_NAME, limit=15)
        if self.ott_deeplinking_page.verify_watch_button():
            self.watchvideo_page.watch_video_for(20)
            self.vision_page.verify_av_playback()
        else:
            self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-84231")
    @pytest.mark.platform_cert_smoke_test
    def test_84231_launch_Freevee_check_foreground_pkg(self):
        """To verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Freevee', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_Freevee_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_Freevee_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.FREEVEE_PACKAGE_NAME,
                                                                       "Freevee")

    @pytest.mark.xray("FRUM-57651")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_57651_freevee_deeplinking_av_playback_movie(self):
        """Deeplink Frevee TV app for movie, check audio/video motion and verify video title on the
        asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Freevee', feedName="Movies", cnt=4,
                                                                    skip=False, select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_Freevee_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("SING STREET", "Sing Street (2016)")
        screen_title = self.guide_page.get_screen_title()
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_Freevee_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.FREEVEE_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        self.watchvideo_page.watch_video_for(170)
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=10000)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_FREEVEE)

    @pytest.mark.xray("FRUM-57653")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_57653_freevee_deeplinking_av_playback_series(self):
        """Deeplink Freevee app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Freevee', feedName="TV",
                                                                    cnt=4, skip=False, select=False,
                                                                    action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_Freevee_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("TIN MAN", "Tin Man")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_Freevee_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.ott_deeplinking_page.screen_title()
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        episode_title = episode_screen_title.title()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_Freevee_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.FREEVEE_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=10000)
        self.vision_page.verify_screen_contains_text(episode_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_FREEVEE)

    @pytest.mark.xray("FRUM-57662")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_57662_verify_freevee_app_is_not_installed(self):
        """To verify Freevee application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.FREEVEE_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Freevee', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_Freevee_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("SING STREET", "Sing Street (2016)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_Freevee_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.FREEVEE_PACKAGE_NAME,
                "Freevee")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.xray("FRUM-64546")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64546_verify_HBOMAX_app_is_not_installed(self):
        """To verify HBOMAX application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.HBO_MAX_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='HBO MAX', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_HBO_MAX_ICON)
        if not program:
            self.text_search_page.search_and_select("PUPPET MASTER", "Puppet Master (1989)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HBO_MAX_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.HBO_MAX_PACKAGE_NAME,
                "HBO MAX")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-57667")
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_57667_uncheck_Freevee_app_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Freevee',
                                                                   no_partnerIdCount=False)
            if program:
                break
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            program = [("Sing Street", 2016)]

        self.menu_page.check_uncheck_app(self, ["Freevee"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("Freevee", self.my_shows_labels.LBL_Freevee_ICON)

    @pytest.mark.xray("FRUM-84191")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.platform_cert_smoke_test
    def test_launch_HBO_MAX_check_foreground_pkg(self):
        """Sample testcase to verify HBO MAX OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='HBO MAX', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_HBO_MAX_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HBO_MAX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.HBO_MAX_PACKAGE_NAME,
                                                                       "HBO MAX")

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-64539")
    def test_64539_HBOMAX_deeplinking_av_playback_movie(self):
        """Deeplink HBO MAX app for movie, check audio/video motion and verify video title on the asset detail
        screen """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='HBO MAX', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_HBO_MAX_ICON)
        if not program:
            self.text_search_page.search_and_select("MY COUSIN VINNY", "My cousin vinny (1992)")
        screenTitle = self.guide_page.get_screen_title()
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screenTitle)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_HBO_MAX_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.HBO_MAX_PACKAGE_NAME, limit=15)
        current_screen = self.vision_page.get_screen_text()
        if self.ott_deeplinking_labels.LBL_HBOMAX_PROFILE_PAGE in current_screen.upper():
            self.screen.base.press_enter()
        self.wtw_page.wait_for_screen_ready(timeout=10000)
        self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        time.sleep(2)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_HBOMAX)

    @pytest.mark.xray("FRUM-64562")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures('setup_adhoc_OTT_provider_and_functionality')
    def test_64562_uncheck_HBOMAX_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='HBO MAX',
                                                                   no_partnerIdCount=False)
            if program:
                break
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            program = [("My Cousin Vinny", 1992)]

        self.menu_page.check_uncheck_app(self, ["HBO Max"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("HBO MAX",
                                                                     self.my_shows_labels.LBL_HBO_MAX_ICON)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-84216")
    @pytest.mark.platform_cert_smoke_test
    def test_84216_launch_pluto_tv_check_foreground_pkg(self):
        """To verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Pluto TV', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_PLUTO_TV_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PLUTO_TV_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.PLUTO_PACKAGE_NAME,
                                                                       "Pluto TV")

    @pytest.mark.xray("FRUM-64518")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64518_pluto_tv_deeplinking_av_playback_movie(self):
        """Deeplink Pluto TV app for movie, check audio/video motion and verify video title on the
        asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Pluto TV', feedName="Movies", cnt=4,
                                                                    skip=False, select=False,
                                                                    action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PLUTO_TV_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("GOOD HAIR", "Good Hair (2009)")
        screen_title = self.guide_page.get_screen_title()
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PLUTO_TV_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.PLUTO_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=10000)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_PLUTO_TV)

    @pytest.mark.xray("FRUM-64525")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64525_verify_pluto_tv_app_is_not_installed(self):
        """To verify Pluto TV application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.PLUTO_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Pluto TV', feedName="Movies", cnt=4,
                                                                    select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PLUTO_TV_ICON)
        if not program:
            self.text_search_page.search_and_select("GOOD HAIR", "Good Hair (2009)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PLUTO_TV_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.PLUTO_PACKAGE_NAME,
                "Pluto TV")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.xray("FRUM-64519")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64519_pluto_tv_deeplinking_av_playback_series(self):
        """Deeplink Pluto TV app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Pluto TV', feedName="TV",
                                                                    cnt=4, skip=False, select=False,
                                                                    action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PLUTO_TV_ICON)
        if not program:
            self.text_search_page.search_and_select("AMERICAN PICKERS", "American Pickers")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_PLUTO_TV_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.ott_deeplinking_page.screen_title()
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        episode_title = episode_screen_title.title()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PLUTO_TV_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.PLUTO_PACKAGE_NAME, limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=10000)
        self.vision_page.verify_screen_contains_text(episode_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_PLUTO_TV)

    @pytest.mark.xray("FRUM-64529")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    def test_64529_uncheck_pluto_tv_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='Pluto TV',
                                                                   no_partnerIdCount=False)
            if program:
                break
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            program = [("Good Hair", 2009)]

        self.menu_page.check_uncheck_app(self, ["Pluto TV"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("Pluto TV",
                                                                     self.my_shows_labels.LBL_PLUTO_TV_ICON)

    @pytest.mark.xray("FRUM-64590")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64590_verify_Discovery_Plus_app_is_not_installed(self):
        """To verify Discovery+ application is not installed on the device"""
        result = self.text_search_page.is_app_installed(self.apps_and_games_labels.DISCOVERYPLUS_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='discovery+', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_DISCOVERYPLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("GOLD RUSH", "Gold Rush")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_DISCOVERYPLUS_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISCOVERYPLUS_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.DISCOVERYPLUS_PACKAGE_NAME,
                "discovery+")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-84214")
    @pytest.mark.platform_cert_smoke_test
    def test_84214_launch_showtime_anytime_check_foreground_pkg(self):
        """To verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Showtime Anytime',
                                                                    feedName="Movies", cnt=4, select=False,
                                                                    action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_SHOWTIME_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_SHOWTIME_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.SHOWTIME_PACKAGE_NAME,
                                                                       "Showtime Anytime")

    @pytest.mark.xray("FRUM-64601")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64601_showtime_anytime_deeplinking_av_playback_series(self):
        """Deeplink Showtime Anytime app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Showtime Anytime', feedName="TV",
                                                                    cnt=4, skip=False, select=False,
                                                                    action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_SHOWTIME_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("THE CHI", "The Chi")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_SHOWTIME_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.ott_deeplinking_page.screen_title()
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        episode_title = episode_screen_title.title()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_SHOWTIME_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.SHOWTIME_PACKAGE_NAME, limit=15)
        self.wtw_page.wait_for_screen_ready()
        self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=2000)
        self.vision_page.verify_screen_contains_text(episode_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_SHOWTIME_ANYTIME)

    @pytest.mark.xray("FRUM-64599")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64599_showtime_anytime_deeplinking_av_playback_movie(self):
        """Deeplink Showtime Anytime app for movie, check audio/video motion and verify video title on the
        asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Showtime Anytime', feedName="Movies",
                                                                    cnt=4, skip=False, select=False,
                                                                    action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_SHOWTIME_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("HIGH LIFE", "High Life (2019)")
        screen_title = self.guide_page.get_screen_title()
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_SHOWTIME_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.SHOWTIME_PACKAGE_NAME, limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        self.wtw_page.wait_for_screen_ready()
        self.screen.base.press_enter()
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=2000)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_SHOWTIME_ANYTIME)

    @pytest.mark.xray("FRUM-64525")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64525_verify_showtime_anytime_app_is_not_installed(self):
        """To verify Showtime Anytime application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.SHOWTIME_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='Showtime Anytime', feedName="Movies",
                                                                    cnt=4, select=False,
                                                                    action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_SHOWTIME_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("HIGH LIFE", "High Life (2019)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_SHOWTIME_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.SHOWTIME_PACKAGE_NAME,
                "Showtime Anytime")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.xray("FRUM-64610")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    def test_64610_uncheck_showtime_anytime_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        program = self.ott_deeplinking_page.return_program_from_service_api(feed_list, "High Life",
                                                                            ott="Showtime Anytime", fallback_year=2019)
        self.menu_page.check_uncheck_app(self, ["SHOWTIME Anytime"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("Showtime Anytime",
                                                                     self.my_shows_labels.LBL_SHOWTIME_ICON)

    @pytest.mark.xray("FRUM-84220")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.platform_cert_smoke_test
    def test_84220_launch_Discovery_Plus_app_check_foreground_pkg(self):
        """Sample testcase to verify Discovery + OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='discovery+', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_DISCOVERYPLUS_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_DISCOVERYPLUS_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISCOVERYPLUS_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       DISCOVERYPLUS_PACKAGE_NAME, "discovery+")

    @pytest.mark.xray("FRUM-64519")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64519_Discovery_Plus_deeplinking_av_playback_series(self):
        """Deeplink Discovery+ app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='discovery+', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_DISCOVERYPLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("RIVER MONSTERS", "River Monsters")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_DISCOVERYPLUS_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.ott_deeplinking_page.screen_title()
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        episode_title = episode_screen_title.title()
        self.log.info("episode tittle:{}".format(episode_title))
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_DISCOVERYPLUS_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.DISCOVERYPLUS_PACKAGE_NAME,
                                                          limit=15)
        self.watchvideo_page.watch_video_for(20)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=2000)
        self.vision_page.verify_screen_contains_text(episode_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_DISCOVERYPLUS)

    @pytest.mark.xray("FRUM-64593")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    def test_64593_uncheck_Discovery_PLUS_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="TV")
        for feed in feed_list:
            program = self.service_api.get_show_available_from_OTT(feedName=feed, OTT='discovery+',
                                                                   no_partnerIdCount=False)
            if program:
                break
        else:
            self.log.info(" Program not found using service api hence hardcoding it.")
            program = [("RIVER MONSTERS", "River Monsters")]

        self.menu_page.check_uncheck_app(self, ["Discovery+"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0])
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.nav_to_more_option()
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("discovery+",
                                                                     self.my_shows_labels.LBL_DISCOVERYPLUS_ICON)

    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.xray("FRUM-84226")
    @pytest.mark.platform_cert_smoke_test
    def test_84226_launch_paramount_plus_check_foreground_pkg(self):
        """To verify OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Paramount+', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_PARAMOUNT_PLUS_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PARAMOUNT_PLUS_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(
            self.apps_and_games_labels.PARAMOUNT_PLUS_PACKAGE_NAME,
            "Paramount+")

    @pytest.mark.xray("FRUM-64616")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64616_paramount_plus_deeplinking_av_playback_series(self):
        """Deeplink Paramount Plus app for series and check audio/video motion"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Paramount+', feedName="TV", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_PARAMOUNT_PLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("NCIS:NEW ORLEANS", "NCIS: New Orleans")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_PARAMOUNT_PLUS_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        screen_title = self.ott_deeplinking_page.screen_title()
        episode_screen_title = self.ott_deeplinking_page.trim_ep_from_series_screentitle(screen_title)
        episode_title = episode_screen_title.title()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PARAMOUNT_PLUS_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.PARAMOUNT_PLUS_PACKAGE_NAME,
                                                          limit=15)
        self.watchvideo_page.watch_video_for(50)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=2000)
        self.vision_page.verify_screen_contains_text(episode_title,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_PARAMOUNT_PLUS)

    @pytest.mark.xray("FRUM-64614")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64614_paramount_plus_deeplinking_av_playback_movie(self):
        """Deeplink Paramount Plus app for movie, check audio/video motion and verify video title on the
        asset detail screen"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Paramount+', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_PARAMOUNT_PLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("ORPHAN", "Orphan (2009)")
        screen_title = self.guide_page.get_screen_title()
        screen_title_after_year_trim = self.ott_deeplinking_page.trim_year_from_movie_screentitle(screen_title)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PARAMOUNT_PLUS_ICON)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.PARAMOUNT_PLUS_PACKAGE_NAME,
                                                          limit=15)
        self.ott_deeplinking_page.verify_screen_title(screen_title_after_year_trim)
        self.watchvideo_page.watch_video_for(50)
        self.vision_page.verify_av_playback()
        self.ott_deeplinking_page.press_pause_button()
        self.ott_deeplinking_page.press_pause_button()
        self.wtw_page.wait_for_screen_ready(timeout=2000)
        self.vision_page.verify_screen_contains_text(screen_title_after_year_trim,
                                                     region=self.vision_page.locators.SCREEN_TITLE_OF_PARAMOUNT_PLUS)

    @pytest.mark.xray("FRUM-64621")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    def test_64621_verify_paramount_plus_app_is_not_installed(self):
        """To verify Paramount Plus application is not installed on the device"""
        result = self.screen.base.is_app_installed(self.apps_and_games_labels.PARAMOUNT_PLUS_PACKAGE_NAME)
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(
            self, OTT='Paramount+', feedName="Movies", cnt=4, select=False, action_screen=True,
            icon=self.my_shows_labels.LBL_PARAMOUNT_PLUS_PREVIEW_ICON)
        if not program:
            self.text_search_page.search_and_select("ORPHAN", "Orphan (2009)")
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PARAMOUNT_PLUS_ICON)
        if result:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.PARAMOUNT_PLUS_PACKAGE_NAME,
                "Paramount+")
        else:
            self.ott_deeplinking_assertions.verify_ott_screen_with_package(
                self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME,
                "GooglePlay")

    @pytest.mark.xray("FRUM-84189")
    @pytest.mark.ott_deeplink_4
    @pytest.mark.platform_cert_smoke_test
    def test_84189_launch_Pbs_Kids_app_check_foreground_pkg(self):
        """Sample testcase to verify PBS KIDS OTT application launch and check foreground package is correct"""
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, OTT='PbsKids', feedName="Kids", cnt=4,
                                                                    skip=False, select=False, action_screen=True,
                                                                    icon=self.my_shows_labels.LBL_PBS_KIDS_PREVIEW_ICON)
        if not program:
            pytest.skip("Test requires OTT program.")
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.search_ott_provider(self, self.my_shows_labels.LBL_PBS_KIDS_PREVIEW_ICON)
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PBS_KIDS_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.
                                                                       PBS_KIDS_PACKAGE_NAME, "PbsKids")

    @pytest.mark.xray("FRUM-64626")
    @pytest.mark.ott_deeplink
    @pytest.mark.ott_deeplink_3
    @pytest.mark.test_stabilization
    def test_64626_uncheck_paramount_plus_and_deeplink_from_search(self):
        feed_list = self.wtw_page.get_feed_name(feedtype="Movies")
        program = self.ott_deeplinking_page.return_program_from_service_api(feed_list, "ORPHAN",
                                                                            ott="Paramount+", fallback_year=2009)
        self.menu_page.check_uncheck_app(self, ["Paramount+"], check=False)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program[0][0], program[0][0], year=program[0][1])
        self.ott_deeplinking_assertions.verify_app_provider_in_strip("Paramount+",
                                                                     self.my_shows_labels.LBL_PARAMOUNT_PLUS_ICON)
