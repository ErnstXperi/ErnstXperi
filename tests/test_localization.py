from tools.logger.logger import Logger
from set_top_box.client_api.home.conftest import *
import pytest
from set_top_box.client_api.home.labels_loki import Loki_HomeLabels


@pytest.mark.usefixtures("setup_home")
class TestLocalization(object):

    @pytest.mark.demo
    def test_home_screen(self, loki_home_label):
        loki_labels = Loki_HomeLabels()
        expected_val = getattr(loki_labels, loki_home_label)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(expected_val.upper())
