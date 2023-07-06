from mind_api.middle_mind import field
from set_top_box.conf_constants import HydraBranches
from set_top_box.test_settings import Settings


class GuideLabels():
    LBL_VIEW_MODE = "guide.GridGuideScreenView"
    LBL_LIVE_TV_VIEW_MODE = "watchvideo.screens.WatchLiveTvScreenView"
    LBL_LIVE_TV_SCREEN = "TvWatchLiveHdScreen"
    LBL_VOD_VIEW_MODE = 'watchvideo.screens.WatchVodScreenView'
    LBL_SCREENTITLE = "GUIDE"
    LBL_CHANNEL_OPTIONS_WATCH_NOW = "Watch now"
    LBL_PROGRAM_OPTIONS_WATCH_LIVE = "Watch live"
    LBL_PROGRAM_OPTIONS_CREATE_ONEPASS = "Create a OnePass for this series"
    LBL_CREATE_ONEPASS_WITH_THIS_OPTIONS = "Create OnePass with these options"
    LBL_CREATE = "Create"
    LBL_CREATE_ONEPASS_SUBSTRING = "Create OnePass"
    LBL_PROGRAM_OPTIONS_RECORD_EPISODE = "Record just this episode"
    LBL_PROGRAM_OPTIONS_BOOKMARK_EPISODE = "Bookmark this episode"
    LBL_PROGRAM_OPTIONS_MORE_INFO = "More info"
    LBL_RECORD_OVERLAY_MENU_ITEM = [u'Watch live', u'More info']
    LBL_PPV_ICON = "hydra_icon_ppv.png"
    LBL_CATCHUP_ICON = "hydra_icon_status_catch_up.png"
    LBL_RECORD_OVERLAY_CATCHUP_ICON = "hydra_icon_source_socu"
    LBL_WATCH_NOW_FROM_CATCHUP = "Watch now from Catch Up"
    LBL_RECORDING_NOW_ICON = 'hydra_icon_status_recording_now.png'
    LBL_ONEPASS_ICON = 'hydra_icon_status_onepass.png'
    LBL_WATCH_NOW_FROM_CABLECO3_SOCU = "Watch now from Cableco3 SOCU"
    LBL_WATCH_NOW_FROM_CABLECO_SOCU = "Watch now from Cableco SOCU"
    LBL_WATCH_NOW_FROM_CABLECO11_SOCU = "Watch now from Cableco11 SOCU"
    LBL_REC_OVERLAY_FIRST_AIRED = "First aired"
    # Show attributes (shown in parenthesis after description e.g. (SAP, CC, R) )
    LBL_CC_SHOW_ATTRIBUTE = "CC"
    LBL_REPEAT_SHOW_ATTRIBUTE = "R"
    LBL_SAP_SHOW_ATTRIBUTE = "SAP"
    LBL_3D_SHOW_ATTRIBUTE = "3D"
    LBL_MY_SHOWS = "My Shows"
    LBL_SOCU = "SOCU"
    LBL_FAVORITE_CHANNELS = "Favorite Channels"
    LBL_CHANNEL_OPT_OVERLAY = "ChannelOptionsOverlay"
    LBL_LIVE_AND_UPCOMING = "Live & Upcoming"
    LBL_ONE_PASS = "OnePass"
    LBL_USE_THESE_OPTIONS = "Use these OnePass options"
    LBL_RECORD = "Record"
    LBL_RECORD_STRING = "Record"
    LBL_RECORD_MOVIE = "Record Movie"
    LBL_ALL_SHOWS = "All shows"
    LBL_RECORD_THIS_MOVIE = "Record this movie with these options"
    LBL_WATCH_NOW_FROM = "Watch now from"
    LBL_RENT_AND_WATCH_NOW_IPPPV = "Rent and Watch Now"  # beginning of the IPPPV option text, currently airing show
    LBL_RENT_THIS_SHOW = "Rent This Show"  # beginning of the IPPPV option text, future show
    # Warning message on the Record overlay when failed to retrieve purchase info for a PPV program
    LBL_UNABLE_TO_GET_PURCHASE_INFO_FOR_PPV_PROGRAM = "Unable to get purchase information for this pay-per-view program."
    LBL_PROGRAM_OPTIONS_RECORD_EPISODE_WITH_THESE_OPTIONS = "Record this episode with these options"
    LBL_PROGRAM_OPTIONS_RECORD_SHOW_WITH_THESE_OPTIONS = "Record this show with these options"
    LBL_RECORD_SUCCESS_WHISPER = "This episode is now scheduled to record."
    LBL_RECORD_SUCCESS_WHISPER_MOVIE = "This movie is now scheduled to record."
    LBL_RECORD_AGAIN = "Record again"
    LBL_WATCH_SCREEN = "TvWatch"
    LBL_CANCEL = "Cancel"
    LBL_MODIFY = "Modify"
    LBL_CREATE_ON_OPTIONS_OVERLAY = "Create"
    LBL_MODIFY_ONEPASS = "Modify OnePass"
    LBL_MODIFY_RECORDING = "Modify recording"
    LBL_OVERLAY_STORAGE_LIMIT_TITLE = "Storage Limit"
    LBL_OVERLAY_STORAGE_LIMIT_OK = "OK, continue anyway"
    LBL_YES_CANCEL = "Yes, cancel"
    LBL_CANCEL_REC_CONFIRMATION = "cancel"
    SUBSCRIBED_CHANNEL_COLOR = "ffebebeb"
    NOT_SUBSCRIBED_CHANNEL_COLOR = "888888"
    CHANNEL_NOT_SUBSCRIBED = "Channel Not Subscribed"
    LBL_FAVORITES_OPTION = "Favorites"
    LBL_ALL_CHANNELS_TIP_TEXT = "all channels"
    LBL_FAVORITE_CHANNELS_TIP_TEXT = "favorite channels"
    LBL_EMPTY_FAVORITE_CHANNELS_TEXT = 'You have not selected any favorite channels.'
    LBL_RECORD_SCHEDULED = "scheduled to record."
    LBL_CHECKED = "hydra_icon_checkbox_checked.png"
    LBL_UNCHECKED = 'hydra_icon_checkbox_unchecked.png'
    LBL_FAVORITE_CHANNELS_SCREEN_NAME = "SettingsFavoriteChannels"
    LBL_RECORD_OVERLAY = "RecordOverlay"
    LBL_RECORDING_OPTIONS_OVERLAY = "RecordingOptionsOverlay"
    LBL_ALREADY_RECORDING_OVERLAY = "AreadyRecordingOverlay"
    LBL_START_RECORDING_PADDING = "5 min early"
    LBL_STOP_RECORDING_PADDING = "30 min longer"
    LBL_GUIDE_SCREEN = "GridGuide"
    LBL_GUIDE_LOADING = "GuideListModel obtained"
    LBL_MODIFY_RECORDING = "Modify recording"
    LBL_RESUME_OVERLAY = "VODResumeStartOverOverlay"
    LBL_SOCU_PLAYBACK_SCREEN = "TvWatchStreamingVideoScreen"
    LBL_RECORDING_PLAYBACK_SCREEN = "TvWatchRecordingHdScreen"
    LBL_TRY_AGAIN_SCREEN = "TryAgainLaterOverlay"
    LBL_ONEPASS_OPTIONS_OVERLAY = "OnePassOptionsOverlay"
    LBL_ONEPASS_WHISPER_TEXT = "A OnePass has been created"
    LBL_ONEPASS_WHISPER_UPDATE_TEXT = "Your OnePass has been updated"
    LBL_TITLE_NOT_AVAILABLE = "Title not available"
    LBL_ONEPASS_MANAGER = "OnePass Manager"
    LBL_ON_DEMAND_SCREEN_TITLE = "ON DEMAND"
    LBL_VOD_SCREEN = "VodBrowseMainScreen"
    LBL_VOD_BROWSE_GALLERY_SCREEN = "VodBrowseGalleryScreen"
    LBL_HDMI_OVERLAY = "HDMI Not Permitted"
    LBL_KEEP_UNTIL = ["Space needed", "As long as possible"]
    LBL_KEEP_UNTIL_MENU = "Keep until:"
    LBL_STOPRECORDING = ["On time", "1 min longer", "2 min longer", "3 min longer", "4 min longer", "5 min longer",
                         "10 min longer", "15 min longer", "30 min longer", "1 hr longer", "1 hr 30 min longer", "3 hr longer"]
    LBL_STARTRECORDING = ["On time", "1 min early", "2 min early", "3 min early", "4 min early", "5 min early", "10 min early"]
    LBL_STOP_RECORDING = ["On time", "1 minute longer", "2 minutes longer", "3 minutes longer", "4 minutes longer",
                          "5 minutes longer", "10 minutes longer", "15 minutes longer", "30 minutes longer",
                          "1 hour longer", "1 1/2 hours longer", "3 hours longer"]
    LBL_START_RECORDING = ["On time", "1 minute early", "2 minutes early", "3 minutes early",
                           "4 minutes early", "5 minutes early", "10 minutes early"]
    LBL_START_RECORDING_MENU = 'Start recording:'
    LBL_STOP_RECORDING_MENU = 'Stop recording:'
    LBL_EXPLICIT_RECORD_ICON = "hydra_icon_status_single_explicit_record.png"
    LBL_CANCEL_ONEPASS_WHISPER = "This series will not record."
    LBL_CANCEL_ONEPASS_OVERLAY = "CancelOnePassOverlay"
    LBL_SOCU_SOURCE_ICON_HEADER = "hydra_icon_source_socu"
    LBL_RESUME_PLAYING = "Resume playing"
    LBL_STARTOVER = "Start over from beginning"
    LBL_PLAYBACK_IN_PAUSE_MODE = "playPause"
    LBL_PLAYBACK_IN_PLAY_MODE = "playNormal"
    LBL_WATCH_NOW = "Watch Now"
    LBL_WATCH_NOW_FROM = "Watch now"
    LBL_RECORDING_AND_BOOKMARK_OPTIONS = "Recording & Bookmark Options"
    LBL_ONEPASS_AND_RECORDING_OPTIONS = "OnePass & Recording Options"
    LBL_RENT_OPTIONS = "Rent Options"
    LBL_UPCOMING_AIRINGS = "Upcoming Airings"
    LBL_ALL_EPISODES = "All Episodes"
    LBL_ALL_UPCOMING_EPISODES = "All Upcoming Episodes"
    LBL_UPCOMING = "Upcoming"
    LBL_MAY_ALSO_LIKE = "May Also Like"
    LBL_CAST = "Cast"
    LBL_START_FROM_MENU = "Start from:"
    LBL_RENT_OR_BUY_MENU = "Rent or buy:"
    LBL_CHANNEL_MENU = "Channel:"
    LBL_KEEP_AT_MOST_MENU = "Keep at most:"
    LBL_RECORD_MENU = "Record:"
    LBL_EVERYTHING = "Everything"
    LBL_INCLUDE_MENU = "Include:"
    LBL_STREAMING_VIDEO_ONLY = "Streaming videos only"
    LBL_RECOVER_STRIP = "Recover"
    LBL_NEW_AND_RERUNS = "New & reruns"
    LBL_NON_EPISODIC_STRIP_ORDER = [LBL_WATCH_NOW, LBL_RECOVER_STRIP, LBL_RECORDING_AND_BOOKMARK_OPTIONS, LBL_CAST,
                                    LBL_MAY_ALSO_LIKE, LBL_RENT_OPTIONS, LBL_UPCOMING_AIRINGS]
    LBL_EPISODIC_STRIP_ORDER = [LBL_WATCH_NOW, LBL_RENT_OPTIONS, LBL_ONEPASS_AND_RECORDING_OPTIONS,
                                LBL_CAST, LBL_MAY_ALSO_LIKE, LBL_ALL_EPISODES, LBL_UPCOMING,
                                LBL_UPCOMING_AIRINGS, LBL_ALL_UPCOMING_EPISODES]
    LBL_UPCOMING_AIRINGS_LIST_SCREEN = "UpcomingAiringsList"
    LBL_NEW_ICON = 'hydra_icon_status_new.png'
    LBL_HD_ICON = 'hydra_icon_hd.png'
    LBL_SD_ICON = 'hydra_icon_sd.png'
    LBL_UHD_ICON = 'hydra_icon_uhd.png'
    LBL_LIVE_ICON = 'hydra_icon_live.png'
    LBL_HD_SD_ICONS = [LBL_HD_ICON, LBL_SD_ICON]
    LBL_GUIDE_BANNER_ACTION_NO_ACTION = 'noOpUiAction'
    LBL_GUIDE_BANNER_ACTION_SCREEN_UI_NAVIGATE = 'screenUiNavigateAction'
    LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE = 'uiNavigateAction'
    LBL_GUIDE_BANNER_LIVE_TV_UI_ACTION = 'liveTvUiAction'
    LBL_WTW_SCREEN_VIEW = 'whattowatch2.WTWScreenView'
    LBL_WATCH_NOW_FROM_MY_SHOWS = "Recording in My Shows"
    LBL_RECORDING = "Recording"
    LBL_REPLAY = "Replay"
    LBL_HD = "HD"
    LBL_UPCOMING_EPISODES_LIST_SCREEN = "UpcomingEpisodesList"
    LBL_ADD_TO_FAVORITE_CHANNELS = "Add to Favorite Channels"
    LBL_EMPTY_SEARCH_MESSAGE = "There are no matching shows, movies, videos, or people."
    LBL_RENT_THIS_SHOW = "Rent This Show"
    LBL_PURCHASE_CONFIRM_OVERLAY_TITLE = "Confirm Purchase"
    LBL_INFO_OVERLAY = "overlay.InfoOverlayView"
    LBL_PURCHASED_CONFIRMED_TITLE = "Purchase Confirmed"
    LBL_TRANSACTION_PROBLEM_TITLE = "Transaction Problem"
    LBL_RENT_FOR = "Rent for"
    LBL_NO = "No"
    LBL_CONFIRM_PURCHASE_OVERLAY_BODY = "Confirm that you want to purchase this show"
    LBL_CONFIRM_PURCHASE_OVERLAY_MENU_ITEMS = [u'Rent for', u'No']
    LBL_WATCH_NOW_RECORD_OVERLAY = "Watch now"
    # Text in OSD when IPPPV feature is ON on a managed device
    LBL_PPV_UPSELL_OVERLAY = "Press OK/SELECT for Pay Per View info" \
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_15) else \
        "Press OK for Pay Per View info."
    LBL_DOWNLOAD_OVERLAY = "Player download failure. Can't play now."
    LBL_DOWNLOAD_OVERLAY_TITLE = "Download Error"
    LBL_NEW_ONLY = "New only"
    LBL_LAUNCH_APP = "Launch App"
    LBL_RECORDINGS_ONLY = "Recordings only"
    LBL_NEW_ONLY = "New only"
    LBL_CHANNELS_WATCH_NOW_OVERLAY = "Channels:"
    LBL_STATUS_MESSAGE_NDVR_OFFER_RESTRICTION = "Recording prohibited due to copyright restrictions."
    LBL_NOT_AVAILABLE_TO_WATCH_OR_RECORD = "This show is not available to watch or to record."
    LBL_NOT_AVAILABLE_TO_RECORD = "This show is not available to record."
    LBL_RECORD_THIS_MOVIE_INFOCARD = "Record this movie"
    LBL_RECORD_THIS_SHOW = "Record this show"
    LBL_COMMON_IMAGE_PATH = "com/tivo/applib/ResAppLibImages/applib/images/hydra/1080p/"
    LBL_NON_RECORDABLE_CELL_ICON = "hydra_icon_status_not_recordable_cell.png"
    LBL_NON_RECORDABLE_ICON = "hydra_icon_status_not_allowed.png"
    LBL_ICON_START_RATING_HALF = "hydra_icon_star_half.png"
    LBL_ICON_START_RATING_EMPTY = "hydra_icon_star_empty.png"
    LBL_ICON_START_RATING_FULL = "hydra_icon_star_full.png"
    # Disconnected Guide service whisper when opening One Line Guide
    LBL_WHISPER_OLG_DISCONNECTED_GUIDE_SERVICE = "There is an issue with the guide, " \
        "but you can still watch live TV and change channels as usual. We are working to fix the problem."
    # The text on the Guide Cell or One Line Guide tile when service connection is down
    LBL_DS_PROGRAM_CELL = "Select to watch"
    LBL_EPG_PAST_NUMBER_OF_HOURS = 72
    LBL_STATUS_MESSAGE_NDVR_CHANNEL_RESTRICTION = "Channel does not allow recording."
    LBL_IPPPV_CHANNEL = "8863"
    LBL_SCREEN_SAVER_WAIT_TIME = 180
    LBL_TEN_SECONDS = 10
    LBL_TWENTY_SECONDS = 20
    LBL_THIRTY_SECONDS = 30
    LBL_FORTY_SECONDS = 40
    PLUTO_PACKAGE_NAME = "tv.pluto.android"
    NETFLIX_PACKAGE_NAME = "com.netflix.ninja"
    PRIME_PACKAGE_NAME = "com.amazon.amazonvideo.livingroom"
    YOUTUBE_PACKAGE_NAME = "com.google.android.youtube.tv"
    YOUTUBE_MUSIC_PACKAGE_NAME = "com.google.android.youtube.tvmusic"
    YOUTUBE_KIDS_PACKAGE_NAME = "com.google.android.youtube.tvkids"
    GOOGLE_PLAY_PACKAGE_NAME = "com.android.vending"
    VUDU_PACKAGE_NAME = 'air.com.vudu.air.DownloaderTablet'
    STARZ_PACKAGE_NAME = "com.bydeluxe.d3.android.program.starz"
    AMAZON_PACKAGE_NAME = "com.amazon.amazonvideo.livingroom"
    HULU_PACKAGE_NAME = "com.hulu.livingroomplus"
    HBO_PACKAGE_NAME = "com.hbo.hbonow"
    DISNEY_PLUS_PACKAGE_NAME = "com.disney.disneyplus"
    GOOGLE_PLAY_MOVIES_PACKAGE_NAME = "com.google.android.videos"
    PANDORA_PACKAGE_NAME = "com.pandora.android.atv"
    SPOTIFY_PACKAGE_NAME = "com.spotify.tv.android"
    ACCUWEATHER_PACKAGE_NAME = "com.accuweather.android"
    STINGRAY_PACKAGE_NAME = "com.stingray.tv.stingraymusic"
    LBL_SOCU_FALLBAC_IMG = "partnerSourceLogo"
    LBL_SUBSCRIBED_CHANNEL_ONLY = "DG_ShowOnlyEntitledChannels"
    SHOW_TIME_PACKAGE_NAME = "com.showtime.showtimeanytime"
    EPIX_PACKAGE_NAME = "com.epix.epix"
    PBS_KIDS_PACKAGE_NAME = "org.pbskids.video"
    LBL_SELECT_WATCH_CHANNEL = "Select to watch"

    def __init__(self):
        self.THIRD_PARTY_APP_PACKAGES = {"netflix": self.NETFLIX_PACKAGE_NAME,
                                         "prime video": self.PRIME_PACKAGE_NAME,
                                         "vudu": self.VUDU_PACKAGE_NAME,
                                         "starz": self.STARZ_PACKAGE_NAME,
                                         "hbo": self.HBO_PACKAGE_NAME,
                                         "pluto": self.PLUTO_PACKAGE_NAME,
                                         "youtube": self.YOUTUBE_PACKAGE_NAME,
                                         "youtube_music": self.YOUTUBE_MUSIC_PACKAGE_NAME,
                                         "youtube_kids": self.YOUTUBE_KIDS_PACKAGE_NAME,
                                         "play_store": self.GOOGLE_PLAY_PACKAGE_NAME,
                                         "disney_plus": self.DISNEY_PLUS_PACKAGE_NAME,
                                         "google_play_movies": self.GOOGLE_PLAY_MOVIES_PACKAGE_NAME,
                                         "hulu": self.HULU_PACKAGE_NAME,
                                         "pandora": self.PANDORA_PACKAGE_NAME,
                                         "spotify": self.SPOTIFY_PACKAGE_NAME,
                                         "accuweather": self.ACCUWEATHER_PACKAGE_NAME,
                                         "stingray": self.STINGRAY_PACKAGE_NAME,
                                         "showtime": self.SHOW_TIME_PACKAGE_NAME,
                                         "epix": self.EPIX_PACKAGE_NAME,
                                         "pbs": self.PBS_KIDS_PACKAGE_NAME
                                         }
        self.ON_DEMAND_SCREENS = {"on_demand": self.LBL_VOD_SCREEN,
                                  "on_demand_sub_folders": self.LBL_VOD_BROWSE_GALLERY_SCREEN}
