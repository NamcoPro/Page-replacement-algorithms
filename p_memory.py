class Page:
    def __init__(self, value, operation = None):
        """Value will be the page adress abstracted to a number.
        Operation will be handled with a 'w' for write, 'r' for read.
        Ref serves as the referenced bit."""
        self.value = value
        self.operation = operation
        self.ref = 1

    def referenced(self):
        return self.ref

    def dereference(self):
        """For the case of algorithms requiring deferencing of pages"""
        self.ref = 0

    def rereference(self):
        self.ref = 1

    def wants_write(self):
        return (self.operation == "w")

    def wants_read(self):
        return (self.operation == "r")

    def address(self):
        return self.value

class Physical_Memory:
    """Mimics a physical address space of pages."""
    def __init__(self, size = 0):
        self.size = size    #size of the address space
        self.pages = []     #list container for the page objects
        self.faults = 0     #number of page faults

    def full(self):
        return (len(self.pages) == self.size)

    def page_faults(self):
        return self.faults

    def address_in_space(self, page):
        """Linear search for finding a page address."""
        for i in range(len(self.pages)):
            if(self.pages[i].address() == page.address()):
                return (True, i)

        return (False, None)

    def print_pages(self):
        for page in self.pages:
            print page.address(),

        print
