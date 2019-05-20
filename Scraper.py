from bs4 import BeautifulSoup
from Images import Image


def main():
    path = "/home/schmidtt/PycharmProjects/PMSS_Scraper/html/"
    f = open(path + "EVELYN K. WELLS - PINE MOUNTAIN SETTLEMENT SCHOOL COLLECTIONS.html")
    web_page = BeautifulSoup(f, 'html.parser')
    for image in web_page.find_all('img'):
        temp = Image()
        for attribute in str(image).split():
            if "aria-describedby" in attribute:
                temp.caption_link = attribute[18:-1]
                print(temp.caption_link)
        # print(str(image).split())
        # print(image)


if __name__ == "__main__":
    main()
