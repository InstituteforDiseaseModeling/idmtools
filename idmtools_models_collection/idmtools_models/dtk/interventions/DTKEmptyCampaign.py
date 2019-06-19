from typing import Dict

from idmtools_models.dtk.defaults.IDTKDefault import IDTKDefault


class DTKEmptyCampaign(IDTKDefault):
    @staticmethod
    def campaign() -> Dict:
        return {
            "Campaign_Name": "Empty campaign",
            "Events": [],
            "Use_Defaults": 1
        }
