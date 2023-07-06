from .labels import GuideLabels


class BlueridgeGuideLabels(GuideLabels):
    LBL_WATCH_NOW = "Watch Now"
    LBL_RECOVER_STRIP = "Recover"
    LBL_BOOKMARK_OPTIONS = "Bookmark Options"
    LBL_CAST = "Cast"
    LBL_MAY_ALSO_LIKE = "May Also Like"
    LBL_UPCOMING_AIRINGS = "Upcoming Airings"
    LBL_CAST = "Cast"
    LBL_ALL_EPISODES = "All Episodes"
    LBL_ALL_UPCOMING_EPISODES = "All Upcoming Episodes"
    LBL_UPCOMING = "Upcoming"
    LBL_ONEPASS_OPTIONS = "OnePass & Recording Options"
    LBL_RECORDING_AND_BOOKMARK_OPTIONS = "Recording & Bookmark Options"
    LBL_NON_EPISODIC_STRIP_ORDER = [LBL_WATCH_NOW, LBL_RECOVER_STRIP, LBL_BOOKMARK_OPTIONS,
                                    LBL_RECORDING_AND_BOOKMARK_OPTIONS, LBL_CAST,
                                    LBL_MAY_ALSO_LIKE, LBL_UPCOMING_AIRINGS]
    LBL_EPISODIC_STRIP_ORDER = [LBL_WATCH_NOW, LBL_ONEPASS_OPTIONS,
                                LBL_CAST, LBL_MAY_ALSO_LIKE, LBL_ALL_EPISODES, LBL_UPCOMING,
                                LBL_UPCOMING_AIRINGS, LBL_ALL_UPCOMING_EPISODES]
