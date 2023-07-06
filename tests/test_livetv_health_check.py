import pytest

from set_top_box.client_api.guide.conftest import setup_guide, channel_status_store
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from set_top_box.test_settings import Settings
from set_top_box.shared_context import ExecutionContext
from tools.logger.logger import Logger


@pytest.mark.livetv_health_check
class TestLiveTvHealthCheck(object):
    """
    TC: To verify channel and playback URL health check
    param: -
    status: -
    """

    def pytest_generate_tests(self, metafunc):
        """
        Hook to generate TC ids for every channel. Uses in TestLiveTvHealthCheck
        """
        if "channel_ids" in metafunc.fixturenames:
            channels_ids = []
            if not metafunc.config.getoption("skip_health_check"):
                channels_ids = ExecutionContext.service_api.channels_ids
            metafunc.parametrize("channel_ids", channels_ids)

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.log = Logger(__name__)

    @pytest.mark.usefixtures("channel_status_store")
    def test_livetv_health_check(self, channel_ids):
        channel_detail = self.service_api.channel_details[channel_ids]
        channel = (channel_ids, channel_detail[1], channel_detail[2], channel_detail[3], channel_detail[0])
        status, result, url_status, url = self.guide_page.playback_status_check_on_device(self, channel)
        self.service_api.cached_channel_info(
            [channel_ids, channel_detail[0], status, result, url_status, url, channel_detail[5]])
        self.guide_assertions.verify_channel_playback_status(status, result, url=url)
