from bs4 import BeautifulSoup
from Images import Image
import copy
import csv
from StackClass import Stack
from QueueClass import Queue


def caption_link(attribute, Image):
    """
    This function takes a given attribute, checks to see if it is the attribute for linking images with captions, and
    then stores that information in the instance of the Images class
    :param attribute: a string for an attribute of an html tag
    :param Image: an instance of the Images class for storing the given  information
    :return: None
    """
    if "aria-describedby" in attribute:
        Image.caption_link = attribute[18:-1]


def image_file_path_info(attribute, Image):
    """
    This function is for extracting the filename of an image from it's src filepath. In addition, we can extract the
    upload date
    :param attribute: a string for an attribute of an html tag
    :param Image: an instance of the Images class for storing the given  information
    :return: None
    """
    if "src=" in attribute:
        ext = attribute[-5:-1]  # Assuming the extension is 3 characters long save the last few characters
        if "." not in ext:  # If the "." is not in the extension, the extension is 4 characters long
            ext = attribute[-6:-1]
        slash_total = attribute.count("/")
        slash_count = 0

        for char in attribute:
            # A slash count is used to know where in the file path we are. When count == total, we are in the file name
            if slash_total == slash_count:
                Image.file_name += char
            if slash_total-2 <= slash_count < slash_total:
                Image.upload_date += char
            if char == "/":
                slash_count += 1
        Image.upload_date = Image.upload_date[:-1]
        hyphen_total = Image.file_name.count("-")
        hyphen_count = 0
        final_file = ""
        for char in Image.file_name:
            if char == "-":
                hyphen_count += 1
            if not hyphen_count == hyphen_total:
                final_file += char

        Image.file_name = final_file
        Image.file_name += ext  # once the file name is obtained, append the file's extension


def image_resolution(attribute, Image):
    if "width=" in attribute:
        Image.image_resized_resolution[0] = attribute[7:-3]
    if "height=" in attribute:
        Image.image_resized_resolution[1] = attribute[8:-1]


def bibliography_pairings(web_page):               #pairing the information together that is in each row of the bibliography table
    split_tags = []                                 #empty list before we start to split tags
    tags = web_page.select("table tbody tr td p")    #goes down into the html until we get to the information we are trying to extract
    for row in tags:
        split_tags.append(str(row).split("\n"))

    for tag in split_tags:  # split the tags and use a stack to store the data
        # print(tag)
        s = Stack()
        word = ""
        variable1 = ""
        variable2 = ""
        for link in tag:
            for char in link:   #breaks up the 1 hugee link into smaller links
                if char == "<":
                    s.push("<")     #scans through characters to look for < or >
                if char == ">":
                    s.pop()
                else:
                    if s.size() == 0:  #will print only the words within the link/tag
                        word += char

            print(word)








#         for every <td> tag append text between <td> and </td>
#         store each string of data in a queue
#         iterate through bibliography queue
#   dequeue two items at a time(so they will be in correct pairs,
#   combining them as a tuple and appending to a list


def write_csv(dict):
    with open('images.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile)
        csv_data = [["Filename", "Transcription", "Upload Date", "Resolution"]]
        for image in dict.keys():
            csv_data.append([dict[image].file_name, dict[image].transcription,
                             dict[image].upload_date, dict[image].image_resized_resolution[0] + "x" +
                             dict[image].image_resized_resolution[1]])
        filewriter.writerows(csv_data)
        csvfile.close()


def main():
    # path = input("Please enter the file path to the directory where the html files are stored: ")
    path = "/Users/bereacollege/Documents/internship/PMSS_Scraper/html/"
    f = open(path + "EVELYN K. WELLS - PINE MOUNTAIN SETTLEMENT SCHOOL COLLECTIONS.html")
    web_page = BeautifulSoup(f, 'html.parser')
    # pmss_images = {}
    # for image in web_page.find_all('img'):
    #     temp = Image()
    #     for attribute in str(image).split():
    #
    #         # this is for pulling out the id that will be used for linking images and captions
    #         caption_link(attribute, temp)
    #
    #         # this is to pull the filename out of the html
    #         image_file_path_info(attribute, temp)
    #
    #         image_resolution(attribute, temp)
    #
    #         # Using the temporary variable's information to copy over to a proper variable
    #     if temp.file_name != "cropped.jpg":
    #         pmss_images[temp.file_name] = copy.copy(temp)
    # for image in pmss_images.keys():
    #     print(image + ": ")
    #     pmss_images[image].list_images()
    #     print()
    #
    # write_csv(pmss_images)
    bibliography_pairings(web_page)


if __name__ == "__main__":
    main()
