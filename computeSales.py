#Essential imported libraries
import os.path
import time
import re

#Global dictionaries are used
afm_dict = {}   #{afm, {product_name, total_cost}}
prod_dict = {}  #{product_name, {afm, total_cost}}

#F_MAIN : THIS IS WHERE THE PROGRAM STARTS
#         the program is continuously displaying the main menu
#         after each task is completed
def main():
    action = 0
    while (action != 4):
        #Displaying Menu
        print('\n----------MENU----------')
        print('1. Read new input file')
        print('2. Print statistics for a specific product')
        print('3. Print statistics for a specific AFM') 
        print('4. Exit')
        #Asking for input preference
        action = parse(input('Give your preference: '))
        #Calling selected function based on preference
        if (action == 1):
            read_new_input_file()
        elif (action == 2):
            print_product_stats()
        elif (action == 3):
            print_afm_stats()
        elif (action == 4):
            return
        else:
            print('Input Invalid!')

#F1 : INPUT FILE READ
#     reads a file and saves receipts information so that
#     various stats can be generated
def read_new_input_file():

    #Asks user for file name and opens file if it exists
    file_name = input('Please enter file name: ')
    if (not os.path.isfile(file_name)):
        print('No such file found.')
        return
    f = open(file_name, 'r', encoding='utf-8')
    #---------------------------------------------------
    
    #Scans file, extracts receipt, analyzes its information and adds it to the dictionaries
    line = ' '
    while (line): #Repeats for every receipt
        #Step 1 - Extracts Receipt Text without dashes (EX: [ΑΦΜ: 2196911440][ΤΖΑΤΖΙΚΙ:	1	1.29	1.29][ΣΥΝΟΛΟ:	1.29])
        enabled, line, receipt_string = extract_receipt_from_text(line, f)
        if (receipt_string == ""):
            continue
        #Step 2 - Analyzes Receipt Information (EX: {[ΑΦΜ][2196911440]}{[ΤΖΑΤΖΙΚΙ][1][1.29][1.29]}{[ΣΥΝΟΛΟ][1.29]})
        enabled, temp_dict, temp_afm = analyze_receipt(enabled, receipt_string)
        #Step 3 - Adds Data to Dictionaries if receipt is enabled
        add_data_to_dicts(enabled, temp_dict, temp_afm)
    #--------------------------------------------------------------------------------------
    f.close()

#F2 : PRINTS STATISTICS FOR A SPECIFIC PRODUCT: 
#     displays total cost of product that has been ordered for each AFM
def print_product_stats():
    #Asks product name, converts it to UPPER CASE and checks if exists
    product_name = input("Please enter product name: ").upper()
    if (product_name not in prod_dict):
        return
    #Creates new sorted dict (by key: afm) and prints each afm with its corresponding cost
    sorted_prod_dict = sorted((prod_dict[product_name]).items())
    for k, v in sorted_prod_dict:
        print(k, "%.2f" % v)

#F3 : PRINTS STATISTICS FOR A SPECIFIC AFM: 
#     displays total cost of each product ordered by this specific AFM
def print_afm_stats():
    #Asks afm number and checks if exists
    afm_number = input("Please enter afm number: ")
    if (afm_number not in afm_dict):
        
        return
    #Creates new sorted dict (by key: product name) and prints each product name with its corresponding cost
    sorted_afm_dict = sorted((afm_dict[afm_number]).items())
    for k, v in sorted_afm_dict:
        print(k, "%.2f" % v)

#-------------------------------------------
#INTERMEDIATE FUNCTIONS
#-------------------------------------------

#f_extract_receipt_from_text : reads each line and tries to construct a string 
#                              (receipt_string) with valid receipt information
def extract_receipt_from_text(line, f):
    line = f.readline() #Reads Line
    enabled = True #Each receipt starts as a valid one. If a mistake is detected, it becomes invalid (false)
    receipt_string = "" #This is the string where the receipt information will be stored. We only store the 
                        #internal part of a receipt (without the dashes)
    line_counter = 0  #Needed to check which line of a specific receipt we are in
    while (line and line != "\n"): #Repeats every line in receipt
        #Dashes have to be in first line, ΑΦΜ has to be in second line
        if ((line_counter == 0 and "-" not in line) or (line_counter == 1 and "ΑΦΜ" not in line)):
            break
        #Inserts line into receipt_string
        if ("-" not in line):
            receipt_string += line
        #After this line we exit the loop
        if (line[0:6] == "ΣΥΝΟΛΟ"):
            break
        else: #Proceeds to next line
            line_counter += 1
            line = f.readline()
    return enabled, line, receipt_string

#f_analyze_receipt: takes as input a receipt_string and analyzes its information
#
def analyze_receipt(enabled, receipt_string):
    temp_lines = receipt_string[:-1].splitlines() #Splits based on new line character
    #Evaluating first (afm) line
    temp_afm = temp_lines[0].split(":") #Splits based on ":" [ΑΦΜ: 7370682019] -> [ΑΦΜ][ 7370682019]
    temp_afm[1] = str(temp_afm[1]).strip() #Removes whitespace on afm number
    if (len(temp_afm[1]) != 10 or parse(temp_afm[1]) == -1): #Checking for: afm being 10 digits long
        enabled = False
    #Evaluating intermediate (product) lines
    temp_sum = 0.0
    temp_dict = {} #temporary dictionary to store {product_name, accumulative_cost}
    for i in range(1, len(temp_lines)-1):
        temp_products = re.split(':|\t| ', temp_lines[i]) #Splits every ":, tab or space" 
        #print(temp_products)
        real_temp_products = [] #real_temp_products[0]= name,  real_temp_products[1]= quantity
        for j in range(len(temp_products)):
            #print(temp_products[j])
            if (temp_products[j] != ""): 
                real_temp_products.append(temp_products[j])
        # print(real_temp_products)
        #Evaluating product multiplication
        if (round(float(real_temp_products[1]) * float(real_temp_products[2]), 2) != round(float(real_temp_products[3]), 2)):
            enabled = False
        temp_sum += round(float(real_temp_products[3]), 2)
        #Insert data to temp_dict. If product already exists, adds up to the current cost
        if (real_temp_products[0].upper() in temp_dict):
            temp_dict[real_temp_products[0].upper()] += round(float(real_temp_products[3]), 2)
        else:
                temp_dict[real_temp_products[0].upper()] = round(float(real_temp_products[3]), 2)
    #Evaluating last (total) line
    temp_total = temp_lines[len(temp_lines)-1].split(":") # temp_total[1] is the actual total amount
    if ("ΣΥΝΟΛΟ" not in temp_total[0] or round(float(temp_total[1]), 2) != round(temp_sum, 2)): #Checking for: correct sum and sum text
        enabled = False
    #Returns
    return enabled, temp_dict, temp_afm[1]

#f_add_data_to_dicts: If receipt is enabled (is valid), this function fills up
#                     the receipt data into the 2 dictionaries
def add_data_to_dicts(enabled, temp_dict, temp_afm):
    if (enabled == True): #If receipt is valid
        for k in temp_dict.keys(): #For each product_name in temp_dict

            #Filling up afm_dict data (#No3 - {afm, {product_name, total_cost}})
            if (temp_afm in afm_dict): #if afm already exists
                if (k in afm_dict[temp_afm]): #if product_name already exists then adds up product cost
                    afm_dict[temp_afm][k] += temp_dict[k]
                    afm_dict[temp_afm][k] = round(afm_dict[temp_afm][k], 2)
                else: #if product_name doesn't exist, just add another product (with its cost)
                    afm_dict[temp_afm][k] = temp_dict[k]
            else: #if afm doesn't exist, add another afm with a product_name and cost
                afm_dict[temp_afm] = {}
                afm_dict[temp_afm][k] = temp_dict[k]
            #-------------------------------------------------------------------

            #Filling up prod_dict data (#No2 - {product_name, {afm, total_cost}})
            if (k in prod_dict): #if product_name already exists
                if (temp_afm in prod_dict[k]): #if afm already exists then adds up product cost
                    prod_dict[k][temp_afm] += temp_dict[k]
                    prod_dict[k][temp_afm] = round(prod_dict[k][temp_afm], 2)
                else: #if afm doesn't exist, just add another afm (with product cost)
                    prod_dict[k][temp_afm] = temp_dict[k]
            else: #if product_name doesn't exist, add another product_name with an afm and cost
                prod_dict[k] = {}
                prod_dict[k][temp_afm] = temp_dict[k]
            #-------------------------------------------------------------------

#-------------------------------------------
#UTILITY FUNCTIONS
#-------------------------------------------

#F_PARSE : Tries to convert a value into a numeric one
def parse(value):
    if (type(value) is float or type(value) is int):
        return value
    elif value.isdigit(): #if string
        return int(value) if float(value).is_integer else float(value)
    else:
        return -1

#Necessary to start program
if __name__ == "__main__":
    main()