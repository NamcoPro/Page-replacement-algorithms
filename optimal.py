from sys import argv
from p_memory import Physical_Memory, Page


class PM_Optimal(Physical_Memory):
    """An optimal page replacement algorithm class. The bloat is real.
    It considers all the new pages at once and makes decisions on how
    far the next page will be."""
    def __init__(self, size = 0):
        Physical_Memory.__init__(self, size)
        self.pages_left = []

    def buffer_pages(self, filename):
        """loads all the pages from the filename into self.pages_left."""
        rfile = open(filename, "r")
        data = rfile.read()
        rfile.close()
        temp_pages = data.split(" ")

        #splitting the temp_pages because of the format
        for i in range(len(temp_pages)):
            temp_pages[i] = temp_pages[i].split(":")

        #operation format. Assumes they're of the form operation:address
        operation_for = 1
        if(len(temp_pages[0]) == 1):
            operation_for = 0

        for i in range(len(temp_pages)):
            temp = None
            if(operation_for):
                temp = Page(temp_pages[i][1], 0, temp_pages[i][0])

            else:
                temp = Page(temp_pages[i][0])

            #finally putting the pages in the buffer
            self.pages_left.append(temp)

    def update_page_distances(self, index):
        """Uses the given index to update distances on the main physical
        address space."""
        for i in range(len(self.pages)):
            #assume that the address is never found
            distance = float("inf")
            for j in range(index, len(self.pages_left)):
                if(self.pages[i].address() == self.pages_left[j].address()):
                    distance = j
                    break

            self.pages[i].assign_value(distance)

    def max_distance_index(self):
        """searches the pages in the physical space to find a maximum distance.
        The index will be used to remove that page when there's a fault."""
        max_index = 0
        max_dist = 0
        for i in range(len(self.pages)):
            #doesn't get bigger than this
            if(self.pages[i].value() == float("inf")):
                return i

            if(max_dist < self.pages[i].value()):
                max_dist = self.pages[i].value()
                max_index = i

        return max_index

    def run_optimal_replacement(self):
        """This runs the optimal replacement algorithm to the address space."""
        #look that goes through all of the pages
        for i in range(len(self.pages_left)):
            page_hit, index = self.address_in_space(self.pages_left[i])

            #the case where there is a page hit, the loop continues
            if(page_hit):
                pass

            #the case where a page is added to the end of the list
            elif(not self.full()):
                self.pages.append(self.pages_left[i])
                self.faults += 1

            #the address space is full and the address referenced isn't found
            else:
                """Update the current pages, finds the one with the maximum
                distance, removes it, and finally inserts a new page."""
                self.update_page_distances(i)
                index = self.max_distance_index()
                self.pages.pop(index)
                self.pages.append(self.pages_left[i])
                self.faults += 1

            #self.print_pages() #for debugging

def optimal_algorithm(page_amount, filename):
    """Setup the page amount, load all the pages, and execute the algorithm."""
    physical_memory = PM_Optimal(page_amount)
    physical_memory.buffer_pages(filename)
    physical_memory.run_optimal_replacement()
    print physical_memory.page_faults()


if (__name__ == "__main__"):
    if(len(argv) < 3):
        print "python optimal.py <Number of physical memory pages>",
        print "<access sequence file>"

    else:
        optimal_algorithm(int(argv[1]), argv[2])
