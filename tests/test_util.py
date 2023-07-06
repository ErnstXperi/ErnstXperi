import pytest

from set_top_box.client_api.util.conftest import setup_util  # noqa: F401
from set_top_box.test_settings import Settings
from set_top_box.client_api.home.conftest import enable_stay_awake


@pytest.mark.usefixtures('setup_util')
class TestUtil:

    @pytest.mark.demo
    def test_1_test_dumping(self):

        failed_ctr = 0
        pass_ctr = 0
        local = self.driver.driver_config.screen_dump_location + "/SceneGraph.xml"
        on_device = self.driver.driver.screen_dump_graph
        on_device_png = self.driver.driver.screen_dump_png
        if self.driver.driver._AndroidDriver__adb.verify_file_exists(on_device):
            self.driver.driver._AndroidDriver__adb.rm_from_device(on_device)

        if self.driver.driver._AndroidDriver__adb.verify_file_exists(on_device_png):
            self.driver.driver._AndroidDriver__adb.rm_from_device(on_device_png)

        for _ in range(100):
            try:
                self.driver.driver.get_screen_dump_graph(local)
                if not self.driver.driver._AndroidDriver__adb.verify_file_exists(on_device) or \
                        not self.driver.driver._AndroidDriver__adb.verify_file_exists(on_device_png):
                    failed_ctr += 1
                self.screen.transform_xml()
                self.driver.driver._AndroidDriver__adb.rm_from_device(on_device)
                self.driver.driver._AndroidDriver__adb.rm_from_device(on_device_png)

                self.screen.sys_commands.rm_rf_CommandONMAC(local)
                pass_ctr += 1
            except Exception:
                failed_ctr += 1
                self.log.info("Dump failed current ctr: {}".format(failed_ctr))
        if failed_ctr:
            raise AssertionError("Dump failed times: {}".format(failed_ctr))

    @pytest.mark.demo
    def test_2_dump_stability_on_transition(self):
        errors_list = []
        repeats = 1000
        dump_type = "full_no_png"
        local = self.driver.driver_config.screen_dump_location + "/SceneGraph.xml"
        on_device = self.driver.driver.screen_dump_graph
        on_device_png = self.driver.driver.screen_dump_png

        list_of_shortcuts = [self.home_labels.LBL_MYSHOWS_SHORTCUT,
                             self.home_labels.LBL_ONDEMAND_SHORTCUT,
                             self.home_labels.LBL_WHATTOWATCH_SHORTCUT,
                             self.home_labels.LBL_GUIDE_SHORTCUT,
                             self.home_labels.LBL_SEARCH_SHORTCUT,
                             ]

        for _i in range(repeats):
            try:
                if not self.driver.driver.verify_foreground_app(Settings.app_package):
                    self.log.error("HYDRA not on foreground")
                    self.driver.driver.launch_app(Settings.app_package)
                    self.cls.screen.wait_for_screen_ready(timeout=40000)
                shortcut_index = _i % len(list_of_shortcuts)
                self.home_page.back_to_home_short()

                exp_title = list_of_shortcuts[shortcut_index]

                shortcut_number = self.home_labels.LBL_SHORTCUTS_NUM.get(exp_title)
                self.log.step(f"{_i}: GOTO: {exp_title}")
                self.home_page.screen.base.type_number(shortcut_number)

                self.driver.driver._AndroidDriver__adb.rm_from_device(on_device)
                self.driver.driver._AndroidDriver__adb.rm_from_device(on_device_png)
                self.log.step(f"{_i}: START test dump")
                self.screen.get_json(dump_type)
                self.log.step(f"{_i}: Finish test dump")

                act_title = self.home_page.screen_title()
                if exp_title not in act_title:
                    errors_list.append("{}:Wrong screen. screen exp:{}, act: {}".format(_i, exp_title, act_title))
                    self.log.step("{}:BAD screen. screen exp:{}, act: {}".format(_i, exp_title, act_title))
                else:
                    self.log.step("{}:GOOD screen. screen exp:{}, act: {}".format(_i, exp_title, act_title))
                self.screen.sys_commands.rm_rf_CommandONMAC(local)
            except Exception as err:
                errors_list.append("{}:ERR:{}".format(_i, err))
                self.log.info("{}:BAD: Global exception".format(_i))
        if errors_list:
            raise AssertionError("Dump failed times: {}. \n details :{}".format(len(errors_list), errors_list))
        else:
            print("SUCCESS: {}".format(repeats))

    @pytest.mark.demo
    def test_1_longpress_keyevent_server(self):

        failed_ctr = 0
        for i in range(3):
            self.watchvideo_page.calc_end_time_for_30_m_show(self, vital_gap=8)
            row = self.service_api.channels_with_current_show_start_time(duration=1800)
            channels = self.service_api.get_random_encrypted_unencrypted_channels(encrypted=True,
                                                                                  grid_row=row)
            self.home_page.back_to_home_short()
            self.home_page.select_menu_shortcut(self.home_labels.LBL_GUIDE_SHORTCUT)
            self.guide_assertions.verify_guide_title()
            self.watchvideo_page.enter_channel_number(channels[0][0])
            for _ in range(33):
                self.driver.driver.long_press_key(28, self.driver.driver.keys.OK)
                try:
                    self.menu_page.wait_for_screen_ready(self.guide_labels.LBL_RECORD_OVERLAY)
                    self.guide_assertions.verify_overlay()
                except Exception:
                    failed_ctr += 1
                    self.log.info("Failed long press count: {}".format(failed_ctr))
                else:
                    self.guide_page.press_back_button()
        if failed_ctr:
            raise AssertionError("Failed long press count: {}".format(failed_ctr))

    @pytest.mark.usefixtures("enable_stay_awake")
    def test_goto_livetv_mtbc(self):
        channel = self.service_api.get_random_encrypted_unencrypted_channels(Settings.tsn, transportType="stream",
                                                                             filter_channel=True)
        if not channel:
            pytest.skip("There are no encrypted channels")
        channel_number = channel[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.watch_channel(self, channel_number)
        self.watchvideo_assertions.verify_livetv_mode()
