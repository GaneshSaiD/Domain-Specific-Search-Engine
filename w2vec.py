from gensim.test.utils import datapath
from gensim.models import KeyedVectors
import os.path
import csv
import time
from datetime import datetime
import configparser
import json
from config import FilesConfig
from config import CSVColumnConfig
from Crawler import *
from text_cleaning import *

def w2v_sim(url, text):
    url = url
    text = text

    save_not_crawled = "/home/ubuntu/DSSE/Not_Saved.txt"
    csv_filename = FilesConfig.csv_file_name + "Similarity.csv"
    counter = 0
    with open(csv_filename, "a") as trail_csvFile:
        file_exists = os.path.isfile(csv_filename)
        row_dict = {}
        colum_alias_dict = eval(CSVColumnConfig.colum_alias_dict)
        column_names = CSVColumnConfig.csv_column_names
        csv_writer = csv.DictWriter(trail_csvFile, fieldnames=column_names)
        if not file_exists:
            csv_writer.writeheader()
        row_dict["URL"] = url
        try:
            corpus = as_list_soup(text)
            if (
                (len(corpus) < 100)
                or ("This site can’t be reached" in corpus)
                or ("document not found" in corpus)
                or ("No document" in corpus)
                or ("page not found" in corpus)
                or ("under construction" in corpus)
            ):
                print("Not enough content in", url, " adding to not_crawled list.")
                # if the content from url is Not enough then  add it  to not_crawled list
                # saving all the urls that were not_crawled to a text file
                with open(save_not_crawled, "a") as filehandle:
                    # for listitem in not_crawled:
                    filehandle.write("%s\n" % url + "Not enough content" + "\n")
            else:
                config = configparser.ConfigParser()
                config.read("listnames_as_tuple.ini")
                all_the_lists = config.items("lists")
                for list_name, list_values in all_the_lists:
                    sim_list_300 = w2v_model_300.wmdistance(list_name, corpus)
                    wmsimilarity = 1 / (
                        1 + sim_list_300
                    )  # Similarity is the negative of the distance.

                    # Writing these results to a csv file
                    row_dict[colum_alias_dict[list_name]] = wmsimilarity
                csv_writer.writerow(row_dict)
        except Exception as ex:
            # execption_message= str(ex)
            print(
                "url passed no corpus found for url  ",
                url,
                "Exception ERROR -1 " + str(ex),
            )
            # appending the error message along with the url to a text file
            with open(save_not_crawled, "a") as filehandle:
                filehandle.write("%s\n" % url + "\n" + str(ex) + "\n")
                pass  # skip

    counter += 1
