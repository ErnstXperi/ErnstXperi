"""
Created on Sep 21, 2015
@author: ramnik_kaur
"""

import os

from set_top_box.conf_constants import BranchRegistry, DriverTypeList, FeAlacarteFeatureList, HydraBranchVersion, \
    HydraBranches, MindEnvList, MsoList, PlatformList
from tools.keychain import UTAFKeychain


class Settings(object):
    # Settings
    ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    XLS_ROOT = ROOT + "/xsls/"
    CERT_AND_KEY_ROOT_IPTV_PROV = ROOT + "/mind_api/iptv_provisioning_mind/certs/"
    PROV_TOOL_PATH = ROOT + "/mind_api/iptv_provisioning_mind/"
    PROV_DEVICE_INFO_FILE_PATH = ROOT + "/test_data/provisioning/"
    TEST_APP_FOR_APPSGAMES = ROOT + "/test_data/test_app.apk"
    TEST_DATA = os.path.join(ROOT, "test_data")
    QOE_YML_FILE = ROOT + "/set_top_box/qoe_events_and_attributes.yml"
    wondershaper_script = os.path.join(ROOT, "test_data", "wondershaper.sh")
    log_path = ""
    root_log_path = ""
    artifacts_mode = "global"
    utaf_analytics = 1
    language = "en_us"
    hub = ""
    morpheus_rls = ""
    device_id = ""
    appium_ip = ""
    testcaseid = ""
    os_version = "6.0.1"  # "7.1.2"
    androidbuild = ""
    songbird = ""
    skip_health_check = False
    skip_pc_check = False
    localization = False
    perf_location = "/tmp/perf.txt"
    timeout = 3600  # One hour
    timeout_mid = 7200  # Two Hour
    longrun_timeout = 1080000  # 30 hours
    mtbr_location = "/tmp/mtbr.txt"
    select_tivo_box = "Living Room (8D960019038544C)"
    host_username = "qwarts"
    username = "unmanaged1"
    password = "th1sbetterwork"
    tivo_pt = ""
    google_account = UTAFKeychain("streamers_google_account")
    google_password = UTAFKeychain("streamers_google_password")
    adb_path = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
    build_source = ""
    build_version = 'release'
    mso = ""
    tsn = ""
    push_test_conf = "true"
    ca_device_id = ""
    pcid = ""
    specified_pcid = ""
    firmware = ""
    device_serial_no = ""
    hsn = ""
    device_model = ""
    platform = ""
    build = ""
    aut_build = ""  # for version.ini
    DG_HDUI_WIP = ""
    CCB_SWITCH_OVERRIDE = ""
    SLS_ENDPOINTS_OVERRIDE = ""
    SLS_INSTANCE_OVERRIDE = ""
    QE_TESTING_DEVICE_TYPE = ""
    TIMEOUT_TO_DIMMING_SCREEN = 21600000  # default value is 900000 milliseconds (15 minutes)
    TIMEOUT_SERVICE_LOGIN = 30000
    MEDIA_HEALTH_EVENT_INTERVAL_OVERRIDE = 300000
    BLOCK_DEFAULT_LOCALE_COUNTRY_ASSERT_REMOVE_IN_IPTV_26358 = ""
    WELCOME_SPLASH_TIMEOUT_MS = ""
    WIDGET_TIMEOUT_MS = None  # override timeout value of the widgets displayed in Watch Video screens
    branch = HydraBranches.MAINLINE
    stage = ""
    app_env_config = ""
    manage_id = ""
    tscdui_conf = ""
    app_package = "com.tivo.hydra.app"
    # TODO
    # It's better to move 'screen_saver_package' variable to core_api.hardwaredriver.android.androiddriver
    # since it's Android specific package + it's usually the same for different android platforms
    screen_saver_package = "com.google.android.backdrop"
    driver_type = ""
    device_ip = ""
    port = 5555
    driver_restart_time_max_second = 120
    xlst_parser = "xsltproc"
    ui_xml_xslt = "hydra_menus.xsl"
    netflix = "com.netflix.ninja"
    test_environment = "staging"
    trickplay_bar_timeout = 12
    trickplay_bar_timeout_in_pause_mode = 60
    amino_manufacturer = 'Evolution Digital'
    puck_manufacturer = 'SEI Robotics'
    arris_remote = 'NexusIR'
    amino_remote = 'Amino_Ir_Generic'
    xiaomi_remote = 'Xiaomi Remote'
    puck_remote = 'TiVo Remote'
    firetv_remote = 'Amazon Fire TV Remote'
    rasp_ip = ""
    rasp_user = ""
    rasp_ws_remote_dst = "/home/pi/wondershaper"  # path on remote pi
    rasp_pwd = ""
    transport = None
    rasp_dump = ""
    rasp_nic_to_box = ""  # ethernet port to be limited to
    use_zipalign = "false"
    fail_build_upon_install_failure = "true"
    rpmdir = None
    yukon_server = 'localhost'
    vt_hardware = ""
    vt_video_input = None
    dut_hub = None
    vt_audio_device = "default"
    vt_save_audio = True
    vt_result = {}
    app_repackager = "utaf_ipa"
    remove_screen_dump = False
    good_channels = ""
    socu_channels = ""
    ndvr_channels = ""
    tplus_channels = ""
    loki_labels = ""
    equipment_id = ""
    mode = ""
    rail_id = ""
    check_ndvr_enabled = False
    check_provisioning = False
    mso_locality = ""
    ndvr_disk_max_limit_time = 5000  # 50 hours and 00 min
    ndvr_disk_max_limit_percent = 0  # 0%
    feature_4k = ""
    rooted = False
    dbg_dump_type = "full"
    dbg_verbose_mode = 0
    sdcard_stats = ""
    test_window_start = ""
    test_window_end = ""
    mind_mode = ""
    feed_list_root = "/screens/wtwnNav"  # old implementation - "/feedList/streamerRoot" feedlist root for wtw
    google_id = ""
    procstats_sys_mem_usage = ""
    proc_stats_uptime_elapsed_time = ""
    proc_stats_mem_usage = ""
    build_download_url = "NO_DOWNLOAD"
    meminfo_ram = ""
    meminfo_zram = ""
    meminfo_lostram = ""
    xray_ids = ""
    tv_listener = ""
    app_package_listener = ""
    bh_status = ""
    exo_prop_url = "http://live1.nokia.tivo.com/kqedplus/vxfmt=dp/playlist.m3u8?device_profile=hlsclr"
    exo_prop_path = f"/sdcard/Android/data/{app_package}/files/exo.properties"
    device_resolution = "non_4k"
    package_list_4k = {'444': ["Cableco5-Staging-4K-Frumos01", "Cableco11-Staging-4K-Frumos01"]}
    use_channels_from_packages = ""  # comma separated package names e.g. "444,555"
    exclude_packages_from_use = ""  # comma separated package names e.g. 444,555
    drm_type = ""
    reboot_required = "true"
    error_id = ""
    human_error = ""
    bugreports = False
    media_audio_flinger = False
    # Video Quality Tool score
    vqt_score = ""
    channel_playback_info = "playback not started or used in case or mso might be external"

    telus_unsupported = ['socu', 'vod', 'ndvr']

    SHORTEST_WAIT_TIME = 5

    # List of params which can be updated in tcdui_test.conf, property names exactly same as in tcdui_test.conf
    TCDUI_TEST_CONF_PROPS = ["DG_HDUI_WIP", "TIMEOUT_TO_DIMMING_SCREEN", "TIMEOUT_SERVICE_LOGIN",
                             "MEDIA_HEALTH_EVENT_INTERVAL_OVERRIDE", "WELCOME_SPLASH_TIMEOUT_MS", "CCB_SWITCH_OVERRIDE",
                             "SLS_ENDPOINTS_OVERRIDE", "BLOCK_DEFAULT_LOCALE_COUNTRY_ASSERT_REMOVE_IN_IPTV_26358",
                             "WIDGET_TIMEOUT_MS", "SLS_INSTANCE_OVERRIDE", "QE_TESTING_DEVICE_TYPE"]

    # TiVo EULA
    pactsafe_url = 'https://pactsafe.io/'
    pactsafe_site_id = '23140eac-7498-4f19-be3f-1f9c88ca59a7'
    pactsafe_site_id_qas = '0d61f1fe-d144-4b93-b800-50810ad85458'
    tivo_plus_group_key = 'group-skysjr0mb'
    tivo_eula_group_key = 'agreement-flow'
    tivo_eula_group_key_qas = 'agreement-flow-qas'

    splunk_hec_url = "https://splunk-hec.oip1.tivo.com"
    ott_list = ['GooglePlay']
    display_priority_dict = None
    ignore_external_assert_tests = ["test_frum_61729_Assert_continue_and_verify_the_crash_signature"]
    scrncap_unsupported_models = ['AFTS']  # Screencap and Screenrecord commands does not work on these models
    api_additional_headers = dict()  # do NOT set this param, it's set automatically in appropriate place

    #  BlackList VOD Mix Folders
    @staticmethod
    def blacklist_vod_folder():
        folder = []
        if Settings.mso.lower() == MsoList.CC3:
            folder = ["TestVOD", "Cableco3VodInteg", "Experiments", "Series2"]
            return folder
        elif Settings.mso.lower() == MsoList.CC5:
            folder = ["TiVO-POLAND"]
            return folder
        elif Settings.mso.lower() == MsoList.SECV:
            folder = ["Help and Tutorials"]
            return folder
        else:
            return folder

    # Blacklist particular vod asset
    @staticmethod
    def blacklist_vod_asset():
        asset = []
        if Settings.mso.lower() == MsoList.EASTLINK:
            asset = ["BANG! The Bert Berns Story"]
            return asset
        else:
            return asset

    #  WhilteList VOD Mix Folders
    @staticmethod
    def whitelist_vod_folder():
        folder = []
        if Settings.mso.lower() in [MsoList.CC3, MsoList.CC11, MsoList.CC5]:
            folder = ["QE"]
            return folder
        else:
            return None

    #  Content provider app
    CONTENT_PROVIDER_APP = ROOT + "/test_data/content_provider_app.apk"
    CONTENT_PROVIDER_APP_PACKAGE = "com.tivo.hydra.mpa"

    #  Pluto TV app
    PLUTO_TV_APP = ROOT + "/test_data/pluto_tv_app.apk"
    PLUTO_TV_PACKAGE_NAME = "tv.pluto.android"

    @staticmethod
    def is_vod_supported():
        """
        If VOD is not supported, ON DEMAND menu shortcut is not shown on the Home screen
        """
        return Settings.mso.lower() not in [MsoList.METRONET, MsoList.TELUS]

    @staticmethod
    def is_aut_update_enabled():
        return Settings.build and Settings.build_source

    @staticmethod
    def is_vision_tester_enabled():
        return Settings.vt_hardware and Settings.vt_video_input

    @staticmethod
    def vision_tester_hardware():
        return Settings.vt_hardware

    @staticmethod
    def is_purchase_controls_enabled():
        return True if not Settings.is_cc3() and not Settings.is_tds() and not Settings.is_cc2() else False

    @staticmethod
    def is_dev_host():
        return True if Settings.driver_type.lower() == DriverTypeList.DEV_HOST else False

    @staticmethod
    def is_feature_4k():
        print(f"is_feature_4k: {Settings.feature_4k}")
        if Settings.feature_4k.lower() == 'false' or bool(Settings.feature_4k.lower()) is False:
            return False
        else:
            return True

    # Test Environment Checks Begin #
    @staticmethod
    def is_internal_environment():
        """
        Environment that used internally like USQE1, CDVRQE1, Staging
        """
        return True if Settings.test_environment.lower() in MindEnvList.INTERNAL_ENV_LIST else False

    @staticmethod
    def is_staging():
        current_env = Settings.test_environment.lower()
        return current_env in (MindEnvList.PREPROD, MindEnvList.STAGING, MindEnvList.LATAM_STAGING)

    @staticmethod
    def is_usqe1():
        return True if Settings.test_environment.lower() == MindEnvList.USQE_1 else False

    @staticmethod
    def is_cdvrqe1():
        return True if Settings.test_environment.lower() == MindEnvList.CDVRQE_1 else False

    @staticmethod
    def is_prod():
        return True if Settings.test_environment.lower() == MindEnvList.PROD else False
    # Test Environment Checks End #

    # Platform Checks Begin #
    @staticmethod
    def is_managed():
        return True if Settings.platform.lower() in PlatformList.MANAGED_STREAMERS_LIST else False

    @staticmethod
    def is_unmanaged():
        return True if Settings.platform.lower() in PlatformList.UNMANAGED_STREAMERS_LIST else False

    @staticmethod
    def is_android_tv():
        return True if Settings.platform.lower() in PlatformList.ANDROID_STREAMERS_LIST else False

    @staticmethod
    def is_technicolor():
        return True if Settings.platform.lower() == PlatformList.TECHNICOLOR else False

    @staticmethod
    def is_amino():
        return True if Settings.platform.lower() == PlatformList.AMINO else False

    @staticmethod
    def is_puck():
        return Settings.platform.lower() == PlatformList.PUCK

    @staticmethod
    def is_jade():
        return Settings.platform.lower() == PlatformList.JADE

    @staticmethod
    def is_jade_hotwire():
        return Settings.platform.lower() == PlatformList.JADE_HOTWIRE

    @staticmethod
    def is_jade_21():
        return Settings.platform.lower() == PlatformList.JADE_21

    @staticmethod
    def is_jade_millicom():
        return Settings.platform.lower() == PlatformList.JADE_MILLICOM

    @staticmethod
    def is_ruby():
        return Settings.platform.lower() == PlatformList.RUBY

    @staticmethod
    def is_sonytv():
        return Settings.platform.lower() == PlatformList.SONYTV

    @staticmethod
    def is_googletv():
        return Settings.platform.lower() == PlatformList.GOOGLETV

    @staticmethod
    def is_hisensetv():
        return Settings.platform.lower() == PlatformList.HISENSETV

    @staticmethod
    def is_tcltv():
        return Settings.platform.lower() == PlatformList.TCLTV

    @staticmethod
    def is_omnitv():
        return Settings.platform.lower() == PlatformList.OMNITV

    @staticmethod
    def is_force1():
        return Settings.platform.lower() == PlatformList.FORCE1

    @staticmethod
    def is_fuse4k():
        return Settings.platform.lower() == PlatformList.FUSE4K

    @staticmethod
    def is_falcon3():
        return Settings.platform.lower() == PlatformList.FALCON3

    @staticmethod
    def is_arris():
        return True if Settings.platform.lower() == PlatformList.ARRIS else False

    @staticmethod
    def is_fire_tv():
        return True if Settings.platform.lower() == PlatformList.FIRE_TV else False

    @staticmethod
    def is_mibox():
        return True if Settings.platform.lower() == PlatformList.MIBOX else False

    @staticmethod
    def is_nvidia():
        return True if Settings.platform.lower() == PlatformList.NVIDIA else False

    @staticmethod
    def is_toshiba():
        return True if Settings.platform.lower() == PlatformList.TOSHIBA else False

    @staticmethod
    def is_apple_tv():
        return True if Settings.platform.lower() == PlatformList.APPLE_TV else False

    @staticmethod
    def is_stb():
        return True if Settings.platform.lower() in PlatformList.STB_LIST else False

    @staticmethod
    def is_smartbox():
        return True if Settings.platform.lower() in PlatformList.STB_SMARTBOX_LIST else False

    @staticmethod
    def is_stb_series7():
        return True if Settings.platform.lower() in PlatformList.STB_SERIES_7_LIST else False

    @staticmethod
    def is_stb_series6():
        return True if Settings.platform.lower() in PlatformList.STB_SERIES_6_LIST else False

    @staticmethod
    def is_stb_series5():
        return True if Settings.platform.lower() in PlatformList.STB_SERIES_5_LIST else False

    @staticmethod
    def is_keystone():
        return True if Settings.platform.lower() == PlatformList.KEYSTONE else False

    @staticmethod
    def is_topaz():
        return True if Settings.platform.lower() == PlatformList.TOPAZ else False

    @staticmethod
    def is_taos():
        return True if Settings.platform.lower() == PlatformList.TAOS else False

    @staticmethod
    def is_minos():
        return True if Settings.platform.lower() == PlatformList.MINOS else False

    @staticmethod
    def is_argon():
        return True if Settings.platform.lower() == PlatformList.ARGON else False

    @staticmethod
    def is_devhost():
        return True if Settings.driver_type.lower() == DriverTypeList.DEV_HOST else False
    # Platform Checks End #

    # Voice check Begin #
    @staticmethod
    def is_voice_C2C():
        # Voice C2C is available for specific MSOs in default apks or for apks with "voice" in the name.
        # Other voice implementation available for streamers: OnDevice, Tivo voice

        # list of MSOs that have C2C available in default apks -> To be updated after C2C onboarding for new MSOs
        voice_c2c_mso_list = [MsoList.TDS, MsoList.MIDCO, MsoList.RCN]
        return Settings.mso.lower() in voice_c2c_mso_list or "voice" in Settings.stage
    # Voice check end #

    # MSO Checks Begin #
    @staticmethod
    def is_cc2():
        return True if Settings.mso.lower() == MsoList.CC2 else False

    @staticmethod
    def is_cc3():
        return True if Settings.mso.lower() == MsoList.CC3 else False

    @staticmethod
    def is_cc11():
        return True if Settings.mso.lower() == MsoList.CC11 else False

    @staticmethod
    def is_cc5():
        return True if Settings.mso.lower() == MsoList.CC5 else False

    @staticmethod
    def is_tds():
        return True if Settings.mso.lower() == MsoList.TDS else False

    @staticmethod
    def is_rcn():
        return True if Settings.mso.lower() == MsoList.RCN else False

    @staticmethod
    def is_telus():
        return True if Settings.mso.lower() == MsoList.TELUS else False

    @staticmethod
    def is_millicom():
        return True if Settings.mso.lower() == MsoList.MILLICOM else False

    @staticmethod
    def is_llapr():
        return True if Settings.mso.lower() == MsoList.LLA else False

    @staticmethod
    def is_llacr():
        return True if Settings.mso.lower() == MsoList.LLACR else False

    @staticmethod
    def is_llacl():
        return True if Settings.mso.lower() == MsoList.LLACL else False

    @staticmethod
    def is_mediacom():
        return True if Settings.mso.lower() == MsoList.MEDIACOM else False

    @staticmethod
    def is_abb():
        return True if Settings.mso.lower() == MsoList.ABB else False

    @staticmethod
    def is_bluestream():
        return True if Settings.mso.lower() == MsoList.BLUESTREAM else False

    @staticmethod
    def is_grande():
        return True if Settings.mso.lower() == MsoList.GRANDE else False

    @staticmethod
    def is_entouch():
        return True if Settings.mso.lower() == MsoList.ENTOUCH else False

    @staticmethod
    def is_hotwire():
        return True if Settings.mso.lower() == MsoList.HOTWIRE else False

    @staticmethod
    def is_astound():
        return True if Settings.mso.lower() == MsoList.ASTOUND else False

    @staticmethod
    def is_eastlink():
        return True if Settings.mso.lower() == MsoList.EASTLINK else False

    @staticmethod
    def is_blueridge():
        return True if Settings.mso.lower() == MsoList.BLUERIDGE else False

    @staticmethod
    def is_secv():
        return True if Settings.mso.lower() == MsoList.SECV else False

    @staticmethod
    def is_armstrong():
        return True if Settings.mso.lower() == MsoList.ARMSTRONG else False

    @staticmethod
    def is_sectv():
        return True if Settings.mso.lower() == MsoList.SECTV else False

    @staticmethod
    def is_metronet():
        return True if Settings.mso.lower() == MsoList.METRONET else False

    @staticmethod
    def is_breezeline():
        return True if Settings.mso.lower() == MsoList.BREEZELINE else False

    @staticmethod
    def is_altafiber():
        return True if Settings.mso.lower() == MsoList.CBT else False

    @staticmethod
    def is_internal_mso():
        return True if Settings.mso.lower() in MsoList.INTERNAL_MSO_LIST else False

    @staticmethod
    def is_external_mso():
        return True if Settings.mso.lower() in MsoList.EXTERNAL_MSO_LIST else False

    @staticmethod
    def is_ndvr_applicable():
        ndvr_not_applicable_mso = [MsoList.MEDIACOM]
        return False if Settings.mso.lower() in ndvr_not_applicable_mso else True
    # MSO Checks End #

    # Button Check
    @staticmethod
    def is_replay_available():
        return True if Settings.platform.lower() in PlatformList.REPLAY_BUTTON_DEVICES else False

    @staticmethod
    def is_advance_available():
        return True if Settings.platform.lower() in PlatformList.ADVANCE_BUTTON_DEVICES else False

    @staticmethod
    def is_info_available():
        return True if Settings.platform.lower() in PlatformList.INFO_BUTTON_DEVICES else False

    @staticmethod
    def hydra_branch(name: str = None) -> HydraBranchVersion:
        """
        Method to get object of hydra version. The object can be compared the the instance of another branch object
        Args:
            name: str,

        Returns:
            HydraBranchVersion object
        """
        if name is None and Settings.branch:
            name = Settings.branch
        elif name is None and not isinstance(Settings.branch, str):
            raise ValueError("Settings.branch has value '{}' but expected non empty string".format(Settings.branch))
        if isinstance(name, str):
            branch_obj = BranchRegistry.get_branch(name.lower())
        else:
            raise ValueError("Unsupported type: {}".format(type(name)))
        return branch_obj

    BRANCH_REGISTRY = None

    @staticmethod
    def branch_registry() -> BranchRegistry:
        if Settings.BRANCH_REGISTRY is None:
            Settings.BRANCH_REGISTRY = BranchRegistry()
        return Settings.BRANCH_REGISTRY

    @staticmethod
    def mdrm_ndvr_feature():
        if Settings.is_cc11():
            return FeAlacarteFeatureList.NDVR1008011
        else:
            return FeAlacarteFeatureList.NDVR

    @staticmethod
    def has_basic_keyboard():
        if Settings.is_millicom() or Settings.is_llacr():
            return False
        else:
            return True

    @staticmethod
    def is_netflix_supported():
        platforms_not_supported = [PlatformList.JADE, PlatformList.RUBY]
        return Settings.platform.lower() not in platforms_not_supported

    @staticmethod
    def date_format_supported():
        # weekday day/month supported mso list
        mso_list = [MsoList.LLACR, MsoList.MILLICOM]
        if Settings.mso.lower() in mso_list:
            return '%a %d/%m'
        else:
            return '%a %m/%d'
