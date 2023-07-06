from datetime import datetime
from requests.exceptions import ReadTimeout
import configparser
import decorator
import glob
import hashlib
import logging
import operator
import os
import re
import shutil
import sys
import time
import yaml

import pytest
from hamcrest.core import assert_that
from validators import domain
from validators.ip_address import ipv4, ipv6

from tools.networking.network_tools import NetworkTools
from set_top_box.test_settings import Settings
from set_top_box.shared_context import ExecutionContext
from core_api.hardwaredriver import driverfactory
from tools.logger.logger import Logger
from tools.sys_commands import Commands
from tools.analytics import CoverageAnalytics
from tools.keychain import UTAFKeychain
from mind_api.iptv_provisioning_mind.iptv_prov_api import IptvProvisioningApi
from mind_api.mind_interface import MindInterface
from mind_api.middle_mind.loki_api_helper import LokiApiHelper
from mind_api.middle_mind.health_api_helper import HealthApiHelper
from mind_api.eula.eulahandler import EULAHandler
from mind_api.middle_mind.api_parser import ApiParser
from set_top_box.mso_features import MSOFeatures
from tools.key_event_server_if import KeyEventServerIf
from tools.tcdui_config_parser import TcduiConf, TcdiuConfSelector
from set_top_box.conf_constants import PlatformList, MsoList, DriverTypeList, MindEnvList, HydraBranches, LanguageList
from tools.logger.logger import PerfLogger
from core_api.hardwaredriver.driverfactory import AppCrashError, InfraHardwareError, ConfigurationError
from mind_api.middle_mind.device_provisioning_api_helper import DeviceProvisioningApiHelper
from set_top_box import conftst_helpers
from tools.clients.CallStackAnalyzer.call_stack_analyzer import CallStackAnalyzer

logger = Logger(__name__)
health_check = True

# reduce subpackages logging (non UTAF logs)
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
logging.getLogger("chardet.charsetprober").setLevel(logging.INFO)
logging.getLogger("paramiko.transport").setLevel(logging.INFO)
logging.captureWarnings(True)


def add_user_option(parser, opt_name, help_text):
    # add as command line argument
    parser.addoption("--{}".format(opt_name),
                     default=None,
                     action="store",
                     dest=opt_name,
                     help=help_text)
    # if command line argument is not present
    # take it from pytest.ini file
    parser.addini(opt_name, help_text)


def get_user_option(config, opt_name, default=None):
    # add as command line argument
    cmd_opt = None
    ini_opt = None
    try:
        cmd_opt = config.getoption(opt_name, None)
        ini_opt = config.getini(opt_name)
    except ValueError:
        pass

    # if command line argument is not present
    # take it from pytest.ini file
    if cmd_opt:
        result_opt = cmd_opt
    elif ini_opt:
        result_opt = ini_opt
    else:
        result_opt = default
    if "path" in opt_name:
        result_opt = Commands.resolve_unix_path(result_opt)
    return result_opt


def pytest_addoption(parser):
    add_user_option(parser, opt_name="log_path", help_text="Path to store Log File")
    add_user_option(parser, opt_name="artifacts_mode", help_text="Path to store Log File")
    add_user_option(parser, opt_name="bugreports", help_text="option to generate bugreport always")
    parser.addoption("--skip_health_check", action="store_true", help="skip health check")
    parser.addoption("--skip_pc_check", action="store_true", help="skip pc check")
    parser.addoption("--localization", action="store_true", help="run localization tests")
    parser.addoption("--songbird", action="store_true", help="enable songbird report capture")
    parser.addini("custom_cfg_files", help="multi-value parameter to push custom files to a DUT")
    add_user_option(parser, opt_name="device_id", help_text="device id of the android device")
    add_user_option(parser, opt_name="equipment_id", help_text="equipment device id of the android device")
    add_user_option(parser, opt_name="os_version", help_text="os version android device")
    add_user_option(parser, opt_name="hub", help_text="appium hub")
    add_user_option(parser, opt_name="appium_ip", help_text="appium server ip")
    add_user_option(parser, opt_name="testcaseid", help_text="Test case ID")
    add_user_option(parser, opt_name="mso", help_text="MSO of the device")
    add_user_option(parser, opt_name="tsn", help_text="TSN of the device")
    add_user_option(parser, opt_name="ca_device_id", help_text="CA Device ID of the device")
    add_user_option(parser, opt_name="hsn", help_text="hsn")
    add_user_option(parser, opt_name="platform", help_text="Device platform. amino, mibox, arris, firetv etc")
    add_user_option(parser, opt_name="build_source", help_text="Build source")
    add_user_option(parser, opt_name="branch", help_text="Current branch")
    add_user_option(parser, opt_name="build", help_text="Current build")
    add_user_option(parser, opt_name="stage", help_text="Build stage aka test_envornment+apk config")
    add_user_option(parser, opt_name="app_env_config", help_text="Replacement of stage: voice, nonpersistent etc")
    add_user_option(parser, opt_name="test_environment",
                    help_text="staging/usqe1/cdvrqe1/prod")  # set_top_box.conf_constants.MindEnvList
    add_user_option(parser, opt_name="tcdui_conf", help_text="path to tscdui_test.conf file")
    add_user_option(parser, opt_name="manage_id", help_text="managed/unmanaged")
    add_user_option(parser, opt_name="build_version", help_text="release, etc")

    add_user_option(parser, opt_name="app_package", help_text="App package name")
    add_user_option(parser, opt_name="username", help_text="username for SAML login(unmanaged)")
    add_user_option(parser, opt_name="password", help_text="password for SAML login(unmanaged)")
    add_user_option(parser, opt_name="DG_HDUI_WIP", help_text="DG_HDUI_WIP flags")
    add_user_option(parser, opt_name="CCB_SWITCH_OVERRIDE", help_text="add CCB_SWITCH overrides to tcdui_test.conf")
    add_user_option(parser, opt_name="SLS_ENDPOINTS_OVERRIDE", help_text="add SLS_ENDPOINTS overrides to test.conf")
    add_user_option(parser, opt_name="SLS_INSTANCE_OVERRIDE", help_text="add SLS_INSTANCE overrides to test.conf")
    add_user_option(parser, opt_name="TIMEOUT_TO_DIMMING_SCREEN",
                    help_text="Configuring time for the Dimming screen appearance")
    add_user_option(parser, opt_name="TIMEOUT_SERVICE_LOGIN", help_text="Timeout for service login")
    add_user_option(parser, opt_name="MEDIA_HEALTH_EVENT_INTERVAL_OVERRIDE",
                    help_text="Configure interval to get media health event")
    add_user_option(parser, opt_name="media_audio_flinger",
                    help_text="option to generate media audio logs")
    add_user_option(parser, opt_name="QE_TESTING_DEVICE_TYPE",
                    help_text="define the type of QE Automation Box")
    add_user_option(parser, opt_name="driver_type",
                    help_text="driver type to use like android_tv, appletv, firetv, appium, estream4k")
    add_user_option(parser, opt_name="device_ip",
                    help_text="Ip address of device under test")
    add_user_option(parser, opt_name="port", help_text="Device port")
    add_user_option(parser, opt_name="adb_path", help_text="adb path")

    add_user_option(parser, opt_name="language", help_text="default is en_us")
    add_user_option(parser, opt_name="transport", help_text="SSH(if connection using PI)")
    add_user_option(parser, opt_name="rasp_ip", help_text="Raspberry PI ip")
    add_user_option(parser, opt_name="rasp_user", help_text="Username to login to PI")
    add_user_option(parser, opt_name="rasp_pwd", help_text="Password to login to PI")
    add_user_option(parser, opt_name="rasp_dump", help_text="path to dump file in PI(/home/pi/dump)")
    add_user_option(parser, opt_name="rasp_nic_to_box", help_text="rasp pi ethernet interface to be limited to")
    add_user_option(parser, opt_name="vt_hardware", help_text="Name of video source hardware for VisionTester")
    add_user_option(parser, opt_name="vt_video_input", help_text="ID of video input for testing (VisionTester)")
    add_user_option(parser, opt_name="dut_hub", help_text="ID of VT hub for testing (VisionTester)")
    add_user_option(parser, opt_name="vt_audio_device", help_text="ID of audio input. (VisionTester)")
    add_user_option(parser, opt_name="use_zipalign", help_text="flag to select android app zipalign: true/false")
    add_user_option(parser,
                    opt_name="fail_build_upon_install_failure",
                    help_text="flag to skip build installation failure: true/false")
    add_user_option(parser, opt_name="rpmdir", help_text="DIR path of rmp server (apple tv builds)")
    add_user_option(parser, opt_name="push_test_conf", help_text="Push or not tcdui_test.conf to sdcard True/False")
    add_user_option(parser, opt_name="yukon_server", help_text="hostname or ip of Yukon server")
    add_user_option(parser, opt_name="dbg_dump_type", help_text="dump type: full, full_no_png, light, focused")
    add_user_option(parser, opt_name="dbg_verbose_mode", help_text="Mode number. 0 is the lowest")
    add_user_option(parser, opt_name="vt_save_audio", help_text="save audio file for vision tester")
    add_user_option(parser, opt_name="rail_id", help_text="test rail id for case")
    add_user_option(parser, opt_name="mso_locality", help_text="device locality")
    add_user_option(parser, opt_name="check_ndvr_enabled", help_text="check current device is an active nDVR")
    add_user_option(parser, opt_name="check_provisioning", help_text="check provisioning for current device")
    add_user_option(parser, opt_name="sdcard_stats", help_text="sdcard statistics")
    add_user_option(parser, opt_name="meminfo_stats", help_text="meminfo statistics")
    add_user_option(parser, opt_name="feature_4k", help_text="check current device is 4k")
    add_user_option(parser, opt_name="rooted", help_text="handle rooted device")
    add_user_option(parser, opt_name="app_repackager", help_text="configuration for app repackager")
    add_user_option(parser, opt_name="remove_screen_dump", help_text="option to remove screen dump")
    add_user_option(parser, opt_name="WIDGET_TIMEOUT_MS", help_text="Option to increase/decrease trickplay timout")
    add_user_option(parser, opt_name="WELCOME_SPLASH_TIMEOUT_MS", help_text="option to increase/decrease WS screen")
    add_user_option(parser, opt_name="mind_mode", help_text="Flag to change mind mode using cfg: openapi, trio, auto")
    # If use_channels_from_packages set, get_channel_search() returns only channels that related to pointed packages
    add_user_option(parser, opt_name="use_channels_from_packages", help_text="Comma separated package name list")
    # To exclude channel packages to be used from execution
    add_user_option(parser, opt_name="exclude_packages_from_use", help_text="Comma separated package name list")
    add_user_option(parser, opt_name="drm_type", help_text="Adds given DRM Type")
    add_user_option(parser, opt_name="reboot_required", help_text="Reboot device if required between suite level True/False")
    add_user_option(parser, opt_name="utaf_analytics", help_text="Int. Level of collected analytics: 0 - 4")
    add_user_option(parser, opt_name="ignore_external_assert_tests",
                    help_text="Ignore external by default given tests")
    return parser


def initialize_mind_api():
    mind_if = MindInterface(Settings)
    ExecutionContext.mind_if = mind_if
    ExecutionContext.pps_api_helper = DeviceProvisioningApiHelper(Settings, mso=Settings.mso, device_type="set_top_box")
    ExecutionContext.service_api = mind_if.service
    ExecutionContext.iptv_prov_api = IptvProvisioningApi(Settings, mind_if.service, ExecutionContext.pps_api_helper)
    ExecutionContext.vod_api = mind_if.vod_api
    ExecutionContext.loki_labels = LokiApiHelper(Settings, mso=Settings.mso, device_type="set_top_box")
    ExecutionContext.api_parser = ApiParser(settings=Settings, device_type="set_top_box")
    ExecutionContext.health_api = HealthApiHelper(settings=Settings, mso=Settings.mso, device_type="set_top_box")
    ExecutionContext.eula_api = EULAHandler(Settings)


def skip_health_check(fun):
    global health_check

    def wrapper(fun, *args, **kwargs):
        if health_check:
            return fun(*args, **kwargs)
        return lambda: None

    return decorator.decorator(wrapper, fun)


@pytest.fixture(autouse=True, scope="session")
def add_drm_type():
    """
    Takes DRMType param from the pytest ini and adds DRMType.
    """
    if Settings.drm_type:
        user_drm_type = Settings.drm_type
        logger.debug(f"user_drm_type: {user_drm_type}")

        FE_PACKAGES = ["preferNative", "preferVerimatrix"]
        if user_drm_type not in FE_PACKAGES:
            raise AssertionError(f"Given {user_drm_type} not in {FE_PACKAGES}")

        DRM_FEATURES_FOR_MSO = {
            "cableco11": ['Linear', 'Ndvr1008011', 'Ndvr1008012', 'Socu', 'Vod'],
            "cableco5": ['Linear', 'Ndvr', 'Socu', 'Vod']}
        feature_list = DRM_FEATURES_FOR_MSO.get(Settings.mso.lower())
        if not feature_list:
            logger.debug(f"DRM feature list is empty for the mso {Settings.mso.lower()}")
        else:
            response = ExecutionContext.iptv_prov_api.fe_alacarte_get_package_native_drm()
            logger.debug(f"Get DRM info: {response}")
            alacart_packages = response.get("deviceAlaCartePackage")
            logger.debug(f"Device ala cart packages: {alacart_packages}")
            existing_drm_type = conftst_helpers.get_existing_drm_type(FE_PACKAGES, alacart_packages)
            logger.debug(f"Existing drm type: {existing_drm_type}")

            add_attr = [feature_list, user_drm_type]
            remove_attr = [feature_list, existing_drm_type, alacart_packages]

            if Settings.is_cc11():
                add_attr.append('usqe1')
                remove_attr.append('usqe1')

            if not existing_drm_type:
                logger.debug("Device has not provisioned with any DRMType")
                conftst_helpers.add_drm_type_and_feature(*add_attr)
            elif len(existing_drm_type) == 1 and user_drm_type == existing_drm_type[0]:
                logger.debug(f"Provisioned DRMType {existing_drm_type} is matching user's DRMType {user_drm_type}")
                conftst_helpers.check_and_add_drm_type_and_feature(alacart_packages, *add_attr)
            elif len(existing_drm_type) == 1 and user_drm_type != existing_drm_type[0]:
                logger.debug(f"Provisioned DRMType {existing_drm_type} is not matching with user's DRMType {user_drm_type}")
                conftst_helpers.remove_drm_type_and_feature(*remove_attr)
                conftst_helpers.add_drm_type_and_feature(*add_attr)
            elif len(existing_drm_type) == 2:
                logger.debug(f"Provisioned DRMType {existing_drm_type} is not matching with user's DRMType {user_drm_type}")
                conftst_helpers.remove_drm_type_and_feature(*remove_attr)
                conftst_helpers.add_drm_type_and_feature(*add_attr)
            try:
                notification_res = ExecutionContext.service_api.get_notificationSend()
                logger.debug(f"Send notification response: {notification_res}")
            except Exception as ex:
                logger.error("After 6 retries, get_notificationSend request failed with:\n{}".format(ex))


def update_params_after_setting_actual_tsn():
    """
    These params need to be updated with actual TSN
    """
    ExecutionContext.service_api.set_settings_dependent_variables(is_re_request_endpoints=True)
    if ExecutionContext.service_api.get_max_mind_version(set_mind_version=True) is None:
        # Satisfied condition means that maxMindVersion failed to be retried
        # (bodyConfigSearch returned empty bodyConfig). Possible cause - box wasn't started.
        # Incorrect maxMindVersion may lead to unexpected futher failures.
        logger.warning("Could not get maxMindVersion after setting actual TSN")
    # Some requests require caDeviceId and since it's not mandatory param for Managed boxes,
    # let's set it here if it's not set yet
    if Settings.is_internal_environment() and not Settings.is_external_mso() and not Settings.ca_device_id:
        setattr(Settings, "ca_device_id", get_actual_device_id(mode="ca_device_id"))
    add_channel_packages()


def check_mandatory_params():
    if Settings.is_managed():
        mandatory_args = ['device_ip', 'mso', 'driver_type', 'platform']
    elif Settings.is_unmanaged():
        mandatory_args = ['device_ip', 'mso', 'driver_type', 'platform']
    else:  # keep tsn as mandatory param for STBs, and the rest
        mandatory_args = ['device_ip', 'mso', 'tsn', 'driver_type', 'platform']
    args = map(operator.itemgetter(0), Settings.__dict__.items())
    arg_check = list(set(mandatory_args) - set(args))
    if len(arg_check) > 0:
        raise pytest.UsageError(None, f"Missing Argument : {arg_check}")
    for arg in mandatory_args:
        test = getattr(Settings, arg)
        if not test:
            raise pytest.UsageError(None, f"Mandatory argument : {arg} has no value")
    param_value_validation()
    if not Settings.log_path:
        Settings.log_path = os.path.join(os.getcwd(), "log_dir")
    os.makedirs(Settings.log_path, exist_ok=True)
    # conftst_helpers.generate_artifacts_folder(Settings)
    # TODO: TSN block should be moved to get_dut_env() fixture
    find_and_dump_tsn_common()
    update_params_after_setting_actual_tsn()
    # TODO: Create session scope fixture for health checks
    if Settings.check_ndvr_enabled:
        check_nDVR_active()
    if Settings.check_provisioning:
        check_device_provisioning()


@pytest.fixture(autouse=True, scope="session")
@skip_health_check
def gen_good_channels():
    setattr(Settings, 'mso_locality', get_mso_service_id())
    logger.warning(f"Mso Service Id : {Settings.mso_locality}")
    if Settings.is_android_tv():
        setattr(Settings, 'good_channels', get_good_channels())
        logger.warning(f"Good channel list updated with channels: {Settings.good_channels}")
        setattr(Settings, 'socu_channels', get_socu_channels())
        logger.warning(f"SOCU channel list updated with channels: {Settings.socu_channels}")
        setattr(Settings, 'ndvr_channels', get_ndvr_channels())
        logger.warning(f"NDVR channel list updated with channels: {Settings.ndvr_channels}")
        setattr(Settings, 'tplus_channels', get_tivoplus_channels())
        logger.warning(f"NDVR channel list updated with channels: {Settings.tplus_channels}")
        if Settings.localization:
            setattr(Settings, 'loki_labels', get_loki_labels())


def param_value_validation():
    """
    Checking if param has correct value
    """
    error_msgs = ""
    params_to_validate = {
        "Settings.mso": Settings.mso in vars(MsoList).values(),
        "Settings.platform": Settings.platform in vars(PlatformList).values(),
        "Settings.driver_type": Settings.driver_type in vars(DriverTypeList).values(),
        "Settings.test_environment": Settings.test_environment in vars(MindEnvList).values(),
        "Settings.branch": Settings.branch in vars(HydraBranches).values(),
        "Settings.language": Settings.language in vars(LanguageList).values(),
        "Settings.push_test_conf": Settings.push_test_conf in ["true", "false"],
        "Settings.use_zipalign": Settings.use_zipalign in ["true", "false"],
        "Settings.fail_build_upon_install_failure": Settings.fail_build_upon_install_failure in ["true", "false"],
        "Settings.port": str(Settings.port).isdigit() and 1 < int(Settings.port) < 65536,
        "Settings.device_ip": ipv4(Settings.device_ip) or ipv6(Settings.device_ip) or domain(Settings.device_ip),
    }
    for param, value in params_to_validate.items():
        if not value:
            error_msgs += f"'{param}' param contains not supported '{eval(param)}' value\n"
    if error_msgs:
        raise pytest.UsageError(None, error_msgs)


def pytest_configure(config):
    settings = [item for item in Settings.__dict__.items() if not item[0].startswith('_')]
    config.addinivalue_line("markers", "notapplicable(name) : mark tests not to get executed")
    custom_markers = read_dynamic_marker()
    for custom_marker, values in custom_markers.items():
        config.addinivalue_line("markers", f"{custom_marker} : mark tests not to get executed")

    for atr, value in settings:
        try:
            setattr(Settings, atr, get_user_option(config, atr, value))
        except ValueError:
            pass
    initialize_mind_api()
    check_mandatory_params()
    # temporary workaround due to parameter renaming
    if Settings.stage and not Settings.app_env_config:
        logger.warning("Obsolete configuration 'stage'. Pls use app_env_config instead")
        Settings.app_env_config = Settings.stage
    if Settings.vt_video_input and "@" in Settings.vt_video_input:
        # parsing VT config
        input_type, vt_video_input = Settings.vt_video_input.split("@")
        Settings.vt_video_input = vt_video_input
        if input_type and "vision" not in input_type:
            Settings.vt_hardware = input_type
    Settings.dbg_verbose_mode = int(Settings.dbg_verbose_mode)
    Settings.utaf_analytics = int(Settings.utaf_analytics)
    global health_check
    try:
        health_check = not config.getoption('skip_health_check')
    except Exception:
        pass
    Settings.build = conftst_helpers.get_build_number(Settings)
    logger.warning(f"Build number to install is {Settings.build}")
    path = os.path.join(Settings.root_log_path or Settings.log_path, 'buildname.txt')
    with open(path, "wt") as build_file:
        build_file.write(Settings.build)
    get_deeplink_ott_list()


def read_dynamic_marker():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + '/test_execution_markers.yml') as yfile:
        execution_markers = yaml.load(yfile, Loader=yaml.FullLoader)

    return execution_markers


def pytest_collection_modifyitems(config, items):
    mso_features = MSOFeatures()
    custom_markers = read_dynamic_marker()
    selected = []
    deselected = []
    check = False
    unsupported_list = mso_features.get_unsupported_features(Settings.mso.lower())
    for item in items:
        item_marker_names = [mark.name for mark in item.iter_markers()]

        for custom_marker, tests in custom_markers.items():
            for test_file, test_case_from_yaml in tests.items():
                # https://jira.tivo.com/browse/CA-6886
                # item.name collected test name, may have additional symbols, if parametrized
                for test_c in test_case_from_yaml:
                    if test_c in item.name:
                        item.add_marker(custom_marker)
                        break
        not_applicable = [mark.args[0] for mark in item.iter_markers(name="notapplicable")]
        check = any(check_item in item_marker_names for check_item in unsupported_list)
        if check or (True in not_applicable):
            deselected.append(item)
        else:
            selected.append(item)
    config.hook.pytest_deselected(items=deselected)
    items[:] = selected


def pytest_collection_finish(session):
    selected_markers = []
    for item in session.items:
        for marker in item.own_markers:
            selected_markers.append(marker.name)
    session.config.cache.set("selected_markers", list(set(selected_markers)))


@pytest.fixture(autouse=True, scope="function")
def setup_add_api_headers_test_scope(request):
    """
    This fixture sets Settings.api_additional_headers.
    It should be run before every test to provider specific params for API headers requested by service team
    for collecting statistics data.

    Settings.api_additional_headers: it's used in mind_api.open_api.open_api.SeriviceOpenAPI, next keys are set:
     - assigned_marker_names: str, comma-separated markers assigned to currently running test e.g. "marker1, marker_2, test_3"
     - test_case_name: currently running test name e.g. test_one or test_one[True-False-param1] (if parametrized test)
    """
    assigned_marker_name_list = list()
    api_additional_headers = dict()
    markers_obj_list = request.node.own_markers
    for marker_obj in markers_obj_list:
        assigned_marker_name_list.append(marker_obj.name)
    api_additional_headers["assigned_marker_names"] = ", ".join(map(str, assigned_marker_name_list))
    api_additional_headers["test_case_name"] = request.node.name
    setattr(Settings, "api_additional_headers", api_additional_headers)


def get_env_conf(name=None, default=None):
    """
    Method to get parameters from OS environment variables. It can get all OS variables if name is not specified

    :param name: str, name of OS variable to be extracted
    :param default: any, default parameter value in case of OS doesn't have parameter
    :return: str, dict
    """
    if name is not None:
        conf = os.environ.get(name, default)
    else:
        conf = os.environ
    return conf


@pytest.fixture(autouse=False, scope="session")
def add_loggers(request):
    """
    The fixture to configure loggers
    It uses built-in pytest arguments to configure loggigng level and files

        Parameters:
            log_level or --log-level general log level for capturing
            log_file_level or --log-file-level  level of log to be stored to a file. Usually lower than general log
            log_file or --log-file  path where logs will be saved
    """
    log_level = request.config.getini("log_level") or request.config.getoption("--log-level") or "INFO"
    log_file_level = request.config.getini("log_file_level") or request.config.getoption("--log-file-level") or "DEBUG"
    log_file = request.config.getini("log_file") or request.config.getoption("--log-file")
    if not log_file:
        log_file = os.path.join(os.path.abspath(Settings.log_path), "pytest.log")
    else:
        log_file = os.path.abspath(log_file)
    logger.info("General loglevel: '{}', File: '{}'".format(log_level, log_file_level))
    logger.info("Test's logs will be stored: '{}'".format(log_file))
    logger.setup_cli_handler(level=log_level)
    logger.setup_filehandler(level=log_file_level, filename=log_file)


def setup_re_activating_account(request):
    """
    Sometimes, account may be cancelled after running the tests.
    So need to check:
     - Account state is active, activate account if it's canceled

    Args:
        request: request pytest fixture

    Returns:
        bool, True if status changed from canceled to active
              False if account already is in active state
    """
    logger.info("Setting up... Re-activating account if it's canceled")
    device_status = ExecutionContext.pps_api_helper.get_device_details(Settings.ca_device_id)[0]["status"]
    if device_status != "active":
        request.cls.acc_locked_page.re_activate_device()
        return True
    return False


def setup_bind_hsn(request):
    """
    Sometimes, HSN may not have binding after running the tests.
    So need to check:
     - HSN is bound, bind HSN if binding is not found

    Args:
        request: request pytest fixture

    Returns:
        bool, True if HSN was unbound and became bound
              False if HSN was already bound
    """
    logger.info("Setting up... Binding HSN if it's not bound")
    if Settings.is_managed():
        binding_get = ExecutionContext.iptv_prov_api.device_binding_get(
            Settings.hsn, request.cls.service_api.get_mso_partner_id(Settings.tsn))
        if "error" in binding_get["type"] and (binding_get["debug"] == "1014" or binding_get["debug"] == "1015"):
            ExecutionContext.iptv_prov_api.bind_hsn(Settings.hsn,
                                                    request.cls.service_api.get_mso_partner_id(Settings.tsn),
                                                    request.cls.service_api.getPartnerCustomerId(Settings.tsn))
            return True
        elif "error" in binding_get["type"]:
            raise AssertionError(f"deviceBindingGet failed with: \n{binding_get}")
    return False


def push_custom_config_files(request):
    """
    Method to push any custom files from host's space to DUT
    files are defined in pytest.ini  in parameter 'custom_cfg_files'
    custom_cfg_files - is multiline parameter ':' separated
    """
    if Settings.is_android_tv():
        config = get_user_option(request.config, "custom_cfg_files", "")
        logger.info("Next files are going to be pushed :{}".format(config))
        for line in config.splitlines():
            if ":" in line:
                src, _, dst = line.partition(":")
                request.cls.driver.driver.push_file(src, dst)
            else:
                raise ValueError("Unsupported parameter format. '{}'".format(line))


def remove_custom_config_files(request):
    """
    Method to remove any custom files from host's space to DUT
    files are defined in pytest.ini  in parameter 'custom_cfg_files'
    custom_cfg_files - is multiline parameter ':' separated
    """
    if Settings.is_android_tv():
        config = get_user_option(request.config, "custom_cfg_files", "")
        logger.info("Next files are going to be removed :{}".format(config))
        for line in config.splitlines():
            if ":" in line:
                src, _, dst = line.partition(":")
                src = os.path.expandvars(src)
                # logic to calculate remote path to prevent removal of root folder
                src_basename = os.path.basename(src) or os.path.basename(os.path.dirname(src))
                dst_norm_path = dst if os.path.basename(dst) else os.path.join(dst, src_basename)
                request.cls.driver.driver.remove_folder_from_device(dst_norm_path)
            else:
                raise ValueError("Unsupported parameter format. '{}'".format(line))


@pytest.fixture(autouse=True, scope="session")
def get_app_package_name():
    Logger(__name__).info("FIXTURE: get_app_package_name")
    if Settings.is_android_tv() and not Settings.is_dev_host():
        if Settings.is_managed():
            Settings.app_package = "com.tivo.hydra.app"
        else:
            if Settings.is_unmanaged() and Settings.mso.lower() == "blueridge":
                Settings.app_package = f"com.tivo.androidtv.{Settings.mso.lower()}"
            elif Settings.is_unmanaged() and Settings.mso.lower() == "mediacom":
                Settings.app_package = "com.tivo.androidtv.xtreamtv"
            else:
                Settings.app_package = f"com.tivo.android.{Settings.mso.lower()}"
    elif Settings.is_apple_tv():
        Settings.app_package = conftst_helpers.get_aut_name_apple_tv(Settings)


@pytest.fixture(autouse=True, scope="session")
def initialize_driver_session(request):
    Logger(__name__).info("FIXTURE: Driver INIT")
    driver_config = driverfactory.DeviceDriverConfig(
        device_ip=Settings.device_ip,
        driver_type=Settings.driver_type,
        screen_cap_location=Settings.log_path,
        screen_dump_location=Settings.log_path,
        system_log_location=Settings.log_path,
        target_app=Settings.app_package,
        device_id=Settings.device_id,
        adb_path=Settings.adb_path,
        platform_os_version=Settings.os_version,
        appium_ip=Settings.appium_ip,
        appium_hub=Settings.hub,
        port=Settings.port,
        transport=Settings.transport,
        rasp_ip=Settings.rasp_ip,
        rasp_user=Settings.rasp_user,
        rasp_pwd=Settings.rasp_pwd,
        rasp_dump=Settings.rasp_dump,
        rpmdir=Settings.rpmdir,
        driver_restart_time_max_second=Settings.driver_restart_time_max_second,
        xlst_parser=Settings.xlst_parser,
        rasp_nic_to_box=Settings.rasp_nic_to_box,
    )
    driver_factory = driverfactory.DriverFactory(driver_config)
    session = request.node
    for item in session.items:
        cls = item.getparent(pytest.Class)
        setattr(cls.obj, "driver", driver_factory)
    yield
    try:
        logger.info("Session driver finalization")
        driver_factory.close()
    except Exception as err:
        logger.info(f"Session driver finalized failed: {err}")


@pytest.fixture(autouse=False, scope="session")
def get_dut_env(request):
    find_and_dump_tsn_common()


@pytest.fixture(autouse=True, scope="function")
def get_dut_viewport_resolution(request):
    log = Logger(__name__)
    if not hasattr(request.config.option, "viewport"):
        try:
            lines = request.cls.driver.driver.find_str_in_log("viewport:", since="start") or ""
        except Exception as err:
            log.info(f"Failed to get viewport: {err}")
            lines = ""
        result = re.search(r"viewport: \((?P<width>\d+), (?P<height>\d+)\)", lines)
        log.info(f"Searching viewport info in DUT logs: {result}")
        if result:
            width = result.group("width")
            height = result.group("height")
            request.config.option.viewport = f"{width}, {height}"
    else:
        log.debug(f"Viewport in DUT logs: {request.config.option.viewport}")


@pytest.fixture(autouse=True, scope="class")
def setup_driver(request):
    Logger(__name__).info("FIXTURE: Driver START")
    request.cls.screen = request.cls.driver.screen
    push_custom_config_files(request)
    get_sdcard_stats(request)
    try:
        request.cls.driver.start()
    except Exception as err:
        if "reboot the device" in str(err):
            hard_device_reboot(Settings.device_ip)
        elif "App with bundle identifier" in str(err):
            install_build_function(request)
        else:
            raise
    finally:
        request.cls.driver.start()
    get_sdcard_stats(request)
    Settings.driver = request.cls.driver
    request.config.Settings = Settings
    request.cls.api = ExecutionContext.service_api
    request.cls.service_api = ExecutionContext.service_api
    request.cls.mind_if = ExecutionContext.mind_if
    request.cls.iptv_prov_api = ExecutionContext.iptv_prov_api
    request.cls.vod_api = ExecutionContext.vod_api
    request.cls.pps_api_helper = ExecutionContext.pps_api_helper
    request.cls.loki_labels = ExecutionContext.loki_labels
    request.cls.api_parser = ExecutionContext.api_parser
    request.cls.health_api = ExecutionContext.health_api
    request.cls.eula_api = ExecutionContext.eula_api
    update_device_specific_prop(request)
    check_and_enable_notifications(request)
    check_and_free_device_memory(request)
    get_device_resolution(request)

    yield
    if health_check and (Settings.bugreports or request.session.testsfailed):
        logger.info("Taking bugreport")
        conftst_helpers.generate_bugreport(request)
    remove_custom_config_files(request)
    remove_bugreports(request)
    items_to_finalize = (request.cls.driver.close,
                         )
    for item in items_to_finalize:
        try:
            item()
        except Exception as error:
            logger.error("Finalization of {} is failed with error '{}'".format(item, error))


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_setup(item):
    logger.info("FIXTURE: init_artifacts_folder")
    request = item._request
    artifacts = conftst_helpers.generate_artifacts_folder(Settings, request)
    # TODO: refresh DUT logs
    try:
        # TODO: set new screenshot path
        if hasattr(request.cls, "driver"):
            request.cls.driver.driver.screen_cap_location = artifacts
            request.cls.driver.driver.system_log_location = artifacts
    except Exception as err:
        logger.error(f"Unable update screenshot location. Error: {err}")
    # pytest.log
    config = item.config
    logging_plugin = config.pluginmanager.get_plugin("logging-plugin")
    filename = os.path.join(artifacts, "pytest.log")
    if not os.path.exists(filename):  # to avoid log overriding
        logging_plugin.set_log_path(filename)
    yield


def update_device_specific_prop(request):
    try:
        mrphus = ExecutionContext.service_api.get_morpheus_release_info()
        logger.info("Morpheus release: {}".format(mrphus))
        glob_vars = request.config.option
        glob_vars.morpheus_rls = Settings.morpheus_rls = mrphus
        if health_check:
            tsns = ExecutionContext.service_api.get_npvr_and_internal_tsn()
            if tsns:
                glob_vars.external_id = tsns["externalId"]
                glob_vars.internal_id = tsns["internalId"]
            Settings.bh_status = str(ExecutionContext.service_api.get_feature_status("diagnosticsLoggingEnabled"))
            if not Settings.pcid:
                Settings.pcid = ExecutionContext.service_api.getPartnerCustomerId()
        if Settings.is_android_tv():
            Settings.google_id = request.cls.driver.driver.get_google_id()
        glob_vars.os_version = Settings.os_version
        glob_vars.device_model = Settings.device_model
        glob_vars.hsn = Settings.hsn
        glob_vars.tsn = Settings.tsn
        glob_vars.firmware = Settings.firmware
        glob_vars.ui_error_code = ""
        glob_vars.url_error_code = ""
        glob_vars.channel_name = ""
        glob_vars.ndvr_store_resp = ""
        glob_vars.socu_store_resp = ""
        glob_vars.livetv_post_resp = ""
        glob_vars.livetv_channels = Settings.good_channels
        glob_vars.socu_channels = Settings.socu_channels
        glob_vars.ndvr_channels = Settings.ndvr_channels
        glob_vars.tivoplus_channels = Settings.tplus_channels
        glob_vars.google_account = Settings.google_account
        glob_vars.google_password = Settings.google_password
        glob_vars.rail_id = ""
        glob_vars.device_serial_no = Settings.device_serial_no
        glob_vars.pcid = Settings.pcid
        glob_vars.mso_locality = Settings.mso_locality
        glob_vars.sdcard_stats = Settings.sdcard_stats
        glob_vars.google_id = Settings.google_id
        glob_vars.proc_stats_mem_usage = Settings.proc_stats_mem_usage
        glob_vars.proc_stats_uptime_elapsed_time = Settings.proc_stats_uptime_elapsed_time
        glob_vars.procstats_sys_mem_usage = Settings.procstats_sys_mem_usage
        glob_vars.meminfo_ram = Settings.meminfo_ram
        glob_vars.meminfo_zram = Settings.meminfo_zram
        glob_vars.meminfo_lostram = Settings.meminfo_lostram
        glob_vars.bh_status = ""
        glob_vars.xray_id = ""
        glob_vars.bh_status = Settings.bh_status
        glob_vars.vt_video_input = Settings.vt_video_input
        glob_vars.vt_server = Settings.dut_hub
        glob_vars.dut_hub = Settings.dut_hub
        glob_vars.error_id = ""
        glob_vars.human_error = ""
        glob_vars.drm_type = Settings.drm_type
    except Exception as e:
        logger.info("Device specific prop population failed: {}".format(e))


def get_installed_app_version(driver, env_config):
    try:
        info = driver.get_app_info(env_config.app_package)
        version = info['versionName']
        branch = info['versionBranch']
        logger.info("Installed build version={}".format(version))
    except Exception as err:
        logger.debug("Unable to detect installed build info with error: {}".format(err))
        version = ""
        branch = ""
    return version, branch


def get_tcdui_test_path():
    """
    method to get path to tcdui_test.conf file according to settings
    supports: appletv and android boxes.

    For managed devices file will be generated from golden
    For unmanaged - golden will returned
    """
    if Settings.tscdui_conf:
        tcdui_file = Settings.tscdui_conf
    elif not os.path.exists(os.path.join(Settings.ROOT, 'test_data/provisioning/specializations.csv')):
        # for MSO executions
        platform = "apple_tv" if Settings.is_apple_tv() else "android"
        tcdui_file = os.path.join(Settings.ROOT, f'test_data/provisioning/{platform}/tcdui_test.conf')
    else:
        # config is different from streamer 1.13 branch.
        branch = "streamer-1-13"
        if Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13):
            branch = "streamer-1-11"
        utaf_path = os.path.abspath(__file__).partition("set_top_box")[0]
        specialization_file_path = os.path.join(utaf_path,
                                                f"test_data/provisioning/set_top_box/{branch}/specializations.csv")

        selector = TcdiuConfSelector(os.path.join(Settings.ROOT, 'test_data/provisioning/'),
                                     Settings.log_path, specialization_file_path=specialization_file_path)
        platform = "apple_tv" if "apple" in Settings.driver_type else "android"
        # for android OneAPK - env is configuring using tcdui_test.conf
        tcdui_file = selector.get_custom_tcduiconf(platform=platform,
                                                   mso=Settings.mso,
                                                   app_env_config=Settings.app_env_config,
                                                   test_environment=Settings.test_environment,
                                                   manage_id=Settings.manage_id,
                                                   )

        tmp_tcdui_location = os.path.join(Settings.log_path, "tcdui_test.conf")
        tcdui_parser = TcduiConf()
        if tcdui_file != tmp_tcdui_location:
            Commands().cp(tcdui_file, tmp_tcdui_location)
        else:
            logger.info("tcdui_test changing in the same file")
        tcdui_parser.load(tmp_tcdui_location)
        for item in Settings.TCDUI_TEST_CONF_PROPS:
            # Handle Overlay as per BZSTREAM-10014
            if MindEnvList.PROD in Settings.test_environment.lower() and "IPTV_26358" in item:
                setattr(Settings, f"{item}", "true")
            if eval(f"Settings.{item}"):
                eval(f"tcdui_parser.update({item}=Settings.{item})")
        tcdui_parser.dump(tmp_tcdui_location)
        tcdui_file = tmp_tcdui_location
    return tcdui_file


@pytest.fixture(autouse=False, scope="class")
def pre_run_setup(request):
    """
    This fixture comes in handy for pipelines that run test_mandatory_test before other tests
    that cancel account and/or clear HSN binding to automatically get account back to normal.
    Handles cases:
     - When somebody aborted run while test canceled account or removed HSN binding (e.g. run stuck)
     - Cleanup fixture failed to re-activate account or bind HSN (e.g. service issue)
     - Added new test without cleanup fixture
    Actions:
     - Re-activates account if it canceled
     - Binds HSN if it's unbound
     - Relaunches the Hydra app when either account state changed from canceled to active or HSN got bound
    """
    logger.info("Fixture: pre_run_setup")
    used_for_markers = ["account_locked", "hospitality", "fasu"]
    is_run = False
    selected_tests = request.config.cache.get("selected_markers",
                                              [])  # for cases when tests passed in not with -m param
    passed_in_markers = request.config.getoption("-m")
    # acc_reactivation marker is not assigned to any test, it's needed only for mandatory_test when running it from Jenkins
    # if one of used_for_markers markers is passed in
    if "acc_reactivation" in passed_in_markers:
        is_run = True
    else:
        # Checking if one of selected markers is one of used_for_markers
        for marker in selected_tests:
            if marker in used_for_markers:
                is_run = True
                break
    if is_run and Settings.ca_device_id and Settings.is_internal_environment() and not Settings.is_external_mso():
        got_reactivated = setup_re_activating_account(request)
        got_bound = setup_bind_hsn(request)
        # devhost does not support app relaunch
        if (not Settings.is_dev_host() or not Settings.is_apple_tv()) and \
                (got_reactivated or got_bound) and request.cls.screen.base.is_app_installed(Settings.app_package):
            request.cls.home_page.relaunch_hydra_app()
    else:
        logger.info("pre_run_setup fixture skipped")


@pytest.fixture(autouse=True, scope="class")
def install_build(request):
    Logger(__name__).info("FIXTURE: Install_build_function")
    install_build_function(request)


def install_build_function(request):  # noqa: C901
    """
    Fixture to install build to a device if `Settings.build` and `Settings.build_source` are specified.
    Alse there is a verification of already installed version and required version - if they are equal the installation
    process will be skipped
    """
    Settings.aut_build, aut_branch = get_installed_app_version(request.cls.driver, Settings)
    logger.debug("Existing build info: {}/{}".format(Settings.aut_build, aut_branch))
    if Settings.is_aut_update_enabled():
        logger.info("Requested build update to: {}".format(Settings.build))
        if Settings.build and not re.search(Settings.build, Settings.aut_build):
            logger.info("Going to download and deploy build: {}".format(Settings.build))
            build_path = request.cls.driver.download_build(source=Settings.build_source,
                                                           branch=Settings.branch,
                                                           mso=Settings.mso,
                                                           stage=Settings.stage,
                                                           app_env_config=Settings.app_env_config,
                                                           test_environment=Settings.test_environment,
                                                           manage_id=Settings.manage_id,
                                                           build_number=Settings.build,
                                                           platform=Settings.platform,
                                                           version=Settings.build_version,
                                                           use_zipalign=Settings.use_zipalign,
                                                           )
            Settings.build_download_url = request.cls.driver.get_download_url()

            tcdui_test_conf = get_tcdui_test_path()
            provision_file = os.path.join(Settings.ROOT,
                                          'test_data/provisioning/apple_tv/Automation.mobileprovision')
            if build_path:
                request.cls.driver.install(build_path,
                                           certificate=get_env_conf("DEV_CERTIFICATE"),
                                           provision_file=get_env_conf("TVOS_PROVISIONING", provision_file),
                                           tcdui_conf=tcdui_test_conf)
            logger.info("Current version: {}".format(request.cls.driver.get_app_info(Settings.app_package)))
            if Settings.is_android_tv():
                request.cls.driver.launch_app(Settings.app_package)
            time.sleep(5)  # app loading delay
        else:
            logger.info("No needs to update build. Cur: {}/{}, Requested:{}".format(Settings.aut_build,
                                                                                    aut_branch,
                                                                                    Settings.build))
        if Settings.rooted and Settings.is_android_tv():
            exo_properties = {}
            path = None
            if Settings.exo_prop_url:
                exo_properties['playUrl'] = Settings.exo_prop_url
            exo_properties['debugLevel'] = 0
            if Settings.exo_prop_path:
                path = Settings.exo_prop_path
            request.cls.driver.driver.set_exo_properties(exo_properties, path)
    request.config.option.build = Settings.build


@pytest.fixture(autouse=True, scope="class")
def push_tcdui_test_conf(request):
    """
    This fixture is run once before running the tests of class scope
    """
    is_push_enabled = Settings.push_test_conf.lower() == "true"
    platform_allowed = Settings.is_android_tv() and not Settings.is_dev_host()
    is_aut_reinstalled = Settings.is_aut_update_enabled() and not re.search(Settings.build, Settings.aut_build)
    if is_push_enabled and platform_allowed and not is_aut_reinstalled:
        logger.info("push_tcdui_test_conf> tcduitest.conf needs to be updated")
        tcdui_test_conf = get_tcdui_test_path()
        if not request.cls.driver.driver.examine_device_test_conf(tcdui_test_conf) or \
                Settings.platform == PlatformList.FALCON3:
            request.cls.driver.driver.push_file(tcdui_test_conf, request.cls.driver.driver.remote_tcdui_test_conf)
            request.cls.driver.driver.stop_app(Settings.app_package)
            request.cls.driver.driver.launch_app(Settings.app_package)
            try:
                request.cls.screen.wait_for_screen_ready(timeout=40000)
            except Exception:
                logger.info("Failure observed in wait_for_screen_ready")
        else:
            logger.info("tcdui_test.conf - remain same, reboot don't required")
    else:
        logger.info("push_tcdui_test_conf> tcduitest.conf existing will be used")


@pytest.fixture(autouse=True)
def verify_app_state(request):
    logger.info("Executing fixture: verify_app_state")
    drv = request.cls.driver.driver
    if request.cls.driver.driver.driver_name == "android Driver" and Settings.app_package:
        if not request.cls.driver.driver.verify_foreground_app(Settings.app_package):
            request.cls.driver.driver.launch_app(Settings.app_package)
            # waiting 3 seconds to not catch previously issued screen ready event
            time.sleep(3)
            request.cls.screen.wait_for_screen_ready(timeout=40000)
        if Settings.is_unmanaged() and Settings.app_package in request.cls.driver.driver.get_current_focused_app()[0]:
            try:
                request.cls.screen.refresh()
            except Exception as e:
                logger.info("Screendump failed with error: {}".format(e))
            if "NoNetworkScreen" in request.cls.guide_page.view_mode():
                request.cls.screen.base.press_enter()
    elif Settings.is_apple_tv() and not drv.verify_foreground_app(Settings.app_package):
        # temporaty condition to test appium integration
        drv.launch_app(Settings.app_package)
        request.cls.screen.wait_for_screen_ready(timeout=40000)
    request.cls.driver.driver.current_tc = request.node.name


@pytest.fixture(autouse=False, scope="class")
def run_state_log(request):
    """
    The method for generating memory consumption log per run
    """
    Logger(__name__).info("FIXTURE: run_state_log")
    if request.cls.driver.driver.driver_name == "android Driver" and Settings.app_package:
        logger.info(request.cls.driver.driver.get_app_memory_usage_info(Settings.app_package))
        logger.info(request.cls.driver.driver.get_cpu_usage_info())
    yield
    if request.cls.driver.driver.driver_name == "android Driver" and Settings.app_package:
        logger.info(request.cls.driver.driver.get_app_memory_usage_info(Settings.app_package))
        logger.info(request.cls.driver.driver.get_cpu_usage_info())


@pytest.fixture(autouse=False, scope="class")
def device_reboot_to_imporve_device_perf(request):
    reboot_required = Settings.reboot_required
    logger.debug(f"reboot_required: {reboot_required}")
    if eval(Settings.reboot_required.title()):
        passed_in_marker = request.config.getoption("-m")
        logger.debug(f"DRTIDP passed_in_marker: {passed_in_marker}")
        available_markers = ["p1_regression_tests", "full_regression_tests", "E2E"]
        if passed_in_marker in available_markers and not Settings.is_apple_tv():
            logger.step("Rebooting the device to improve performance..")
            home_label = request.cls.home_labels.LBL_HOME_SCREEN_NAME
            request.cls.driver.driver.current_tc = "device_reboot_to_imporve_device_perf"
            try:
                request.cls.home_page.relaunch_hydra_app(home_label, wait_reboot=180, reboot=True)
            except Exception:
                logger.info("Device has rebooted but still not up. Waiting for device to come up")
                time.sleep(45)
            if request.cls.driver.driver.get_foreground_package() != Settings.app_package:
                request.cls.driver.driver.launch_app(Settings.app_package)
            logger.info("Waiting for home sccreen to load with wait_for_screen_ready")
            request.cls.home_page.wait_for_screen_ready(request.cls.home_labels.LBL_HOME_SCREEN_NAME, 1200000)
            logger.info("Device reboot is successfull")


@pytest.fixture(autouse=False, scope="class")
def clean_ftux_and_sign_in(request):
    logger.step("Fixture: clean_ftux_and_sign_in")
    # workaround to update XrayID on fixture stage
    request.config.option.xray_id = f"https://jira.tivo.com/browse/{conftst_helpers.get_current_xray_id(request)}"
    request.cls.home_page.guide_page = request.cls.guide_page
    if Settings.media_audio_flinger and not Settings.is_apple_tv():
        request.cls.driver.driver.media_audio_flinger_logs()
    if Settings.is_apple_tv():
        # instead of getting CPU stat we are checking keyeventserver and rebot devise if not available
        request.cls.screen.wait_for_screen_ready(timeout=60000)  # before check hydra we should wait for start
        check_and_recover_appletv(request)
    request.cls.driver.driver.current_tc = "clean_ftux_and_sign_in"
    if request.cls.driver.driver.driver_name == "android Driver" and Settings.app_package:
        (current_focus, focus_app) = request.cls.driver.driver.get_current_focused_app()
        logger.info("mFocusedApp: {} mCurrentFocus:{}".format(focus_app, current_focus))
        if Settings.app_package in focus_app and Settings.app_package not in current_focus:
            logger.info("Device is sleeping.. Waking Up")
            request.cls.home_page.wake_up_box()
        if request.cls.driver.driver.get_foreground_package() != Settings.app_package:
            logger.debug("AUT is not on foreground")
            request.cls.driver.driver.launch_app(Settings.app_package)
            request.cls.screen.wait_for_screen_ready(timeout=40000)
            if not request.cls.driver.driver.verify_foreground_app(Settings.app_package):
                request.cls.driver.driver.launch_app(Settings.app_package)
                request.cls.screen.wait_for_screen_ready(timeout=40000)
        if Settings.is_unmanaged() and Settings.app_package in request.cls.driver.driver.get_current_focused_app()[0]:
            try:
                request.cls.screen.refresh()
            except Exception:
                logger.debug("Handle ExitConfirmationOverlay [IPTV-20629]")
                request.cls.screen.base.press_down()
                request.cls.screen.base.press_enter()
            if "NoNetworkScreen" in request.cls.guide_page.view_mode():
                request.cls.screen.base.press_enter()
            if not request.cls.driver.driver.verify_foreground_app(Settings.app_package):
                request.cls.driver.driver.launch_app(Settings.app_package)
                request.cls.screen.wait_for_screen_ready(timeout=40000)
        # fix for mtbc
        if request.cls.driver.driver.get_foreground_package() != Settings.app_package:
            logger.debug("Handle MTBC issue")
            request.cls.screen.base.press_home()
            request.cls.screen.wait_for_screen_ready(timeout=40000)
            if not request.cls.driver.driver.verify_foreground_app(Settings.app_package):
                request.cls.driver.driver.launch_app(Settings.app_package)
                request.cls.screen.wait_for_screen_ready(timeout=40000)
        # For Dimming Screeen
        if Settings.app_package in current_focus:
            request.cls.screen.handle_external_assert(raise_error=False)
            try:
                request.cls.screen.refresh()
            except Exception:
                logger.debug("assert was seen bit late. refer: CA-22478")
            if request.cls.home_labels.LBL_DIMMING_SCREEN_VIEW_MODE == request.cls.guide_page.view_mode():
                logger.info("Pressing ENTER to return to TiVo screen")
                request.cls.screen.base.press_enter()

    request.cls.screen.handle_external_assert(raise_error=False)
    try:
        request.cls.screen.refresh()
    except Exception:
        logger.debug("assert was seen bit late. refer: CA-22478")
    request.cls.home_page.dismiss_popup_overlay(request.cls)
    if Settings.is_unmanaged() and "signin" in request.cls.home_page.view_mode():
        request.cls.home_page.proceed_with_sign_in()
    if Settings.is_android_tv() and not Settings.is_dev_host():
        logger.debug("Stop uiautomator after clean_ftux_and_sign_in")
        request.cls.driver.driver.stop_app("com.github.uiautomator")  # stop uiautomtr as it enable tts CA-5521
    request.cls.home_page.skip_ftux()
    if Settings.is_amino():
        logger.info("Fixture: clean_ftux_and_sign_in: handle what's new overlay in amino box")
        request.cls.home_page.back_to_home_short()
        request.cls.home_assertions.verify_menu_item_available(request.cls.home_labels.LBL_LIVETV_SHORTCUT)
        request.cls.home_page.select_menu_shortcut_num(request.cls,
                                                       request.cls.home_labels.LBL_LIVETV_SHORTCUT,
                                                       refresh=True)
        if request.cls.home_page.verify_onscreen_trickplay_overlay() or request.cls.home_page.is_overlay_shown():
            # close any channel error overlay to avoid test failure
            request.cls.screen.base.press_enter()
        request.cls.home_page.back_to_home_short()

    # Disable TTS
    if Settings.is_android_tv() and not Settings.is_dev_host():
        logger.step("To disable TTS")
        request.cls.screen.base.TTS_on_off()
        # Check guide all channel option
        logger.step("Check guide all channel option")
        if health_check:
            # skip giude check if --skip_health_check
            #
            # TODO
            # Remove try catch and add next variables to all conftest.py files, if they are absent:
            #   - request.cls.guide_assertions
            #   - request.cls.home_page
            #   - request.cls.home_labels
            # try ... catch hides exception and so somebody may think that verify_guide_all_channel_option()
            # was run while it wasn't
            try:
                # TODO: wrap to a function in guide page
                if request.cls.home_page.is_overlay_shown() and request.cls.home_page.get_overlay_code() == \
                        request.cls.home_labels.LBL_REMIND_ME_LATER_OVERLAY:
                    request.cls.screen.base.press_down()
                    request.cls.screen.base.press_enter()
                request.cls.guide_assertions.verify_guide_all_channel_option(request.cls)
            except Exception as ex:
                logger.error(f"Failed in verifying guide channel option and proceeding further; exception: {ex}")
                request.cls.home_page.back_to_home_short()


@pytest.fixture(autouse=True)
def test_case_logger(request):
    """
        This method is to print test rail URL along with current test name
    """
    # get markers name in a list
    if not Settings.xray_ids:
        Settings.xray_ids = read_xray_ids()
    rail_ids = ''
    Settings.rail_id = ""
    xray_id = ""
    request.config.option.xray_id = ""
    ids = ['xray', 'testrail']
    for name in ids:
        for mark in request.node.own_markers:
            if name in mark.name and name == "xray":  # look for the word testrail
                xray_id = mark.args[0]  # format is a tuple
                break
            elif name in mark.name and name == "testrail":
                rail_ids = mark.kwargs['ids']
                # no need to loop through rest of list
                break

    coverage = CoverageAnalytics()
    coverage.subject = f"{request.node.name}".split("[")[0]
    coverage.set("job_id", os.getenv("BUILD_URL"))
    logger.step("::::::::::: Test case name start: {} :::::::::::::::".format(request.node.name))
    request.cls.screen.base.add_dut_log("TEST_CASE_START", "I", request.node.name)
    if not rail_ids:
        case_id = re.search(r'(\d+)', request.node.name)
        if case_id is not None:
            if len(str(case_id.group(0))) > 6:
                Settings.rail_id = "https://testrail.tivo.com//index.php?/cases/view/" + str(case_id.group(0))
                logger.step("::::::::::: Test rail link: {} :::::::::::::::".format(Settings.rail_id))
            else:
                Settings.rail_id = "https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=" + str(case_id.group(0))
                logger.step("::::::::::: Testopia case link: {} :::::::::::::::".format(Settings.rail_id))
    else:
        for rail_id in rail_ids:
            rail_id = re.sub(r'^C|T', '', rail_id)
            Settings.rail_id = "https://testrail.tivo.com//index.php?/cases/view/" + str(rail_id)
            logger.step("::::::::::: Test rail link: {} :::::::::::::::".format(Settings.rail_id))

    if not xray_id and request.node.name in Settings.xray_ids.keys():
        xray_id = Settings.xray_ids.get(request.node.name)['jira_id'][0]
    request.config.option.xray_id = "https://jira.tivo.com/browse/" + str(xray_id)
    logger.step("::::::::::: xray link: {} :::::::::::::::".format(request.config.option.xray_id))

    request.config.option.rail_id = Settings.rail_id
    request.config.option.build_download_url = Settings.build_download_url
    request.config.option.channel_playback_info = Settings.channel_playback_info
    yield
    request.config.option.test_window_start = Settings.test_window_start
    request.config.option.test_window_end = Settings.test_window_end
    logger.step("::::::::::: Test case name end: {} :::::::::::::::".format(request.node.name))
    if Settings.is_android_tv() and not Settings.is_dev_host():
        request.cls.screen.base.add_dut_log("TEST_CASE_END", "I", request.node.name)
        request.cls.screen.base.store_test_case_logs(request.node.name)
    coverage.commit_events()


def get_crash_state(item):
    """
    Function to get crash or assertion overlay state
    Args:
        item: obj, pytest obj, request ot item

    Returns:
        None or crash marker
    """
    crash_status = None
    try:
        # try for failure before driver is initialized
        crash_status = item.cls.driver.base.driver.get_event_raw_log("KernelPanic", timeout=500)
        item.cls.driver.base.driver.state_holder.set_status("KernelPanic", False)
        logger.info("Crash state: {}".format(crash_status))
    except Exception as error:
        logger.info("Crash detection failed with error: {}".format(error))
    return crash_status


def check_and_add_crash_details_to_stack_trace(request):
    attributes = request.__dict__
    current_tc = attributes.get('originalname')
    logger.info(f"\n========= START: Checking crash signature from test case: {current_tc} =========\n")
    crash_sign = []
    test_case_marker = f"TEST_CASE_START: {current_tc}"
    for marker in request.cls.home_labels.LBL_CRASH_MARKER:
        crash_log = request.cls.driver.driver.find_str_in_log(string=marker, since=test_case_marker)
        logger.info(f"::::crash_log:::: {crash_log}\n")
        if crash_log:
            crash_sign.append(crash_log)
    logger.info(f"\n========= END: Checking crash signature from test case: {current_tc} =========\n")
    return crash_sign


def clean_call_stack_hash(call_stack):
    """
    Function clean up call stack remove line numbers and anything else not needed
    convert to MD5 hash
    This is the signature of the error helps in linking Jiras
    Args
        item: string, call stack

    Returns:
        String MD5 hash
    """
    regex1 = re.compile(r"(E   )[ ]*[\n]*[a-zA-Z: \[\]0-9!.'$_\-,()\"=&>/{}?%\\<;*#\S]+", flags=re.MULTILINE)
    regex2 = re.compile(r"(:[0-9]+:)", flags=re.MULTILINE)
    regex3 = re.compile(r"\n+$", flags=re.MULTILINE)
    regex4 = re.compile(r"^(AppCrashError)[:\wa-zA-Z -\.=]+[\n]*", flags=re.MULTILINE)
    regex5 = re.compile(r"<<<<<<<<<<<=============================>>>>>>>>>>>", flags=re.MULTILINE)

    cs_filtered = re.findall(r"(?P<path>: in \w+|, in \w+|> {1,}\w.*)|(?P<error>^ {4}\w[^|\n]*\n[\w. ]*: )", call_stack)[1:]
    call_stack_filtered = "\n".join([i for line in cs_filtered for i in line if i])

    call_stack = regex1.sub('', call_stack)
    call_stack = regex2.sub('', call_stack)
    call_stack = regex3.sub('', call_stack)
    call_stack = regex4.sub('', call_stack)
    call_stack = regex5.sub('', call_stack)
    logger.step("::::::::::: call stack: {} :::::::::::::::".format(call_stack))

    call_stack_hash = hashlib.md5(call_stack_filtered.encode()).hexdigest()
    logger.step("::::::::::: call stack hash: {} :::::::::::::::".format(call_stack_hash))
    return call_stack_hash


tc_passed = (None, None)  # TC_NAME, PASSED STATUS


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    # extra = getattr(report, 'extra', [])
    crash_state = ""
    setattr(item, "test_status", report.passed)
    global tc_passed

    if report.when in ['setup', 'call']:
        if not tc_passed[0] == item.name:
            tc_passed = (item.name, None)
        if report.passed and (tc_passed[1] is not False):
            tc_passed = (item.name, True)
        elif report.failed:
            tc_passed = (item.name, False)

    if (item.config.option.songbird or Settings.songbird) and report and report.failed:
        logger.warning("Taking songbird as tc failed")
        item.cls.driver.base.capture_songbird()

    if report and report.failed:
        # update shared user_properties in report to share it with reporting plugins
        crash_state = get_crash_state(item)
        report.user_properties.append(("crash_state", crash_state))
        call_hash = clean_call_stack_hash(report.longreprtext)
        report.user_properties.append(("call_stack_hash", call_hash))

    if report.when == 'call':
        upload_channel_playback_details(item)
        if report.failed:

            crash_sign = check_and_add_crash_details_to_stack_trace(item)

            entry = report.longrepr.reprtraceback.reprentries[-1]
            logger.error("{}".format(entry.lines))

            # clean up call stack and create hash
            call_hash = clean_call_stack_hash(report.longreprtext)
            csa = CallStackAnalyzer()
            results = csa.collect(report.longreprtext)
            item.config.option.call_stack_hash = call_hash
            item.config.option.error_id = results['error_id']

            if crash_sign:
                entry.lines.extend(["", "", "---------- Test case might have failed because of below crash. Please check and analyse further."])  # noqa
                entry.lines.extend(["NOTE: This test case has failed 3 times. So, Below crashes are from all 3 runs."])
                for crash in crash_sign:
                    entry.lines.extend(["CRASH NO: {}".format(crash_sign.index(crash) + 1)])
                    entry.lines.extend(["{}".format(crash)])

            entry.lines.extend(["", "", "---------- Automation Error Signature: {}, ei:{}"
                               .format(call_hash, results['error_id'])])

            issue_type = get_issue_type(report.longreprtext)
            item.config.option.error_classification = issue_type
            entry.lines.extend(["", "", "---------- Automation Error Classification: {}".format(issue_type)])

            if item.config.getoption('tbstyle') in ('long', 'auto'):
                # add to traceback verbose screen info
                entry.lines.extend(["", "", "<<<<<<<<<<<=============================>>>>>>>>>>>"])
                if Settings.rail_id:
                    entry.lines.append(f"Testrail Link - {Settings.rail_id} \n")
                report.longrepr.reprtraceback.reprentries = [entry]

            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
                tc_name = item.name
                screenshot = os.path.join(Settings.log_path, f"{timestamp}_{tc_name}_FAIL.png")
                item.cls.driver.base.driver.dump_screen_cap_img(screenshot)
            except Exception as err:
                logger.error("During making fail screenshot got exception: {}".format(err))
    elif report.when == 'setup' and report.failed:
        try:
            crash_sign = check_and_add_crash_details_to_stack_trace(item)
            entry = report.longrepr.reprtraceback.reprentries[-1]
            logger.error("Setup failed")
            logger.error(" {}".format("\n".join(entry.lines)))

            # clean up call stack and create hash
            call_hash = clean_call_stack_hash(report.longreprtext)
            csa = CallStackAnalyzer()
            results = csa.collect(report.longreprtext)
            item.config.option.call_stack_hash = call_hash
            item.config.option.error_id = results['error_id']

            if crash_sign:
                entry.lines.extend(["", "", "---------- Test case might have failed because of below crash. Please check and analyse further."])  # noqa
                entry.lines.extend(["NOTE: This test case has failed 3 times.So below crashes are from all 3 runs."])
                for crash in crash_sign:
                    entry.lines.extend(["CRASH No. {}".format(crash_sign.index(crash) + 1)])
                    entry.lines.extend(["{}".format(crash)])

            entry.lines.extend(["", "", "---------- Automation Error Signature: {}, ei:{}"
                               .format(call_hash, results['error_id'])])

            issue_type = get_issue_type(report.longreprtext)
            item.config.option.error_classification = issue_type
            entry.lines.extend(["", "", "---------- Automation Error Classification: {}".format(issue_type)])

            logger.error("Crash status: {}".format(crash_state))
            if crash_state:
                extended_info = "AppCrashError: crash detected in {}".format(crash_state)
                entry.lines.extend(["", "", "<<<<<<<<<<<=============================>>>>>>>>>>>"])
                entry.lines.append(extended_info)
                report.longrepr.reprtraceback.reprentries = [entry]
            logger.error("<<<<<<<<<<<=============================>>>>>>>>>>>")
        except Exception as err:
            logger.error("Unable to get setup failure signature. Script: {}".format(err))
    elif report.when == 'teardown' and tc_passed[1]:
        clean_up_png(Settings.log_path, tc_passed[0])
        clean_up_png(Settings.log_path, tc_passed[0], extension='mp4', all_files=True)
        clean_up_png(Settings.log_path, tc_passed[0], extension='jpg', all_files=True)
        clean_up_dut_logs(Settings.log_path, tc_passed[0])


def clean_up_dut_logs(report_dir, testcase_name):
    """
    Method to remove DUT logs for passed testcase (controlled outside)
    Args:
        report_dir: str, path where logs are stored
        testcase_name: str, the current TC name to check logs

    Returns:
        None
    """
    extention = "log"
    testcase_name = testcase_name[0:testcase_name.index("[")] if "[" in testcase_name else testcase_name
    list_of_logs = glob.glob1(report_dir, "*{}*.{}".format(testcase_name, extention))
    if list_of_logs:
        logger.info(f"Going to remove DUT logs for passed TC: {list_of_logs}")
        try:
            for file_to_remove in list_of_logs:
                os.remove(os.path.join(report_dir, file_to_remove))
        except Exception as err:
            logger.error("Error raised while cleaning up: {}".format(err))
    else:
        logger.debug("No logs to cleanup for TC: {}".format(testcase_name))


def clean_up_png(path, testcase_name, extension="png", all_files=False):
    """
    method to remove artifacts related to TC.

    Args:
        path: str, path where cleaning will be performed
        testcase_name: str, name of TC (substring of filename to be removed)
        extension: str, extension of files to be removed
        all_files: bool, if True than all files will be removed else except one last

    """
    # Param values separated by a - are listed between [] after test case name for parametrized tests
    testcase_name = testcase_name[0:testcase_name.index("[")] if testcase_name.find("[") != -1 else testcase_name
    list_of_media_files = glob.glob1(path, "*{}*.{}".format(testcase_name, extension))
    if list_of_media_files:
        logger.info("Remove media_files for passed TC: {}".format(testcase_name))
        list_of_media_files.sort()
        if not all_files:
            excepted_media_file = [media_file for media_file in list_of_media_files
                                   if 'setup' not in media_file and 'teardown' not in media_file]
            if excepted_media_file:
                list_of_media_files.remove(excepted_media_file[-1])
        files_to_be_removed = list_of_media_files
        logger.debug("{} {} to be removed: {}".format(len(files_to_be_removed), extension, files_to_be_removed))
        try:
            for media_file in files_to_be_removed:
                os.remove(os.path.join(path, media_file))
        except Exception as err:
            logger.error("Error raised while cleaning up: {}".format(err))
    else:
        logger.info("Nothing to remove for TC: {}".format(testcase_name))


@pytest.fixture(autouse=True, scope="session")
def init_analytics(request):
    coverage = CoverageAnalytics()
    cfg = (UTAFKeychain('UTAFSplunkToken'), Settings.splunk_hec_url)
    file = os.path.join(Settings.root_log_path, "coverage_analytic.json")
    if Settings.utaf_analytics > 0:
        coverage.setup(splunk_cfg=cfg, json_file=file)


@pytest.fixture(autouse=True, scope="session")
@skip_health_check
def precondition():
    logger.info("Checking for Guide feature gridRowSearch service availability")
    response = True
    if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18):
        # Since Guide service in OpenAPI differs from one in older Hydra versions, let's call OpenAPI one
        response = ExecutionContext.service_api.get_guide_rows(ExecutionContext.service_api.get_channel_search())
    else:
        response = ExecutionContext.service_api.get_grid_row_search()
    if not response:
        pytest.fail(f"Guide feature services not available: {response}")
    logger.info("Guide feature services is available.")
    logger.info(
        "Performing check flags enablement on boxes having TSN Prefixes A8F and A9F only. Except MSO cableco5.")
    if Settings.tsn is None or Settings.tsn == '':
        msg = "Please provide the TSN. Checking the flags enablement is based on the TSN of the box."
        logger.info(msg)
        pytest.skip(msg)
    if (Settings.tsn[0:3] == "A8F" or Settings.tsn[0:3] == "A9F") and Settings.mso.lower() != 'cableco5':
        requiredGroups = get_required_groups()
        result = ExecutionContext.service_api.check_groups_enabled(requiredGroups)
        if result is False:
            pytest.fail(f"Tests skipped. Current box have TSN Prefix {Settings.tsn[0:3]} and for this prefix next "
                        f"flags are required: {requiredGroups}.")
    else:
        logger.info(
            "Flags enablement check is not performed on current box as it have "
            f"TSN Prefix {Settings.tsn[0:3]} and MSO {Settings.mso.lower()}.")


def check_device_storage(request):
    logger.info("Fetching disk memory data")
    space = None
    disk_data = request.cls.driver.driver.get_device_memory_info()
    if disk_data:
        for key, value in disk_data.items():
            if 'Mounted_on' in value.keys():
                if value['Mounted_on'] == '/storage/emulated':
                    space = value['Use%']
                    space = space.rstrip('%')
    return space


def is_memory_full(space):
    status = None
    if int(space) > 80:
        logger.info("Memory is Full: {}%".format(space))
        status = 'full'
    return status


def disable_VR(request):
    logger.info("Disabling VR")
    request.cls.driver.driver.remove_folder_from_device(path="/sdcard/VR")


def remove_bugreports(request):
    if Settings.is_android_tv() and not Settings.is_dev_host():
        logger.info("Removing bugreports from device")
        request.cls.driver.driver.remove_folder_from_device(path="/data/user_de/0/com.android.shell/files/bugreports")


def clear_user_data(request):
    logger.info("Clearing User Data")
    clear_package = "com.android.providers.tv"
    if Settings.is_fire_tv():
        clear_package = "com.amazon.providers.tv"
    request.cls.driver.driver.clear_data(clear_package)
    check_and_enable_notifications(request)


def check_and_free_device_memory(request):
    if Settings.is_android_tv() and not Settings.is_dev_host():
        remove_bugreports(request)
        logger.info("Checking device memory")
        storage_data = check_device_storage(request)
        if storage_data:
            memory_full = is_memory_full(storage_data)
            if memory_full:
                disable_VR(request)
                clear_user_data(request)
                request.cls.driver.driver.reboot_and_wait_reconnect(200)
                if not request.cls.driver.driver.verify_foreground_app(Settings.app_package):
                    request.cls.driver.driver.launch_app(Settings.app_package)
                    request.cls.screen.wait_for_screen_ready(timeout=40000)


def get_required_groups():
    mso_features = MSOFeatures()
    unsupported_list = mso_features.get_unsupported_features(Settings.mso.lower())
    default_list = {'wtw': 'DG_digitalsmiths_wtwn', 'search': 'DG_digitalsmiths_search',
                    'live_log': 'DG_live_log_app_events', 'socu': 'AP_clientsocu'}
    required_groups = []
    if unsupported_list:
        for feature in unsupported_list:
            if feature in default_list.keys():
                del default_list[feature]
    required_groups = list(default_list.values())
    return required_groups


@pytest.fixture(autouse=False, scope="module")
@skip_health_check
def is_service_search_alive():
    if not Settings.is_prod():
        logger.info("Checking 'Service Search' availability...")
        payload = {"type": "unifiedItemSearch", "bodyId": "tsn:" + Settings.tsn, "keyword": "%22%22E*%22%22"}
        status_code = ExecutionContext.service_api.get_service_http_status_code(payload, 'post')
        logger.info(f"Received from Service Search, http status code: {status_code}")
        if status_code != 200:
            msg = "'Service Search' is not available at this moment."
            logger.info(msg)
            pytest.skip(msg)
        logger.info("'Service Search' is available.")


@pytest.fixture(autouse=False, scope="module")
@skip_health_check
def is_service_vod_alive():
    if not Settings.is_prod():
        logger.info("Checking 'Service VOD' availability...")
        device_type = ExecutionContext.service_api.get_device_type()
        payload = {"type": "feedItemFind", "bodyId": "tsn:" + Settings.tsn,
                   "applyAccessibilityExclusions": "false", "deviceType": device_type,
                   "displayType": "quick", "feedName": "/predictions", "displayCount": "1"}
        status_code = ExecutionContext.service_api.get_service_http_status_code(payload, 'get')
        logger.info(f"Received from Service VOD, http status code: {status_code}")
        if status_code != 200:
            msg = "'Service VOD' is not available at this moment."
            logger.info(msg)
            pytest.skip(msg)
        logger.info("'Service VOD' is available.")


def hard_device_reboot(device_ip):
    """
    Function to power reboot of device. HardReboot/Cold start
    Args:
        device_ip: str, ip address of device need to be rebooted

    Returns:
        None
    """
    net_tool = NetworkTools()
    net_tool.outlet_reboot(device_ip)
    logger.step("Device:{} rebooted".format(device_ip))
    start = time.time()
    time.sleep(1)
    net_tool.poll_device('ping_device', 180, device_ip)
    finish = time.time() - start
    ping_state = net_tool.ping_device(device_ip)
    if not ping_state:
        raise InfraHardwareError("After reboot device is not pingable in {:.2f}".format(finish))


def check_and_recover_appletv(request):
    """
    function to check KeyEventPort state on AppleTV only
    if port is down box will be rebooted
    """
    retires = 3
    if Settings.is_apple_tv():
        key_availability = None
        key_event_srv = KeyEventServerIf(Settings.device_ip, 12345)
        for cur_try in range(retires):
            key_availability = key_event_srv.is_keyserver_available()
            if key_availability:
                break
            else:
                time.sleep(0.5 * cur_try + 0.2)

        if not key_availability:
            # reboot hydra to recover keyeventserver
            request.cls.driver.driver.stop_app(Settings.app_package)
            time.sleep(5)
            request.cls.driver.driver.launch_app(Settings.app_package)
            time.sleep(20)

        for cur_try in range(retires):
            key_availability = key_event_srv.is_keyserver_available()
            if key_availability:
                break
            else:
                time.sleep(0.5 * cur_try + 0.2)
        else:
            crash_state = request.cls.driver.driver.get_event_raw_log("KernelPanic", timeout=500)
            if crash_state:
                request.cls.driver.driver.state_holder.set_status("KernelPanic", False)
                raise driverfactory.AppCrashError(f"Unable to recover keyEventSrv. Seems hydra crashed: {crash_state}")


@pytest.fixture(autouse=True, scope="function")
def key_event_server_check(request):
    """
    Fixture to check KeyEventPort state  and print state logs

    For DevHost and AppleTV keyeventserver is mandatory and error will be raised if port closed

    """
    retires = 3
    key_availability = None
    key_event_srv = KeyEventServerIf(Settings.device_ip, 12345)
    for cur_try in range(retires):
        key_availability = key_event_srv.is_keyserver_available()
        if key_availability:
            break
        else:
            time.sleep(0.5 * cur_try + 0.2)
    if not key_availability and Settings.is_dev_host():
        raise ConnectionError("There is no sense to continue testing {}"
                              " without KeyEventyServer on {}".format(Settings.platform,
                                                                      Settings.device_ip))
    elif not key_availability and Settings.is_apple_tv():
        check_and_recover_appletv(request)
    elif not key_availability:
        logger.warning("KeyEventServer port is closed on {}".format(Settings.device_ip))
    else:
        logger.info("KeyEventServer is open")


@pytest.fixture(autouse=False)
def handle_crash(request):
    # Temporarily disabling this teardown method. will working on this as part of CA-21980
    yield
    if request.node.name in Settings.ignore_external_assert_tests:
        assertion = False
    else:
        assertion = request.cls.driver.driver.get_event_raw_log("KernelPanic", timeout=500)
    if assertion:
        logger.info("Alert Window Displayed.. Pressing Enter to dismiss")
        request.cls.screen.base.press_enter()
        raise AppCrashError(assertion).with_traceback(sys.exc_info()[2])


@pytest.fixture(autouse=False, scope="class")
@skip_health_check
def is_service_guide_alive(request):
    logger.info("Checking for Guide feature gridRowSearch service availability")
    if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18):
        # Since Guide service in OpenAPI differs from one in older Hydra versions, let's call OpenAPI one
        response = ExecutionContext.service_api.get_guide_rows(ExecutionContext.service_api.get_channel_search())
    else:
        response = ExecutionContext.service_api.get_grid_row_search()
    if not response:
        pytest.fail(f"Guide feature services not available: {response}")
    logger.info("Guide feature services is available.")


@pytest.fixture(autouse=False, scope="class")
@skip_health_check
def is_service_livetv_alive(request):
    logger.info("Checking for livetv feature channelSearch and stationSearch service availability")
    print("\n\n Checking for livetv feature channelSearch and stationSearch service availability \n\n")
    api = ExecutionContext.service_api
    if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_15):
        # There's no stationSearch since Hydra 1.15
        if not api.get_channel_search():
            pytest.fail("LiveTV feature services not available - stationList or channelList is empty")
    else:
        if not api.get_station_search(Settings.tsn) or not api.get_channel_search():
            pytest.fail("LiveTV feature services not available - stationList or channelList is empty")
    logger.info("LiveTV feature services is available.")


@pytest.fixture(autouse=False, scope="class")
@skip_health_check
def is_service_myshows_alive(request):
    if not Settings.is_ndvr_applicable():
        return
    status = "error"
    try:
        response = ExecutionContext.service_api.get_my_shows_item_search(Settings.tsn)
        if response[-1]["type"]:
            status = response[-1]["type"]
        else:
            status = "OK"
    except Exception as my_error:
        logger.info(my_error)

    if status == "error":
        pytest.fail(f"Myshows feature services not available:{status}")
    logger.info("Myshows feature services is available.")


@pytest.fixture(autouse=False, scope="class")
@skip_health_check
def is_service_wtw_alive(request):
    logger.info("Checking for wtw feature feedItemFind service availability")
    response = ExecutionContext.service_api.get_feed_item_find_results("/carousels/ontvNow", full_resp=True)
    status = response.type
    if status == "error":
        pytest.fail(f"What to watch feature services not available:{response}")
    logger.info("WTW feature services is available.")


@pytest.fixture(scope="function")
def setup_perf_log(request):
    tc_name = request.node.name
    request.cls.perf_logger = PerfLogger(Settings)
    request.cls.perf_logger.run_name = tc_name
    num_usrs = os.getenv('NUM_USERS', 0)
    if num_usrs:
        num_all = os.getenv('BUILD_NUMBER_ALL', 0)
        lstf_scenario = os.getenv('LSTF_SCENARIO', "NA")
        num_current = os.getenv('BUILD_NUMBER_CURRENT', 0)
        request.cls.perf_logger.shared_space.vt_result.update({'num_users_locust': num_usrs,
                                                               'build_num_all': num_all,
                                                               'build_num_current': num_current,
                                                               'lstf_scenario': lstf_scenario,
                                                               })
        logger.info(f"Number of locust users {num_usrs}, "
                    f"Build number all is {num_all}, "
                    f"Build number current is {num_current}")
    yield
    request.cls.home_page.stop_events_capturing()


@pytest.fixture(autouse=True, scope="session")
def dump_version_txt(request, precondition):
    logger.info("Extracting data for version.ini file")
    path = os.path.join(Settings.root_log_path or Settings.log_path, 'version.ini')
    config = configparser.ConfigParser()
    data = '[version]\n'
    args_mapping = vars(Settings)
    for mandatory_arg in ['platform', 'tsn', 'test_environment', 'manage_id', 'branch', 'device_ip', 'mso',
                          'build']:
        data += mandatory_arg + '=' + str(args_mapping.get(mandatory_arg)) + "\n"
    config.read_string(data)
    yield
    if hasattr(Settings, 'driver'):
        data = '[version]\n'
        args_mapping = vars(Settings)
        for mandatory_arg in ['morpheus_rls', "firmware", 'os_version', 'device_model', 'hsn', "ca_device_id",
                              "aut_build", "device_serial_no", "pcid"]:
            data += mandatory_arg + '=' + str(args_mapping.get(mandatory_arg)) + "\n"
        config.read_string(data)
    else:
        config['version']['box_os_version'] = 'Unknown'
    config.write(open(path, 'wt'))


@pytest.fixture(autouse=True, scope="session")
def define_dump_type(request):
    # options = vars(request.config.option)
    if not hasattr(Settings, "dbg_dump_type"):
        setattr(Settings, "dbg_dump_type", "full")
    # only manual control until dump will stable
    # if "sanity" in options['markexpr']:
    #     Settings.dbg_dump_type = "full_no_png"
    logger.info("For test run '{}' dump will be used".format(Settings.dbg_dump_type))


def get_actual_tsn():
    """
    Getting actual TSN for Managed and Unmanaged boxes
    """
    logger.info("Getting actual TSN")
    partner_id = ExecutionContext.service_api.getTivoPartnerId(mso=Settings.mso,
                                                               test_environment=Settings.test_environment)
    kwargs = {"partner_id": partner_id}
    if Settings.is_unmanaged():
        kwargs["ca_device_id"] = Settings.ca_device_id
        if Settings.pcid:
            kwargs["pcid"] = Settings.pcid
        else:
            device_details = ExecutionContext.pps_api_helper.get_device_details(Settings.ca_device_id)
            logger.debug(f"Device details: {device_details}")
            pcid = device_details[0]["partnerCustomerId"]
            kwargs["pcid"] = pcid
    else:
        kwargs["hsn"] = Settings.hsn
    return ExecutionContext.service_api.deviceInfoSearch(**kwargs)['deviceInfo']['tivoSerialNumber']


def get_actual_device_id(mode="ca_device_id"):
    """
    Getting actual device id (CA Device ID or HSN) for Managed and Unmanaged boxes

    Args:
        mode (str): one of (ca_device_id, hsn)
    """
    logger.info(f"Getting actual {mode}")
    info = ExecutionContext.iptv_prov_api.fe_alacarte_get_package_native_drm()
    return info["caDeviceId"] if mode == "ca_device_id" else info["hardwareSerialNumber"]


def find_and_dump_tsn_common():
    logger.warning("\nGeneric Info: By default provided TSN is ignored! "
                   "UTAF gets TSN dynamically based on provided params:\n"
                   "\t'hsn' for managed devices\n\t'ca_device_id' for unmanaged devices\n")
    ERR_MSG_TMPT = "To get TSN for {} devices {} must be configured!"
    if Settings.is_managed() and not Settings.hsn:
        msg = ERR_MSG_TMPT.format("Managed", "HSN")
        logger.error(msg)
        raise ConfigurationError(msg)
    elif Settings.is_unmanaged() and not Settings.is_internal_mso():
        logger.warning("Only iMSO's support dynamic TSN. Going to use TSN from pytest.ini: {}".format(Settings.tsn))
    elif Settings.is_unmanaged() and not Settings.ca_device_id:
        msg = ERR_MSG_TMPT.format("UnManaged", "CaDeviceId")
        logger.error(msg)
        raise ConfigurationError(msg)
    else:
        logger.info("Getting TSN for the current {} device..".format(Settings.manage_id))
        try:
            Settings.tsn = get_actual_tsn()
            org_id = f"caDeviceId: {Settings.ca_device_id}" if Settings.is_unmanaged() else f"HSN: {Settings.hsn}"
            logger.warning("TSN: {} is associated with {}".format(Settings.tsn, org_id))
        except (KeyError, AssertionError, ReadTimeout):
            logger.warning(f"Unable to resolve tsn dynamically for the device,taking from *.ini. TSN:{Settings.tsn}")
    if not Settings.tsn:
        raise ConfigurationError("Unable to get TSN. Test execution without TSN is impossible")
    return Settings.tsn


def get_good_channels():
    logger.info("Calling good channels")
    good_channels = ExecutionContext.service_api.fetch_good_channels_from_db(source="ipStream")
    if Settings.mso.lower() == 'metronet' and Settings.test_environment.lower() == 'staging':
        good_channels = ['3', '24', '34', '35', '36']
    logger.info("good channel list: {}".format(good_channels))
    return good_channels


def get_socu_channels():
    socu_channels = ExecutionContext.service_api.fetch_good_socu_channels()
    logger.info("SOCU channel list: {}".format(socu_channels))
    return socu_channels


def get_ndvr_channels():
    ndvr_channels = ExecutionContext.service_api.fetch_good_ndvr_channels()
    logger.info("NDVR channel list: {}".format(ndvr_channels))
    return ndvr_channels


def get_tivoplus_channels():
    tplus_channels = ExecutionContext.service_api.fetch_good_channels_from_db(source="tivoplus")
    logger.info("tivoplus channel list: {}".format(tplus_channels))
    return tplus_channels


@pytest.fixture(autouse=False, scope="function")
def get_and_restore_tcdui_test_conf(request):
    if Settings.is_android_tv():
        logger.info("Start: backup tcdui_test.conf")
        tmp_tcdui_locatoin = os.path.join(Settings.log_path,
                                          request.node.name, "original_file")
        if os.path.exists(tmp_tcdui_locatoin) is False:
            os.makedirs(tmp_tcdui_locatoin)
        request.cls.screen.base.pull_file(request.cls.driver.driver.remote_tcdui_test_conf, tmp_tcdui_locatoin)

        def tear_down():
            logger.info("Start: restore tcdui_test.conf")
            request.cls.screen.base.push_file(f"{tmp_tcdui_locatoin}/tcdui_test.conf",
                                              request.cls.driver.driver.remote_tcdui_test_conf)
            shutil.rmtree(os.path.dirname(tmp_tcdui_locatoin))
            request.cls.home_page.clear_cache_launch_hydra_app()

        request.addfinalizer(tear_down)
    else:
        pytest.skip("AppleTV doesn't support testconf.testconf operations on AppleTV are limited to initial setup only")


def add_channel_packages():
    """
    Adding channel packages to avoid test skipping due to absent needed channels.
    Will be run only if:
        1. MSO and Environment is presented in packages_to_add
        2. At least one package from packages_to_add is not present on an account
    """
    # Updating entitlementWindowEnd date for listed packages
    package_4k = "444"
    packs_to_update_window_end = ["555"]
    tivoplus_packages = ["emo-st-cc11-tivoplus", "emo-usqe1-cc11-tivoplus"]
    packages_to_add = {
        "cableco11 staging": ["100", "emo-st-cc11-basic", "emo-st-cc11-gold", "emo-st-cc11-adult", "emo-st-cc11-ppv",
                              "emo-st-cc11-sports", "emo-st-cc11-unencrypted", "emo-st-cc11-tivoplus",
                              "emo-st-cc11-ndvrpershow"],
        "cableco11 usqe1": ["100", "emo-usqe1-cc11-basic", "emo-usqe1-cc11-adult", "emo-usqe1-cc11-ppv", "555",
                            "emo-usqe1-cc11-sports", "emo-usqe1-cc11-gold", "emo-usqe1-cc11-unencrypted",
                            "emo-usqe1-cc11-tivoplus", "emo-usqe1-cc11-ndvrpershow"],
        "cableco5 staging": ["100", "555"],
        "cableco3 staging": ["100", "emo-st-cc3-basic", "emo-st-cc3-adult", "emo-st-cc3-ppv", "emo-st-cc3-sports",
                             "emo-st-cc3-unencrypted"],
        "cableco3 usqe1": ["100", "emo-usqe1-cc3-basic", "emo-usqe1-cc3-adult", "emo-usqe1-cc3-ppv",
                           "emo-usqe1-cc3-sports",
                           "emo-usqe1-cc3-unencrypted"],
        "cableco staging": ["100", "emo-st-cc-basic", "emo-st-cc-adult", "emo-st-cc-ppv", "emo-st-cc-sports",
                            "emo-st-cc-unencrypted"],
        "cableco usqe1": ["100", "emo-usqe1-cc-basic", "emo-usqe1-cc-adult", "emo-usqe1-cc-ppv", "emo-usqe1-cc-sports",
                          "emo-usqe1-cc-unencrypted"]}
    absent_packages = []
    mso_env = Settings.mso.lower() + " " + Settings.test_environment.lower()
    if mso_env in packages_to_add.keys():
        logger.warning("Checking if channel packages need to be added to the account")
        try:
            all_packages = ExecutionContext.iptv_prov_api.account_entitlement_search(
                ExecutionContext.service_api.getPartnerCustomerId(Settings.tsn),
                ExecutionContext.service_api.get_mso_partner_id(Settings.tsn))
            pacakge_name_list = ExecutionContext.iptv_prov_api.get_account_entitlement_package_names(
                ExecutionContext.service_api.getPartnerCustomerId(Settings.tsn),
                ExecutionContext.service_api.get_mso_partner_id(Settings.tsn), all_packages)
            logger.warning("current entitled package list: {}".format(pacakge_name_list))
            is_tivoplus_group_present = \
                ExecutionContext.iptv_prov_api.check_group_with_service_group_fetch(
                    ExecutionContext.service_api.get_mso_partner_id(Settings.tsn), "DG_lp_tivoplus_100", raise_error=False)
            add_packages_list = packages_to_add.get(mso_env)
            # Add 4k package if use_channels_from_packages is used in pytest.ini parameters
            if Settings.use_channels_from_packages and mso_env in ["cableco11 staging", "cableco5 staging"] and \
               package_4k in str(Settings.use_channels_from_packages):
                logger.warning("Adding 4k package")
                add_packages_list.append(package_4k)
                packs_to_update_window_end.append(package_4k)
            for pack in add_packages_list:
                if pacakge_name_list is not None and pack not in pacakge_name_list:
                    absent_packages.append(({"package": pack}))
                if pack in tivoplus_packages and not is_tivoplus_group_present:
                    # TiVo+ channels require DG_lp_tivoplus_100 service group
                    ExecutionContext.iptv_prov_api.service_group_store(
                        "lp_tivoplus_100", "DG", ExecutionContext.service_api.get_mso_partner_id(Settings.tsn))
            for pack in all_packages:
                # Updating package end date for packages from packs_to_update_window_end only if
                # end_date <= than date now
                if "entitlementWindowEnd" in pack and \
                   datetime.strptime(pack["entitlementWindowEnd"],
                                     ExecutionContext.service_api.MIND_DATE_TIME_FORMAT) <= datetime.now():
                    payload_publish = []
                    payload_remove = []
                    for name in packs_to_update_window_end:
                        if pacakge_name_list is not None and name in pacakge_name_list:
                            payload_publish.append(({"package": name, "start_date": "2015-12-02 09:30:00",
                                                     "end_date": "2099-12-02 09:30:00"}))
                            payload_remove.append(name)
                    # Need to remove expired packages first
                    if payload_remove:
                        ExecutionContext.iptv_prov_api.account_entitlement_remove(
                            payload_remove,
                            ExecutionContext.service_api.getPartnerCustomerId(Settings.tsn),
                            ExecutionContext.service_api.get_mso_partner_id(Settings.tsn))
                    # Adding removed packages with end date in future
                    if payload_publish:
                        ExecutionContext.iptv_prov_api.account_entitlement_publish(
                            payload_publish,
                            ExecutionContext.service_api.getPartnerCustomerId(Settings.tsn),
                            ExecutionContext.service_api.get_mso_partner_id(Settings.tsn))
            check_and_remove_entitlement(package_4k, pacakge_name_list)
            if absent_packages:
                logger.warning("Adding channel packages to the account: {}".format(absent_packages))
                ExecutionContext.iptv_prov_api.account_entitlement_publish(
                    absent_packages,
                    ExecutionContext.service_api.getPartnerCustomerId(Settings.tsn),
                    ExecutionContext.service_api.get_mso_partner_id(Settings.tsn))
            else:
                logger.warning("No need to add channel packages to the account, expected channel packs are present")
        except Exception as ex:
            logger.error(f"Channel packages check failed with: {ex}")


def check_and_remove_entitlement(package_4k, pacakge_name_list):
    exclude_packages_from_use = Settings.exclude_packages_from_use.split(",") \
        if "exclude_packages_from_use" in vars(Settings) and Settings.exclude_packages_from_use else []
    logger.info("Current list of packages to be exculded from execution: {}".format(exclude_packages_from_use))
    if Settings.use_channels_from_packages and package_4k not in str(Settings.use_channels_from_packages) and \
       package_4k in pacakge_name_list:
        logger.info("Removing {} as it is not in {}".format(package_4k, Settings.use_channels_from_packages))
        exclude_packages_from_use.append(package_4k)
    elif not Settings.use_channels_from_packages and package_4k in pacakge_name_list:
        logger.info("Removing {} as use_channels_from_packages is not set".format(Settings.use_channels_from_packages))
        exclude_packages_from_use.append(package_4k)
    exclude_packages_from_use = list(filter(lambda x: x in pacakge_name_list, set(exclude_packages_from_use)))
    if not exclude_packages_from_use:
        logger.info("None of the packages are set for exclusion/removal")
        return
    logger.info("packages list set to remove entitlement: {}".format(exclude_packages_from_use))
    ExecutionContext.iptv_prov_api.account_entitlement_remove(
        exclude_packages_from_use,
        ExecutionContext.service_api.getPartnerCustomerId(Settings.tsn),
        ExecutionContext.service_api.get_mso_partner_id(Settings.tsn))


def get_loki_labels():
    loki_labels = ExecutionContext.loki_labels.fetch_labels_from_loki_table()
    return loki_labels


def check_nDVR_active():
    """
    Used for getting the nDVR TSN associated to current device TSN.
    If no nDVR TSN is received, then current box is not a nDVR.
    """
    logger.warning("Checking current device is an active nDVR..")
    npvr_body_map = ExecutionContext.service_api.npvr_body_map_get()
    if npvr_body_map:
        if 'npvrBodyId' in npvr_body_map.keys():
            if npvr_body_map['npvrBodyId']:
                logger.warning(f"Current Box TSN={Settings.tsn}, MSO={Settings.mso} is a nDVR.\n")
                return
        logger.warning(f"Current Box TSN={Settings.tsn}, MSO={Settings.mso} is NOT a nDVR or nDVR is not active!"
                       f"\n{npvr_body_map}\n")
        raise InfraHardwareError(
            f"Current Box TSN:{Settings.tsn} MSO:{Settings.mso} is NOT a nDVR or nDVR is not active!")


def check_device_provisioning():
    """
    Check provisioning for the current device.
    """
    logger.warning("Checking provisioning for current device..")
    # get partnerId
    partner_id = ExecutionContext.service_api.getTivoPartnerId(
        mso=Settings.mso,
        test_environment=Settings.test_environment)

    # get deviceInfo
    device_info_response = ExecutionContext.service_api.deviceInfoSearch(
        tsn=Settings.tsn,
        partner_id=partner_id)
    if 'deviceInfo' not in device_info_response:
        logger.warning(f"\nNot able to extract TSN from deviceInfoSearch response:\n{device_info_response}\n")
        raise ValueError(f"Not able to extract TSN from deviceInfoSearch response:\n{device_info_response}")

    try:
        if device_info_response['deviceInfo']['contract']['serviceState'] == 'GOOD' and \
                device_info_response['deviceInfo']['contract']['status'] == 'Active':
            logger.warning(f"Current Box TSN={Settings.tsn}, MSO={Settings.mso} is provisioned.\n")
    except Exception as e:
        logger.warning(f"Current Box TSN={Settings.tsn}, MSO={Settings.mso} is NOT provisioned!\n"
                       f"{e}\n")
        raise InfraHardwareError(f"Current Box TSN:{Settings.tsn} MSO:{Settings.mso} is NOT provisioned!")


def get_mso_service_id():
    """
    Getting mso service locality using deviceinfosearch.
    """
    logger.info("Getting service locality of device")
    # get partnerId
    partner_id = ExecutionContext.service_api.getTivoPartnerId(
        mso=Settings.mso,
        test_environment=Settings.test_environment)

    # get deviceInfo
    device_info_response = ExecutionContext.service_api.deviceInfoSearch(
        tsn=Settings.tsn,
        partner_id=partner_id)
    locality = "TIVOCO1"
    try:
        if 'deviceInfo' not in device_info_response:
            logger.warning(
                f"\nNot able to extract msoServiceId from deviceInfoSearch response:\n{device_info_response}\n")

        if 'msoServiceId' in device_info_response['deviceInfo']:
            logger.info(
                "Service locality from deviceInfoSearch:{}".format(device_info_response['deviceInfo']['msoServiceId']))
            locality = device_info_response['deviceInfo']['msoServiceId']
    except Exception:
        device_info_response = ExecutionContext.service_api.fe_device_mso_service_id_get()
        if 'msoServiceId' in device_info_response:
            logger.info("Service locality from feDeviceMsoServiceId:{}".format(
                device_info_response['msoServiceId']))
            locality = device_info_response['msoServiceId']
        else:
            logger.warning(
                "\nNot able to extract msoServiceId from deviceInfoSearch response:\n{device_info_response}\n")
    return locality


def get_sdcard_stats(request):
    """
    get sdcard statistics
    """
    if Settings.is_android_tv() and not Settings.is_dev_host():
        logger.info("Getting sdcard memory statistics")
        sdcard_stats = None
        ram = None
        zram = None
        lostram = None
        sdcard_stats = request.cls.driver.driver.get_device_memory_info(partition="/sdcard")
        ram, zram, lostram = request.cls.driver.driver.meminfo_stats()
        proc_stats = request.cls.driver.driver.proc_stats(package=Settings.app_package, hours=1)
        if sdcard_stats is not None:
            partition = list(sdcard_stats.keys())
            if len(partition) > 0:
                sdcard_stats['data'] = sdcard_stats.pop(partition[0])
                sdcard_stats['data'].update({'partition': partition[0]})
            else:
                logger.info("partition: {}, sdcard_raw_data: {}".format(partition, sdcard_stats))
        Settings.sdcard_stats = sdcard_stats
        logger.info("sdcard statistics:{}".format(Settings.sdcard_stats))
        Settings.proc_stats_mem_usage = {'Memory_usage': proc_stats.get('Memory usage:')}
        for key in proc_stats.keys():
            if 'Start time:' in key:
                Settings.proc_stats_uptime_elapsed_time = {"Total_uptime": proc_stats.get(key)}
                break
        Settings.procstats_sys_mem_usage = {'System_memory_usage': proc_stats.get('System memory usage:')}
        logger.info("procstats statistics:{}".format(proc_stats))
        Settings.meminfo_ram = ram
        Settings.meminfo_zram = zram
        Settings.meminfo_lostram = lostram
        logger.info("meminfo stats:{}, {}, {}".format(Settings.meminfo_ram,
                                                      Settings.meminfo_zram,
                                                      Settings.meminfo_lostram
                                                      )
                    )


def read_xray_ids():
    '''
    Api to get xray ids from test_case_to_xray.yml file
    '''
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + '/test_case_to_xray.yml') as yfile:
        xray_ids = yaml.load(yfile, Loader=yaml.FullLoader)

    return xray_ids


def read_error_classifications():
    '''
    API to get error classifications from Error_Classification.yml file
    '''
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + '/Error_Classification.yml') as yfile:
        error_type = yaml.load(yfile, Loader=yaml.FullLoader)
    return error_type


def get_issue_type(call_stack):
    '''
    API to get issue type based on call stack
    '''
    error_type = read_error_classifications()
    issue_type = "Unclassified"
    for error, error_msgs in error_type.items():
        if any(error_msg in call_stack for error_msg in error_msgs):
            issue_type = error

    return issue_type


def check_and_enable_notifications(request):
    if Settings.is_android_tv() and not Settings.is_dev_host():
        Settings.app_package_listener, Settings.tv_listener = request.cls.driver.driver.get_listeners_details()
        if not Settings.app_package_listener or not Settings.tv_listener:
            request.cls.driver.driver.enable_disable_notification_listener(allow=True)
            Settings.app_package_listener, Settings.tv_listener = request.cls.driver.driver.get_listeners_details()
        request.config.option.app_package_listener = Settings.app_package_listener
        request.config.option.tv_listener = Settings.tv_listener


def get_device_resolution(request):
    try:
        if Settings.is_cc11() or Settings.is_cc5():
            package_ids = None
            package_ids = ExecutionContext.iptv_prov_api.get_account_entitlement_package_names(
                ExecutionContext.service_api.getPartnerCustomerId(Settings.tsn),
                ExecutionContext.service_api.get_mso_partner_id(Settings.tsn))
            logger.info("entitled packages list: {}".format(package_ids))
            if package_ids is not None:
                for package in package_ids:
                    if package in Settings.package_list_4k.keys():
                        Settings.device_resolution = "4k"
                        break
    except Exception as Err:
        logger.warning("Failed to return package list from account entitlement search: {}".format(Err))
        Settings.device_resolution = "unknown"
    request.config.option.device_resolution = Settings.device_resolution


def upload_channel_playback_details(request):
    info = None
    url = None
    if Settings.is_internal_mso():
        try:
            logger.info("Attempting to get cached playback info for test case")
            info = ExecutionContext.service_api.cached_channel_info(None, mode="testcase", use_cached_response=True)
            if isinstance(info, dict) and info['title']:
                if not info['url']:
                    url = request.cls.home_page.get_playback_url_from_dut_log()
                    info.update({'url': url})
            ExecutionContext.service_api.cached_channel_info(None, mode="testcase", use_cached_response=False)
        except Exception as Err:
            logger.info("Exception occured while getting cached channel info for testcase: {}".format(Err))
            ExecutionContext.service_api.cached_channel_info(None, mode="testcase", use_cached_response=False)
            info = None
    else:
        logger.info("playback channel data will not be uploaded to splunk as mso is External mso")
    request.config.option.channel_playback_info = info if info else Settings.channel_playback_info
    logger.info("Playback information: {}".format(request.config.option.channel_playback_info))
    logger.info("cached {}".format(ExecutionContext.service_api.cached_channel_info(None, mode="testcase",
                                                                                    use_cached_response=True)))


def get_deeplink_ott_list():
    deep_link_apps = ['GooglePlay']
    webkits = []
    response = ExecutionContext.service_api.get_service_group_search()
    if len(response) > 0:
        webkits = [group['groupName'] for group in response if 'webkit' in group['groupName']]
        logger.info("webkits identified: {}".format(webkits))
    if len(webkits) > 0:
        ott_dict = get_ott_support_dict()
        for key, value in ott_dict.items():
            if value['webkit'] in webkits and value['deeplink']:
                app = key.replace(' ', '_').replace("(", "").replace(")", "")
                deep_link_apps.append(app)
    Settings.ott_list = deep_link_apps
    logger.info("ott list: {}".format(Settings.ott_list))
    Settings.display_priority_dict = partner_display_priority_list()


def get_ott_support_dict():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/ott_app_support.yml') as yfile:
        ott_dict = yaml.load(yfile, Loader=yaml.FullLoader)
    return ott_dict


@pytest.fixture
def get_overrides(request):
    return define_overrides_per_version(
        test_name=request.node.name,
        version=Settings.hydra_branch() > Settings.hydra_branch(HydraBranches.STREAMER_1_18) and '1.18+' or '<=1.18'
    )


def partner_display_priority_list():
    sorted_priority_dict = None
    try:
        response = ExecutionContext.service_api.partner_info_search()
        if response and 'partnerInfo' in response.keys():
            priority_values = {}
            for partner in response['partnerInfo']:
                if 'image' in partner.keys() and 'msoData' in partner.keys():
                    images = []
                    if isinstance(partner['image'], list):
                        for image in partner['image']:
                            if 'imageUrl' in image.keys():
                                images.append(image['imageUrl'])
                    elif isinstance(partner['image'], dict):
                        if 'imageUrl' in partner['image'].keys():
                            images.append(partner['image'].get('imageUrl'))
                    if len(partner['msoData']) > 0 and 'partnerSortOrder' in partner['msoData'][0]:
                        priority_values.update({partner['msoData'][0]['partnerSortOrder']: images})
        sorted_priority_dict = dict(sorted(priority_values.items(), key=operator.itemgetter(0)))
    except Exception as Err:
        logger.warning("Exception observed while getting display priority_list: {}".format(Err))
    logger.info("Sorted priority ott dict: {}".format(sorted_priority_dict))
    return sorted_priority_dict


def define_overrides_per_version(test_name: str, version: str) -> dict:
    """
    Returns overrides per version of application per test
    Args:
        test_name: name of test, str
        version: app version, str
    Returns:
        dict of override key and override value
    """
    path = os.path.join(Settings.TEST_DATA, 'test_overrides.yml')
    with open(path) as yfile:
        overrides = yaml.load(yfile, Loader=yaml.FullLoader)

    test_overrides = overrides.get(test_name)
    if not test_overrides:
        raise ValueError(f"Overrides not set per test: {test_overrides}")

    version_overrides = test_overrides.get(version)
    if not version_overrides:
        raise ValueError(f"Overrides not set per version: {version}")

    return version_overrides
