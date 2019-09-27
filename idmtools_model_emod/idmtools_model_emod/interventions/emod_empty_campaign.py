from typing import Dict

from idmtools_model_emod.defaults.iemod_default import IEMODDefault


class EMODEmptyCampaign(IEMODDefault):
    @staticmethod
    def campaign() -> Dict:
        return {
            "Campaign_Name": "Empty campaign",
            "Events": [],
            "Use_Defaults": 1
        }
