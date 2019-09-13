from typing import Dict

from idmtools_model_dtk.defaults.idtk_default import IDTKDefault


class DTKEmptyCampaign(IDTKDefault):
    @staticmethod
    def campaign() -> Dict:
        return {
            "Campaign_Name": "Empty campaign",
            "Events": [],
            "Use_Defaults": 1
        }
