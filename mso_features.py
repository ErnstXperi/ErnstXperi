import yaml
import os


class MSOFeatures:

    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        with open(self.dir_path + '/mso_supported_features.yml') as self.yfile:
            self.features_list = yaml.load(self.yfile, Loader=yaml.FullLoader)

    def get_supported_features(self, mso):
        supported_features = []
        if mso not in self.features_list.keys():
            mso = 'all'
        for mso_yml, features in self.features_list.items():
            if mso == mso_yml:
                supported_features = features
                break
        return supported_features

    def get_unsupported_features(self, mso):
        all_features = self.get_supported_features('all')
        supported_features = self.get_supported_features(mso)
        unsupported_features = (list(set(all_features) - set(supported_features)))
        return unsupported_features
