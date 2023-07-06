from set_top_box.client_api.guide.page import GuidePage
from tools.logger.logger import Logger


class AppleTvGuidePage(GuidePage):
    __logger = Logger(__name__)

    def enter_channel_number(self, channel, confirm=False, olg=False, dump=True):
        """
        Hardcoded delay due to method used for guide, olg, live tv,
        thus it's easier not to maintain screen names
        """
        if olg:
            self.navigate_to_channel_from_one_line_guide(channel)
        else:
            self.navigate_to_channel_from_guide_grid(channel)
        if confirm and olg:
            self.pause(3)  # waiting a bit for confirmation to work
            self.press_ok_button(refresh=False)
            if dump:
                self.screen.get_json()  # to avoid waiting 8 seconds in OLG
        elif confirm and not olg:
            self.press_ok_button(refresh=False)
            self.pause(2)  # waiting for opening playback screen in Guide
            if dump:
                self.screen.refresh()
        elif not confirm and olg:
            self.pause(2)  # waiting a bit for tuning to a new channel
            if dump:
                self.screen.get_json()  # to avoid waiting 8 seconds in OLG
        else:
            # TODO: Delay should be replaced to ContentReady
            self.pause(5)
            if dump:
                self.screen.refresh()
        return True

    def channel_change(self, button="channel up"):
        self.log.info("Channel change from one line guide")
        self.open_olg()
        if button == "channel up":
            self.screen.base.press_up()
        else:
            self.screen.base.press_down()
        self.screen.base.press_enter()
