import time

import pytest

from set_top_box.test_settings import Settings
from pytest_testrail.plugin import pytestrail
from set_top_box.conf_constants import HydraBranches
from set_top_box.client_api.wtw.conftest import setup_what_to_watch, setup_to_check_app, hero_promo_check
from set_top_box.client_api.my_shows.conftest import setup_delete_book_marks
from set_top_box.client_api.Menu.conftest import disable_parental_controls, setup_cleanup_parental_and_purchase_controls
from set_top_box.client_api.Menu.conftest import enable_video_providers, disable_video_providers


@pytest.mark.wtw
@pytest.mark.usefixtures("setup_what_to_watch")
@pytest.mark.timeout(Settings.timeout)
class TestWhatToWatchScreen(object):

    @pytest.mark.frumos_11
    @pytest.mark.platform_cert_smoke_test
    def test_202693203_netflix_strip_presence(self):
        """
            Verifies that "Netflix Original" strip is displayed

            Testrail:
               https://testrail.tivo.com/index.php?/tests/view/202693203
            Test case is enhanced to verify source type of netflix

        This case is not valid as We are no longer allowed to show exclusive Netflix content on our browse screens
        on IPTV streamer devices by contractual obligation with Netflix.
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.navigate_to_wtw_strip(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER, 'in')
        self.wtw_assertions.verify_current_strip_title(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER)
        # test case enhancement
        self.watchvideo_page.press_ok_button()
        self.home_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "netflix")
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_11)

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_what_to_watch")
    def test_12784094_promote_what_to_watch_hero_promotion_press_select_wtw_filter(self):
        """
        :Description:
            Promote What To Watch - Hero Promotion - Press SELECT - WTW filter
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/12784094
        """
        self.home_page.go_to_what_to_watch(self)
        action_type_lbl = self.wtw_labels.LBL_AD_ACTION_UI_NAVIGATE
        screen_name_lbl = self.wtw_labels.LBL_WTW_NOW
        hero_promotion = self.wtw_page.find_and_nav_to_hero_promotion_using_gui(self,
                                                                                feed_name='/promotions/whatToWatchHero',
                                                                                action_type=action_type_lbl,
                                                                                screen_name=screen_name_lbl,
                                                                                link_to_top_of_screen=False,
                                                                                is_carousel=False)
        caption = self.wtw_page.get_wtw_nav_caption_according_to_ad(self, hero_promotion)
        self.guide_assertions.press_select_and_verify_wtw_screen()
        # After clicking on AD that leads to category, a WTW screen opens with standard title: WHAT TO WATCH
        # Then dev side is asking server about which screen should be displayed
        # (sometimes it's very fast and sometimes it's about ~1-2 seconds to see the actual title).
        # After getting an answer from the server an actual category will be added to the title.
        # To avoid fails because of too early verification need to wait few seconds
        # and refresh a screen to get an actual title
        self.wtw_page.pause(5)
        self.screen.refresh()
        self.wtw_page.verify_screen_title(caption.upper())
        self.wtw_page.nav_to_browse_options_menu(self)
        self.my_shows_assertions.verify_focused_program(caption, self.my_shows_page.menu_focus())
        self.wtw_page.press_back_button()
        self.wtw_page.verify_screen_title(caption.upper())
        self.wtw_page.press_back_button()
        self.home_assertions.verify_home_title()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_11
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-11"))
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.cloudcore_wtw_predictions
    def test_268993257_long_key_press_infocard_wtw(self):
        """
        Verify that Info card is opened after long press OK on asset on WTW screen

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_WTW_PRIMARY_SCREEN, 30000)
        self.wtw_page.log.step('Call infocard by long press on select button')
        self.screen.base.long_press_enter()
        self.wtw_assertions.verify_infocard_on_long_key_press()

    @pytest.mark.p1_regression
    @pytest.mark.info_cards_action_mode
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_what_to_watch")
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_4863847_info_cards_action_mode_see_more_info_press_select(self):
        """
        :Description:
            Info Cards - Action Mode - See More Info - Press SELECT
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/4863847
        """
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.nav_to_wtw_movies(self)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.wtw_assertions.verify_view_mode(self.wtw_labels.LBL_ACTIONS_SCREEN)

    @pytest.mark.p1_regression
    @pytest.mark.cloud_core_guide_preview
    @pytest.mark.info_cards_action_mode
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_what_to_watch")
    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_4863169_explicit_feedback_info_cards_bookmark_movie(self):
        """
        :Description:
            Explicit Feedback - Info Cards - Bookmark movie
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/4863169
        """
        bookmark_lbl = self.wtw_labels.LBL_WTW_INFO_CARDS_BOOKMARK_MOVIE
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_MOVIES)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_MOVIES)
        self.wtw_page.nav_to_info_card_action_mode(self)
        try:
            title = self.wtw_page.get_preview_panel().get('title', None)
        except Exception:
            title = self.wtw_page.get_overlay_title()
        self.wtw_page.select_menu(bookmark_lbl)
        self.wtw_page.verify_whisper(self.wtw_labels.LBL_WTW_INFO_CARDS_BOOKMARK_MOVIE_WHISPER)
        self.menu_assertions.verify_menu_item_available(bookmark_lbl, expected=False)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.validate_bookmarked_content_in_myshows(self, title)

    @pytestrail.case('C13234007')
    @pytest.mark.xray("FRUM-791")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_what_to_watch")
    def test_C13234007_wtw_hero_promo_ad_not_clickable(self):
        """
        :Description:
            Promote What To Watch - Hero Promotion - Press SELECT - No Action Ad

        """
        self.home_page.go_to_what_to_watch(self)
        action_type_lbl = self.home_labels.LBL_AD_ACTION_NO_OP_UI
        filtered_hero_promotion_list = self.wtw_page.get_wtw_hero_ads_as_per_action_type(self,
                                                                                         action_type=action_type_lbl)
        self.wtw_page.get_hero_promo_on_screen(filtered_hero_promotion_list)
        self.home_page.navigate_to_destination_screen_for_wtw_hero_no_action_ad(self)

    @pytestrail.case('C13234011')
    @pytest.mark.xray("FRUM-1294")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_what_to_watch")
    def test_C13234011_wtw_hero_promo_ad_leads_to_VOD_screen(self):
        """
        :Description:
            Promote What To Watch - Hero Promotion - Press SELECT - walledGardenBrowseUiAction Ad

        """
        self.home_page.go_to_what_to_watch(self)
        action_type_lbl = self.home_labels.LBL_AD_ACTION_WALLED_GARDEN
        filtered_hero_promotion_list = self.wtw_page.get_wtw_hero_ads_as_per_action_type(self,
                                                                                         action_type=action_type_lbl)
        self.wtw_page.get_hero_promo_on_screen(filtered_hero_promotion_list)
        self.home_page.navigate_to_vod_program_screen_for_walledGardenBrowseUiAction_action_type(self)

    @pytestrail.case('C13234010')
    @pytest.mark.xray("FRUM-855")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_what_to_watch")
    def test_C13234010_wtw_hero_promo_ad_leads_to_top_of_ott_app(self):
        """
        :Description:
            Promote What To Watch - Hero Promotion - Press SELECT - uiNavigateAction Ad

        """
        self.home_page.go_to_what_to_watch(self)
        action_type_lbl = self.home_labels.LBL_AD_ACTION_UI_NAVIGATE
        filtered_hero_promotion_list = self.wtw_page.get_wtw_hero_ads_as_per_action_type(self,
                                                                                         action_type=action_type_lbl)
        self.wtw_page.get_hero_promo_on_screen(filtered_hero_promotion_list)
        self.wtw_page.navigate_to_top_of_app_for_from_wtw_hero_ad(self, filtered_hero_promotion_list)

    @pytestrail.case('C13234009')
    @pytest.mark.xray("FRUM-740")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_what_to_watch")
    def test_C13234009_verify_user_able_to_navigate_to_series_screen_from_wtw_hero_ad(self):
        """
        :Description:
            Promote What To Watch - Hero Promotion - Press SELECT - collectionDetailUiAction Ad

        """
        self.home_page.go_to_what_to_watch(self)
        action_type_lbl = self.home_labels.LBL_AD_ACTION_COLLECTION_DETAIL_UI
        filtered_hero_promotion_list = self.wtw_page.get_wtw_hero_ads_as_per_action_type(self,
                                                                                         action_type=action_type_lbl)
        self.wtw_page.get_hero_promo_on_screen(filtered_hero_promotion_list)
        self.home_page.navigate_to_series_screen_for_collectionDetailUiAction_action_type(self)

    @pytestrail.case('C13533971')
    @pytest.mark.xray("FRUM-1294")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_what_to_watch")
    def test_C13533971_verify_user_able_to_navigate_to_livetv_from_wtw_hero_ad(self):
        """
        :Description:
            Promote What To Watch - Hero Promotion - Press SELECT - liveTvUiAction Ad

        """
        self.home_page.go_to_what_to_watch(self)
        action_type_lbl = self.home_labels.LBL_AD_ACTION_LIVETV_UI
        filtered_hero_promotion_list = self.wtw_page.get_wtw_hero_ads_as_per_action_type(self,
                                                                                         action_type=action_type_lbl)
        self.wtw_page.get_hero_promo_on_screen(filtered_hero_promotion_list)
        self.home_page.navigate_to_livetv_for_liveTvUiAction_action_type(self)

    @pytestrail.case('C13533365')
    @pytest.mark.xray("FRUM-681")
    @pytest.mark.slot0_wtw_hero
    @pytest.mark.usefixtures("hero_promo_check")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    @pytest.mark.skipif(Settings.is_fire_tv(), reason="OTT app deeplinking not available on Fire TV")
    def test_C13533365_verify_user_navigates_to_Deeplinked_title_in_OTT_app_from_wtw_hero_ad(self):
        """
                :Description:
                    Promote What To Watch - Hero Promotion - Press SELECT - uiNavigateAction Ad and give uri that tells
                    which content to deeplink to while publishing the Ad.

                """
        self.home_page.go_to_what_to_watch(self)
        action_type_lbl = self.home_labels.LBL_AD_ACTION_UI_NAVIGATE
        filtered_hero_promotion_list = self.wtw_page.get_wtw_hero_ads_as_per_action_type(self,
                                                                                         action_type=action_type_lbl)
        self.wtw_page.get_hero_promo_on_screen(filtered_hero_promotion_list)
        self.home_page.navigate_to_program_in_OTT_app_for_uiNavigateAction_action_type(self)

    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_what_to_watch")
    @pytest.mark.cloudcore_wtw_predictions
    def test_C14379825_verify_wtw_stability(self):
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_assertions.verify_wtw_stability(self)

    @pytest.mark.ott_deeplink_3
    @pytest.mark.ott_deeplink
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    def test_C14379827_verify_wtw_free_movie_and_Tv_has_free_content(self):
        """
        Verify wtw free movie and Tv has free content
        """
        lbl = self.apps_and_games_labels
        tubi_webkit = self.service_api.check_groups_enabled(lbl.TUBITV_WEBKIT_NAME)
        pluto_webkit = self.service_api.check_groups_enabled(lbl.PLUTO_WEBKIT_NAME)
        if not (tubi_webkit or pluto_webkit):
            pytest.skip("webkit is not added. Hence skipping")
        tubi_app = self.screen.base.is_app_installed(lbl.TUBITV_PACKAGE_NAME)
        pluto_app = self.screen.base.is_app_installed(lbl.PLUTO_PACKAGE_NAME)
        if not (pluto_app or tubi_app):
            pytest.skip("Device does not contain required app")
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        strip_index = self.wtw_assertions.is_WTW_category_available(self.wtw_labels.LBL_WTW_FREE_MOVIES_AND_TV)
        self.wtw_page.navigate_to_category_strip(strip_index)
        self.wtw_assertions.verify_category_strip_is_displayed(self.wtw_labels.LBL_WTW_FREE_MOVIES_AND_TV)

    @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    def test_14383646_verify_left_tile_display_on_leftbutton_press_when_not_in_first_position(self):
        """
        Verify if left tile is displayed on pressing left button when not in first tile position

        Testrail link : https://testrail.tivo.com//index.php?/cases/view/14383646
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.screen.base.press_right()
        self.screen.base.press_left()
        self.wtw_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_assertions.verify_wtw_sidepanel_is_not_displayed()

    @pytest.mark.stability
    @pytest.mark.timeout(Settings.timeout)
    def test_14388807_verify_crash_not_seen_in_wtw(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/14388807
        """
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_WTW_BROWSE_OPTS_HOME)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_ON_TV_TODAY)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_ON_TV_TODAY)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_COLLECTIONS)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_COLLECTIONS)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_TV_SERIES)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_TV)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_MOVIES)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_MOVIES)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_BOX_SETS)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_BOX_SETS)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_SPORTS)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_SPORTS)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_KIDS)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_KIDS)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_20933984_verify_more_info_of_actor(self):
        """
        Verify Person Info card is displayed

        https://testrail.tivo.com/index.php?/cases/view/20933984
        """
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_MOVIES)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_MOVIES)
        self.screen.base.press_right()
        self.home_page.press_info_button()
        self.wtw_page.wait_for_screen_ready()
        self.menu_page.select_menu_items(self.wtw_labels.LBL_WTW_INFO_CARD_OPTIONS)
        self.wtw_page.wait_for_screen_ready()
        self.menu_page.select_menu_items(self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO)
        self.wtw_page.wait_for_screen_ready()
        cast_name = self.movie_cdp_page.get_cast_name()
        self.screen.base.press_back()
        self.guide_page.wait_for_screen_ready()
        for i in range(10):
            self.home_page.press_info_button()
            self.wtw_page.wait_for_screen_ready()
            self.wtw_page.verify_screen_title(cast_name.upper())
            self.home_page.press_info_button()

    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_4863181_explicit_feedback_info_cards_bookmark_episode(self):
        """
        Explicit Feedback - Info Cards - Bookmark episode

        Testrail link : https://testrail.tivo.com//index.php?/cases/view/4863181
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        program = self.wtw_page.find_and_nav_to_episode()
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(self.wtw_labels.LBL_WTW_INFO_CARDS_BOOKMARK_EPISODE)
        self.wtw_page.verify_whisper(self.wtw_labels.LBL_WTW_INFO_CARDS_BOOKMARK_EPISODE_WHISPER)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_content_in_any_category(self, program)

    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("disable_video_providers")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_t389366328_netflix_originals(self):
        """
        Testrail:
            https://testrail.tivo.com//index.php?/tests/view/389366328
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_assertions.verify_netflix_strip_not_present()

    @pytest.mark.notapplicable(Settings.is_fire_tv())
    # @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_t389366327_preview_panel_in_netflix_originals(self):
        """
        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/389366327

        This case is not valid as We are no longer allowed to show exclusive Netflix content on our browse screens
        on IPTV streamer devices by contractual obligation with Netflix.
        """
        self.home_page.back_to_home_short()
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.navigate_to_wtw_strip(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER, 'in')
        self.wtw_assertions.verify_current_strip_title(self.wtw_labels.LBL_WTW_NETFLIX_PROVIDER)
        self.wtw_assertions.verify_preview_pane_program_description()
        self.wtw_assertions.verify_netflix_icon_on_wtw_screen()

    # @pytest.mark.test_stabilization
    @pytest.mark.longrun
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.timeout(Settings.timeout)
    def test_389366347_verify_promo_carousel_strip_item(self):
        """
        https://testrail.tivo.com//index.php?/tests/view/389366347
        """
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        carousel = self.wtw_page.get_carousel_from_service()
        if carousel is None:
            pytest.fail("Carousels not found from service!")
        carousel_list = carousel[0:5]
        self.wtw_page.nav_to_browse_options_menu(self)
        self.menu_page.menu_press_back()
        self.wtw_page.nav_to_menu(carousel[0])
        for i in range(len(carousel_list)):
            feed = []
            self.wtw_assertions.verify_current_strip_title(carousel_list[i])
            feed = self.service_api.get_assets_titles_from_wtw_strip(carousel_list[i])
            if feed is None:
                pytest.fail("Asset Title under {} casrouel not found from service", (carousel_list[i]))
            for j in range(len(feed)):
                show = self.my_shows_page.remove_service_symbols(feed[j])
                self.wtw_page.wait_for_screen_ready()
                self.my_shows_assertions.verify_preview_pane_title(self, show)
                self.wtw_assertions.is_atmospheric_image_present()
                self.screen.base.press_right()
                self.wtw_page.wait_for_screen_ready(timeout=30000)
            for k in range(len(feed)):
                self.screen.base.press_left()
            self.my_shows_page.press_down_button()
            self.wtw_page.wait_for_screen_ready()

    @pytest.mark.solutions_tests
    @pytest.mark.xray('FRUM-72606')
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.usefixtures("hero_promo_check")
    @pytest.mark.timeout(Settings.timeout)
    def test_72606_no_carousal_pager(self):
        """
        XRAY TC ID: https://jira.xperi.com/browse/FRUM-72606
        """
        response = self.service_api.get_feed_item_find_results("/promotions/whatToWatchHero", display_count=10,
                                                               full_resp=True)
        hero_promo_feed = response.feeditems if response.feeditems else []
        if hero_promo_feed.feedItems and len(hero_promo_feed.feedItems) != 1:
            pytest.skip("This tests needs only 1 hero promo to be available in WTW hero but has got : {}".format
                        (len(hero_promo_feed.feedItems)))
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_WTW_BROWSE_OPTS_HOME)
        self.wtw_assertions.verify_hero_promo_ads_left_right_carousel()

    @pytest.mark.usefixtures("hero_promo_check")
    @pytest.mark.xray('FRUM-56809')
    def test_56809_hero_promo(self):
        """
        :Description:
            hero pro is hidden after selecting any filter other than All
        """
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        left_menu = self.wtw_labels.LBL_WTW_MENU_LIST
        for option in left_menu:
            self.wtw_page.select_strip_from_wtw_panel(self, option)
            self.wtw_page.wait_for_screen_ready()
            if option is self.wtw_labels.LBL_WTW_BROWSE_OPTS_HOME:
                self.wtw_assertions.verify_wtw_hero_availability_in_filter()
            else:
                self.wtw_assertions.verify_wtw_hero_not_available_in_filter()

    @pytest.mark.full_regression_tests
    @pytest.mark.xray('FRUM-62908')
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_62908_verify_wtw_tiles_time_info_mso_pig_and_image_posters_for_movies(self):
        """
        FRUM-62908
        Verify WTW tile, pig, time and MSO logo is displaying or not on what to watch home screen

        Verify image posters is displaying for movies(what to watch movie screen).
        """
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_WTW_BROWSE_OPTS_HOME)
        self.wtw_page.wait_for_screen_ready()
        self.wtw_assertions.verify_time_info_wtw()
        self.wtw_assertions.verify_primary_branding_icon_wtw()
        self.screen.base.press_enter()
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_video_streaming(refresh=True)
        self.screen.base.press_back()
        self.wtw_page.wait_for_screen_ready()
        self.wtw_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_assertions.verify_wtw_tiles_and_image_posters()
        self.wtw_page.select_strip_from_wtw_panel(self, self.wtw_labels.LBL_MOVIES)
        self.wtw_page.wait_for_screen_ready()
        self.vod_assertions.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH_MOVIES)
        self.wtw_assertions.verify_wtw_tiles_and_image_posters()

    @pytest.mark.p1_regression
    @pytest.mark.xray('FRUM-68732')
    @pytest.mark.frumos_18
    @pytest.mark.timeout(Settings.timeout)
    def test_FRUM_68732_wtw_screen_loading_with_open_apis(self):
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        feed_list = self.wtw_page.get_feed_name(feedtype="Home")
        self.wtw_assertions.verify_screen_components_match_open_api_response(feed_list)

    @pytest.mark.p1_regression
    @pytest.mark.xray('FRUM-68728')
    @pytest.mark.frumos_18
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "OpenApis are called only in streamers 1.18 and above")
    @pytest.mark.skipif(not Settings.is_usqe1(), reason="openApi changes only on usqe1.")
    def test_FRUM_68728_wtw_screen_navigation_with_open_apis(self):
        """
        Currently, Feature not enabled on Staging(only done on usqe1) so, enabling Feature flag and clearing at the
        end of the test case.
        Will remove this once the feature is FAed on staging env. as well.
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.wtw_page.random_navigation_on_wtw_screen(self)
        self.service_properties_assertions.verify_usage_of_open_api()

    @pytest.mark.xray('FRUM-121775')
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/preview/content are supported since Hydra v1.19")
    @pytest.mark.frumos_19
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_121775_wtw_screen_preview_title(self):
        """
        Verifying WTW Screen preview basing on /v1/preview/content (OpenAPI requests)
        Xray:
            https://jira.xperi.com/browse/FRUM-121775
        """
        feed_list = self.wtw_page.get_feed_name(feedtype="Home")
        response = self.service_api.get_feed_item_find_results(feed_list[0], display_count=10,
                                                               full_resp=True)
        feed = response.feeditems.feedItems[0]
        content_id = feed.contentid
        title = self.service_api.get_preview_offer(content_id, mode="content", screen_type='wtwnScreen').title
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.wtw_page.nav_to_show_on_strip(show_name=title, btn='left')
        self.my_shows_assertions.verify_preview_pane_title(self, title)

    @pytest.mark.xray('FRUM-121777')
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/preview/series are supported since Hydra v1.19")
    @pytest.mark.frumos_19
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_121777_wtw_screen_preview_description(self):
        """
        Verifying WTW Screen preview basing on /v1/preview/series (OpenAPI requests)
        Xray:
            ttps://jira.xperi.com/browse/FRUM-121777
        """
        feed_list = self.wtw_page.get_feed_name(feedtype="Home")
        response = self.service_api.get_feed_item_find_results(feed_list[0], display_count=10,
                                                               full_resp=True)
        feed = response.feeditems.feedItems[0]
        collection_id = feed.collectionid
        description = self.service_api.get_preview_offer(collection_id, mode="series", screen_type="wtwnScreen").description
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.wtw_page.nav_to_show_on_strip(show_name=feed.title, btn='left')
        self.my_shows_assertions.verify_preview_pane_description(self, description)

    @pytest.mark.service_reliability
    @pytest.mark.xray('FRUM-142378')
    def test_bring_up_what_to_watch(self):
        """
        Bring up WTW screen
        :return:
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.guide_page.timestamp_test_start()
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.xray('FRUM-142377')
    def test_bring_up_wtw_and_press_down_button(self):
        """
        Bring up WTW
        Go down 1 cell via arrow down
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.guide_page.timestamp_test_start()
        self.screen.base.press_down()
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.xray('FRUM-142383')
    def test_bring_up_wtw_and_rapid_down_button_presses(self):
        """
        Bring up WTW
        10 rapid down arrows
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.guide_page.timestamp_test_start()
        self.watchvideo_page.press_down_multiple_times(10)
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.xray('FRUM-142381')
    def test_bring_up_wtw_and_rapid_right_button_presses(self):
        """
        Bring up WTW
        5 rapid right arrows across horizontal strips
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.guide_page.timestamp_test_start()
        self.watchvideo_page.press_right_multiple_times(5)
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.xray('FRUM-142382')
    def test_bring_up_wtw_and_rapid_left_button_presses(self):
        """
        Bring up WTW
        5 rapid left arrows across horizontal strips
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.watchvideo_page.press_right_multiple_times(15)
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready()
        self.guide_page.timestamp_test_start()
        self.watchvideo_page.press_left_multiple_times(5)
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.xray('FRUM-142380')
    def test_bring_up_wtw_and_press_left_to_bring_browse_options(self):
        """
        Bring up WTW
        Press left button to bring Browse options
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_page.go_to_what_to_watch(self)
        self.wtw_page.wait_for_screen_ready(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)
        self.guide_page.timestamp_test_start()
        self.wtw_page.nav_to_browse_options_menu(self)
        self.guide_page.timestamp_test_end()
