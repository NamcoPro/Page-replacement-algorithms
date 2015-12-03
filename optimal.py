from sys import argv
from p_memory import Physical_Memory, Page

class PM_Optimal(Physical_Memory):
    """An optimal page replacement algorithm class.
    It considers all the new pages at once and makes decisions on how
    far the next page will be."""
    def __init__(self, size = 0):
        Physical_Memory.__init__(self, size)
        self.pages_left = []

    def buffer_pages(self, filename):
        """loads all the pages from the filename into self.pages_left.
        Assigns them a value to indicate their next appearance.
        float('inf') is used to indicate there is no other isntance of that
        particular address."""
        rfile = open(filename, "r")
        data = rfile.read()
        rfile.close()
        temp_pages = data.split(" ")

        #splitting the temp_pages because of the format
        for i in range(len(temp_pages)):
            temp_pages[i] = temp_pages[i].split(":")

        #operation format. Assumes they're of the form operation:address
        operation_for = 1
        if(len(temp_pages(0) == 1):
            operation_for = 0

        #assigning distances for each page
        for i in range(len(temp_pages)):
            #assumes an address will not be found again
            distance = float("inf")
            for j in range(i + 1, len(temp_pages)):
                if(operation_for):
                    #found the same address
                    if(temp_pages[i][1] == temp_pages[j][1]):
                        distance = j - i
                        break
                else:
                    #found the same address
                    if(temp_pages[i] == temp_pages[j]):
                        distance = j - i
                        break

            temp = None
            if(operation_for):
                temp = Page(temp_pages[1], distance, temp_pages[0])

            else:
                temp = Page(temp_pages[1], distance)

            #finally putting the pages in the buffer
            self.pages_left.append(temp)


    def run_optimal_replacement(self):
        """This runs the optimal replacement algorithm to the address space."""
        #look that goes through all of the pages
        for page in self.pages_left:
