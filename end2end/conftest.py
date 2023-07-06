import pytest

from set_top_box.client_api.apps_and_games.assertions import AppsAndGamesAssertions
from set_top_box.client_api.home.assertions import HomeAssertions
from set_top_box.client_api.guide.assertions import GuideAssertions
from set_top_box.client_api.watchvideo.assertions import WatchVideoAssertions
from set_top_box.client_api.wtw.assertions import WhatToWatchAssertions
from set_top_box.client_api.Menu.assertions import MenuAssertions
from set_top_box.client_api.text_search.assertions import TextSearchAssertions
from set_top_box.client_api.my_shows.assertions import MyShowsAssertions
from set_top_box.test_settings import Settings
from set_top_box.client_api.VOD.assertions import VODAssertions
from set_top_box.client_api.program_options.assertions import ProgramOptionsAssertions
from set_top_box.client_api.voice_search.assertions import VoiceSearchAssertions
from set_top_box.factory.page_factory import PageFactory
from set_top_box.factory.label_factory import LabelFactory
from tools.logger.logger import Logger
from set_top_box.client_api.TTS.page import TTSPage


@pytest.fixture(autouse=True, scope="class")
def setup_e2e(request):
    """
    Configure steps to be executed before the test cases run
    :param request:
    :return:
    """
    request.cls.apps_and_games_assertions = AppsAndGamesAssertions(request.cls.screen)
    request.cls.apps_and_games_page = PageFactory("apps_and_games", Settings, request.cls.screen)
    request.cls.apps_and_games_labels = LabelFactory("apps_and_games", Settings)

    request.cls.home_page = PageFactory("home", Settings, request.cls.screen)
    request.cls.home_labels = request.cls.home_page.home_labels = LabelFactory("home", Settings)
    request.cls.home_assertions = HomeAssertions(request.cls.screen)

    request.cls.guide_page = PageFactory("guide", Settings, request.cls.screen)
    request.cls.guide_labels = request.cls.guide_page.guide_labels = LabelFactory("guide", Settings)
    request.cls.guide_assertions = GuideAssertions(request.cls.screen)

    request.cls.watchvideo_assertions = WatchVideoAssertions(request.cls.screen)
    request.cls.watchvideo_page = PageFactory("watchvideo", Settings, request.cls.screen)
    request.cls.watchvideo_labels = request.cls.liveTv_labels = LabelFactory("watchvideo", Settings)

    request.cls.wtw_page = PageFactory("wtw", Settings, request.cls.screen)
    request.cls.wtw_assertions = WhatToWatchAssertions(request.cls.screen)
    request.cls.wtw_assertions.wtw_page = request.cls.wtw_page
    request.cls.wtw_labels = LabelFactory("wtw", Settings)
    request.cls.wtw_page.wtw_labels = request.cls.wtw_labels
    request.cls.wtw_assertions.wtw_labels = request.cls.wtw_labels
    request.cls.wtw_page.home_labels = request.cls.home_labels
    request.cls.wtw_assertions.home_labels = request.cls.home_labels

    request.cls.menu_page = PageFactory("Menu", Settings, request.cls.screen)
    request.cls.menu_assertions = MenuAssertions(request.cls.screen)
    request.cls.menu_labels = request.cls.menu_assertions.menu_labels = request.cls.menu_page.menu_labels \
        = LabelFactory("Menu", Settings)

    request.cls.my_shows_page = PageFactory("my_shows", Settings, request.cls.screen)
    request.cls.my_shows_labels = LabelFactory("my_shows", Settings)
    request.cls.my_shows_assertions = MyShowsAssertions(request.cls.screen)

    request.cls.system_page = PageFactory("system", Settings, request.cls.screen)
    request.cls.system_labels = LabelFactory("system", Settings)
    request.cls.system_page.system_labels = request.cls.system_labels
    request.cls.home_page.system_labels = request.cls.system_labels

    request.cls.program_options_assertions = ProgramOptionsAssertions(request.cls.screen)
    request.cls.program_options_page = PageFactory("program_options", Settings, request.cls.screen)
    request.cls.program_options_labels = LabelFactory("program_options", Settings)

    request.cls.text_search_labels = LabelFactory("text_search", Settings)
    request.cls.text_search_page = PageFactory("text_search", Settings, request.cls.screen)
    request.cls.text_search_page.text_search_labels = request.cls.text_search_labels
    request.cls.text_search_assertions = TextSearchAssertions(request.cls.screen)

    request.cls.tts_page = PageFactory("TTS", Settings, request.cls.screen)

    request.cls.vod_page = PageFactory("VOD", Settings, request.cls.screen)
    request.cls.vod_assertions = VODAssertions(request.cls.screen)
    request.cls.vod_labels = request.cls.vod_page.vod_labels = LabelFactory("VOD", Settings)

    request.cls.voicesearch_page = PageFactory("voice_search", Settings, request.cls.screen)
    request.cls.voicesearch_assertions = VoiceSearchAssertions(request.cls.screen)
    request.cls.voicesearch_labels = request.cls.voice_search_labels = LabelFactory("voice_search", Settings)

    request.getfixturevalue('device_reboot_to_imporve_device_perf')
    request.getfixturevalue('clean_ftux_and_sign_in')
    request.getfixturevalue('disable_parental_controls')
    request.cls.tts_page = TTSPage(request.cls.screen)

    request.cls.live_tv_page = PageFactory("watchvideo", Settings, request.cls.screen)
    request.cls.live_tv_assertions = WatchVideoAssertions(request.cls.screen)
    request.cls.live_tv_labels = LabelFactory("watchvideo", Settings)
    request.cls.guide_assertions.liveTv_labels = request.cls.live_tv_labels

    request.cls.log = Logger(__name__)


@pytest.fixture(autouse=False)
def decrease_screen_saver(request):
    """
    Reduce screen saver timeout to 1 minute,
    afterwards return it default value
    """
    request.cls.driver.driver.set_screen_saver_timeout(60000)
    yield
    request.cls.driver.driver.set_screen_saver_timeout()


@pytest.fixture(autouse=False)
def switch_off_show_only_favorite_channels_in_guide(request):
    """
    Switch off favorite channel filter in guide
    """

    def do():
        try:
            request.cls.log.info('Switching off guide filter')
            request.cls.api.remove_favorite_channel()
            request.cls.home_page.back_to_home_short()
            request.cls.home_assertions.verify_home_title()
            request.cls.home_assertions.verify_menu_item_available(request.cls.home_labels.LBL_GUIDE_SHORTCUT)
            request.cls.home_page.select_menu_shortcut(request.cls.home_labels.LBL_GUIDE_SHORTCUT)
            request.cls.guide_assertions.verify_guide_title()
            if request.cls.guide_page.get_channels_list_mode() != 'all channels':
                if not request.cls.guide_page.is_menu_list():
                    request.cls.guide_page.press_ok_button()
                    assert request.cls.guide_page.is_menu_list()
                else:
                    request.cls.guide_page.switch_channel_option("All")
                    request.cls.guide_assertions.verify_channels_list_mode('all channels')
        except Exception:
            request.cls.log.info("Failed to switch off guide filter")

    do()
    yield
    do()


@pytest.fixture(autouse=False)
def set_screen_saver_default_value(request):
    """
    Set screen saver defalut value start time to 5 mins
    """
    request.cls.driver.driver.set_screen_saver_timeout()  # default value is 300 seconds (5 minutes)
    yield
    request.cls.driver.driver.set_screen_saver_timeout(30 * 60 * 1000)
