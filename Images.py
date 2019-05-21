class Images:
    def __init__(self):
        self.file_name = ""
        self.caption_link = ""
        self.transcription = ""
        self.page_source = ""
        self.image_count = 0
        self.image_dict = {}

    def populate(self):
        """
        This function populates the internal dictionary for storing all images, with the current info stored in the
        self variables
        :return: none
        """
        self.image_dict[self.file_name] = {"Filename": self.file_name,
                                           "Caption Link": self.caption_link,
                                           "Transcription": self.transcription,
                                           "Page Source": self.page_source}
        self.image_count += 1
        self.file_name = ""
        self.caption_link = ""
        self.transcription = ""
        self.page_source = ""

    def list_images(self):
        """
        This is to list out all of the images currently in the image_dict variable
        :return: None
        """
        for image in self.image_dict.keys():
            to_print = image + ":\n"
            for info in self.image_dict[image].keys():
                to_print += info + ": " + self.image_dict[image][info] + "\n"
            print(to_print)
            print()
