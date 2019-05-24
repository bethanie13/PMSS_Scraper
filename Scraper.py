from bs4 import BeautifulSoup
from Image import Image
from Caption import Caption
from Transcription import Transcription
import copy
from Page import Page

import csv
from os import listdir
from os.path import isfile, join


def image_info(page_soup):
    """
    Finds all images on the page and collects as much information as it can
    :param page_soup: A Beautiful Soup object
    :return: A dictionary containing all of the images from the page
    """
    images_dict = {}
    for image in page_soup.find_all('img'):
        temp = Image()

        # Pull out the id that will be used to find this image's caption
        caption_link(image, temp)

        # Pull the filename and upload date for this image
        image_file_path_info(image, temp)

        # Record the resolution information for this image
        image_resolution(image, temp)

        # If resolution information is in the filename, strip that information out
        temp.strip_resolution()

        if temp.file_name != "cropped-pmss_spelman_pntg_edited_2_brightened_x.jpg":  # Ignore the header image
            images_dict[temp.file_name] = copy.copy(temp)  # Copy the image to a dictionary
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


def image_resolution(tag, img):
    """
    Records the resolution of the image that's displayed
    :param tag: A Beautiful Soup Tag object
    :param img: An Image object
    :return: None
    """
    img.image_resized_resolution[0] = tag.get("width")
    img.image_resized_resolution[1] = tag.get("height")


def find_captions(page_soup):
    """
    Finds all text that might be a caption (we don't know until we compare the id attribute with the images
    aria-describedby attribute)
    :param page_soup: Beautiful Soup object
    :return: None
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
    :return: None
    """
    for caption in captions_dict.keys():
        for image in images_dict.keys():
            if captions_dict[caption].image_link == images_dict[image].caption_link:
                images_dict[image].caption = captions_dict[caption].caption


def find_transcriptions(page_soup):
    """""
    Finds all the text that could possibly be a transcription
    :param page_soup: Beautiful Soup object
    :return: None
    """
    content = ""
    transcriptions_dict = {}               #dictionary to store transcriptions
    row_transcript = page_soup.find_all("div")    #finds all the tags that hold div
    tag = ''
    for div in row_transcript:
        if div.get("class"):
            if div.get("class")[0] == "entry-content": #content will hold the correct tag
                content = div
    for tag in content.children:   #trying to reach the lowest level of the tag looks from children of current tag
        if tag.name == "p":
            temp_tag = copy.copy(tag)           #we want information stored in p tag
            if tag.string:
                lowest_level = True
            else:
                lowest_level = False
            while lowest_level != True:
                temp_tag = temp_tag.contents[0]
                if tag.string:
                    lowest_level = True
                else:
                    lowest_level = False


            tag.string
            temp = Transcription()
            temp.transcript_link = tag.get_text()
            transcriptions_dict[] = temp.transcript_link
        print(page_soup.p)
        print(row_transcript.find_all("transcription"))
            # for transcribe in page_soup.find_all("jpg")
        print(transcriptions_dict)

# def image_transcription_linking(transcriptions_dict,ima )


def bibliography_pairings(page_soup):
    rows = page_soup.tbody
    count_data = 0
    bibliography_dict = {}
    variable1 = ""                 #variables to store the informmation of the data in the rows
    variable2 = ""
    if rows:

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


def main():
    # path = input("Please enter the file path to the directory where the html files are stored: ")
    path = "/Users/bereacollege/Documents/internship/PMSS_Scraper/html/"
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    pmss_images = {}
    pmss_pages = []
    for file in onlyfiles:
        if file != ".DS_Store":
            current_page = Page()
            f = open(path + file)
            web_page = BeautifulSoup(f, 'html.parser')
            pmss_images[file] = image_info(web_page)
            captions = find_captions(web_page)
            image_caption_linking(captions, pmss_images[file])
            current_page.images = pmss_images
            # current_page.bibliography = bibliography_pairings(web_page)
            current_page.html = file
            pmss_pages.append(copy.copy(current_page))
            find_transcriptions(web_page)
    # for file in onlyfiles:
    #     if file != ".DS_Store":
    #         for image in pmss_images[file].keys():
    #             # print(image + ": ")
    #             # pmss_images[file][image].list_images()
    #             print(pmss_images[file][image])
    #
    # # write_csv(pmss_images)
    # bibliography_pairings(web_page)





if __name__ == "__main__":
    main()
