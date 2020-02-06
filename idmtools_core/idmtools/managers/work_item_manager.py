import time
from COMPS.Data.WorkItem import WorkItemState
from idmtools.entities import IPlatform
from idmtools.ssmt.idm_work_item import SSMTWorkItem


class WorkItemManager:
    """
    Class that manages an SSMTWorkItem.
    """

    def __init__(self, wi: SSMTWorkItem, platform: IPlatform):
        """
        A constructor.

        Args:
            wi: SSMTWorkItem to manage
            platform: The platform to use
        """
        self.wi = wi
        self.platform = platform
        self.wi.platform = platform

    def process(self, check_status=True):

        # Create work item
        self.create()

        # Run
        self.start_work_item()

        # Check status
        self.wait_till_done(check_status)

    def create(self):
        """
        Create a WorkItem

        Returns: None

        """

        self.platform.create_items([self.wi])

    def start_work_item(self):
        """
        Start to run work item

        Returns: None
        """
        self.platform.run_items([self.wi])

    def wait_till_done(self, check_status=True, timeout=3600):
        """
        Check work item status
        Args:
            check_status: bool to decide if repeat checking
            timeout: repeat checking interval

        Returns: None

        """
        if check_status:
            start = time.clock()
            state = self.wi.status
            states = [WorkItemState.Succeeded, WorkItemState.Failed, WorkItemState.Canceled]
            while state not in states and time.clock() - start < timeout:
                time.sleep(5)
                self.refresh_status()
                state = self.wi.status
                print('State -> {} '.format(state.name))
        else:
            print('WorkItem created in {}.'.format(self.platform.endpoint))

    def refresh_status(self):
        """
        Get the latest status of the work item

        Returns: None
        """
        self.platform.refresh_status(item=self.wi)
