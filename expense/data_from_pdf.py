"""This program uses PyPDF2 module to extract information from DNB bank
statements which are text-formatting PDF files.

PyPDF2 does not have a way to extract images, charts, or other media from PDF
documents, but it can extract text and return it as a Python string.
"""
import os
import PyPDF2
import tabula
import csv
import numpy as np
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# file directory
file_dir = os.getcwd() + os.sep + 'bank_statement'
# import all files in file_dir

# read from pdf file
# pdf_file = 'Credit cards - DNB_jan1.pdf'
# pdf_obj = open(pdf_file, 'rb')
# pdf_reader = PyPDF2.PdfFileReader(pdf_obj)
# num_pages = pdf_reader.numPages
# page_obj = pdf_reader.getPage(0)
# page_text = page_obj.extractText()
# print(page_text)
# or
# table = tabula.read_pdf(pdf_file, encoding='utf-8')
# print(table)

# read from csv file
# csv_file = 'bank_statement.csv'
# csv_obj = open(csv_file, encoding='utf-8')
# csv_reader = csv.reader(csv_obj)
# for row in csv_reader:
#     print(len(row))


file_name = 'expense.csv'
# load it if a DataFrame has been saved
if os.path.exists(file_name):
    expense_df = pd.read_csv(file_name)
# process the raw data if not done
else:
    # read from txt file
    text_file = 'bank_statement.txt'
    # data = np.genfromtxt(text_file)  # this numpy method gets error if each line
    # does not have the same number of columns
    # line_list = []
    # for line in data:
    #     line_list = line
    #     print(line_list)

    data_obj = open(text_file, 'r', encoding='utf-8-sig')
    # if encoding=utf-8 gets ValueError: time data '\ufeff10.12.2018' does not
    # match format '%d.%m.%Y'
    # https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string

    # print(data_obj.read())
    dates = []  # save all dates in datetime format
    amounts = []  # save all amounts in float
    addresses = []  # save all addresses in string
    categories = []  # add a new dimension - type of expense - to each transaction
    category_all = {'Grocery': ['rema', 'kiwi', 'marked', 'extra', 'bunnpris',
                                'meny', 'groenlandtorg', 'scanasia', 'thai take'],
                    'Sport equipment': ['xxl'],
                    'Medicine & care': ['vitusapotek', 'kicks'],
                    'Restaurant': ['eik fjord'],
                    'Appliance & Furniture': ['ikea', 'jernia', 'tilbords',
                                              'kitchn', 'platekompaniet']
                }


    def categorizing(place, cate):
        """categorize the expense at this place"""
        # convert address string to lower case, remove comma and split
        place = place.lower().replace(",", "").split()
        category = []  # receive possible category
        for text in place:
            for key, value in cate.items():
                for v in value:
                    if text in v:
                        category = key
                        break
            if category:
                return category
            elif text == place[-1]:
                print("{} doesn't belong to any existing category, update your "
                      "category.".format(place))


    # read each line into pre-defined lists
    for line in data_obj:
        line_list = line.split()
        dates.append(datetime.strptime(line_list[0], '%d.%m.%Y'))
        # https://chrisalbon.com/python/basics/strings_to_datetime/
        amounts.append(float(line_list[-1].replace(",", "")))  # remove comma in
        # amount and convert to float
        # https://stackoverflow.com/questions/5180184/python-remove-comma-in-dollar-amount
        address = ' '.join(line_list[1:-1])
        addresses.append(address)  # joint the rest together as
        # the whole address
        categories.append(categorizing(address, category_all))
    # close the data file once it fulfills its purpose
    data_obj.close()

    # assert len(dates) == len(amounts) == len(addresses)
    # create a pandas DataFrame to save data of all dimensions
    # https://towardsdatascience.com/pandas-dataframe-a-lightweight-intro-680e3a212b96
    # http://pbpython.com/pandas-list-dict.html
    expense_dict = {'Date': dates, 'Place': addresses, 'Amount': amounts,
                    'Category': categories}
    expense_df = pd.DataFrame(expense_dict)
    # save pandas DataFrame to file

    expense_df.to_csv('expense.csv')
    # https://realpython.com/python-csv/#parsing-csv-files-with-the-pandas-library

# print(expense_df.info())

sns.set()
fig = plt.figure()
# sns.lmplot(x='Date', y='Amount', data=expense_df)
# sns.countplot(x='Date', data=expense_df)
# sns.kdeplot(expense_df.Amount)  # density plot
ctgr_amt = expense_df.groupby('Category')['Amount'].sum().plot(kind='bar')
# or plot.bar()
plt.title('Expense in December 2018 (NOK)', fontweight='bold', loc='left', y=1.02)
# y=1.02 controls the distance of the title to the plot
# plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = True
# plt.rcParams['ytick.left'] = plt.rcParams['ytick.labelleft'] = False
# https://stackoverflow.com/questions/34225839/groupby-multiple-values-and-plotting-results
# plt.ylabel('Expense in December 2018 (NOK)')
ax = plt.gca()
# plt.gca().axes.get_xaxis().set_visible(False)  # remove x ticks
# http://docs.astropy.org/en/stable/visualization/wcsaxes/ticks_labels_grid.html
# plt.gca().yaxis.set_label_position('right')  # does not work
ax.yaxis.tick_right()  # show y ticks on the right
# https://codeyarns.com/2015/06/29/how-to-hide-axis-of-plot-in-matplotlib/
# remove little tick lines while keep the gird on
for tic in ax.yaxis.get_major_ticks():
    tic.tick1On = tic.tick2On = False
# https://stackoverflow.com/questions/20416609/remove-the-x-axis-ticks-while-keeping-the-grids-matplotlib
plt.xlabel('')
plt.xticks(rotation=45)  # rotate x-axis tick labels
plt.tight_layout()  # make the tick labels show in full, otherwise part will be missing
# if the tick label is too long (like text label)
fig.savefig('expense.pdf', bbox_inches='tight', pad_inches=0)  # plt.savefig() will not work
# bbox_inches='tight' can help remove some white margin of the plot, pad_inches=0 will remove all
# https://codeyarns.com/2015/07/29/how-to-remove-padding-around-plot-in-matplotlib/
plt.show()
