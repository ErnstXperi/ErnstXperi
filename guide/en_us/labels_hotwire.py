class HotwireGuideLabels:

    MY_COMMUNITY_PACKAGE_NAME = "com.hotwirecommunications.stb.community"

    def __init__(self):
        super().__init__()
        self.THIRD_PARTY_APP_PACKAGES.update({"my_community": self.MY_COMMUNITY_PACKAGE_NAME})
