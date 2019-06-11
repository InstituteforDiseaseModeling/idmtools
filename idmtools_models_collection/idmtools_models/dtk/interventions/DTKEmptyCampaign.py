from typing import Dict

from idmtools_models.dtk.defaults.IDTKDefault import IDTKDefault


class DTKEmptyCampaign(IDTKDefault):
    @property
    def campaign(self) -> Dict:
        return {
            "Campaign_Name": "Empty campaign",
            "Events": [],
            "Use_Defaults": 1
        }
