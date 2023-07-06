import pytest
import time
from set_top_box.test_settings import Settings
from set_top_box.client_api.movie_cdp.conftest import setup_movie_cdp
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from pytest_testrail.plugin import pytestrail


@pytest.mark.usefixtures("setup_movie_cdp")
@pytest.mark.usefixtures("is_service_wtw_alive")
@pytest.mark.movie_cdp
class TestMovieCDP(object):

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_327520_select_movies_tab(self):
        """
        Navigate to Movie Content Page from What to Watch
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        time.sleep(5)
        self.menu_page.select_menu_items("Movies")
        self.movie_cdp_assertions.verify_screen_title()

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_326159_select_movies_tab(self):
        """
        Navigate to Movie Cast Page from What to Watch
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        time.sleep(5)
        self.menu_page.select_menu_items("Movies")
        self.movie_cdp_assertions.verify_screen_title()
        get_cast_name = self.movie_cdp_page.get_cast_name()
        self.movie_cdp_assertions.verify_screen_title_cast(get_cast_name)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C12792160")
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.timeout(Settings.timeout)
    def test_267264_movie_screen_display(self):
        """
        Verify Movie Screen display
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_PRIMARY_SCREEN, 30000)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SIDE_PANEL, 30000)
        self.menu_page.select_menu_items(self.home_labels.LBL_MOVIES)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 50000)
        self.wtw_assertions.verify_highlight_not_in_netflix_strip()
        self.screen.base.press_enter()
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 50000)
        self.movie_cdp_assertions.movie_screen_validation(self)
