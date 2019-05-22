class Image:
    def __init__(self):
        self.file_name = ""
        self.caption_link = ""
        self.transcription = ""
        self.page_source = ""
        self.upload_date = ""
        self.caption = ""
        self.image_resized_resolution = [0, 0]

    def list_images(self):
        """
        This is to list out all of the information for this image
        :return: None
        """
        print("Filename: " + self.file_name)
        print("Transcription: " + self.transcription)
        print("Upload Date: " + self.upload_date)
        print("Resolution: " + str(self.image_resized_resolution[0]) + "x" + str(self.image_resized_resolution[1]))
        print("Caption: " + self.caption)


