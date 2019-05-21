class Image:
    def __init__(self):
        self.file_name = ""
        self.caption_link = ""
        self.transcription = ""
        self.page_source = ""
        self.upload_date = ""
        self.image_resized_resolution = [0, 0]
        # self.image_count = 0
        # self.image_dict = {}

    # def populate(self):
    #     """
    #     This function populates the internal dictionary for storing all images, with the current info stored in the
    #     self variables
    #     :return: none
    #     """
    #     self.image_dict[self.file_name] = {"Filename": self.file_name,
    #                                        "Caption Link": self.caption_link,
    #                                        "Transcription": self.transcription,
    #                                        "Page Source": self.page_source}
    #     self.image_count += 1
    #     self.file_name = ""
    #     self.caption_link = ""
    #     self.transcription = ""
    #     self.page_source = ""

    def list_images(self):
        """
        This is to list out all of the information for this image
        :return: None
        """
        print("Filename: " + self.file_name)
        print("Transcription: " + self.transcription)
        print("Upload Date: " + self.upload_date)
        print("Resolution: " + self.image_resized_resolution[0] + "x" + self.image_resized_resolution[1])

