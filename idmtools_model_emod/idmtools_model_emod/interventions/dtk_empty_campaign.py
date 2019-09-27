from typing import Dict

from idmtools_model_emod.defaults.idtk_default import IEMODDefault


class DTKEmptyCampaign(IEMODDefault):
    @staticmethod
    def campaign() -> Dict:
        return {
            "Campaign_Name": "Empty campaign",
            "Events": [],
            "Use_Defaults": 1
        }
