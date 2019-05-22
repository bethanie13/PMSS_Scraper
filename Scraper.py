from bs4 import BeautifulSoup
from Image import Image
from Caption import Caption
import copy
import csv
# import scrapy
# from scrapy.crawler import CrawlerProcess


def image_info(page_soup):
    """
    The driver function for gathering all images and information from their tags
    :param page_soup: An instance of a Beautiful Soup object of the web page you want to get information from
    :return:
    """
    images_dict = {}
    for image in page_soup.find_all('img'):
        temp = Image()

        # this is for pulling out the id that will be used for linking images and captions
        caption_link(image, temp)

        # This is for pulling the resolution of the displayed image (not the real resolution of the original image)
        image_resolution(image, temp)

        # this is to pull the filename out of the html
        image_file_path_info(image, temp)

        if temp.file_name != "cropped.jpg":
            images_dict[temp.file_name] = copy.copy(temp)
    return images_dict


def caption_link(tag, img):
    """
    This function takes a given attribute, checks to see if it is the attribute for linking images with captions, and
    then stores that information in the instance of the Images class
    :param tag: a beautiful soup Tag object
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    img.caption_link = tag.get("aria-describedby")


def image_file_path_info(tag, img):
    """
    This function is for extracting the filename of an image from it's src filepath. In addition, we can extract the
    upload date
    :param tag: a beautiful soup Tag object
    :param img: an instance of the Images class for storing the given  information
    :return: None
    """
    file_path = tag.get("src")
    ext = file_path[-4:]
    if "." not in ext:  # If the "." is not in the extension, the extension is 4 characters long
        ext = file_path[-5:]
    file_split = file_path.split("/")
    year = file_split[-3]
    month = file_split[-2]
    img.upload_date = month + "/" + year

    img.file_name = file_split[-1]
    hyphen_total = img.file_name.count("-")
    hyphen_count = 0
    final_file_name = ""
    for char in img.file_name:
        if char == "-":
            hyphen_count += 1
        if not hyphen_count == hyphen_total:
            final_file_name += char
    img.file_name = final_file_name + ext  # once the file name is obtained, append the file's extension


def image_resolution(tag, img):
    """
    Uses the 'width' and 'height' tags to store the width and height of the current image
    :param tag: a beautiful soup Tag object
    :param img: an instance of the Image class
    :return:
    """
    img.image_resized_resolution[0] = tag.get("width")
    img.image_resized_resolution[1] = tag.get("height")


def write_csv(dict_to_write, file_name):
    """
    Uses the csv library to export all of the image's with their info to a .csv file
    :param dict_to_write: A dictionary if instances of the Image class
    :return:
    """
    with open(file_name, 'w') as csvfile:
        file_writer = csv.writer(csvfile)
        csv_data = [["Filename", "Transcription", "Upload Date", "Resolution"]]
        for image in dict_to_write.keys():
            csv_data.append([dict_to_write[image].file_name, dict_to_write[image].transcription,
                             dict_to_write[image].upload_date, dict_to_write[image].image_resized_resolution[0] + "x" +
                             dict_to_write[image].image_resized_resolution[1]])
        file_writer.writerows(csv_data)
        csvfile.close()
    return


def find_captions(page_soup):
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
    for caption in captions_dict.keys():
        for image in images_dict.keys():
            if captions_dict[caption].image_link == images_dict[image].caption_link:
                images_dict[image].caption = captions_dict[caption].caption


# class TestSpider(scrapy.Spider):
#     name = "test"
#
#     start_urls = [
#         "https://pinemountainsettlement.net/",
#     ]
#
#     def parse(self, response):
#         filename = response.url.split("/")[-1] + '.html'
#         with open(filename, 'wb') as f:
#             f.write(response.body)


def main():
    # path = input("Please enter the file path to the directory where the html files are stored: ")
    path = "/home/schmidtt/PycharmProjects/PMSS_Scraper/html/"
    file = "EVELYN K. WELLS - PINE MOUNTAIN SETTLEMENT SCHOOL COLLECTIONS.html"
    csv_name = file[:-5] + '.csv'
    f = open(path + file)
    web_page = BeautifulSoup(f, 'html.parser')
    pmss_images = image_info(web_page)
    captions = find_captions(web_page)
    image_caption_linking(captions, pmss_images)


    for image in pmss_images.keys():
        print(image + ": ")
        pmss_images[image].list_images()
        print()
    # write_csv(pmss_images, csv_name)

    # process = CrawlerProcess({
    #     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    # })
    #
    # process.crawl(TestSpider)
    # process.start()  # the script will block here until the crawling is finished

    # TODO: [Google tesseract] [Abbyy] OCR
    # TODO: What fields are absolutely needed to be filled


if __name__ == "__main__":
    main()
