class Image:
    def __init__(self):
        self.file_name = ""
        self.caption_link = ""
        self.transcription = ""
        self.page_source = ""
        self.upload_date = ""
        self.caption = ""
        self.image_resized_resolution = [0, 0]

    def strip_resolution(self):
        """
        Uses the resolution information to clean up the filename
        :param self: An Image object
        :return: None
        """
        resolution = str(self.image_resized_resolution[0]) + "x" + str(self.image_resized_resolution[1])

        if self.file_name.count(resolution) == 0:
            return
        else:
            final_file = ""
            ext = self.file_name[-4:]  # Assuming the extension is 3 characters long save the last few characters
            if "." not in ext:  # If the "." is not in the extension, the extension is 4 characters long
                ext = self.file_name[-5:]
            self.file_name = self.file_name[:-len(ext)]
            split_name = self.file_name.split("-")
            for piece in split_name:
                if piece != resolution:
                    final_file += piece
        self.file_name = final_file + ext

    def list_images(self):
        """
        This is to list out all of the information for this image
        :return: None
        """
        print("Filename: " + self.file_name)
        print("Transcription: " + self.transcription)
        print("Upload Date: " + self.upload_date)
        print("Resolution: " + str(self.image_resized_resolution[0]) + "x" + str(self.image_resized_resolution[1]))
        if self.caption != "":
            print("Caption: " + self.caption)


