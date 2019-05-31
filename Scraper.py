from bs4 import BeautifulSoup
from Image import Image
from Caption import Caption
import copy
import csv
from os import listdir
from os.path import isfile, join
from Page import Page
import numpy as np


def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """
    levenshtein_ratio_and_distance:
    Calculates levenshtein distance between two strings.
    If ratio_calc = True, the function computes the
    levenshtein distance ratio of similarity between two strings
    For all i and j, distance[i,j] will contain the Levenshtein
    distance between the first i characters of s and the
    first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)
    row = 0
    col = 0

    if s == "" or t == "":
        return 0

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
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
            # Copy the image to a dictionary
            images_dict[temp.file_name[:-len(temp.file_name.split(".")[-1])-1].lower()] = copy.copy(temp)
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


def find_transcriptions(page_soup, img_dict):
    """""
    Finds all the text that could possibly be a transcription
    :param page_soup: Beautiful Soup object
    :param img_dict: Dictionary for the images
    :return: None
    """
    content = ""
    row_transcript = page_soup.find_all("div")  # finds all the tags that hold div
    wanted_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6"]  # these are the only tags we are concerned about
    recording = False  # checks to see if we are in transcript
    current_file = ""
    image_index = 0
    for div in row_transcript:  # look specifically for the div that contains
        if div.get("class"):    # the entry-content because this will hold our transcripts
            if div.get("class")[0] == "entry-content":  # content will hold the correct tag
                content = div
                break

    for tag in content.children:  # trying to reach the lowest level of the tag looks from children of current tag
        if tag.name == "hr":   # tag found at end of page; stops recording
            recording = False
        if tag == "\n":      # new line character used to find where spaces should be added within text
            if recording and current_file != "":
                if len(img_dict[current_file].transcription) != 0:
                    if img_dict[current_file].transcription[-1] == " ":
                        img_dict[current_file].transcription += "\n"
                    else:
                        img_dict[current_file].transcription += " "  # associate image with the transcript
        if tag.name in wanted_tags:
            for main_tags_child in tag.children:
                if main_tags_child.string:
                    if "transcription" in \
                            main_tags_child.string.lower():   # for each tag we look for the string called transcription
                        recording = True

                    elif ".jpg" in main_tags_child.string:
                        split_name = main_tags_child.string.split("[")  # if .jpg found then we will then extract file name
                        current_file = split_name[-1][:-5]
                        image_index += 1

                    elif "[" in main_tags_child.string:  # If we find a bracket, check if it is a filename
                        # a list of keys in our image dictionary
                        keys = list(img_dict)
                        # We assume what we are looking at is a transcript unless we change the filename
                        part_of_transcription = True
                        for section in main_tags_child.string.split("["):  # split the text by the open bracket
                            # split the text by the closed bracket so all that's left is just the text
                            for subsection in section.split("]"):
                                if len(keys) != 0:  # If we have keys in our dictionary
                                    # if our comparison text is at least80% similar to our key,
                                    # assume they are the same
                                    if levenshtein_ratio_and_distance(subsection.lower(), keys[image_index], True) >= .80:
                                        current_file = keys[image_index]  # update the current file
                                        image_index += 1  # increase the image index
                                        part_of_transcription = False  # since we determined it isa file name, this is now False
                        if part_of_transcription:  # If the text was deemed to not be a file
                            record_transcript(img_dict, recording, current_file, main_tags_child)  # record the text

                    elif main_tags_child.name == "span" or \
                            main_tags_child.name == "p":  # looks for tags that likely contain a transcript
                        record_transcript(img_dict, recording, current_file, main_tags_child)
                    elif main_tags_child.name == "div":   # we do not care about other div tags
                        pass

                    elif main_tags_child.parent.name == "p" and main_tags_child.name != "div":
                        record_transcript(img_dict, recording, current_file, main_tags_child)

                    else:  # if we reach any other tag
                        if main_tags_child.previous_sibling:
                            previous_tag = main_tags_child.previous_sibling.name
                        else:
                            previous_tag = None
                        if main_tags_child.next_sibling:
                            next_tag = main_tags_child.next_sibling.name
                        else:
                            next_tag = None
                        if previous_tag == "span" or \
                                next_tag == "span":  # if the tag is near a span tag we save that text
                            record_transcript(img_dict, recording, current_file, main_tags_child)

                else:
                    for grandchild in main_tags_child.children:
                        record_transcript(img_dict, recording, current_file, grandchild)


def record_transcript(img_dict, recording_state, current_file, tag):
    if recording_state and current_file != "" and tag.name != "div":
        img_dict[current_file].transcription += str(
            tag.string)  # associate image with the transcript


def write_csv(page_to_write):
    """
    Uses the csv library to write .csv files containing the image's information
    :param page_to_write: The dictionary containing image objects that will be written to a csv file
    :return:
    """
    ext_len = len(page_to_write.html.split(".")[-1])
    csv_name = page_to_write.html[:-ext_len-1] + ".csv"

    with open(csv_name, 'w') as csvfile:
        file_writer = csv.writer(csvfile)
        csv_data = [["Filename", "Transcription", "Upload Date"]]
        for image in page_to_write.images.keys():
            csv_data.append([page_to_write.images[image].file_name, "\"" + page_to_write.images[image].transcription + "\"",
                             page_to_write.images[image].upload_date])
        file_writer.writerows(csv_data)
        csvfile.close()


def bibliography_pairings(page_soup):
    """
    Pairs the information in the table of the bibliography together with the appropriate data.
    :param page_soup: Beautiful Soup Object
    :return: A dictionary containing all of the bibliography pairings
    """
    rows = page_soup.tbody
    count_data = 0
    bibliography_dict = {}
    title = ""  # variables to store the information of the data in the rows
    info = ""
    if rows:
        for row in rows.children:  # gets the child tag of table row
            if row != "\n":
                for table_data in row.children:  # gets the child tag of table data
                    if table_data != "\n":
                        for p in table_data.children:  # gets the information/tags in the tag p
                            if p != "\n":
                                # store the information two at a time
                                if count_data == 0:
                                    title = p.string  # if the count is 0 then put the information in variable 1
                                    count_data += 1
                                elif count_data != 0:  # if the count is not 0 then put the information in variable 2
                                    info = p.string
                                    count_data += 1
            if count_data == 2:  # if count is 2 then reset the count
                count_data = 0
                bibliography_dict[title] = info  # store variables into the dictionary with key and value
                title = ""
                info = ""

    return bibliography_dict


def main():
    # path = input("Please enter the file path to the directory where the html files are stored: ")
    path = "/home/schmidtt/PycharmProjects/PMSS_Scraper/html/"
    # path = "/Users/bereacollege/Documents/internship/PMSS_Scraper/html/"
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    pmss_pages = []

    for file in onlyfiles:
        if file != ".DS_Store":
            current_page = Page()
            f = open(path + file)
            web_page = BeautifulSoup(f, 'html.parser')
            current_page.images = image_info(web_page)
            captions = find_captions(web_page)
            image_caption_linking(captions, current_page.images)
            current_page.bibliography = bibliography_pairings(web_page)
            current_page.html = file
            find_transcriptions(web_page, current_page.images)
            pmss_pages.append(copy.copy(current_page))
    for page in pmss_pages:
        for image in page.images.keys():
            print(image + " ")
            print(page.images[image])

    to_csv = input("Do you want to create csv files? (y/n): ")
    if to_csv.lower() == "y":
        for page in pmss_pages:
            write_page = input("Do you want to output {}? (y/n): ".format(page.html))
            if write_page.lower() == "y":
                write_csv(page)


if __name__ == "__main__":
    main()
