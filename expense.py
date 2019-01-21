"""This script converts unstructured data from online bank to pandas DataFrame
which is convenient for data analysis.

The sample data 'bank_statement.txt' contains a number of latest transactions
from DNB online bank. The only formal method provided by the online bank to
save the data is print (in paper or pdf), which is known cumbersome to extract
data. Therefore, the data were copied to txt file (later proved that there is
no difference copying to excel. The information of each transaction, containing
date, address, and amount, is stuffed in one column for both txt and excel).

Therefore, the main task is to split the one-column structure into three
columns: date, address and amount. And then, one more dimension (or column)
called category is add to the original data, which classifies the transactions
to several categories. Further, method for visualization is provided.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


# check if the data has been converted to pandas DataFrame and saved to file
file_name = 'expense.csv'
# load it if a DataFrame has been saved
if os.path.exists(file_name):
    expense_df = pd.read_csv(file_name)
# process the raw data if not done
else:
    # read information from txt file
    text_file = 'bank_statement.txt'
    data_obj = open(text_file, 'r', encoding='utf-8-sig')
    dates = []  # save all dates in datetime format
    amounts = []  # save all amounts in float format
    addresses = []  # save all addresses in string format
    categories = []  # add a new dimension - type of expense
    # construct a category dictionary (only an example here)
    category_all = {'Grocery': ['rema', 'kiwi', 'marked', 'extra', 'bunnpris',
                                'meny', 'groenlandtorg', 'scanasia',
                                'thai take'],
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
        category = []  # to receive category
        for text in place:
            for key, value in cate.items():
                for v in value:
                    if text in v:
                        category = key
                        break
            if category:
                return category
            elif text == place[-1]:
                print("{} doesn't belong to any existing category, update "
                      "your category.".format(place))


    # split each line from raw data into pre-defined lists
    for line in data_obj:
        line_list = line.split()
        dates.append(datetime.strptime(line_list[0], '%d.%m.%Y'))
        amounts.append(float(line_list[-1].replace(",", "")))  # remove comma
        # in amount number because it cannot be used for numerical operation
        address = ' '.join(line_list[1:-1])  # except date and amount, the rest
        # text in each line is address so join them together as a whole address
        addresses.append(address)
        categories.append(categorizing(address, category_all))
    # close the data file once it fulfills its purpose
    data_obj.close()

    # create a DataFrame using a dictionary that contains the above lists
    expense_dict = {'Date': dates, 'Place': addresses, 'Amount': amounts,
                    'Category': categories}
    expense_df = pd.DataFrame(expense_dict)
    # save pandas DataFrame to csv file for future use
    expense_df.to_csv('expense.csv')

# plot using the DataFrame
sns.set()
# the plot below will show how much was spent on each category
fig = plt.figure()
ctgr_amt = expense_df.groupby('Category')['Amount'].sum().plot(kind='bar')
plt.title('Expense in December 2018 (NOK)', fontweight='bold', loc='left',
          y=1.02)  # y=1.02 controls the distance of the title to the plot
ax = plt.gca()
ax.yaxis.tick_right()  # show y ticks and labels on the right
# remove little black tick lines of the y axis while keep the gird on
for tic in ax.yaxis.get_major_ticks():
    tic.tick1On = tic.tick2On = False
plt.xlabel('')
plt.xticks(rotation=45)  # rotate x-axis tick labels
plt.tight_layout()  # make the tick labels show in full, otherwise part will
# be missing since the tick labels here are quite long
fig.savefig('expense.pdf', bbox_inches='tight')
# bbox_inches='tight' can help remove some white margin of the plot, add one
# more argument - pad_inches=0 - to remove all white margin
plt.show()
