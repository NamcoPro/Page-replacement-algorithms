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
        is for convenience.
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
        """Replaces a page when a page fualt is happening."""
        self.pages[self.clock_arm] = page
        self.pages[self.clock_arm].assign_value(self.virtual_clock)
        self.update_arm()


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
        address isn't on the physical space, then the page request is trashed
        since it's asking for a page address that doesn't exist."""
        page_hit, index = self.address_in_space(page)

        if(page_hit):
            self.pages[index].rereference()
            self.pages[index].assign_value(self.virtual_clock)

        else:
            #have to ask what to do when it asks to read a page not in
            #the physical memory
            #it can always replace another page, but then what's the deal
            #having a read and write operation?
            self.faults += 1

    def handle_write(self, page):
        """Handles the incoming page if it wants to write. If there's a hit,
        then the referenced page's modifed bit is actualized. If there's a
        fault, then the algorithm is applied. This is absolutely disgusting.
        You might as well not read this abomination of a function."""
        page_hit, index = self.address_in_space(page)

        if(page_hit):
            #page hit for the modified bit
            self.pages[index].modify()
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

            while(1):
                if(self.pages[self.clock_arm].referenced()):
                    self.pages[self.clock_arm].dereference()
                    self.pages[self.clock_arm].assign_value(self.virtual_clock)

                elif(self.pages[self.clock_arm].modified()):
                    pass


                self.update_arm()
                self.update_clock()


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

            #for the possible candidate
            arm_pointer = None
            oldest = -1

            #go through the entire list until it finds an appropiate page
            while(1):
                #the case where it's referenced
                if(self.pages[self.clock_arm].referenced()):
                    #page gets dereferenced and updated on its time
                    self.pages[self.clock_arm].dereference()
                    self.pages[self.clock_arm].assign_value(self.virtual_clock)

                #the case where it's unreferenced
                elif(self.page_age() > self.tau):
                    self.replace_page(page)
                    self.update_arm()
                    return

                else:
                    if(self.page_age() > oldest):
                        oldest = self.page_age()
                        arm_pointer = self.clock_arm

                self.update_arm()
                self.update_clock()

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
        print "python wsclock.py <Number of physical memory pages>,"
        print "<tau> <access sequence file>"

    else:
        wsclock(int(argv[1]), int(argv[2]), argv[3])
