from bs4 import BeautifulSoup
from PMSS_Image import PMSS_Image
from Caption import Caption
import copy
import csv
import os.path
from Page import Page
import numpy as np
import requests
import os
from os import path
import time
import bs4
from Post import Post
from io import open as iopen
import string
from shutil import copy as dm_copy


def levenshtein_ratio_and_distance(s, t, ratio_calc=False):
    # Code adapted from Francisco Javier Carrera Arias from
    # https://www.datacamp.com/community/tutorials/fuzzy-string-python

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
    rows = len(s) + 1
    cols = len(t) + 1
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
            if s[row - 1] == t[col - 1]:
                cost = 0
                # If the characters are the same in the two strings in a given position [i,j]
                # then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package,
                # if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row - 1][col] + 1,  # Cost of deletions
                                     distance[row][col - 1] + 1,  # Cost of insertions
                                     distance[row - 1][col - 1] + cost)  # Cost of substitutions
    if ratio_calc:
        # Computation of the Levenshtein Distance Ratio
        ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
        return ratio
    else:
        # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # print(distance)
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])


def dir_dive():
    """
    A function to find all the names of .tif's and .jpg's
    :return: A dictionary of names of files
    """
    os.chdir("/Volumes/Elements/PMSS_ARCHIVE")  # looks at this specific directory
    tifs = {}  # dictionary to store all of the tif images
    # finds all files within the directory and within all sub-directories
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            original = name  # original file name that includes .tif
            if name[-4:] == ".tif":  # if the extension is tif
                for punct in string.punctuation:  # for every punctuation
                    name = name.replace(punct, "")  # removes all instances of a specific punctuation
                name = name.replace(" ", "")
                # stores the file name with punctuation removed as the key in the dictionary
                # with the original file name as the value
                tifs[name] = original
    return tifs  # returns the dictionary with all tifs


def file_split_website(list_of_images):
    """
    A function that will remove punctuation from all of the file names of images that are on the website.
    :param list_of_images: A list of images from website
    :return: A dictionary of file names
    """
    file_list = {}  # dictionary to store all file names from the web site
    for image in list_of_images:  # for each image in the list of images
        name_to_fix = list_of_images[image].file_name  # store the original file name to be put in the dictionary
        for punct in string.punctuation:  # for every punctuation
            name_to_fix = name_to_fix.replace(punct, "")  # removes all instances of a specific punctuation
            # stores the file name with punctuation removed as the key in the dictionary
            # with the original file name as the value
        file_list[name_to_fix] = image
    return file_list  # returns the dictionary with all the files


def compare_page_to_hdd(web_images, hdd_images):
    """
    A function that will compare the file names of the web site to the file names of the hard drive.
    :param web_images: Images from the web site
    :param hdd_images: Images from the hard drive
    :return: Dictionary of all images that have matched with each other
    """
    match_count = 0
    matched_items = {}  # Dictionary of all images that have matched with each other
    for image in web_images:  # for each image in the dictionary of web images
        for source in hdd_images:  # for each image in the hard drive
            if image[:-3] == source[:-3]:  # removes extensions like tif or jpg and then compares the two file names
                if source[-3:] == "tif":  # if the extension is tif
                    # store the file name from web site as the key and the hard drive file name as the value
                    matched_items[image] = source
                    match_count += 1
    print(f"{match_count} pictures were replaced with their \"tif\" counterpart")
    return matched_items  # return dict with matched file names


def extract_csv_information(filename):
    """

    :param filename:
    :return:
    """
    csv_info_list = []  # creates a list
    with open(filename) as file:
        info = file.read()
        info = info.split("\n")
        for row in info:
            temp = Post()
            col_count = 0
            for column in row.split(","):
                if col_count == 0:
                    temp.id = column
                elif col_count == 1:
                    temp.post_date = column
                elif col_count == 2:
                    temp.post_title = column
                elif col_count == 3:
                    temp.post_content = column
                elif col_count == 4:
                    temp.post_excerpt = column
                elif col_count == 5:
                    temp.meta_value = column.split("/")[-1]
                col_count += 1
            csv_info_list.append(temp)
    return csv_info_list


def web(links_visited, web_url, pages_list):
    """
    Web Crawler that will scan through the pmss webpage and find all different links from various pages
    :param links_visited: List that will store all of the links visited through the crawler
    :param web_url: The Urls that will be visited
    :param pages_list: A list that will hold all the information for every page
    :return: None
    """
    urls_to_skip = ["https://pmss.wpengine.com/?page_id=19612",
                    "https://pmss.wpengine.com/?page_id=48056", "https://pmss.wpengine.com/?attachment_id=3868",
                    "https://pmss.wpengine.com/farm/farm-shell-farm-field-plan-1948/"]
    split_link = web_url.split(".")  # splits the link on a period to get domain
    if len(split_link) > 1:  # base case to ensure that there is a link
        domain = split_link[0] + split_link[1]  # stores the domain
    else:
        return
    ext = ["jpg", "png", "tif", "ppt", "pptx"]  # extensions of images
    if domain != "https://pmsswpengine":  # base case we always need this url for our domain
        return  # it will only scrape data within the domain of pmss
    # base case if we have already visited the link we do not want to re-visit it over
    if web_url in links_visited or web_url in urls_to_skip:
        return
    # TODO: If you want to change the number of pages to crawl through, change the number below
    # if len(links_visited) > 500:  # restriction for the amount of pages we want to search (temporary)
    #     return
    if web_url.split(".")[-1] in ext:  # split url if the end of url is in ext just return
        return
    links_visited.append(web_url)  # append the urls that we visit to a list of links visited
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36\
      (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}  # the User-Agent header mimics a browser

    result = requests.get(web_url, headers=headers)
    plain = result.text  # raw html

    pages_list.append(pages_info(plain, web_url))  # append the page to a list after getting info for it
    page_soup = BeautifulSoup(plain, "html.parser")  # beautiful soup object; parses the html
    for link in page_soup.findAll('a'):  # finds all a tags within html
        if not link.get("class"):  # avoid the html tag with class
            # if len(links_visited) > 500:
            #     return
            if link.contents:  # checks to make sure there are contents before we get the name
                if link.contents[0].name != "img":  # if the link is not for an image
                    if link.parent:  # if the link has a parent tag
                        try:
                            if link.parent.get("class")[0] == "must-log-in":  # if the link goes to a log in page
                                return  # ignore this link
                        except TypeError:  # if a TypeError occurs
                            pass  # keep code going
                    links_destination = link.get('href')  # gets the href and this determines the links destination
                    if not links_destination:
                        return
                    try:
                        if links_destination.split("/")[3] == "wp-admin":
                            return
                    except IndexError:
                        pass
                    if links_destination:
                        web(links_visited, links_destination,
                            pages_list)  # recursive call to keep calling the different links


def pages_info(text, url):
    """
    Driver function for getting information for a page.
    :param text: full html as plain text
    :param url: The url for the web page
    :return: page object
    """
    current_page = Page()  # creates a new page object
    web_page = BeautifulSoup(text, 'html.parser')  # Create a new Beautiful Soup object
    current_page.images = image_info(web_page)
    captions = find_captions(web_page)
    image_caption_linking(captions, current_page.images)
    current_page.bibliography, partial_bib = bibliography_pairings(web_page)  # check for bibliographies on the page
    current_page.url = url  # save the current url with in the page's attributes
    # check_if_guide(web_page, current_page)
    find_transcriptions(web_page, current_page.images)
    show_results(current_page)
    return current_page


def image_info(page_soup):
    """
    Finds all images on the page and collects as much information as it can
    :param page_soup: A Beautiful Soup object
    :return: A dictionary containing all of the images from the page
    """
    images_dict = {}  # create a dictionary for the images
    page_tags = image_tags(page_soup)  # gets the tags for the page
    for image in page_soup.find_all('img'):  # for an image it will find all of the img tags within the html of the page
        if image.get("src"):  # if our image has a src attribute
            temp = PMSS_Image()  # initialize a new image instance

            src = image.get("src")
            # Pull out the id that will be used to find this image's caption
            caption_link(image, temp)

            # Pull the filename and upload date for this image
            image_file_path_info(image, temp)

            # Record the resolution information for this image
            image_resolution(image, temp)

            # If resolution information is in the filename, strip that information out
            temp.strip_resolution()

            # Set the tags for the images as the same tags from the page
            temp.tags = page_tags

            # Attempts to save the image
            download_image(temp, src)

            if image.parent.name == "figure":  # If we are looking at an image from a figure tag
                for tag in image.parent.children:  # for each of the tag's siblings
                    if tag.name == "figcaption":  # if a sibling's tag namme is figcaption
                        temp.caption = tag.string  # save the text as it is the caption for our image
            file_names_skip = ["220px-Norman_Thomas_1937.jpg", "12px-Wikisource-logo.svg.png", "Emma_Lucy_Braun.jpg",
                               # ignore these files because they're irrelevant to scraping
                               "04025r.jpg", "apf1-00354r.jpg", "cropped-pmss_spelman_pntg_edited_2_brightened_x.jpg"]
            if temp.file_name not in file_names_skip and ".gif" not in temp.file_name:  # Ignore the header image
                # Copy the image to a dictionary
                images_dict[temp.file_name[:-len(temp.file_name.split(".")[-1]) - 1].lower()] = copy.copy(temp)
    return images_dict


def download_image(image, src):
    """
    A function that downloads the images that have not been saved from the web site.
    :param image: Instance of the PMSS_Image class
    :param src: The URL from the image that we want to save
    :return: None
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36\
          (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    hdd_image_path = "/Volumes/Elements/Scraped_Images/"
    os.chdir(hdd_image_path)  # changes directory to the location that we want to save images
    upload_date = image.upload_date.split("/")  # gets the upload date to be used in setting the save directory

    for partial_date in upload_date:  # for each part fo the date in the upload date
        try:  # try to go into the csv directory
            os.chdir(partial_date)  # change directory to the partial date
        except FileNotFoundError:  # if the directory does not exist
            os.mkdir(partial_date)  # make directory for the partial date
            os.chdir(partial_date)  # change directory to the newly made directory

    # file path is the path to the file that we are potentially going to save
    file_path = os.getcwd() + "/" + image.file_name
    if not path.exists(file_path):  # if the file name already exists
        if "C:/" not in src and ".gif" not in src:  # if the image URL we want to save is not a hard drive path
            img_resolution = "-" + str(image.image_resized_resolution[0]) + "x" + str(image.image_resized_resolution[1])
            if img_resolution in src:
                src = src.replace(img_resolution, "")
            response = requests.get(src, headers=headers)  # gets the image itself; raw image data
            if response.status_code != 404:  # if the image exists
                with iopen(file_path, "wb") as image_file:  # retrieves image from file path
                    image_file.write(response.content)  # writes the image data in to the file


def caption_link(tag, img):
    """
    This function takes a given attribute, checks to see if it is the attribute for linking images with captions, and
    then stores that information in the instance of the Images class
    :param tag: a string for an attribute of an html tag
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    if tag.get("aria-describedby"):
        img.caption_link = tag.get("aria-describedby")
        # retrieves the link of the caption by looking for the key word of
        # aria-describedby and gets the tag from it


def image_file_path_info(tag, img):
    """
    This function is for extracting the filename of an image from it's src filepath. In addition, we can extract the
    upload date
    :param tag: a string for an attribute of an html tag
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    file_path = tag.get("src")  # looks for the tag of src within its file path
    file_split = file_path.split("/")  # splits the file path when it encounters a /
    img.file_name = file_split[-1]  # retrieves the file name once the file has been split
    year = file_split[-3]  # retrieves the year the image was uploaded from the file name
    month = file_split[-2]  # retrieves the month the image was uploaded from the file name
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
    captions_dict = {}  # a dictionary to store all of the captions
    for caption in page_soup.find_all('dd'):  # for every caption look for the tag "dd"
        temp = Caption()  # temporarily stores a caption for class constructor
        temp.image_link = caption.get('id')  # retrieves the caption through the tag of "id" which will be image link
        temp.caption = caption.string[5:-5]  # save the caption ignoring all the \n's near it
        captions_dict[temp.image_link] = copy.copy(
            temp)  # makes a shallow copy of the image link stored in the dictionary
    for caption in page_soup.find_all('p'):  # for every caption find the "p" tags
        temp = Caption()  # temporarily stores a caption for class constructor
        temp.image_link = caption.get('id')  # retrieves the caption through the tag of "id" which will be image link
        temp.caption = caption.string  # converts caption to a string
        captions_dict[temp.image_link] = copy.copy(
            temp)  # makes a shallow copy of the image link stored in the dictionary

    return captions_dict  # return the dictionary


def image_caption_linking(captions_dict, images_dict):
    """
    Matches image objects with their captions
    :param captions_dict: Dictionary holding all captions from the page
    :param images_dict: Dictionary holding all images from the page
    :return: None
    """
    for caption in captions_dict.keys():  # for every caption of an image in the caption dictionary
        for image in images_dict.keys():  # for every image in the image dictionary
            if images_dict[image].caption_link:  # If a caption link id was found
                if not images_dict[image].caption:  # if a caption has not been found yet
                    # if the caption dictionary matches the image dictionary
                    if captions_dict[caption].image_link == images_dict[image].caption_link:
                        images_dict[image].caption = captions_dict[
                            caption].caption  # then the image will go with the caption


def image_tags(page_soup):
    """
    A function that gets the tags of a web page.
    :param page_soup: Beautiful Soup object
    :return: String of tags
    """
    all_p = page_soup.find_all("p")  # finds all p tags on web page
    tags = ""  # create a string to store all of the tags
    for tag in all_p:  # for each tag within the p tags
        if tag.string:  # if the tag has a string
            if "TAGS:" in tag.string:  # if "TAGS" is in that string
                tag_body = tag.string.split("TAGS:")  # removes "TAGS" from the string
                for descr_tag in tag_body[1].split(";"):  # for each descriptive tag
                    if descr_tag:  # if the descriptive tag is not blank
                        cleaned_tag = descr_tag.replace(u'\xa0', u' ')  # replace "NBSP" with an actual space
                        if len(cleaned_tag) > 2:  # if the tag is bigger than 2 characters
                            while cleaned_tag[0] == " ":  # while the first element is not an actual character
                                cleaned_tag = cleaned_tag[1:]  # save contents except the first element
                            while cleaned_tag[-1] == " ":  # while the last element is not an actual character
                                cleaned_tag = cleaned_tag[:-1]  # save contents except the last element
                            tags += cleaned_tag + ", "  # concatenate the tag to a string
        else:
            for child in tag.children:  # if the tag does not have a string look at the child of the tag
                if child.string:  # if the child has a string

                    if "TAGS:" in child.string:  # if "TAGS" is in that child string
                        tag_body = child.next_sibling.string  # looks at the siblings of that string
                        for descr_tag in tag_body.split(";"):  # for each descriptive tag
                            if descr_tag:  # if the descriptive tag is not blank
                                cleaned_tag = descr_tag.replace(u'\xa0', u' ')  # replace "NBSP" with an actual space
                                if len(cleaned_tag) > 2:  # if the tag is bigger than 2 characters
                                    while cleaned_tag[0] == " ":  # while the first element is not an actual character
                                        cleaned_tag = cleaned_tag[1:]  # save contents except the first element
                                    while cleaned_tag[-1] == " ":  # while the first element is not an actual character
                                        cleaned_tag = cleaned_tag[:-1]  # save contents except the last element
                                    tags += cleaned_tag + ", "  # concatenate the tag to a string
    return tags  # return the string that contains all the tags


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
                            # move to the previous sibling (the text above our current text)
                            current_tag = tag.previous_sibling
                            transcript = ""
                            while current_tag.name not in header_tags:  # keep moving up until we reach a header tag
                                if current_tag.name != "div":  # If it's not related to an image
                                    transcript = get_tags_text(
                                        current_tag) + transcript  # recursive call for getting all of the text
                                # after getting the text for the tag, move back one sibling
                                current_tag = current_tag.previous_sibling
                            # We assume if we encounter just a number, it is a page number for a transcription
                            recording = True
                    if 3 < len(tag.string) <= 8:  # If the text length is between 3 and 8 it is likely to be "page ##"
                        page_source = ""  # This will hold the "page ##" that the transcript comes from since we don't
                        # have an associated image
                        for word in tag.string.split():  # split the string that is in the tag into different words
                            # looking for the word page in order to find where the transcript is separated
                            if word.lower() == "page":
                                page_source += word  # add the word "page" to the page source
                            else:  # if our word is anything other than "page"
                                try:
                                    int(word)  # Is this an integer? (e.g. 1, 2, 3, 4 etc.)
                                    # if int(word) doesn't cause a ValueError, we know it is an integer
                                    page_source += word
                                except ValueError:  # If it is not "page" or a number we don't want to add it
                                    pass
                        if len(page_source) >= 5:  # if the length of the page source is > 2
                            img_dict[
                                page_source] = PMSS_Image()  # Create a new object with page_source as a key
                            # Set the current_file as page_source (so we store the transcript in the right place)
                            current_file = page_source
                            recording = True  # Turn recording on as we are looking at a page's transcription
            for main_tags_child in tag.children:
                if main_tags_child.string:
                    if "transcription" in \
                            main_tags_child.string.lower():  # for each tag we look for the string called transcription
                        recording = True

                    elif ".jpg" in main_tags_child.string:
                        if recording:
                            if "lin_f" in main_tags_child.string:
                                x = 1
                            split_name = main_tags_child.string
                            if "[" in main_tags_child.string or "]" in main_tags_child.string:
                                if "[" in main_tags_child.string:
                                    split_name = split_name.split(
                                        "[")[1]  # if .jpg found then we will then extract file name
                                if "]" in main_tags_child.string:
                                    split_name = split_name.split("]")[0]
                                current_file = split_name
                                if " " in current_file:
                                    for piece in current_file.split(" "):
                                        if ".jpg" in piece:
                                            current_file = piece
                                if current_file[:-4] not in img_dict:
                                    # if the current file is not in the image dictionary
                                    img_dict[current_file[:-4]] = PMSS_Image()
                                    # we need to store the transcript into the dictionary and note that is an outlier
                                    img_dict[current_file[:-4]].file_name = current_file
                                    image_index += 1
                                current_file = current_file[:-4]

                            else:
                                current_file = main_tags_child.string
                                if " " in current_file:
                                    for piece in current_file.split(" "):
                                        if ".jpg" in piece:
                                            current_file = piece
                                img_dict[current_file[:-4]] = PMSS_Image()
                                img_dict[current_file[:-4]].file_name = current_file
                                current_file = current_file[:-4]

                    elif "[" in main_tags_child.string:  # If we find a bracket, check if it is a filename
                        # a list of keys in our image dictionary
                        keys = list(img_dict)
                        # We assume what we are looking at is a transcript unless we change the filename
                        part_of_transcription = True
                        for section in main_tags_child.string.split("["):  # split the text by the open bracket
                            # split the text by the closed bracket so all that's left is just the text
                            for subsection in section.split("]"):
                                if len(keys) != 0 and image_index > len(keys):  # If we have keys in our dictionary
                                    # if our comparison text is at least 80% similar to our key,
                                    # assume they are the same
                                    print(subsection.lower())
                                    print(keys[image_index])
                                    if levenshtein_ratio_and_distance(subsection.lower(), keys[image_index],
                                                                      True) >= .80:
                                        current_file = keys[image_index]  # update the current file
                                        image_index += 1  # increase the image index
                                        # since we determined it is a file name, this is now False
                                        part_of_transcription = False
                        if part_of_transcription:  # If the text was deemed to not be a file
                            record_transcript(img_dict, recording, current_file, main_tags_child)  # record the text

                    elif main_tags_child.name == "span" or \
                            main_tags_child.name == "p":  # looks for tags that likely contain a transcript
                        record_transcript(img_dict, recording, current_file, main_tags_child)
                    elif main_tags_child.name == "div":  # we do not care about other div tags
                        pass

                    # if the tags parent is the p tag and the child is not in the div tag
                    elif main_tags_child.parent.name == "p" and main_tags_child.name != "div":
                        record_transcript(img_dict, recording, current_file,
                                          main_tags_child)  # we record the transcription into the dictionary

                    else:  # if we reach any other tag
                        if main_tags_child.previous_sibling:  # if the child of the main tag is in the previous level
                            # make the previous tag the previous level of the main tags child which is in the same level
                            previous_tag = main_tags_child.previous_sibling.name
                        else:
                            previous_tag = None  # if not there is no previous tag
                        if main_tags_child.next_sibling:  # if the child of the main tag is in the next level
                            # make the next tag the next level of the main tags child which is in the same level
                            next_tag = main_tags_child.next_sibling.name
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
    if tag.string:  # if we are at the last descendant (the text)
        return tag.string  # return the string
    transcript = ""  # a variable to build the full text into
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


def bibliography_pairings(page_soup):
    """
    Pairs the information in the table of the bibliography together with the appropriate data.
    :param page_soup: Beautiful Soup Object
    :return: A dictionary containing all of the bibliography pairings
    """
    table = page_soup.find_all("table")  # finds all the table tags on the specific web page
    if table:  # if the table tag exists
        table = table[-1]  # looks at the last table on the page

    count_data = 0  # used to store data in twos (count data will increment to 2 and then reset to 0 when data is saved
    bibliography_dict = {}  # dictionary that will store all of the bibliographies
    # list of all possible row titles lowered to use as a reference for comparing information
    table_row_titles_lower = ["title", "alt. title", "identifier", "creator", "alt. creator", "subject keyword",
                              "subject lcsh", "date digital", "date original", "date",
                              "publisher", "contributor", "type", "format", "source", "language", "relation",
                              "coverage temporal", "coverage spatial", "rights", "donor", "description", "acquisition",
                              "citation", "processed by", "last updated", "bibliography"]
    # list of all possible row titles for storing information
    table_row_titles = ["Title", "Alt. Title", "Identifier", "Creator", "Alt. Creator", "Subject Keyword",
                        "Subject LCSH", "Date digital", "Date original", "Date",
                        "Publisher", "Contributor", "Type", "Format", "Source", "Language", "Relation",
                        "Coverage Temporal", "Coverage Spatial", "Rights", "Donor", "Description", "Acquisition",
                        "Citation", "Processed by", "Last updated", "Bibliography"]
    count_key = 0  # stores how many keys have been saved
    row_title_list = []  # list of all the row titles
    row_info_list = []  # list of all the row information

    for tbody in table:  # for each tbody in the table
        if tbody != "\n" and tbody.name != "colgroup":  # if tbody is not a new line or colgroup tag
            for row in tbody.children:  # for each row in the table
                if row != "\n" and row.name != "colgroup":  # if row is not a new line or colgroup tag
                    for table_data in row.children:  # for each table data in the children of the rows
                        # if table data is not a new line or colgroup tag
                        if table_data != "\n" and table_data.name != "colgroup":
                            if count_data == 0:  # if this is the first item
                                bibliography_text_retrieval(table_data, row_title_list)  # recursively get the text

                            if count_data != 0:  # if this is the second item
                                bibliography_text_retrieval(table_data, row_info_list)  # recursively get the text

                            count_data += 1  # increment counter of how much data has been stored

                if count_data > 1:  # if we have at least two data items
                    count_data = 0  # reset counter
                    if len(row_title_list) == len(
                            row_info_list):  # if the length of title list and info list are the same
                        for i in range(len(row_title_list)):  # for each item
                            # if the current item is not in the reference list
                            if row_title_list[i].lower() not in table_row_titles_lower:
                                is_part_of_dict = False  # assume it is not a part of the bibliography
                                for title in table_row_titles_lower:  # for each item in the reference list
                                    # if the reference item and the row title are similar but not an exact match
                                    if levenshtein_ratio_and_distance(title, row_title_list[i].lower(), True) >= .80:
                                        is_part_of_dict = True  # title is a part of the bibliography
                                        item_index = table_row_titles_lower.index(title)  # index of the reference item
                                        # add the item to the bibliography using the storing list and index
                                        # this is so the title that is stored is formatted correctly
                                        bibliography_dict[table_row_titles[item_index]] = row_info_list[i]
                                        count_key += 1  # increment how many keys have been saved
                                        break
                                if not is_part_of_dict:  # if no reference items match
                                    bibliography_dict = {}  # clear the dictionary
                                    return bibliography_dict, True  # return empty dictionary
                            else:  # if the current item is in the reference list
                                bibliography_dict[row_title_list[i]] = row_info_list[i]  # add item to the dictionary
                                count_key += 1  # increment how many keys have been saved
                        row_title_list = []  # clear the title lists
                        row_info_list = []  # clear the info lists
                    else:  # if the length of title list and info list are not the same
                        full_title = ""  # string for holding all of the text in the title list
                        full_info = ""  # string for holding all of the text in the info list
                        for title in row_title_list:  # for each title in the list
                            full_title += title  # add the title to the full string
                        for info in row_info_list:  # for each piece of info in the list
                            full_info += info  # add the info to the full string
                        # if the title is not in the reference list
                        if full_title.lower() not in table_row_titles_lower:
                            is_part_of_dict = False  # assume it is not part of the bibliography
                            for title in table_row_titles_lower:
                                # if the reference item and the row title are similar but not an exact match
                                if levenshtein_ratio_and_distance(title, full_title, True) >= .80:
                                    is_part_of_dict = True  # title is a part of the bibliography
                                    item_index = table_row_titles_lower.index(title)  # index of the reference item
                                    # add the item to the bibliography using the storing list and index
                                    # this is so the title that is stored is formatted correctly
                                    bibliography_dict[table_row_titles[item_index]] = full_info
                                    count_key += 1  # increment how many keys have been saved
                                    break
                            if not is_part_of_dict:  # if no reference items match
                                bibliography_dict = {}  # clear the dictionary
                                return bibliography_dict, True  # return empty dictionary
                        else:  # if the title is in the reference list
                            bibliography_dict[full_title] = full_info  # add the title and info to the bibliography
                            count_key += 1  # increment how many keys have been saved
                        row_title_list = []  # clear the title lists
                        row_info_list = []  # clear the info lists

    if 5 <= count_key <= len(table_row_titles) - 6:  # if the amount of keys saved is between 5 and 20
        return bibliography_dict, True  # return while indicating only a portion of the bibliography was found
    else:
        return bibliography_dict, False  # return full bibliography


def bibliography_text_retrieval(tag, column_list):
    """
    Recursive function for getting text from table data
    :param tag: Beautiful Soup tag object
    :param column_list: List containing all the information in a column within a specific row
    :return: None
    """

    if tag.string:  # if we are at the last descendant (the text of the tag)
        text = ""  # text that will be appended to column list
        if "\n" in tag.string:  # if there exists a new line character within the tag's string
            for piece in tag.string.split("\n"):  # split on new line character to ignore them
                if piece != "":  # if the current part of the split string is not empty
                    text += piece + " "  # add the part and a space
        else:  # if there is not a new line character
            text = tag.string  # add the tag's string to the text variable
        if isinstance(text, bs4.element.NavigableString):  # if the type of text is a Navigable String
            column_list.append(text)  # if it is append text to the column list
        return
    for child in tag.children:  # for each of the current tag's children
        bibliography_text_retrieval(child, column_list)  # recursive function call to build the bibliography
    return  # return the full text


def check_if_guide(page_soup, page):
    header_tags = ["h1", "h2"]  # header tags we need to check in
    for header in header_tags:  # for each header in the list of header tags
        entry_title = page_soup.find(header, attrs={
            "class": "entry-title"})  # finds and stores the tag who's class is entry-title
        if entry_title:  # if the tag was found
            if entry_title.string:  # if the tag has a string
                if "GUIDE" in entry_title.string:  # if GUIDE is in that string
                    page.is_guide = True  # mark page as being a GUIDE page


def show_results(page):
    """
    Shows the list of pages that we visit
    :param page: List of all the web pages
    :return: None
    """
    print(page.url + "\n\n")  # prints the current pages URL
    for image in page.images.keys():  # for an image in the pages return a list of keys from dictionary
        print(image)  # prints image's file name
        print(page.images[image])  # prints image information


def create_master_list(pages_list):
    """
    Combine all of the images and bibliographies into one structure respectively
    :param pages_list: List of pages
    :return: Complete list of all the bibliographies, all of the images, and list of guide pages
    """
    list_of_images = {}  # Dictionary that will contain all the images
    list_of_bibs = []  # List that will contain all the bibliographies
    guide_pages = []  # List that will contain all the URLs for the guide pages
    transcript_counter = 0
    caption_counter = 0
    duplicate_counter = 0
    alt_captions_counter = 0
    no_caption_counter = 0

    for page in pages_list:  # for each page in the list of pages
        for image in page.images.keys():  # for each image in the pages dictionary of images
            try:
                if list_of_images[image]:  # if image key is already in the list of images
                    if page.images[image].caption:
                        if list_of_images[image].caption:
                            if list_of_images[image].caption == page.images[image].caption:
                                duplicate_counter += 1
                            else:
                                if levenshtein_ratio_and_distance(page.images[image].caption,
                                                                  list_of_images[image].caption, True) > .80:
                                    duplicate_counter += 1
                                else:
                                    list_of_images[image].alt_captions.append(
                                        page.images[image].caption)  # add current caption to alt captions
                                    alt_captions_counter += 1
                        else:
                            list_of_images[image].caption = page.images[image].caption
                        list_of_images[image].url_sources += page.url + " "

            except KeyError:
                list_of_images[image] = page.images[image]  # if image is not in the dictionary add it to it
                list_of_images[image].url_sources += page.url + " "

            if list_of_images[image].transcription:
                transcript_counter += 1
            if page.images[image].caption:
                caption_counter += 1
        if page.bibliography:  # if there is a bibliography for the page
            list_of_bibs.append(page.bibliography)  # append bibliography to the list of bibliographies
        if page.is_guide:  # if this is a GUIDE page
            guide_pages.append(page.url)  # append the URL to the list of GUIDE URLs

    for image in list_of_images.keys():
        if not list_of_images[image].caption:
            no_caption_counter += 1
    return list_of_bibs, list_of_images, guide_pages, transcript_counter, \
        caption_counter, duplicate_counter, alt_captions_counter, no_caption_counter  # return all 3 structures


def write_csv(images: dict, bibliographies: list):
    """
    Uses the csv library to write .csv files containing the image's information
    :param images: The master list of all images that were scraped
    :param bibliographies: The master list of all bibliographies that were scraped
    :return: None
    """
    contentdm_columns = ["Title", "Alt. Title", "Identifier", "Creator", "Subject Keywords", "Subject", "Date",
                         "Date Digitized", "Date Uploaded", "Date Accepted", "Publisher", "Contributors", "Type",
                         "Format", "Source", "Language", "Relation", "Coverage Spatial", "Coverage Temporal",
                         "Rights", "Audience", "Description", "Transcript", "Originating Institution", "Filename"]
    identifier = 0
    saved_file_names = []
    # using the os module, the current directory plus /csv/ is where they will be stored
    csv_path = "/Users/bereacollege/Desktop/PMSS_Scraper/csv/"
    try:  # try to go into the csv directory
        os.chdir(csv_path)
    except FileNotFoundError:  # if the csv directory doesnt exist
        os.mkdir(csv_path)  # make the csv directory
        os.chdir(csv_path)  # change to the csv directory
    for root, dirs, files in os.walk("/Users/bereacollege/Desktop/for CONTENTdm/Images/", topdown=False):
        for name in files:
            saved_file_names.append(name[:-4])
    to_remove = []
    for image in images:
        if image not in saved_file_names:
            to_remove.append(image)
    print(f"{len(to_remove)} items have been removed.")
    final_master_list = {}
    for image in images:
        if image not in to_remove:
            final_master_list[image] = images[image]
    images = final_master_list
    with open("Images_for_contentdm.csv", 'w') as csvfile:  # open csv file for the page we are currently on
        file_writer = csv.writer(csvfile)  # store the writer for the csv file to a variable
        csv_data = [contentdm_columns]  # the first row are the column headings
        for image in images.keys():  # for each image in our images dictionary
            csv_data.append([images[image].file_name, "", identifier, "Unknown", images[image].tags, "", "",
                             images[image].upload_date, images[image].upload_date, "Image", "",
                             "Helen Hayes Wykle & Ann Angel Eberhardt", "",
                             "", "", "", "", "", "",
                             "All rights reserved, Pine Mountain Settlement School", "", images[image].caption, images[image].transcription,
                             "Pine Mountain Settlement School", images[image].file_name])  # append the file name, transcription, and upload date
            identifier += 1
        file_writer.writerows(csv_data)  # write the information to the file
        csvfile.close()  # close the file

    with open("Bibliographies_for_contentdm.csv", 'w') as csvfile:  # open csv file for the page we are currently on
        bib_file_writer = csv.writer(csvfile)  # store the writer for the csv file to a variable
        csv_data = [contentdm_columns]
        headers = ["Title", "Alt. Title", "Identifier", "Alt. Creator",
                   "Subject Keyword", "Subject LCSH", "Date", "Date digital", "", "Acquisition",
                   "Publisher", "Contributor", "Type", "Format", "Source", "Language", "Relation",
                   "Coverage Spatial", "Coverage Temporal", "Rights", "", "Description",
                   "Creator"]  # the first row are the column headings
        for bib in bibliographies:  # for each image in our images dictionary
            try:
                tags = bib["Subject Keyword"]
                tags = tags.split(";")
                current_bib = []
                final_tags = ""
                for tag in tags:
                    if tag:  # if the descriptive tag is not blank
                        cleaned_tag = tag.replace(u'\xa0', u' ')  # replace "NBSP" with an actual space
                        if len(cleaned_tag) > 2:  # if the tag is bigger than 2 characters
                            while cleaned_tag[0] == " ":  # while the first element is not an actual character
                                cleaned_tag = cleaned_tag[1:]  # save contents except the first element
                            while cleaned_tag[-1] == " ":  # while the last element is not an actual character
                                cleaned_tag = cleaned_tag[:-1]  # save contents except the last element
                            final_tags += cleaned_tag + ", "  # concatenate the tag to a string
                bib["Subject Keyword"] = final_tags
            except KeyError:
                pass
            bib["Identifier"] = identifier
            current_keys = bib.keys()
            for header in headers:
                if header in current_keys:
                    current_bib.append(bib[header])
                else:
                    current_bib.append("")
            csv_data.append(current_bib)  # append the file name, transcription, and upload date
            identifier += 1
        bib_file_writer.writerows(csv_data)  # write the information to the file
        csvfile.close()  # close the file


def compare_scraped_and_phpmyadmin_images(list_of_posts: list, image_dictionary: dict):
    """
    A function that compares of all of the images scraped to all of the images within PHPmyadmin
    :param list_of_posts: Lists that stores the posts from PHP Admin
    :param image_dictionary: Dictionary that stores all of the images
    :return: None
    """
    image_matches = 0  # counter to see how many images match
    print(len(list_of_posts))  # prints the number of posts within phpmyadmin
    print(len(image_dictionary))  # prints the number of images in the dictionary
    for post in list_of_posts:  # for each post in the list of posts of PHPmyadmin
        for scraped_img in image_dictionary.keys():  # for each image scraped from the website that is in the img dict
            if post.meta_value == image_dictionary[scraped_img].file_name:  # if the post value equals the image scraped
                print(f"{post.meta_value}: True")  # images have matched
                image_matches += 1  # increase matched images counter

    print(f"{image_matches}/{len(list_of_posts)} images matched")  # print the number of images that have matched


def print_results(pages: list, images: dict, transcript_counter: int, caption_counter: int, duplicate_counter: int,
                  bibliographies: list, alt_captions_counter: int, no_caption_counter: int):
    """
    A function that prints all of the results from the program.
    :param pages: List of all the pages that we have scraped
    :param images: Dictionary that stores all the images that we have
    :param transcript_counter: Integer, and it keeps up with how many transcripts we have found
    :param caption_counter:  Integer, and it keeps up with how many captions we have found with our images
    :param duplicate_counter: Integer, and it keeps up with how many duplicate captions we have found
    :param bibliographies: List of all the bibliographies that we have scraped
    :param alt_captions_counter: Integer, and it keeps up with how many alternate captions we have found
    :param no_caption_counter: Integer, and it keeps up with how many images do not have captions
    :return: None
    """
    print(f"{len(pages)} pages scraped")  # prints how many pages that we have scraped
    print(f"{len(images)} images scraped")  # prints how many images that we have scraped
    print(f"{transcript_counter} transcriptions scraped")  # prints how many transcriptions we have scraped
    # prints the number of captions we have scraped
    print(f"{caption_counter - (duplicate_counter + alt_captions_counter)} captions scraped")
    print(f"{no_caption_counter} images with no captions")  # prints how many images we do not have with captions
    print(f"{alt_captions_counter} alternate captions scraped")  # prints how many alternate captions we have scraped
    print(f"{duplicate_counter} duplicate captions scraped")  # prints how many duplicate captions we have scraped
    print(f"{len(bibliographies)} bibliographies scraped")  # prints the how many bibliographies that we have scraped


def write_result_files(bibliographies: list, images: dict, guide_pages: list):
    """
    A function that will write the results as files.
    :param bibliographies: List of bibliographies
    :param images: Dictionary that stores all of the images
    :param guide_pages: A list of all the guided web pages
    :return: None
    """
    with open("Bibliographies_list", "w") as bib_file:  # opens the bibliography file
        info_to_write = f"{len(bibliographies)} bibliographies\n\n"  # writes the number of bibliographies
        for bib in bibliographies:  # for each bibliography in the list of bibliographies
            for attr in bib.keys():  # for each column in each bibliography
                info_to_write += f"{attr}: {bib[attr]}\n"  # write the column name and what is stored there
            info_to_write += "\n\n"
        bib_file.write(info_to_write)  # writes all bibliography info into the file
    with open("images_list", "w") as img_file:  # opens the image file
        info_to_write = f"{len(images)} images\n\n"  # writes the number of images
        for img in images.keys():  # for each image in the list of images
            # add the image information
            info_to_write += f"File name: {images[img].file_name}\n" \
                f"Caption: {images[img].caption}\n" \
                f"Resized resolution: {images[img].image_resized_resolution[0]}x" \
                f"{images[img].image_resized_resolution[1]}\n" \
                f"Transcription: {images[img].transcription}\n" \
                f"Upload date: {images[img].upload_date}\n\n\n"
        img_file.write(info_to_write)  # writes all image info into the file

    with open("guide_urls", "w") as guide_file:  # opens the file in write mode
        info_to_write = f"{len(guide_pages)} guide pages\n\n"  # add the number of guide pages there are
        for url in guide_pages:  # for each url in the url list
            info_to_write += f"{url}\n"  # puts URL in the file
        guide_file.write(info_to_write)  # write all the information into the file


def package_contents(images):
    scraped_path = "/Volumes/Elements/Scraped_Images/"
    source_path = "/Volumes/Elements/PMSS_ARCHIVE"
    for root, dirs, files in os.walk(scraped_path, topdown=False):
        for name in files:
            if name[:-4] in images:
                if images[name[:-4]].file_name[-3:] != "tif":
                    if not path.exists("/Users/bereacollege/Desktop/for CONTENTdm/Images/" + name):
                        dm_copy(root + "/" + name, "/Users/bereacollege/Desktop/for CONTENTdm/Images/")
    all_filenames = {}
    for root, dirs, files in os.walk(source_path, topdown=False):
        for name in files:
            all_filenames[name] = root
    for image in images:
        if images[image].file_name in all_filenames.keys():
            if images[image].file_name[-3:] == "tif":
                if not path.exists("/Users/bereacollege/Desktop/for CONTENTdm/Images/" + images[image].file_name):
                    dm_copy(all_filenames[images[image].file_name] + "/" + images[image].file_name, "/Users/bereacollege/Desktop/for CONTENTdm/Images/")


def run_time():
    """
    Calculates and prints out how long the program ran
    :return: None
    """
    time_run = time.time() - start_time
    mins = time_run // 60
    secs = time_run - (60 * mins)
    mins = str(mins).split(".")[0]
    print(f"~~----{mins}m {secs}s run time----~~")


def main():
    pages_list = []
    links_visited = []  # list of links visited
    web(links_visited, 'https://pmss.wpengine.com/', pages_list)
    print("~~----Scraping Results----~~")
    bib_master_list, images_master_list, guide_pages, transcript_counter, \
        caption_counter, duplicate_counter, alt_captions_counter, no_caption_counter = create_master_list(
            pages_list)  # Save the master lists to variables

    print_results(pages_list, images_master_list, transcript_counter, caption_counter, duplicate_counter,
                  bib_master_list, alt_captions_counter, no_caption_counter)
    write_result_files(bib_master_list, images_master_list, guide_pages)

    hdd_images = dir_dive()
    stripped_images = file_split_website(images_master_list)
    items_to_fix = compare_page_to_hdd(stripped_images, hdd_images)
    for to_change in items_to_fix:
        images_master_list[stripped_images[to_change]].file_name = hdd_images[items_to_fix[to_change]]
    package_contents(images_master_list)
    write_csv(images_master_list, bib_master_list)

    # for image in images_master_list.keys():
    #     captions = images_master_list[image].alt_captions
    #     captions.append(images_master_list[image].caption)

    # phpmyadmin_images = extract_csv_information("image_list_with_captions-j45ab3_posts.csv")
    run_time()


start_time = time.time()

if __name__ == "__main__":
    main()
