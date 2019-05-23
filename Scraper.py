from bs4 import BeautifulSoup
from Image import Image
from Caption import Caption
import copy
import csv


def image_info(page_soup):
    images_dict = {}
    for image in page_soup.find_all('img'):
        temp = Image()

        # this is for pulling out the id that will be used for linking images and captions
        caption_link(image, temp)

        # this is to pull the filename out of the html
        image_file_path_info(image, temp)

        image_resolution(image, temp)

        # Using the temporary variable's information to copy over to a proper variable
        if temp.file_name != "cropped.jpg":
            images_dict[temp.file_name] = copy.copy(temp)
    return images_dict


def caption_link(tag, img):
    """
    This function takes a given attribute, checks to see if it is the attribute for linking images with captions, and
    then stores that information in the instance of the Images class
    :param tag: a string for an attribute of an html tag
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    img.caption_link = tag.get("aria-describedby")


def image_file_path_info(tag, img):
    """
    This function is for extracting the filename of an image from it's src filepath. In addition, we can extract the
    upload date
    :param tag: a string for an attribute of an html tag
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    file_path = tag.get("src")
    file_split = file_path.split("/")
    img.file_name = file_split[-1]
    year = file_split[-3]
    month = file_split[-2]
    img.upload_date = month + "/" + year
    img.file_name = file_split[-1]

    ext = img.file_name[-4:]  # Assuming the extension is 3 characters long save the last few characters
    if "." not in ext:  # If the "." is not in the extension, the extension is 4 characters long
        ext = img.file_name[-5:]

    hyphen_total = img.file_name.count("-")
    hyphen_count = 0
    final_file = ""
    for char in img.file_name:
        if char == "-":
            hyphen_count += 1
        if not hyphen_count == hyphen_total:
            final_file += char

    img.file_name = final_file + ext  # once the file name is obtained, append the file's extension


def image_resolution(tag, img):
    """
    Records the resolution of the image that's displayed
    :param tag: A Beautiful Soup Tag object
    :param img: An Image object
    :return:
    """
    img.image_resized_resolution[0] = tag.get("width")
    img.image_resized_resolution[1] = tag.get("height")


def find_captions(page_soup):
    """
    Finds all text that might be a caption (we don't know until we compare the id attribute with the images
    aria-describedby attribute)
    :param page_soup: Beautiful Soup object
    :return:
    """
    captions_dict = {}
    for caption in page_soup.find_all('dd'):
        temp = Caption()
        temp.image_link = caption.get('id')
        temp.caption = caption.string[5:-5]
        captions_dict[temp.image_link] = copy.copy(temp)
    for caption in page_soup.find_all('p'):
        temp = Caption()
        temp.image_link = caption.get('id')
        temp.caption = caption.string
        captions_dict[temp.image_link] = copy.copy(temp)
    return captions_dict


def image_caption_linking(captions_dict, images_dict):
    """
    Matches image objects with their captions
    :param captions_dict: Dictionary holding all captions from the page
    :param images_dict: Dictionary holding all images from the page
    :return:
    """
    for caption in captions_dict.keys():
        for image in images_dict.keys():
            if captions_dict[caption].image_link == images_dict[image].caption_link:
                images_dict[image].caption = captions_dict[caption].caption

                
def write_csv(dict_to_write, csv):
    """
    Uses the csv library to write .csv files containing the image's information
    :param dict_to_write:
    :return:
    """
    with open(csv, 'w') as csvfile:
        file_writer = csv.writer(csvfile)
        csv_data = [["Filename", "Transcription", "Upload Date", "Resolution"]]
        for image in dict_to_write.keys():
            csv_data.append([dict_to_write[image].file_name, dict_to_write[image].transcription,
                             dict_to_write[image].upload_date, dict_to_write[image].image_resized_resolution[0] + "x" +
                             dict_to_write[image].image_resized_resolution[1]])
        file_writer.writerows(csv_data)
        csvfile.close()


def bibliography_pairings(web_page):               #pairing the information together that is in each row of the bibliography table
    rows = web_page.tbody
    count_data = 0
    bibliography_dict = {}
    variable1 = ""                 #variables to store the informmation of the data in the rows
    variable2 = ""
    for row in rows.children:            #gets the child tag of table row
        if row != "\n":
            for table_data in row.children:     #gets the child tag of table data
                if table_data != "\n":
                    for p in table_data.children: #gets the information/tags in the tag p
                        if p != "\n":
                            if count_data == 0:
                                variable1 = p.string #if the count is 0 then retrieve the information and put it in variable 1
                                count_data += 1
                            elif count_data != 0: #if the count is not 0 then retrieve the information and put it in variable 2
                                variable2 = p.string
                                count_data += 1
        if count_data == 2:                     #if count is 2 then reset the count
            count_data = 0
            bibliography_dict[variable1] = variable2  #store variables into the dictionary with key and value
            variable1 = ""
            variable2 = ""
    print(bibliography_dict)

def main():
    # path = input("Please enter the file path to the directory where the html files are stored: ")

    path = "/home/schmidtt/PycharmProjects/PMSS_Scraper/html/"
    file = "EVELYN K. WELLS - PINE MOUNTAIN SETTLEMENT SCHOOL COLLECTIONS.html"
    f = open(path + file)
    web_page = BeautifulSoup(f, 'html.parser')
    pmss_images = image_info(web_page)
    captions = find_captions(web_page)
    image_caption_linking(captions, pmss_images)

    for image in pmss_images.keys():
        print(image + ": ")
        pmss_images[image].list_images()
        print()

    # write_csv(pmss_images)
    bibliography_pairings(web_page)
if __name__ == "__main__":
    main()
