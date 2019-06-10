class Page:
    def __init__(self):
        self.images = {}  # A dictionary to contain the images from the web page
        self.bibliography = {}  # A dictionary to contain information in the bibiliography
        self.html = ""

    def view_bibliography(self):
        if self.bibliography:
            for row_title in self.bibliography:
                print(f"{row_title}: {self.bibliography[row_title]}")


