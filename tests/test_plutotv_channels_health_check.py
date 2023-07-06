import pytest
from hamcrest import assert_that

from set_top_box.client_api.guide.conftest import setup_guide, channel_status_store, enable_wip_1
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_pluto_tv_app
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from set_top_box.test_settings import Settings
from set_top_box.conf_constants import HydraBranches
from tools.logger.logger import Logger
from set_top_box.shared_context import ExecutionContext


@pytest.mark.plutotv_health_check
@pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
@pytest.mark.usefixtures("enable_wip_1")
class TestPlutoTvHealthCheck(object):
    """
    TC: To verify plutotv channels health
    param: -
    status: -
    """

    def pytest_generate_tests(self, metafunc):
        """
        Hook to generate TC ids for every channel. Uses in TestLiveTvHealthCheck
        """
        if "pluto_channels" in metafunc.fixturenames:
            pluto_channels = []
            if not metafunc.config.getoption("skip_health_check"):
                pluto_channels = ExecutionContext.service_api.pluto_channels
            metafunc.parametrize("pluto_channels", pluto_channels)

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.log = Logger(__name__)
        self.channel_list_generator = self.service_api

    @pytest.mark.usefixtures("channel_status_store")
    def test_plutotv_channels_health_check(self, pluto_channels):
        channel_detail = self.channel_list_generator.pluto_channel_details[pluto_channels]
        channel = (pluto_channels, channel_detail[0], channel_detail[1], channel_detail[2])
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.home_assertions.verify_error_overlay_not_shown()
        status, package = self.guide_page.check_package()
        self.service_api.cached_channel_info(
            [pluto_channels, channel_detail[0], status, None, None, None, channel_detail[4]])
        assert_that(status is True, f"Expected pacakge: {Settings.PLUTO_TV_PACKAGE_NAME} but was Actual: {package}")
