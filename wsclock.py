from sys import argv
from p_memory import Physical_Memory, Page

class WS_Page(Page):
    """Same as the other Page class expect its reference bit is off."""
    def __init__(self, addr, val = 0, operation = None):
        Page.__init__(self, addr, val, operation)
        self.ref = 0

class PM_wsclock(Physical_Memory):
    """A class representing physical memory using the wsclock page replacement
    algorithm. The pages will be put on a 'circular list'."""
    def __init__(self, size = 0, tau = 5):
        """the clock_arm is for the traversing the circular list, the -1
        is for convenience. Lists can be accessed with -1.
        tau is the parameter for replacing pages.
        virtual_clock determines the page values and how old they are."""
        Physical_Memory.__init__(self, size)
        self.clock_arm = -1
        self.tau = tau
        self.virtual_clock = 0

    def page_age(self):
        """Gives the age of the page pointed on."""
        return (self.virtual_clock - self.pages[self.clock_arm].value())

    def replace_page(self, page):
        """Replaces a page when a page fault is happening."""
        self.pages[self.clock_arm] = page
        self.pages[self.clock_arm].assign_value(self.virtual_clock)
        self.update_arm()

    def point_at(self, index):
        """Updates the clock arm to the current index."""
        self.clock_arm = index

    def page_arm(self):
        """The returns the page in the current arm position."""
        return self.pages[self.clock_arm]

    def update_arm(self):
        """Updates the clock_arm on the circular list."""
        if(not self.full()):
            self.clock_arm += 1
        else:
            self.clock_arm = ((self.clock_arm + 1) % self.size)

    def update_clock(self):
        """Updates the virtual time."""
        self.virtual_clock += 1

    def update_with_page(self, page):
        """Page handler for the WSclock algorithm. It calls functions to deal
        with the current page depending on whether it needs to be read or
        written. The pages' virtual clock will be updated as fit.
        Not necessary, it's just to make the main function a little cleaner?"""
        self.update_clock()

        if(page.wants_read()):
            self.handle_read(page)

        elif(page.wants_write()):
            self.handle_write(page)

        else:
            self.handle_no_operation(page)

    def handle_read(self, page):
        """Handles the incoming page if it wants a read. If the requested
        address isn't on the physical space, then the page address is added
        without a modified bit."""
        page_hit, index = self.address_in_space(page)

        if(page_hit):
            #refeferencing the bit, no big deal.
            self.pages[index].rereference()
            self.pages[index].assign_value(self.virtual_clock)

        else:
            self.faults += 1

            #candidates of indices in case nothing is found
            #class 0: not referenced and not modifed
            #class 1: not referenced and modified
            #class 2: referenced and not modified
            #class 3: referenced and modified
            candidates = [[] for i in range(4)]

            #for traversing the clock_arm
            once = 1
            current_arm = self.clock_arm
            while(once):
                if(self.page_arm().referenced() and self.page_arm().modified()):
                    self.page_arm().dereference()
                    candidates[3].append(self.clock_arm)

                elif(self.page_arm().referenced()):
                    self.page_arm().dereference()
                    candidates[2].append(self.clock_arm)

                elif(self.page_arm().modified()):
                    candidates[1].append(self.clock_arm)

                #Here it looks for the age of the page since it's not referenced
                #and not modified. if it's older than tau then it is removed.
                elif(self.page_age() > self.tau):
                    self.replace_page(page)
                    return

                else:
                    candidates[0].append(self.clock_arm)

                self.update_arm()
                self.update_clock()

                if(current_arm == self.clock_arm):
                    once = 0

            #the loop in case nothing was found
            for classes in candidates:
                oldest = float("inf")
                arm_pointer = None
                for indices in classes:
                    #the smallest value means it's the oldest
                    if(self.pages[indices].value() < oldest):
                        oldest = self.pages[indices].value()
                        arm_pointer = indices

                #something was found
                if(arm_pointer != None):
                    self.point_at(arm_pointer)
                    self.replace_page(page)
                    return

    def handle_write(self, page):
        """Handles the incoming page if it wants to write. If there's a hit,
        then the referenced page's modifed bit is actualized. If there's a
        fault, then the algorithm is applied. """
        page_hit, index = self.address_in_space(page)

        if(page_hit):
            #page hit for the modified bit
            self.pages[index].modify()
            self.pages[index].rereference()
            self.pages[index].assign_value(self.virtual_clock)

        elif(not self.full()):
            #adds the page
            self.pages.append(page)
            #assigns the page the current time
            self.pages[self.clock_arm].assign_value(self.virtual_clock)
            #moves to the next page
            self.update_arm()
            #updates faults
            self.faults += 1

        else:
            self.faults += 1

            #candidates of indices in case nothing is found
            #class 0: not referenced and not modifed
            #class 1: not referenced and modified
            #class 2: referenced and not modified
            #class 3: referenced and modified
            candidates = [[] for i in range(4)]

            #for traversing the clock_arm
            once = 1
            current_arm = self.clock_arm
            while(once):
                if(self.page_arm().referenced() and self.page_arm().modified()):
                    self.page_arm().dereference()
                    candidates[3].append(self.clock_arm)

                elif(self.page_arm().referenced()):
                    self.page_arm().dereference()
                    candidates[2].append(self.clock_arm)

                elif(self.page_arm().modified()):
                    candidates[1].append(self.clock_arm)

                #Here it looks for the age of the page since it's not referenced
                #and not modified. if it's older than tau then it is removed.
                elif(self.page_age() > self.tau):
                    self.replace_page(page)
                    return

                else:
                    candidates[0].append(self.clock_arm)

                self.update_arm()
                self.update_clock()

                if(current_arm == self.clock_arm):
                    once = 0

            #the loop in case nothing was found
            for classes in candidates:
                oldest = float("inf")
                arm_pointer = None
                for indices in classes:
                    #the smallest value means it's the oldest
                    if(self.pages[indices].value() < oldest):
                        oldest = self.pages[indices].value()
                        arm_pointer = indices

                #something was found
                if(arm_pointer != None):
                    self.point_at(arm_pointer)
                    self.replace_page(page)
                    return

    def handle_no_operation(self, page):
        """Handles the incoming page without regards to operations."""
        page_hit, index = self.address_in_space(page)

        if(page_hit):
            self.pages[index].rereference()
            self.pages[index].assign_value(self.virtual_clock)

        elif(not self.full()):
            #adds the page
            self.pages.append(page)
            #assigns the page the current time
            self.pages[self.clock_arm].assign_value(self.virtual_clock)
            #moves to the next page
            self.update_arm()
            #updates faults
            self.faults += 1

        else:
            self.faults += 1

            #candidates of indices in case nothing is found
            #class 0: not referenced and not modifed
            #class 1: not referenced and modified
            #class 2: referenced and not modified
            #class 3: referenced and modified
            candidates = [[] for i in range(4)]

            #for traversing the clock_arm
            once = 1
            current_arm = self.clock_arm
            while(once):
                if(self.page_arm().referenced() and self.page_arm().modified()):
                    self.page_arm().dereference()
                    candidates[3].append(self.clock_arm)

                elif(self.page_arm().referenced()):
                    self.page_arm().dereference()
                    candidates[2].append(self.clock_arm)

                elif(self.page_arm().modified()):
                    candidates[1].append(self.clock_arm)

                #Here it looks for the age of the page since it's not referenced
                #and not modified. if it's older than tau then it is removed.
                elif(self.page_age() > self.tau):
                    self.replace_page(page)
                    return

                else:
                    candidates[0].append(self.clock_arm)

                self.update_arm()
                self.update_clock()

                if(current_arm == self.clock_arm):
                    once = 0

            #the loop in case nothing was found
            for classes in candidates:
                oldest = float("inf")
                arm_pointer = None
                for indices in classes:
                    #the smallest value means it's the oldest
                    if(self.pages[indices].value() < oldest):
                        oldest = self.pages[indices].value()
                        arm_pointer = indices

                #something was found
                if(arm_pointer != None):
                    self.point_at(arm_pointer)
                    self.replace_page(page)
                    return

def wsclock(page_amount, tau, filename):
    physical_memory = PM_wsclock(page_amount, tau)

    rfile = open(filename, "r")
    data = rfile.read()
    rfile.close()
    pages = data.split(" ")

    for p in pages:
        page_values = p.split(":")
        if(len(page_values) == 1):
            current_page = WS_Page(page_values)

        else:
            #in case it's of the form operation:address
            current_page = WS_Page(page_values[1], page_values[0])

        physical_memory.update_with_page(current_page)
        #print current_page.address(),
        #physical_memory.print_pages() #for debbugging

    print physical_memory.page_faults()

if __name__ == '__main__':
    if(len(argv) < 4):
        print "python wsclock.py <Number of physical memory pages>",
        print "<tau> <access sequence file>"

    else:
        wsclock(int(argv[1]), int(argv[2]), argv[3])
