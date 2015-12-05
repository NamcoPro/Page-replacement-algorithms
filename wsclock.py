from sys import argv
from p_memory import Physical_Memory, Page

class PM_wsclock(Physical_Memory):
    """A class representing physical memory using the wsclock page replacement
    algorithm. The pages will be put on a 'circular list'."""
    def __init__(self, size = 0, tau):
        """the clock_arm is for the traversing the circular list.
        tau is the parameter for replacing pages.
        virtual_clock determines the page values and how old they are."""
        Physical_Memory.__init__(self, size)
        self.clock_arm = 0
        self.tau = tau
        self.virtual_clock = 0

    def update_arm(self):
        """Updates the clock_arm on the clock, there can be a modulo 0, but
        the implementation takes cares of this problem."""
        self.clock_arm = ((self.clock_arm + 1) % len(self.pages))

    def update_clock(self):
        """Updates the virtual time."""
        self.virtual_clock += 1

    def update_with_page(self, page):
        """Page handler for the WSclock algorithm. It calls functions to deal
        with the current page depending on whether it needs to be read or
        written."""
