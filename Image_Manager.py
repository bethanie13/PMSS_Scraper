import os


def dir_dive():
    os.chdir("/Volumes/Elements/PMSS_ARCHIVE")
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            if name[-4:] == ".tif":
                print(name)


def main():
    dir_dive()


if __name__ == "__main__":
    main()
