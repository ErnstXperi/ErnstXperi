"""
    @author: iurii.nartov@tivo.com
    @created: Dec-25-2019
"""

from tools.datatemplates import MapCompare


class MetaData(type):
    """ MetaClass for Constant storing"""
    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__"):
                yield self.__dict__[attr]

    def __setattr__(self, key, value):
        raise PermissionError("The dataclass is only for constants! Define value inside of config file:"
                              "{}".format(__file__))


class HydraBranchVersion(MapCompare):

    def __init__(self, name, prio):
        super().__init__(name, prio)


class HydraBranches(metaclass=MetaData):
    MAINLINE_4TH = "b-hydra-mainline4-th"
    MAINLINE = "b-hydra-mainline"
    STREAMER_1_5 = "b-hydra-streamer-1-5"
    STREAMER_1_6 = "b-hydra-streamer-1-6"
    STREAMER_1_7 = "b-hydra-streamer-1-7"
    STREAMER_1_9 = "b-hydra-streamer-1-9"
    STREAMER_1_11 = "b-hydra-streamer-1-11"
    STREAMER_1_13 = "b-hydra-streamer-1-13"
    STREAMER_1_15 = "b-hydra-streamer-1-15"
    STREAMER_1_16 = "b-hydra-streamer-1-16"
    STREAMER_1_17 = "b-hydra-streamer-1-17"
    STREAMER_1_18 = "b-hydra-streamer-1-18"
    STREAMER_1_19 = "b-hydra-streamer-1-19"


class BranchRegistry:

    __BRANCH_OBJ = {}
    __BRANCH_PRIO = {HydraBranches.MAINLINE_4TH: 90,
                     HydraBranches.MAINLINE: 100,
                     HydraBranches.STREAMER_1_5: 2,
                     HydraBranches.STREAMER_1_6: 3,
                     HydraBranches.STREAMER_1_7: 4,
                     HydraBranches.STREAMER_1_9: 5,
                     HydraBranches.STREAMER_1_11: 6,
                     HydraBranches.STREAMER_1_13: 7,
                     HydraBranches.STREAMER_1_15: 8,
                     HydraBranches.STREAMER_1_16: 9,
                     HydraBranches.STREAMER_1_17: 10,
                     HydraBranches.STREAMER_1_18: 11,
                     HydraBranches.STREAMER_1_19: 12,
                     }

    @staticmethod
    def get_branch(branch: str) -> HydraBranchVersion:
        if branch not in BranchRegistry.__BRANCH_OBJ.keys():
            hydra_branch = HydraBranchVersion(branch, BranchRegistry._extract_key(branch))
            BranchRegistry.__BRANCH_OBJ[branch] = hydra_branch
        else:
            hydra_branch = BranchRegistry.__BRANCH_OBJ[branch]
        return hydra_branch

    @staticmethod
    def _extract_key(value: str) -> int:
        if value in BranchRegistry.__BRANCH_PRIO.keys():
            return BranchRegistry.__BRANCH_PRIO[value]
        raise ValueError(
            "keys map doesnt contain value: '{}'. Avalaible: {}".format(value, BranchRegistry.__BRANCH_PRIO.keys()))

    @property
    def b_hydra_mainline4_th(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.MAINLINE_4TH)

    @property
    def b_hydra_mainline(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.MAINLINE)

    @property
    def b_hydra_streamer_1_5(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_5)

    @property
    def b_hydra_streamer_1_6(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_6)

    @property
    def b_hydra_streamer_1_7(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_7)

    @property
    def b_hydra_streamer_1_9(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_9)

    @property
    def b_hydra_streamer_1_11(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_11)

    @property
    def b_hydra_streamer_1_13(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_13)

    @property
    def b_hydra_streamer_1_15(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_15)

    @property
    def b_hydra_streamer_1_16(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_16)

    @property
    def b_hydra_streamer_1_17(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_17)

    @property
    def b_hydra_streamer_1_18(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_18)

    @property
    def b_hydra_streamer_1_19(self) -> HydraBranchVersion:
        return BranchRegistry.get_branch(HydraBranches.STREAMER_1_19)


class DriverTypeList(metaclass=MetaData):
    # Android TV driver types
    ANDROID_TV = "android_tv"
    ESTREAM4K = "estream4k"
    FIRE_TV = "firetv"

    APPLE_TV = "appletv"
    TVOS_GENERIC = "tvos_generic"
    APPLE_TV_4K = "appletv4k"
    DEV_HOST = "devhost"
    APPIUM = "appium"

    # STB driver types
    MINOS = "minos"
    ARGON = "argon"


class FeaturesList(metaclass=MetaData):
    """
    Feature name in featureStatusList (response for featureStatusSearch request)
    """
    HOSPITALITY = "hospitalityMode"
    SOCU = "clientSocu"
    VOICE = "voiceControl"
    IPPPV = "ipppv"
    PURCHASE_PIN = "purchasePin"
    NDVR = "cloudRecording"


class DeviceInfoStoreFeatures(metaclass=MetaData):
    """
    Feature list for DeviceInfoStore and DeviceInfoGet
    """
    SOCU = "clientsocu"
    VOICE = "voice"
    IPPPV = "ipppv"
    PURCHASE_PIN = "purchasePin"
    NDVR = "ndvr"


class BodyConfigFeatures(metaclass=MetaData):
    """
    Feature list from BodySearch and BodyConfigSearch
    """
    SOCU = "supportsSocu"
    VOICE = "supportsVoiceControl"
    IPPPV = "ipPayPerView"
    PURCHASE_PIN = "supportsPurchasePin"
    NDVR = "cloudRecording"


class MindEnvList(metaclass=MetaData):
    """
    Values for test_environment input param
    """
    STAGING = "staging"
    LATAM_STAGING = "latam_staging"
    USQE_1 = "usqe1"
    USQE_3A = "usqe3a"
    CDVRQE_1 = "cdvrqe1"
    PROD = "prod"
    LATAM_PROD = "latam_prod"
    PREPROD = "preprod"

    INTERNAL_ENV_LIST = [STAGING, USQE_1, CDVRQE_1, USQE_3A]


class MsoList(metaclass=MetaData):
    CC2 = "cableco"
    CC3 = "cableco3"
    CC5 = "cableco5"
    CC11 = "cableco11"
    CC12 = "cableco12"
    CBT = "cbt"
    RCN = "rcn"
    TDS = "tds"
    LLA = "llapr"
    LLACR = "llacr"
    LLAGD = "llagd"
    LLACL = "llacl"
    METRONET = "metronet"
    TELUS = "telus"
    MIDCO = "midco"
    MILLICOM = "millicom"
    BLUESTREAM = "bluestream"
    GRANDE = "grande"
    BLUERIDGE = "blueridge"
    SECV = "secv"
    SECTV = "sectv"
    ARMSTRONG = "armstrong"
    MEDIACOM = "mediacom"
    ABB = "abb"
    ENTOUCH = "entouch"
    HOTWIRE = "hotwire"
    ASTOUND = "astound"
    EASTLINK = "eastlink"
    BREEZELINE = "breezeline"

    INTERNAL_MSO_LIST = [CC2, CC3, CC5, CC11, CC12]
    EXTERNAL_MSO_LIST = [CBT, RCN, TDS, LLA, LLAGD, LLACL, METRONET, TELUS, MIDCO, MILLICOM, BLUESTREAM, GRANDE,
                         BLUERIDGE, SECV, SECTV, ARMSTRONG, LLACR, MEDIACOM, ABB, ENTOUCH, HOTWIRE, ASTOUND, EASTLINK,
                         BREEZELINE]


class FeAlacarteFeatureList(metaclass=MetaData):
    """
    Used in pr1ProvDeviceAlaCarteUpdate
    """
    LINEAR = "Linear"
    NDVR = "Ndvr"
    SOCU = "Socu"
    VOD = "Vod"
    NDVR1008011 = "Ndvr1008011"
    NDVR1008012 = "Ndvr1008012"


class FeAlacartePackageTypeList(metaclass=MetaData):
    """
    FE AlaCarte package type e.g. VideoProvider, Device, preferNative
    Used in pr1ProvDeviceAlaCarteUpdate
    """
    NATIVE = "preferNative"
    VERIMATRIX = "preferVerimatrix"
    DEFAULT = "Default"
    VIDEO_PROVIDER = "VideoProvider"
    DEVICE = "Device"


class LanguageList(metaclass=MetaData):
    ENGLISH = "en_us"
    SPANISH = "es_us"


class VodPackageType(metaclass=MetaData):
    """
    http://w3-engr/d-docs/autodocs/b-trioschema-mainline/trioschema/packageType.html
    """
    ASK_ME_LATER = "askMeLater"
    DYNAMIC_PVOD = "dynamicPvod"
    DYNAMIC_TVOD = "dynamicTvod"
    FVOD = "fvod"
    PVOD = "pvod"
    SVOD = "svod"
    TVOD = "tvod"
    ZVOD = "zvod"
    CUBI_ZVOD = "freeZeroPurchase"
    FREE = "free"
    FREE_VOD_LIST = [FVOD, ZVOD, CUBI_ZVOD, FREE]


class PlatformList(metaclass=MetaData):
    # Managed streamers
    AMINO = "amino"
    ARRIS = "arris"
    TECHNICOLOR = "technicolor"
    PUCK = "puck"
    JADE = "jade"
    RUBY = "ruby"
    FORCE1 = "force1"
    FUSE4K = "fuse4k"
    FALCON3 = "falcon3"
    JADE_HOTWIRE = "jadehotwire"
    JADE_21 = "jade21"
    JADE_MILLICOM = "jademillicom"

    # Unmanaged streamers
    MIBOX = "mibox"
    FIRE_TV = "firetv"
    APPLE_TV = "appletv"
    NVIDIA = "nvidia"
    ATOM = "atom"
    INSIGNIA = "insignia"
    JETSTREAM = "jetstream"
    TOSHIBA = "toshiba"
    SONYTV = "sonytv"
    GOOGLETV = "googletv"
    HISENSETV = "hisense"
    TCLTV = "tcltv"
    OMNITV = "omnitv"
    TIVO_4K = "tivo4k"

    # Set-top boxes
    MINOS = "minos"
    ARGON = "argon"
    ARRIS_SMARTBOX = "arrissmartbox"
    EVO_SMARTBOX = "evosmartbox"
    SMARTBOX = "smartbox"
    KEYSTONE = "keystone"
    TOPAZ = "topaz"
    TAOS = "taos"

    # Grouping plaforms
    MANAGED_STREAMERS_LIST = [AMINO, ARRIS, TECHNICOLOR, PUCK, JADE, RUBY, FORCE1, FALCON3, JADE_HOTWIRE, JADE_21,
                              JADE_MILLICOM, FUSE4K]
    UNMANAGED_STREAMERS_LIST = [MIBOX, FIRE_TV, APPLE_TV, NVIDIA, ATOM, INSIGNIA, JETSTREAM, TOSHIBA, SONYTV, GOOGLETV,
                                HISENSETV, TCLTV, OMNITV, TIVO_4K]
    ANDROID_STREAMERS_LIST = [AMINO, ARRIS, TECHNICOLOR, MIBOX, FIRE_TV, NVIDIA, PUCK, ATOM, INSIGNIA, JETSTREAM,
                              TOSHIBA, JADE, RUBY, SONYTV, GOOGLETV, FORCE1, HISENSETV, TCLTV, OMNITV, FALCON3,
                              JADE_HOTWIRE, JADE_21, JADE_MILLICOM, FUSE4K, TIVO_4K]
    STB_LIST = [MINOS, ARGON, ARRIS_SMARTBOX, EVO_SMARTBOX, KEYSTONE, TOPAZ, TAOS]
    STB_SERIES_7_LIST = [KEYSTONE, TOPAZ]
    STB_SMARTBOX_LIST = [ARRIS_SMARTBOX, EVO_SMARTBOX, SMARTBOX]
    STB_SERIES_6_LIST = [MINOS, TAOS]
    STB_SERIES_5_LIST = [ARGON]
    REPLAY_BUTTON_DEVICES = [AMINO]
    ADVANCE_BUTTON_DEVICES = [AMINO, PUCK, ARRIS]
    INFO_BUTTON_DEVICES = [AMINO, ARRIS]


class DebugEnvPropValues(metaclass=MetaData):
    """
    Possible values for DEBUGENV property in tcdui_test.conf
    """
    CONNECTION_INDICATOR = "CONNECTION_INDICATOR"  # square with red/green colors depending on if there is connection
    ACTIVITY_INDICATOR = "ACTIVITY_INDICATOR"  # square with red/green colors depending on if user is in active state


class DeviceFeatureSearchFeatures(metaclass=MetaData):
    """
    Request type = deviceFeatureSearch
    """
    FORCE_BACKHAUL = "forceBackhaul"
    INACTIVITY_TIME = "inactivityTime"


class BailButtonList(metaclass=MetaData):
    """
    Streamer bail buttons
    """
    GUIDE = "guide"
    HOME = "home"
    BACK = "back"
    EXIT = "exit"
    APPS = "apps"
    VOD = "vod"


class LongevityConstants(metaclass=MetaData):
    """
    Longevity Constants
    """
    HIGH_COUNTER = 10
    MED_COUNTER = 6
    LOW_COUNTER = 3


class DumpPath(metaclass=MetaData):
    """
    Screen Dump Path
    """
    PATH = {"OLD_PATH": "/sdcard/",
            "ANDROID_APP_STORAGE": "/storage/emulated/0/Android/data/{}/files/",
            "ANDROID_APP_STORAGE_V11": "/storage/emulated/0/Documents/",
            }


class DateTimeFormats(metaclass=MetaData):
    ISO_DATE_TIME = "%Y-%m-%dT%H:%M:%S"  # 2099-12-02T11:30:59
    ISO_DATE_TIME_WITH_Z = "%Y-%m-%dT%H:%M:%SZ"  # 2099-12-02T11:30:59Z
    ISO_ZONED_DATE_TIME = "%Y-%m-%dT%H:%M:%S.%f%z"  # e.g. 2022-10-03T07:00:00.000+00:00
    TRIO_DT = "%Y-%m-%d %H:%M:%S"  # e.g. 2022-10-03 09:00:00
    DAY_OF_THE_WEEK_DT = "%a %m/%d %I:%M%p"  # e.g. Mon 10/03 05:01AM
    TIME_AMPM = "%I:%M%p"  # e.g. 09:01AM
    DATE = "%m/%d/%Y"  # e.g. 10/03/2022


class NotificationSendReqTypes(metaclass=MetaData):
    """
    NSR Info: https://wiki.tivo.com/wiki/Microservices/Notification_Sender(NSR)/IDD
    FCM Info: https://confluence.corp.xperi.com/display/PATMT/Messaging+Phase+1%3A+FCM+Transport+DRD
    MTS Info: https://confluence.corp.xperi.com/display/ProductArchitecture/E2E+HLD%3A+User+Messaging+for+Managed+Android
    """
    NO_REQ = "NO_REQ"  # test does not need to make FCM/NSR (may be applicable for old tests that use app restart)
    FCM = "FCM"  # Firebase Cloud Messaging
    NSR = "NSR"  # reliable notification send
    MTS = "MTS"  # messaging targeting system


class RemoteCommands(metaclass=MetaData):
    """
    Remote commands are sent by NotificationSendReqTypes requests
    """
    FEATURE_STATUS = "featureStatus"
    SERVICE_CALL = "serviceCall"
    REMOVE_ALL_MESSAGES = "removeAllMessage"
    REMOVE_MESSAGE = "removeMessage"
    DEVICE_MESSAGE = "deviceMessage"
