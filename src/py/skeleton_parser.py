
"""
FILE: skeleton_parser.py
------------------
Skeleton parser for programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0 or money == "NULL":
        return money
    return sub(r'[^\d.]', '', money)

def escapeQuote(string):
    if string == None:
        return string
    return '\"' + sub(r'\"','\"\"',string) + '\"'

"""
Schema of Item table is
Items (ItemID, SellerID, Name, Buy_Price, First_Bid, Currently,
Number_of_Bids, Started, Ends, Description)
"""
def parseItem(dictionary):
    with open("../../tmp/items.dat", "a") as f:
        item = []
        item.append(dictionary["ItemID"])
        item.append(dictionary["Seller"]["UserID"])
        item.append(escapeQuote(dictionary["Name"]))
        item.append(transformDollar(dictionary.get("Buy_Price", "NULL")))
        item.append(transformDollar(dictionary["First_Bid"]))
        item.append(transformDollar(dictionary["Currently"]))
        item.append(dictionary["Number_of_Bids"])
        item.append(transformDttm(dictionary["Started"]))
        item.append(transformDttm(dictionary["Ends"]))
        item.append(escapeQuote(dictionary["Description"]))
        f.write("|".join(map(lambda s: s or "", item)))
        f.write("\n")

"""
Schema of User table is
User (UserID, Rating, Location, Country)
"""
def parseUser(dictionary):
    with open("../../tmp/users.dat", "a") as f:
        bids = dictionary.get("Bids")
        users = set()
        if bids != None:
            for bid in bids:
                info = []
                bidder = bid["Bid"]["Bidder"]
                info.append(bidder["UserID"])
                info.append(bidder["Rating"])
                info.append(escapeQuote(bidder.get("Location", "NULL")))
                info.append(escapeQuote(bidder.get("Country", "NULL")))
                users.add("|".join(info))

        seller = []
        seller.append(dictionary["Seller"]["UserID"])
        seller.append(dictionary["Seller"]["Rating"])
        seller.append(escapeQuote(dictionary.get("Location", "NULL")))
        seller.append(escapeQuote(dictionary.get("Country", "NULL")))
        users.add("|".join(seller))
        f.write("\n".join(users))
        f.write("\n")

"""
Schema of Categories table is
Categories (ItemID, Category)
"""
def parseCategory(dictionary):
    with open("../../tmp/category.dat", "a") as f:
        category = ["|".join([dictionary["ItemID"], c]) \
                    for c in dictionary.get("Category")]

        f.write("\n".join(category))
        f.write("\n")

"""
Schema of Bids table is
Bids (ItemID, UserID, Time, Amount)
"""
def parseBids(dictionary):
    with open("../../tmp/bids.dat", "a") as f:
        bids = dictionary.get("Bids")
        if bids != None:
            for bid in bids:
                info = []
                info.append(dictionary["ItemID"])
                info.append(bid["Bid"]["Bidder"]["UserID"])
                info.append(transformDttm(bid["Bid"]["Time"]))
                info.append(transformDollar(bid["Bid"]["Amount"]))
                f.write("|".join(info) + "\n")

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items']
        # creates a Python dictionary of Items for the supplied json file
        for item in items:
            """
            TODO: traverse the items dictionary to extract information from the
            given `json_file' and generate the necessary .dat files to generate
            the SQL tables based on your relation design
            """
            parseItem(item)
            parseUser(item)
            parseCategory(item)
            parseBids(item)

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
        # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print("Success parsing " + f)

if __name__ == '__main__':
    main(sys.argv)
