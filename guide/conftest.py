from datetime import datetime, timedelta

import pytest

from set_top_box.client_api.apps_and_games.assertions import AppsAndGamesAssertions
from set_top_box.client_api.home.assertions import HomeAssertions
from set_top_box.client_api.guide.assertions import GuideAssertions
from set_top_box.client_api.watchvideo.assertions import WatchVideoAssertions
from set_top_box.client_api.Menu.assertions import MenuAssertions
from set_top_box.client_api.my_shows.assertions import MyShowsAssertions
from set_top_box.client_api.voice_search.assertions import VoiceSearchAssertions
from set_top_box.test_settings import Settings
from set_top_box.client_api.VOD.assertions import VODAssertions
from set_top_box.factory.label_factory import LabelFactory
from set_top_box.factory.page_factory import PageFactory
from core_api.stb.base import StreamerBase
from tools.logger.logger import Logger
from set_top_box.client_api.program_options.assertions import ProgramOptionsAssertions
from mind_api.url_resolver import UrlResolver


__log = Logger(__name__)


@pytest.fixture(autouse=True, scope="class")
def setup_guide(request):
    """
    Configure steps to be executed before the test cases run
    :param request:
    :return:
    """
    request.cls.log = Logger(__name__)

    request.cls.apps_and_games_page = PageFactory("apps_and_games", Settings, request.cls.screen)
    request.cls.apps_and_games_assertions = AppsAndGamesAssertions(request.cls.screen)
    request.cls.apps_and_games_labels = LabelFactory("apps_and_games", Settings)

    request.cls.home_page = PageFactory("home", Settings, request.cls.screen)
    request.cls.home_assertions = HomeAssertions(request.cls.screen)
    request.cls.home_labels = request.cls.home_page.home_labels = LabelFactory("home", Settings)

    request.cls.wtw_page = PageFactory("wtw", Settings, request.cls.screen)
    request.cls.wtw_page.labels = request.cls.wtw_labels = LabelFactory("wtw", Settings)

    request.cls.guide_page = PageFactory("guide", Settings, request.cls.screen)
    request.cls.guide_labels = LabelFactory("guide", Settings)
    request.cls.guide_page.guide_labels = request.cls.guide_labels
    request.cls.guide_assertions = GuideAssertions(request.cls.screen)
    request.cls.guide_assertions.guide_labels = request.cls.guide_labels
    request.cls.home_page.guide_page = request.cls.guide_page

    request.cls.watchvideo_assertions = WatchVideoAssertions(request.cls.screen)
    request.cls.watchvideo_page = PageFactory("watchvideo", Settings, request.cls.screen)
    request.cls.watchvideo_labels = LabelFactory("watchvideo", Settings)
    request.cls.watchvideo_assertions.watchvideo_labels = request.cls.watchvideo_labels
    request.cls.watchvideo_page.watchvideo_labels = request.cls.watchvideo_labels

    request.cls.guide_assertions.watchvideo_labels = request.cls.watchvideo_labels

    request.cls.liveTv_labels = LabelFactory("watchvideo", Settings)

    request.cls.my_shows_page = PageFactory("my_shows", Settings, request.cls.screen)
    request.cls.my_shows_labels = LabelFactory("my_shows", Settings)
    request.cls.my_shows_assertions = MyShowsAssertions(request.cls.screen)

    request.cls.voicesearch_page = PageFactory("voice_search", Settings, request.cls.screen)
    request.cls.voicesearch_assertions = VoiceSearchAssertions(request.cls.screen)
    request.cls.voicesearch_labels = request.cls.voice_search_labels = LabelFactory("voice_search", Settings)

    request.cls.menu_page = PageFactory("Menu", Settings, request.cls.screen)
    request.cls.menu_assertions = MenuAssertions(request.cls.screen)
    request.cls.menu_labels = request.cls.menu_page.menu_labels = LabelFactory("Menu", Settings)

    request.cls.text_search_page = PageFactory("text_search", Settings, request.cls.screen)

    request.cls.vod_assertions = VODAssertions(request.cls.screen)
    request.cls.vod_labels = LabelFactory("VOD", Settings)
    request.cls.vod_page = PageFactory("VOD", Settings, request.cls.screen)

    request.cls.acc_locked_page = PageFactory("account_locked", Settings, request.cls.screen)

    request.cls.program_options_assertions = ProgramOptionsAssertions(request.cls.screen)

    request.cls.system_page = PageFactory("system", Settings, request.cls.screen)
    request.cls.base = StreamerBase(request.cls.screen)

    request.getfixturevalue('device_reboot_to_imporve_device_perf')
    request.getfixturevalue('clean_ftux_and_sign_in')
    request.getfixturevalue('disable_parental_controls')


@pytest.fixture(autouse=False, scope="function")
def setup_cleanup_list_favorite_channels_in_guide(request):
    def tear_down():
        __log.info("Tearing down")
        request.cls.home_page.back_to_home_short()
        request.cls.home_assertions.verify_menu_item_available(request.cls.home_labels.LBL_GUIDE_SHORTCUT)
        request.cls.home_page.select_menu_shortcut(request.cls.home_labels.LBL_GUIDE_SHORTCUT)
        if not request.cls.guide_page.is_menu_list():
            request.cls.guide_page.press_ok_button()
        else:
            request.cls.guide_page.switch_channel_option("All")
    request.addfinalizer(tear_down)


@pytest.fixture(autouse=False, scope="function")
def setup_add_favorite_channels_in_guide(request):
    request.cls.home_page.back_to_home_short()
    request.cls.home_assertions.verify_menu_item_available(request.cls.home_labels.LBL_GUIDE_SHORTCUT)
    request.cls.home_page.select_menu_shortcut(request.cls.home_labels.LBL_GUIDE_SHORTCUT)
    request.cls.guide_page.get_live_program_name(request)
    request.cls.guide_page.switch_channel_option("All")
    request.cls.base = StreamerBase(request.cls.screen)
    request.cls.home_page.back_to_home_short()
    request.cls.home_assertions.verify_menu_item_available(request.cls.home_labels.LBL_MENU_SHORTCUT)
    request.cls.home_page.select_menu_shortcut(request.cls.home_labels.LBL_MENU_SHORTCUT)
    request.cls.menu_page.nav_to_top_of_list()
    request.cls.menu_page.select_menu_category(request.cls.menu_labels.LBL_SETTINGS_SHORTCUT)
    request.cls.menu_page.select_menu_items(request.cls.menu_labels.LBL_USER_PREFERENCES_SHORTCUT)
    request.cls.menu_page.select_menu_items(request.cls.menu_labels.LBL_FAVOURITE_CHANNELS)
    request.cls.screen.refresh()
    request.cls.screen.wait_for_screen_ready(request.cls.guide_labels.LBL_FAVORITE_CHANNELS_SCREEN_NAME)
    menu = request.cls.base.menu_list_images()
    if request.cls.guide_labels.LBL_CHECKED not in menu[0]:
        index = request.cls.menu_page.find_first_unchecked(request.cls.guide_labels.LBL_UNCHECKED)
        request.cls.menu_page.menu_navigate_up_down(0, index)
        request.cls.menu_page.select_item()


@pytest.fixture(autouse=False, scope="function")
def channel_status_store(request):
    """
    Channel status store
    """
    def tear_down():
        channel = request.cls.service_api.cached_channel_info(None, mode="live_tv", use_cached_response=True)
        __log.info("channel details: {}".format(channel))
        channel_name_index = 1
        ui_error_code_index = 3
        url_error_code_index = 4
        request.config.option.ui_error_code = str(channel[ui_error_code_index])
        request.config.option.url_error_code = str(channel[url_error_code_index])
        request.config.option.channel_name = str(channel[channel_name_index])
        if isinstance(channel, list):
            status = request.cls.base.health_api.db_store(channel, livetv=True)
            request.config.option.livetv_post_resp = str(status)
            # request.cls.guide_assertions.verify_channel_store_response(status)
            if not status:
                __log.warning("Failed to store channel details to DB")
    request.addfinalizer(tear_down)


@pytest.fixture(autouse=False, scope="function")
def toggle_mind_availability(request):
    """
    Toggle mind availability backdoor to simulate 'Service is down' state
    """
    def setup(expected):
        __log.info("Turning the Mind service {}".format(expected))
        request.cls.home_page.back_to_home_short()
        request.cls.home_page.toggle_mind_availability()
        if expected == "ON":
            for i in range(3):
                if request.cls.home_page.wait_for_connected_disconnected_state(
                        error_code=request.cls.home_labels.LBL_ERROR_CODE_C219, timeout=10):
                    break
            else:
                raise AssertionError("Did not get C219 error")
        elif expected == "OFF":
            for i in range(3):
                if request.cls.home_page.wait_for_connected_disconnected_state(timeout=10, wait_disconnect=False):
                    break
            else:
                request.cls.guide_page.relaunch_hydra_app()
    setup("ON")
    yield
    setup("OFF")


@pytest.fixture(autouse=False, scope="function")
def toggle_guide_rows_service_availability(request):
    """
    Toggle /v1/guideRows service
    """
    restrict_download_speed_to = 1  # kbt/s
    __log.info("Slowing the /v1/guideRows service DOWN, speed {} kbt/s".format(restrict_download_speed_to))
    url = UrlResolver(Settings).get_endpoints("cloudcore-guide")
    domain = url.replace("https://", "").replace(":443", "")
    request.cls.guide_page.set_download_limit_with_ip(domain, restrict_download_speed_to)
    yield
    request.cls.guide_page.relax_bandwidth_restrictions()


@pytest.fixture(autouse=False, scope="function")
def switch_tivo_service_rasp(request):
    """
    Simulate 'Service is down' state using Raspberry PI
    """
    def setup(expected):
        request.cls.home_page.back_to_home_short()
        if expected == "ON":
            request.cls.guide_page.set_download_limit_with_ip(ip_addr=request.cls.home_page.get_tivoservice_url(),
                                                              speed=1)
            request.cls.guide_page.relaunch_hydra_app()
            if request.cls.home_page.wait_for_connected_disconnected_state(
                    error_code=request.cls.home_labels.LBL_ERROR_CODE_C229, timeout=80):
                __log.info("Disconnected state: Error {}".format(request.cls.home_labels.LBL_ERROR_CODE_C229))
            else:
                request.cls.home_page.relax_bandwidth_restrictions()
                raise AssertionError("Disconnected state: Did not get error {}"
                                     .format(request.cls.home_labels.LBL_ERROR_CODE_C229))
        elif expected == "OFF":
            request.cls.home_page.relax_bandwidth_restrictions()
            request.cls.home_assertions.verify_connected_disconnected_state_happened(timeout=330, wait_disconnect=False)
    setup("ON")
    yield
    setup("OFF")


@pytest.fixture(autouse=False, scope="function")
def enable_wip_1(request):
    """
    enable wip 1 group to play pluto tv channels
    """
    def setup():
        request.cls.screen.base.modify_tcdui_conf("device", DG_HDUI_WIP="1")
    setup()


@pytest.fixture(autouse=False, scope="function")
def remove_channel_package_sports(request):
    """
    Remove package to get unsubscribed channels
    """
    def setup(expected):
        package = "emo-st-cc11-sports"
        if expected == "ON":
            __log.info("Remove package {}".format(package))
            request.cls.iptv_prov_api.account_entitlement_remove(
                [package],
                request.cls.service_api.getPartnerCustomerId(Settings.tsn),
                request.cls.service_api.get_mso_partner_id(Settings.tsn))
            request.cls.home_page.clear_cache_launch_hydra_app()
        elif expected == "OFF":
            __log.info("Restore package {}".format(package))
            request.cls.iptv_prov_api.account_entitlement_publish(
                [{'package': package, 'start_date': '2022-08-22 10:04:14', 'end_date': '2072-08-21 10:04:14'}],
                request.cls.service_api.getPartnerCustomerId(Settings.tsn),
                request.cls.service_api.get_mso_partner_id(Settings.tsn))
    setup("ON")
    yield
    setup("OFF")


@pytest.fixture(autouse=False, scope="function")
def setup_prepare_params_for_guide_cells_test(request, icon, expected, is_olg):
    """
    Setting params and then making /v1/guideRows request to get a random show for further testing.
    Applicable since Hydra v1.18.

    Args:
        icon (str): one of (new, ppv, socu, non_rec_pg, non_req_crr);
                    non_rec_pg = non-recordable icon on Guide Cell in Past Guide
                    non_req_crr = non-recordable icon on Guide Cell in Current or Future Guide (copyright restriction)
        expected (bool): True - icon should be shown, False - there should not be icon
        is_olg (bool): True - checking icons in One Line Guide, False - checking icons in Grid Guide
    """
    __log.info(f"setup_prepare_params_for_guide_cells_test: icon {icon}; expected {expected}")
    ends_in_gt = 180 if is_olg else 600
    # Let's skip using ends_in_gt for Past Guide
    ends_in_gt = None if icon == "non_rec_pg" else ends_in_gt
    # duration_gt should be 9 minutes or more to see program name and icons on Guide Cells
    duration_gt = 600
    is_live = True if is_olg else None
    get_playable_live_tv = is_live
    exclude_tplus_channels = True
    exclude_plutotv_channels = True
    is_ppv = False if is_live else None
    find_appropriate = True if not is_live else None
    params_for_test = {
        "is_live": is_live, "ends_in_gt": ends_in_gt, "find_appropriate": find_appropriate, "duration_gt": duration_gt,
        "get_playable_live_tv": get_playable_live_tv, "exclude_tplus_channels": exclude_tplus_channels, "is_ppv": is_ppv,
        "exclude_plutotv_channels": exclude_plutotv_channels}
    if icon == "new":
        params_for_test["is_new"] = expected
    elif icon == "ppv":
        params_for_test["is_ppv"] = expected
        # To avoid test skipping due to not available channels with working playback if is_olg is True
        params_for_test["get_playable_live_tv"] = None
    elif icon == "socu":
        params_for_test["is_startover"] = expected
    elif icon == "non_rec_pg":
        # Non-recordable icon on a show in Past Guide
        end_time = datetime.now()
        start_time = (end_time - timedelta(hours=2)).timestamp()
        end_time = end_time.timestamp()
        params_for_test["is_recordable_chan"] = expected
        params_for_test["start_time"] = start_time
        params_for_test["end_time"] = end_time
        params_for_test["take_not_ended_shows"] = False
        params_for_test["is_live"] = None  # to be able to check icon in One Line Guide
        params_for_test["find_appropriate"] = True
        params_for_test["is_recordable_in_the_past"] = False
        icon = "non_recordable"
    elif icon == "non_req_crr":
        # Non-recordable icon on an in-progress show on a channel that allows
        # (show not allowed to record due to copyright restriction)
        params_for_test["is_copyright_restricted"] = expected
        icon = "non_recordable"
    params_for_test["icon"] = icon
    olg_tile = None
    channel_show = request.cls.service_api.get_random_channel_from_guide_rows(**params_for_test)
    if is_olg:
        # The tile we need is the 1st one
        olg_tile = request.cls.service_api.get_one_line_guide_cells(channel_show[0][2])[0]
    show_title = olg_tile.title if is_olg else channel_show[0][1].title
    show_title_full = show_title if channel_show[0][1].content_type != "movie" else \
        show_title + " (" + str(channel_show[0][1].movie_year) + ")"
    params_for_test["show_title"] = show_title_full
    params_for_test["station_id"] = channel_show[0][2].station_id
    params_for_test["channel_number"] = channel_show[0][2].channel_number
    params_for_test["steps"] = channel_show[0][3]
    request.config.cache.set("params_for_test", params_for_test)


@pytest.fixture(autouse=False, scope="function")
def unsubscribed_channel_check(request):
    """
    Checks DG_showentitledchannels is added or not
    """
    mandatory = request.cls.service_api.check_groups_enabled(request.cls.guide_labels.LBL_SUBSCRIBED_CHANNEL_ONLY)
    if mandatory:
        pytest.skip("DG group is added to show only subscribed channels")
