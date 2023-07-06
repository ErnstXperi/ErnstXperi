import pytest

from set_top_box.client_api.guide.conftest import setup_guide, channel_status_store
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from set_top_box.test_settings import Settings
from set_top_box.conf_constants import HydraBranches
from tools.logger.logger import Logger
from set_top_box.shared_context import ExecutionContext


@pytest.mark.tivoplus_health_check
@pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13))
class TestTivoPlusHealthCheck(object):
    """
    TC: To verify plutotv channels health
    param: -
    status: -
    """

    def pytest_generate_tests(self, metafunc):
        """
        Hook to generate TC ids for every channel. Uses in TestLiveTvHealthCheck
        """
        if "tivoplus_channels" in metafunc.fixturenames:
            tivoplus_channels = []
            if not metafunc.config.getoption("skip_health_check"):
                tivoplus_channels = ExecutionContext.service_api.tivoplus_channels
            metafunc.parametrize("tivoplus_channels", tivoplus_channels)

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.log = Logger(__name__)
        self.channel_list_generator = self.service_api

    @pytest.mark.usefixtures("channel_status_store")
    def test_tivoplus_channels_health_check(self, tivoplus_channels):
        channel_detail = self.channel_list_generator.tivoplus_channel_details[tivoplus_channels]
        channel = (tivoplus_channels, channel_detail[0], channel_detail[1], channel_detail[2])
        status, result, url_status, url = self.guide_page.playback_status_check_on_device(self, channel, url_check=False,
                                                                                          tplus=True)
        self.service_api.cached_channel_info(
            [tivoplus_channels, channel_detail[0], status, result, url_status, url, channel_detail[3]])
        self.guide_assertions.verify_channel_playback_status(status, result, url=url)
