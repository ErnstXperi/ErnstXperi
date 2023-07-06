import pytest

from set_top_box.factory.page_factory import PageFactory
from set_top_box.factory.label_factory import LabelFactory
from tools.logger.logger import Logger
from set_top_box.client_api.api_integration.assertions import APIAssertions
from set_top_box.test_settings import Settings


__logger = Logger(__name__)


@pytest.fixture(autouse=True, scope="class")
def setup_api_tester(request):
    """
    Configure steps to be executed before the test cases run
    :param request:
    :return:
    """
    request.cls.api_assertions = APIAssertions(request.cls.screen)
    request.cls.home_page = PageFactory("home", Settings, request.cls.screen)
    request.cls.home_labels = request.cls.home_page.home_labels = LabelFactory("home", Settings)
