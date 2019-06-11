from bs4 import BeautifulSoup
from PMSS_Image import PMSS_Image
from Caption import Caption
import copy
import csv
from os import listdir
from os.path import isfile, join
from Page import Page
import numpy as np
import requests
import os
import sys
from PIL import Image, ExifTags
from PIL.TiffTags import TAGS
import time
import bs4


def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """
    Levenshtein_ratio_and_distance:
    Calculates levenshtein distance between two strings.
    If ratio_calc = True, the function computes the
    Levenshtein distance ratio of similarity between two strings
    For all i and j, distance[i,j] will contain the Levenshtein
    distance between the first i characters of s and the
    first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows, cols), dtype=int)
    row = 0
    col = 0

    if s == "" or t == "":
        return 0

    # Populate matrix of zeros with the indices of each character of both strings
    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0  # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                     distance[row][col-1] + 1,          # Cost of insertions
                                     distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc:
        # Computation of the Levenshtein Distance Ratio
        ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])


def image_info(page_soup):
    """
    Finds all images on the page and collects as much information as it can
    :param page_soup: A Beautiful Soup object
    :return: A dictionary containing all of the images from the page
    """
    images_dict = {}            # create a dictionary for the images
    for image in page_soup.find_all('img'):  # for an image it will find all of the img tags within the html of the page
        if image.get("src"):
            img_src = image.get("src")
            temp = PMSS_Image()

            # Pull out the id that will be used to find this image's caption
            caption_link(image, temp)

            # Pull the filename and upload date for this image
            image_file_path_info(image, temp)

            # Record the resolution information for this image
            image_resolution(image, temp)

            # If resolution information is in the filename, strip that information out
            temp.strip_resolution()

            if image.parent.name == "figure":
                for tag in image.parent.children:
                    if tag.name == "figcaption":
                        temp.caption = tag.string

            if temp.file_name != "cropped-pmss_spelman_pntg_edited_2_brightened_x.jpg":  # Ignore the header image
                # Copy the image to a dictionary
                images_dict[temp.file_name[:-len(temp.file_name.split(".")[-1]) - 1].lower()] = copy.copy(temp)
    return images_dict


def caption_link(tag, img):
    """
    This function takes a given attribute, checks to see if it is the attribute for linking images with captions, and
    then stores that information in the instance of the Images class
    :param tag: a string for an attribute of an html tag
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    if tag.get("aria-describedby"):
        img.caption_link = tag.get("aria-describedby")  # retrieves the link of the caption by looking for the key word of
    # aria-describedby and gets the tag from it


def image_file_path_info(tag, img):
    """
    This function is for extracting the filename of an image from it's src filepath. In addition, we can extract the
    upload date
    :param tag: a string for an attribute of an html tag
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    file_path = tag.get("src")      # looks for the tag of src within its file path
    file_split = file_path.split("/")   # splits the file path when it encounters a /
    img.file_name = file_split[-1]      # retrieves the file name once the file has been split
    year = file_split[-3]               # retrieves the year the image was uploaded from the file name
    month = file_split[-2]              # retrieves the month the image was uploaded from the file name
    img.upload_date = month + "/" + year  # uploads the date of the image based on month and year


def image_resolution(tag, img):
    """
    Records the resolution of the image that's displayed
    :param tag: A Beautiful Soup Tag object
    :param img: An Image object
    :return: None
    """
    img.image_resized_resolution[0] = tag.get("width")  # outputs the width resolution of the image
    img.image_resized_resolution[1] = tag.get("height")  # outputs the height resolution of the image


def find_captions(page_soup):
    """
    Finds all text that might be a caption (we don't know until we compare the id attribute with the images
    aria-describedby attribute)
    :param page_soup: Beautiful Soup object
    :return: captions_dict
    """
    captions_dict = {}                            # a dictionary to store all of the captions
    for caption in page_soup.find_all('dd'):     # for every caption look for the tag "dd"
        temp = Caption()                       # temporarily stores a caption for class constructor
        temp.image_link = caption.get('id')     # retrieves the caption through the tag of "id" which will be image link
        temp.caption = caption.string[5:-5]
        captions_dict[temp.image_link] = copy.copy(temp)   # makes a shallow copy of the image link stored in the dictionary
    for caption in page_soup.find_all('p'):         # for every caption find the "p" tags
        temp = Caption()                      # temporarily stores a caption for class constructor
        temp.image_link = caption.get('id')    # retrieves the caption through the tag of "id" which will be image link
        temp.caption = caption.string           # converts caption to a string
        captions_dict[temp.image_link] = copy.copy(temp)  # makes a shallow copy of the image link stored in the dictionary

    return captions_dict                        # return the dicitonary


def image_caption_linking(captions_dict, images_dict):
    """
    Matches image objects with their captions
    :param captions_dict: Dictionary holding all captions from the page
    :param images_dict: Dictionary holding all images from the page
    :return: None
    """
    for caption in captions_dict.keys():  # for every caption of an image in the caption dictionary
        for image in images_dict.keys():  # for every image in the image dictionary
            if images_dict[image].caption_link:
                if not images_dict[image].caption:
                    if captions_dict[caption].image_link == images_dict[
                            image].caption_link:  # if the caption dictionary matches the image dictionary
                        images_dict[image].caption = captions_dict[caption].caption  # then the image will go with the caption


def find_transcriptions(page_soup, img_dict):
    """""
    Finds all the text that could possibly be a transcription
    :param page_soup: Beautiful Soup object
    :param img_dict: Dictionary for the images
    :return: None
    """
    content = ""  # This will contain the html from the div tag where class == page-content
    all_divs = page_soup.find_all("div")  # finds all the tags that hold div
    article_tags = page_soup.find_all("article")
    header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]  # these are the only tags we are concerned about
    recording = False  # Boolean for checking if we are in transcript
    current_file = ""  # The image we are associating our transcript with
    image_index = 0  # The index of the file we are looking at
    for article in article_tags:
        if article.get("class"):
            if "category-cabbage_main" in article["class"]:
                return
    for div in all_divs:  # look specifically for the div that contains
        if div.get("class"):  # the entry-content because this will hold our transcripts
            if div.get("class")[0] == "entry-content":  # content will hold the correct tag
                content = div
                break

    for tag in content.children:  # trying to reach the lowest level of the tag looks from children of current tag
        # if tag.name == "hr":   # tag found at end of page; stops recording
        #     recording = False
        if tag == "\n":  # new line character used to find where spaces should be added within text
            if recording and current_file != "":
                if len(img_dict[current_file].transcription) != 0:
                    if img_dict[current_file].transcription[-1] == " ":
                        img_dict[current_file].transcription += "\n"
                    else:
                        img_dict[current_file].transcription += " "  # associate image with the transcript

        if tag.name in header_tags or tag.name == "p":  # looks for only the tags stored in the variable of wanted tags
            if tag.name == "p":  # looks for appropriate tag name by finding the p tag
                if tag.string:
                    if "2" in tag.string:  # If we find a place where there is a number 2
                        if 0 < len(tag.string) <= 3:  # If that number 2 is the only thing in the tag
                            current_tag = tag.previous_sibling  # move to the previous sibling (the text above our current text)
                            transcript = ""
                            while current_tag.name not in header_tags:  # keep moving up until we reach a header tag
                                if current_tag.name != "div":  # If it's not related to an image
                                    transcript = get_tags_text(
                                        current_tag) + transcript  # recursive call for getting all of the text
                                current_tag = current_tag.previous_sibling  # after getting the text for the tag, move back one sibling
                            recording = True  # We assume if we encounter just a number, it is a page number for a transcription
                    if 3 < len(tag.string) <= 8:  # If the text length is between 3 and 8 it is likely to be "page ##"
                        page_source = ""  # This will hold the "page ##" that the transcript comes from since we don't
                        # have an associated image
                        for word in tag.string.split():  # split the string that is in the tag into different words
                            if word.lower() == "page":  # looking for the word page in order to find where the transcript is seperated
                                page_source += word  # add the word "page" to the page source
                            else:  # if our word is anything other than "page"
                                try:
                                    int(word)  # Is this an integer? (e.g. 1, 2, 3, 4 etc.)
                                    page_source += word  # if int(word) doesn't cause a ValueError, we know it is an integer
                                except ValueError:  # If it is not "page" or a number we don't want to add it
                                    pass
                        if len(page_source) >= 5:  # if the length of the page source is > 2
                            img_dict[
                                page_source] = PMSS_Image()  # Create a new object with page_source as a key
                            current_file = page_source  # Set the current_file as page_source (so we store the transcript in the right place)
                            recording = True  # Turn recording on as we are looking at a page's transcription
            for main_tags_child in tag.children:
                if main_tags_child.string:
                    if "transcription" in \
                            main_tags_child.string.lower():  # for each tag we look for the string called transcription
                        recording = True

                    elif ".jpg" in main_tags_child.string:
                        if recording:
                            split_name = main_tags_child.string.split(
                                "[")  # if .jpg found then we will then extract file name
                            current_file = split_name[-1][:-6]
                            image_index += 1
                            if current_file not in img_dict:
                                img_dict[current_file] = PMSS_Image()  # if the current file is not in the image dictionary
                                img_dict[
                                    current_file].file_name = "Outlier"  # we need to store the image into the dictionary and note that is an outlier

                    elif "[" in main_tags_child.string:  # If we find a bracket, check if it is a filename
                        # a list of keys in our image dictionary
                        keys = list(img_dict)
                        # We assume what we are looking at is a transcript unless we change the filename
                        part_of_transcription = True
                        for section in main_tags_child.string.split("["):  # split the text by the open bracket
                            # split the text by the closed bracket so all that's left is just the text
                            for subsection in section.split("]"):
                                if len(keys) != 0 and image_index > len(keys):  # If we have keys in our dictionary
                                    # if our comparison text is at least80% similar to our key,
                                    # assume they are the same
                                    print(subsection.lower())
                                    print(keys[image_index])
                                    if levenshtein_ratio_and_distance(subsection.lower(), keys[image_index],
                                                                      True) >= .80:
                                        current_file = keys[image_index]  # update the current file
                                        image_index += 1  # increase the image index
                                        part_of_transcription = False  # since we determined it is a file name, this is now False
                        if part_of_transcription:  # If the text was deemed to not be a file
                            record_transcript(img_dict, recording, current_file, main_tags_child)  # record the text

                    elif main_tags_child.name == "span" or \
                            main_tags_child.name == "p":  # looks for tags that likely contain a transcript
                        record_transcript(img_dict, recording, current_file, main_tags_child)
                    elif main_tags_child.name == "div":  # we do not care about other div tags
                        pass

                    elif main_tags_child.parent.name == "p" and main_tags_child.name != "div":  # if the tags parent is the p tag and the child is not in the div tag
                        record_transcript(img_dict, recording, current_file,
                                          main_tags_child)  # we record the transcription into the dictionary

                    else:  # if we reach any other tag
                        if main_tags_child.previous_sibling:  # if the child of the main tag is in the previous level
                            previous_tag = main_tags_child.previous_sibling.name  # make the previous tag the previous level of the main tags child which is in the same level
                        else:
                            previous_tag = None  # if not there is no previous tag
                        if main_tags_child.next_sibling:  # if the child of the main tag is in the next level
                            next_tag = main_tags_child.next_sibling.name  # make the next tag the next level of the main tags child which is in the same level
                        else:
                            next_tag = None  # if not there is no next tag
                        if previous_tag == "span" or \
                                next_tag == "span":  # if the tag is near a span tag we save that text
                            record_transcript(img_dict, recording, current_file, main_tags_child)

                else:
                    for grandchild in main_tags_child.children:  # in the lowest level tag record the text
                        record_transcript(img_dict, recording, current_file,
                                          grandchild)  # record the text(transcript) using record_transcript function


def get_tags_text(tag):
    """
    Recursive function for traveling down a tag and all of it's descendents to extract all of the text
    :param tag: Beautiful Soup object that we will be extracting all of the text from
    :return base case: Return the string of current tag
    :return for the function: Return the full transcript
    """
    if tag.string:  # if we are at the last descendent (the text)
        return tag.string  # return the string
    transcript = ""  # a variable to build wthe full text into
    for child in tag.children:  # for each of the current tag's children
        transcript = transcript + get_tags_text(child)  # recursive function call to build the transcript
    return transcript  # return the full text


def record_transcript(img_dict, recording_state, current_file, tag):
    """
    Records the transcription and puts it into the dictionary with the image
    :param img_dict: Dictionary containing images for a page
    :param recording_state: boolean for if we are recording a transcript or not
    :param current_file: Holds a string for transcription to ensure it goes to correct position in dictionary
    :param tag: Beautiful Soup Object
    :return: None
    """
    # if the recording state and current file are not empty
    if recording_state and current_file != "" and tag.name != "div":  # and the tag name is not div
        img_dict[current_file].transcription += str(tag.string)  # associate image with the transcript


def write_csv(page_list):
    """
    Uses the csv library to write .csv files containing the image's information
    :param page_list: A list of pages that will have their contents output
    :return:
    """
    to_csv = input("Do you want to create csv files? (y/n): ")  # input check for if the user wants to output csv files
    csv_path = os.getcwd() + "/csv/"  # using the os module, the current directory plus /csv/ is where they will be stored
    try:  # try to go into the csv directory
        os.chdir(csv_path)
    except FileNotFoundError:  # if the csv directory doesnt exist
        os.mkdir(csv_path)  # make the csv directory
        os.chdir(csv_path)  # change to the csv directory
    if to_csv.lower() == "y":  # if the user responded yes
        for page in page_list:  # for each page in our list of page objects
            write_page = input(f"Do you want to output {page.html}? (y/n): ")  # Ask the user if they want to output the page
            if write_page.lower() == "y":  # if the user said yes to output the page
                ext_len = len(page.html.split(".")[-1])  # get the length of the extension
                csv_name = page.html[:-ext_len - 1] + ".csv"  # remove the current extension and add .csv to the end

                with open(csv_name, 'w') as csvfile:  # open csv file for the page we are currently on
                    file_writer = csv.writer(csvfile)  # store the writer for the csv file to a variable
                    csv_data = [["Filename", "Transcription", "Upload Date"]]  # the first row are the column headings
                    for image in page.images.keys():  # for each image in our images dictionary
                        csv_data.append([page.images[image].file_name, "\"" + page.images[image].transcription + "\"",
                                         page.images[image].upload_date])  # append the file name, transcription, and upload date
                    file_writer.writerows(csv_data)  # write the information to the file
                    csvfile.close()  # close the file


def bibliography_pairings(page_soup):
    """
    Pairs the information in the table of the bibliography together with the appropriate data.
    :param page_soup: Beautiful Soup Object
    :return: A dictionary containing all of the bibliography pairings
    """
    rows = page_soup.find_all("tbody")  # the rows of the table will be within the tbody of the html
    if rows:
        rows = rows[-1]

    count_data = 0  # used to store data in twos (count data will increment to 2 and then reset to 0 when data is saved
    bibliography_dict = {}
    table_row_titles = ["title", "alt. title", "identifier", "creator", "alt. creator", "subject keyword",
                        "subject lcsh", "date digital", "date original", "date",
                        "publisher", "contributor", "type", "format", "source", "language", "relation",
                        "coverage temporal", "coverage spatial", "rights", "donor", "description", "acquisition",
                        "citation", "processed by", "last updated", "bibliography"]
    title = ""  # variables to store the information of the data in the rows
    info = ""
    count_key = 0
    row_title_list = []
    row_info_list = []
    if rows:
        for row in rows.children:  # gets the child tag of table row
            if row != "\n":
                for table_data in row.children:  # gets the child tag of table data
                    if table_data != "\n":
                        if count_data == 0:
                            bibliography_text_retrieval(table_data, row_title_list)

                        if count_data != 0:
                            bibliography_text_retrieval(table_data, row_info_list)

                        # get_tags_text(table_data)
                        # if len(table_data.contents) != 0:
                        #     for p in table_data.children:  # gets the information/tags in the tag p
                        #         if p != "\n":
                        #             # store the information two at a time
                        #             if count_data == 0:
                        #                 title = p.string  # if the count is 0 then put the information in variable 1
                        #                 count_data += 1
                        #             elif count_data != 0:  # if the count is not 0 then put the information in variable 2
                        #                 info = p.string
                        #                 count_data += 1
                        # if table_data.children > 1:
                        #     for index in bibliography_dict:
                        #         if len(bibliography_dict) % 2 == 0:

                        # else:
                        #     if table_data.string != "\n":
                        #         # store the information two at a time
                        #         if count_data == 0:
                        #             if not table_data.string:
                        #                 title = "None"
                        #                 count_data += 1
                        #             else:
                        #                 title = table_data.string  # if the count is 0 then put the information in variable 1
                        #                 count_data += 1
                        #         elif count_data != 0:  # if the count is not 0 then put the information in variable 2
                        #             if not table_data.string:
                        #                 info = "None"
                        #                 count_data += 1
                        #             else:
                        #                 info = table_data.string
                        #                 count_data += 1
                        count_data += 1
            if count_data > 1:  # if count is 2 then reset the count
                count_data = 0
                if len(row_title_list) == len(row_info_list):
                    for i in range(len(row_title_list)):
                        if row_title_list[i].lower() not in table_row_titles:
                            # bibliography_dict = {}
                            return bibliography_dict, True
                        bibliography_dict[row_title_list[i]] = row_info_list[i]
                        count_key += 1
                    row_title_list = []
                    row_info_list = []
                else:
                    full_title = ""
                    full_info = ""
                    for title in row_title_list:
                        full_title += title
                    for info in row_info_list:
                        full_info += info
                    if full_title.lower() not in table_row_titles:
                        # bibliography_dict = {}
                        return bibliography_dict, True
                    bibliography_dict[full_title] = full_info
                    count_key += 1
                    row_title_list = []
                    row_info_list = []
                # if title == None:
                #     return bibliography_dict, False
                # if title.lower() not in table_row_titles:
                #     return bibliography_dict, False
                # bibliography_dict[title] = info  # store variables into the dictionary with key and value
                # count_key += 1
                # title = ""
                # info = ""
    if 5 <= count_key <= len(table_row_titles)-5:
        return bibliography_dict, True
    else:
        return bibliography_dict, False


def bibliography_text_retrieval(tag, column_list):

    if tag.string:  # if we are at the last descendant (the text
        text = ""
        if "\n" in tag.string:
            for piece in tag.string.split("\n"):
                if piece != "":
                    text += piece + " "
        else:
            text = tag.string
        if isinstance(text, bs4.element.NavigableString):
            column_list.append(text)  #
        return
    for child in tag.children:  # for each of the current tag's children
        bibliography_text_retrieval(child, column_list)  # recursive function call to build the transcript
    return   # return the full text


def check_if_guide(page_soup, page):
    header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
    entry_title = ""
    for header in header_tags:
        entry_title = page_soup.find_all(header, attrs={"class": "entry-title"})
    if entry_title:
        if "GUIDE" in entry_title:
            page.is_guide = True


def dir_dive():
    """
    A function to find all the names of .tif's and .jpg's
    :return: A list of names of files
    """
    os.chdir("/Volumes/Elements/PMSS_ARCHIVE")
    tifs = []
    img_count = 0
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            if name[-4:] == ".tif" or name[-4:] == ".jpg":
                tifs.append(name[:-4])
                img_count += 1
    print(img_count)
    return tifs


def compare_page_to_hdd(pages, tif_list):
    """
    WIP
    :param pages:
    :param tif_list:
    :return:
    """
    for page in pages:
        for image in page.images.keys():
            if image in tif_list:
                print("{} from {}: True".format(image, page.html))
            else:
                print("{} from {}: False".format(image, page.html))


def extract_image_info():
    """
    WIP
    :return:
    """
    img = Image.open("/Volumes/Elements/PMSS_ARCHIVE/series_05_governance/BOARD_PHOTOS/DSCF0014.jpg")
    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
    print(exif)
    img = Image.open("/Volumes/Elements/PMSS_ARCHIVE/series_13_education/education_series_13/jpg_educat_series_13/1940s_unknown_ed_obligation_015.jpg")
    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
    print(exif)
    img = Image.open("/Volumes/Elements/PMSS_ARCHIVE/series_05_governance/BOARD_REPORTS/1937-38_annual_board_report/jpg_1937_38_annual_board/1937-38_boar002.jpg")
    if img._getexif():
        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
        print(exif)

    with Image.open("/Volumes/Elements/PMSS_ARCHIVE/series_13_education/little_school/little_school_001.tif") as img:
        meta_dict = {TAGS[key]: img.tag[key] for key in img.tag.keys()}
        print(meta_dict)


def pages_info(text, url):
    """
    Driver function for getting information for a page.
    :param text: full html as plain text
    :param url: The url for the webpage
    :return: page object
    """
    current_page = Page()
    print(url)
    web_page = BeautifulSoup(text, 'html.parser')
    current_page.images = image_info(web_page)
    captions = find_captions(web_page)
    image_caption_linking(captions, current_page.images)
    # TODO: The following 3 lines are for getting bibliographies
    current_page.bibliography, partial_bib = bibliography_pairings(web_page)
    if partial_bib:
        print(f"Partial bibliography was found at: {url}")
        # input()
    current_page.html = url
    check_if_guide(web_page, current_page)
    # TODO: This is for getting transcriptions
    # find_transcriptions(web_page, current_page.images)
    # TODO: Print out all the information gathered from the page
    show_results(current_page)
    return current_page


def show_results(page):
    """
    Shows the list of pages that we visit
    :param page_list: A list of all the web pages
    :return: None
    """
    print(page.html + "\n")
    page.view_bibliography()
    print()
    for image in page.images.keys():    # for an image in the pages return a list of keys from dictionary
        print(image)
        print(page.images[image])


def web(links_visited, web_url, pages_list):
    """
    Web Crawler that will scan through the pmss webepage and find all different links from various pages
    :param links_visited: A list that will store all of the links visited through the crawler
    :param web_url: The Urls that will be visited
    :return: None
    """
    split_link = web_url.split(".")  # splits the link on a period to get domain
    if len(split_link) > 1:       # base case to ensure that there is a link
        domain = split_link[0] + split_link[1]  # stores the domain
    else:
        return
    ext = ["jpg", "png", "tif"]
    if domain != "https://pmsswpengine":   # base case we always need this url for our domain
        return                          # it will only scrape data within the domain of pmss
    if web_url in links_visited:  # base case if we have already visited the link we do not want to re-visit it over
        return
    # TODO: If you want to change the number of pages to crawl through, change the number below
    if len(links_visited) > 500:  # restriction for the amount of pages we want to search (temporary)
        return
    if web_url.split(".")[-1] in ext:  # split url if the end of url is in ext just return
        return
    links_visited.append(web_url)   # append the urls that we visit to a list of links visited
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}   # the User-Agent header makes our code not look like a bot
    result = requests.get(web_url, headers=headers)
    plain = result.text  # raw html

    pages_list.append(pages_info(plain, web_url))  # append the page to a list after getting info for it
    page_soup = BeautifulSoup(plain, "html.parser")  # beautiful soup object; parses the html
    for link in page_soup.findAll('a'):  # finds all a tags within html
        if not link.get("class"):    # avoid the html tag with class
            if len(links_visited) > 500:
                return
            # title_link = link.get('title')  # gets the title of the link
            # print(title_link)
            if link.contents:
                if link.contents[0].name != "img":
                    if link.parent:
                        try:
                            if link.parent.get("class")[0] == "must-log-in":
                                return
                        except TypeError:
                            pass
                    links_destination = link.get('href')  # gets the href and this determines the links destination
                    # print(links_destination)
                    web(links_visited, links_destination, pages_list)  # recursive call to keep calling the different links


def create_master_list(pages_list):
    """
    Combine all of the images and bibliographies into one structure respectively
    :param pages_list: A list of pages
    :return: A complete list of all the bibliographies and all of the images
    """
    list_of_images = {}
    list_of_bibs = []

    for page in pages_list:
        for image in page.images.keys():
            try:
                if list_of_images[image]:
                    list_of_images[image].alt_captions.append(list_of_images[image].caption)
            except KeyError:
                list_of_images[image] = page.images[image]
            # list_of_images[image] = page.images[image]
        if page.bibliography:
            list_of_bibs.append(page.bibliography)
    return list_of_bibs, list_of_images


start_time = time.time()


def main():
    # TODO: uncomment the following 5 lines to run for a specific page
    # path = os.getcwd() + "/html/"  # TODO: make html folder in same directory if it doesn't exist
    # file = "CONIFER INDEX - PINE MOUNTAIN SETTLEMENT SCHOOL COLLECTIONS.htm" # TODO: put filename here
    # f = open(path + file)
    # pmss_pages = pages_info(f, file)
    # show_results(pmss_pages)
    #  write_csv(pmss_pages)
    pages_list = []
    links_visited = []  # list of links visited
    web(links_visited, 'https://pmss.wpengine.com/', pages_list)
    print(pages_list)
    bib_master_list, images_master_list = create_master_list(pages_list)
    for bib in bib_master_list:
        for row_title in bib.keys():
            print(f"{row_title}: {bib[row_title]}")
        print()
    for image in images_master_list:
        print("Image in Master List:")
        print(image)

    print(f"--- {time.time() - start_time} seconds ---")


if __name__ == "__main__":
    main()
