from sys import argv
from p_memory import Physical_Memory, Page

class PM_2ndchance(Physical_Memory):
    """This particular kind of second chance doesn't mind the read and write
    operations. R:1 and W:1 will be treated the same."""

    def send_page_back(self, index, rereference):
        """The rereference parameter is intended for hits
        or dereferencing pages."""
        if(rereference):
            self.pages[index].rereference()

        else:
            self.pages[index].dereference()

        tmp_page = self.pages.pop(index)
        self.pages.append(tmp_page)

    def update_with_page(self, page):
        """Page handler. Puts pages on the space, dereferences them, and updates
        faults."""
        page_loaded, index = self.address_in_space(page)
        #the case where there is a page hit
        #the page is updated and sent into the back of the list
        if(page_loaded):
            self.send_page_back(index, 1)

        #the case where a page is added to the end of the list
        elif(not self.full()):
            self.pages.append(page)
            self.faults += 1

        #the address space is full and the address referenced isn't found
        else:
            #loop in search of an available space
            while(1):
                #referenced addresses are dereferenced and sent back
                if(self.pages[0].referenced()):
                    self.send_page_back(0, 0)

                #new page is sent to the back
                else:
                    self.pages.pop(0)
                    self.pages.append(page)
                    self.faults += 1
                    break

def second_chance(page_amount, filename):
    #making the address of size page_amount
    physical_memory = PM_2ndchance(page_amount)

    rfile = open(filename, "r")
    data = rfile.read()
    rfile.close()
    pages = data.split(" ")

    for p in pages:
        page_values = p.split(":")
        if(len(page_values) == 1):
            current_page = Page(page_values)

        else:
            #in case it's of the form operation:address
            current_page = Page(page_values[1], page_values[0])

        physical_memory.update_with_page(current_page)
        #physical_memory.print_pages() for debbugging

    print physical_memory.page_faults()

if (__name__ == "__main__"):
    if(len(argv) < 3):
        print "python second.py <Number of physical memory pages>",
        print "<access sequence file>"

    else:
        second_chance(int(argv[1]), argv[2])
