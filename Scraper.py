from bs4 import BeautifulSoup
from Images import Images


def caption_link(attribute, Images):
    """
    This function takes a given attribute, checks to see if it is the attribute for linking images with captions, and
    then stores that information in the instance of the Images class
    :param attribute: a string for an attribute of an html tag
    :param Images: an instance of the Images class for storing the given  information
    :return: None
    """
    if "aria-describedby" in attribute:
        Images.caption_link = attribute[18:-1]


def image_file_name(attribute, Images):
    """
    This function is for extracting the filename of an image from it's src filepath
    :param attribute: a string for an attribute of an html tag
    :param Images: an instance of the Images class for storing the given  information
    :return: None
    """
    if "src=" in attribute:
        ext = attribute[-5:-1]  # Assuming the extension is 3 characters long save the last few characters
        if "." not in ext:  # If the "." is not in the extension, the extension is 4 characters long
            ext = attribute[-6:-1]
        slash_total = attribute.count("/")
        slash_count = 0

        for char in attribute:

            if slash_total == slash_count:
                Images.file_name += char
            if char == "/":
                slash_count += 1
        hyphen_total = Images.file_name.count("-")
        hyphen_count = 0
        final_file = ""
        for char in Images.file_name:
            if char == "-":
                hyphen_count += 1
            if not hyphen_count == hyphen_total:
                final_file += char

        Images.file_name = final_file
        Images.file_name += ext  # once the file name is obtained, append the file's extension


def main():
    # path = input("Please enter the file path to the directory where the html files are stored: ")
    path = "/home/schmidtt/PycharmProjects/PMSS_Scraper/html/"
    f = open(path + "EVELYN K. WELLS - PINE MOUNTAIN SETTLEMENT SCHOOL COLLECTIONS.html")
    web_page = BeautifulSoup(f, 'html.parser')
    pmss_images = Images()
    for image in web_page.find_all('img'):
        for attribute in str(image).split():

            # this is for pulling out the id that will be used for linking images and captions
            caption_link(attribute, pmss_images)

            # this is to pull the filename out of the html
            image_file_name(attribute, pmss_images)

            # Using the temporary variable's information to copy over to a proper variable
        pmss_images.populate()
    pmss_images.list_images()


if __name__ == "__main__":
    main()
