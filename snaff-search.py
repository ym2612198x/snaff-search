import json
import argparse
import codecs
import re
import time


# args
arg_parser = argparse.ArgumentParser(description='Snaffler log parser')
arg_parser.add_argument('-i', '--input', required=True, help='Filename of Snaffler log')
# arg_parser.add_argument('-o', '--output', help='Output filename, prints to stdout if none', default=None)
arg_parser.add_argument('-d', '--duplicate', help='Include duplicate entries', action="store_true", default=False)
arg_parser.add_argument('-e', '--exclude', help='List of words to exclude from results (comma separated eg. ".inc,example,etc")')
arg_parser.add_argument('-w', '--include', help='List of words to include in results (comma separated eg. "password,username,.ps1")')
arg_parser.add_argument('-n', '--names', help='Only print filenames of found items', action="store_true")
arg_parser.add_argument('-yellow', '--yellow', help='Only print yellow items', action="store_true")
arg_parser.add_argument('-green', '--green', help='Only print green items', action="store_true")
arg_parser.add_argument('-red', '--red', help='Only print red items', action="store_true")
arg_parser.add_argument('-black', '--black', help='Only print black items', action="store_true")
arg_parser.add_argument('-shares', '--shares', help='Print share info', action="store_true")
arg_parser.add_argument('-all', '--all', help='Print all items', action="store_true")
arg_parser.add_argument('-v', '--verbose', help='Show verbose messages', action="store_true", default=False)
args = arg_parser.parse_args()
categories = {}
# colour categories
if args.all:
    categories["Black"] = True
    categories["Red"] = True
    categories["Green"] = True
    categories["Yellow"] = True
else:
    categories["Black"] = args.black
    categories["Red"] = args.red
    categories["Green"] = args.green
    categories["Yellow"] = args.yellow
# excluded words
if args.exclude:
    categories["exclude"] = args.exclude.split(",")
    # remove spaces and make lowercase
    no_space_list = []
    for exclude_word in categories["exclude"]:
        exclude_word = exclude_word.replace(" ", "").lower()
        no_space_list.append(exclude_word)
    categories["exclude"] = no_space_list
else:
    categories["exclude"] = None
# included words
if args.include:
    categories["include"] = args.include.split(",")
    # remove spaces and make lowercase
    no_space_list = []
    for include_word in categories["include"]:
        include_word = include_word.replace(" ", "").lower()
        no_space_list.append(include_word)
    categories["include"] = no_space_list
else:
    categories["include"] = None
# other
categories["duplicate"] = args.duplicate
categories["verbose"] = args.verbose
categories["shares"] = args.shares


# colours
RST = '\033[0;39m'
INFO = '\033[36m'
BAD = '\033[31m'
GOOD = '\033[34m'
DETAIL = '\033[33m'
OTHER = '\033[30m'


# vars
snaffler_entries_list = []


# funcs
def banner(categories):

    print(f"""{BAD}

     _______  __    _  _______  _______  _______         _______  _______  _______  ______    _______  __   __ 
    |       ||  |  | ||   _   ||       ||       |       |       ||       ||   _   ||    _ |  |       ||  | |  |
    |  _____||   |_| ||  |_|  ||    ___||    ___| ____  |  _____||    ___||  |_|  ||   | ||  |       ||  |_|  |
    | |_____ |       ||       ||   |___ |   |___ |____| | |_____ |   |___ |       ||   |_||_ |       ||       |
    |_____  ||  _    ||       ||    ___||    ___|       |_____  ||    ___||       ||    __  ||      _||       |
     _____| || | |   ||   _   ||   |    |   |            _____| ||   |___ |   _   ||   |  | ||     |_ |   _   |
    |_______||_|  |__||__| |__||___|    |___|           |_______||_______||__| |__||___|  |_||_______||__| |__|                                                                         
     {RST}{INFO}v1.1{RST}

    """)
    print(f"{INFO}[*] Input:\t{DETAIL}{categories['input']}{RST}")
    print(f"{INFO}[*] Duplicates:\t{DETAIL}{categories['duplicate']}{RST}")
    print(f"{INFO}[*] Include:\t{DETAIL}{categories['include']}{RST}")
    print(f"{INFO}[*] Exclude:\t{DETAIL}{categories['exclude']}{RST}")
    print(f"{INFO}[*] Black:\t{DETAIL}{categories['Black']}{RST}")
    print(f"{INFO}[*] Red:\t{DETAIL}{categories['Red']}{RST}")
    print(f"{INFO}[*] Green:\t{DETAIL}{categories['Green']}{RST}")
    print(f"{INFO}[*] Yellow:\t{DETAIL}{categories['Yellow']}{RST}")
    print(f"{INFO}[*] Shares:\t{DETAIL}{categories['shares']}{RST}")
    print(f"{INFO}[*] Verbose:\t{DETAIL}{categories['verbose']}{RST}")
    print("")


def verbose_print(message):

    if args.verbose:
        print(f"{message}")


def check_snaff_file(input_file):

    is_it_json = ""
    snaffler_data = []
    with open(input_file, 'r') as file:
        try:
            data = json.load(file)
            snaffler_data = data.get('entries', [])
            is_it_json = True
        except Exception as e:
            # not a json file
            snaffler_data = ""
            is_it_json = False

    return is_it_json, snaffler_data


def get_snaff_shares_json(snaffler_json_data):

    for snaffler_entry in snaffler_json_data:
        COLOUR = ''
        # only get warning entries
        if snaffler_entry["level"] == "Warn":
            if len(snaffler_entry["eventProperties"]) != 0:
                    colour = list(snaffler_entry["eventProperties"])[0]
                    log_type = snaffler_entry["eventProperties"][colour]["Type"]
                    if log_type == "ShareResult":
                        temporary_dict = {}
                        share_path = snaffler_entry["eventProperties"][colour][log_type]["SharePath"]
                        temporary_dict["path"] = share_path
                        temporary_dict["colour"] = colour.upper()
                        if temporary_dict['colour'] == "YELLOW":
                            COLOUR = DETAIL
                        elif temporary_dict['colour'] == "GREEN":
                            COLOUR = GOOD
                        elif temporary_dict['colour'] == "RED":
                            COLOUR = BAD
                        elif temporary_dict['colour'] == "BLACK":
                            COLOUR = OTHER
                        print(f"{INFO}[*] Class:{COLOUR}\t{temporary_dict['colour']}{RST}")
                        print(f"{INFO}[*] Path:{COLOUR}\t{temporary_dict['path']}{RST}")
                        print("")


def get_snaff_shares_other(input_file):

    snaffler_log = codecs.open(input_file, 'r', encoding='utf-8', errors='ignore')
    for x in snaffler_log.readlines():
        COLOUR = ''
        # get shares from log
        if '[Share] ' in x:
            result = re.split(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z \[Share\] ", x)[1]
            share_name = re.split(r"\{\w+\}<", result)[1]
            share_name = re.split(r">\(", share_name)[0]
            share_name = share_name.rstrip()
            # get the colour bit
            colour = re.search(r"\{\w+\}", result).group()
            if colour == "{Yellow}":
                classification = "YELLOW"
                COLOUR = DETAIL
            elif colour == "{Green}":
                COLOUR = GOOD
                classification = "GREEN"
            elif colour == "{Red}":
                classification = "RED"
                COLOUR = BAD
            elif colour == "{Black}":
                classification = "BLACK"
                COLOUR = OTHER
            print(f"{INFO}[*] Class:\t{COLOUR}{classification}{RST}")
            print(f"{INFO}[*] Path:\t{COLOUR}{share_name}{RST}")
            print("")


def get_snaff_files_json(snaffler_json_data):

    for snaffler_entry in snaffler_json_data:
        # only get warning entries
        if snaffler_entry["level"] == "Warn":
            # for some reason, some entries dont have event properties
            if len(snaffler_entry["eventProperties"]) != 0:
                temporary_dict = {}
                try:
                    colour = list(snaffler_entry["eventProperties"])[0]
                    temporary_dict["colour"] = colour.upper()
                except:
                    pass
                try:
                    log_type = snaffler_entry["eventProperties"][colour]["Type"]
                    # only get file results, not shares
                    if log_type == "FileResult":
                        try:
                            full_name = snaffler_entry["eventProperties"][colour][log_type]["FileInfo"]["FullName"]
                            temporary_dict["fullname"] = full_name
                        except:
                            pass
                        try:
                            why = snaffler_entry["eventProperties"][colour][log_type]["MatchedRule"]["RuleName"]
                            temporary_dict["why"] = why
                        except:
                            pass
                        try:
                            # match context contains the extra details of why the file was logged
                            # ie. the string that triggered the collection of the file
                            # if the match context is just because of the filenmame, we dont want it
                            # so we set it to None
                            match_context = snaffler_entry["eventProperties"][colour][log_type]["TextResult"]["MatchContext"].strip()
                            entry_name = snaffler_entry["eventProperties"][colour][log_type]["FileInfo"]["Name"].strip()
                            if match_context == entry_name or match_context == full_name:
                                match_context = None
                            temporary_dict["extra"] = match_context
                        except:
                            pass
                except:
                    pass

            else:
                verbose_print("NO EVENT PROPERTIES")
                try:
                    # this is for when the log does have an eventProperties element
                    # gotta do it dirty
                    # get the {Colour} bit
                    colour = re.search(r" \{\w+\}", snaffler_entry["message"]).group()
                    if (colour == ""):
                        verbose_print("colour is null")
                        quit()
                    if colour == " {Red}":
                        found_colour = "Red"
                    elif colour == " {Green}":
                        found_colour = "Green"
                    elif colour == " {Yellow}":
                        found_colour = "Yellow"
                    elif colour == " {Other}":
                        found_colour = "Black"
                    temporary_dict["colour"] = found_colour.upper()
                    verbose_print(found_colour)
                    # get the why and extra parts dirty
                    why_extra_dirty = re.split(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z", snaffler_entry["message"])
                    why_part = re.search(r"<\w+\|", why_extra_dirty[1]).group()
                    # this leaves us with eg. KeerpPassOrKeyInCode
                    why_part = why_part.split("<")[1]
                    why_part = why_part.split("|")[0]
                    # gross but it gets us the 'extra' part
                    extra = re.split(r">\(.+\) ", why_extra_dirty[2])[1]
                    temporary_dict["why"] = why_part
                    temporary_dict["extra"] = extra
                except:
                    # just bail on the line if we cant get the stuff
                    pass
            snaffler_entries_list.append(temporary_dict)

    return snaffler_entries_list


def get_snaff_files_other(input_file):

    files = []
    snaffler_log = codecs.open(input_file, 'r', encoding='utf-8', errors='ignore')
    for x in snaffler_log.readlines():
        if '[File]' in x:
            try:
                # cut out all the time and date
                result = re.split(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z", x)
                # get the {Colour} bit
                colour = re.search(r" \{\w+\}", result[1]).group()
                if colour == " {Red}":
                    classification = "RED"
                elif colour == " {Green}":
                    classification = "GREEN"
                elif colour == " {Yellow}":
                    classification = "YELLOW"
                elif colour == " {Black}":
                    classification = "BLACK"
                # get they why part
                # dirty
                why = re.search(r"<\w+\|", x).group()
                why = why.split("<")[1]
                why = why.split("|")[0]

                # get the filename deets including any extra info at the end
                file1_raw = re.split(r">\(", result[2])
                filename =  re.split(r"\) .+$", file1_raw[1])[0]

                # try and get the extra bit from the filename
                try:
                    extras =  x = re.search(r"\).+$", file1_raw[1]).group()
                    extras = extras.split(") ")[1]
                except:
                    extras = "None"

                temporary_dict = {}
                temporary_dict["fullname"] = filename
                temporary_dict["colour"] = classification
                temporary_dict["why"] = why
                temporary_dict["extra"] = extras
                # file_list = [classification, filename, extras, why]
                files.append(temporary_dict)
            except Exception as e:
                print(f"{BAD}[-] Error:\n{DETAIL}{e}{RST}")

    return files


def trim_snaff_entries(snaffler_entries_list, categories):

    trimmed_snaffler_list = [] # final list to return
    verbose_print(f"{OTHER}[!] Snaffer list at start: {DETAIL}{len(snaffler_entries_list)}{RST}")

    # find words that match if 'include' mode is enabled
    if categories["include"]:
        included_results_filenames = []
        # include an entry if the word is in the filename bit
        verbose_print(f"{OTHER}[!] Checking filenames for matching words{RST}")
        for entry in snaffler_entries_list:
            # lowercase it to match our included words
            try:
                full_name = entry["fullname"].lower()
                if any(include_word in full_name for include_word in categories["include"]):
                    verbose_print(f"{OTHER}[!] Adding {DETAIL}{full_name}{RST} - {BAD}{include_word}{RST}")
                    included_results_filenames.append(entry)
                else:
                    continue
            except:
                pass
        # include an entry if the word is in the extra bit
        included_results_extras = []
        verbose_print(f"{OTHER}[!] Checking extras for matching words{RST}")
        for entry in snaffler_entries_list:
            # added try in case extras = None
            try:
                # lowercase it to match our included words
                extra = entry["extra"].lower()
                if any(include_word in extra for include_word in categories["include"]):
                    verbose_print(f"{OTHER}[!] Adding:\n{DETAIL}{extra}{RST}")
                    verbose_print(f"{BAD}{include_word}{RST}")
                    included_results_extras.append(entry)
                else:
                    continue
            except:
                pass
        included_results_list = included_results_filenames + included_results_extras
        trimmed_snaffler_list = included_results_list
        verbose_print(f"{OTHER}[!] Trimmed length after inclusions: {DETAIL}{len(trimmed_snaffler_list)}{RST}")
    # if include mode isn't enabled
    # just make trimmed_snaffler_list equal to snaffler_entries_list
    else:
        trimmed_snaffler_list = snaffler_entries_list

    # trim exclude words if 'exclude' mode is enabled
    if categories["exclude"]:
        list_after_filename_exclude = []
        # first, exclude a word if it's in the filename
        verbose_print(f"{OTHER}[!] Checking filenames for excluded words{RST}")
        for entry in trimmed_snaffler_list:
            try:
                # lowercase it to match our excluded words
                full_name = entry["fullname"].lower()
                if any(exclude_word in full_name for exclude_word in categories["exclude"]):
                    verbose_print(f"{OTHER}[*] Skipping:\n{DETAIL}{full_name}{RST}")
                    verbose_print(f"{BAD}{exclude_word}{RST}")
                    continue
                else:
                    verbose_print(f"{OTHER}[*] Not skipping:\n{DETAIL}{full_name}{RST}")
                    list_after_filename_exclude.append(entry)
            except:
                pass

        # now check if any exclude words are in the extra bit
        list_after_extras_exclude = []
        verbose_print(f"{OTHER}[!] Checking extras for excluded words{RST}")
        for entry in list_after_filename_exclude:
            # only check the entry if it has an 'extra' part
            try:
                # lowercase it to match our excluded words
                extra = entry["extra"].lower()
                if any(exclude_word in extra for exclude_word in categories["exclude"]):
                    verbose_print(f"{OTHER}[*] Skipping {DETAIL}{full_name}{RST} - {BAD}{exclude_word}{RST}")
                    continue
                else:
                    list_after_extras_exclude.append(entry)
            except:
                pass
        trimmed_snaffler_list = list_after_extras_exclude
        verbose_print(f"{OTHER}[!] Trimmed length after exclusions: {DETAIL}{len(trimmed_snaffler_list)}{RST}")
    # if exclude mode isn't enabled, do nothing
    else:
        trimmed_snaffler_list = trimmed_snaffler_list

    # trim unwanted colours
    colours_trimmed_list = []
    if categories["Black"] == True:
        verbose_print(f"{OTHER}[!] Including black entries{RST}")
        for entry in trimmed_snaffler_list:
            if entry["colour"] == "BLACK":
                colours_trimmed_list.append(entry)
    if categories["Red"] == True:
        verbose_print(f"{OTHER}[!] Including red entries{RST}")
        for entry in trimmed_snaffler_list:
            if entry["colour"] == "RED":
                colours_trimmed_list.append(entry)
    if categories["Green"] == True:
        verbose_print(f"{OTHER}[!] Including green entries{RST}")
        for entry in trimmed_snaffler_list:
            if entry["colour"] == "GREEN":
                colours_trimmed_list.append(entry)
    if categories["Yellow"] == True:
        verbose_print(f"{OTHER}[!] Including yellow entries{RST}")
        for entry in trimmed_snaffler_list:
            if entry["colour"] == "YELLOW":
                colours_trimmed_list.append(entry)
    trimmed_snaffler_list = colours_trimmed_list
    verbose_print(f"{OTHER}[!] Snaffler list length after colour filter: {DETAIL}{len(trimmed_snaffler_list)}{RST}")

    # if duplicate mode is wanted, do nothing and leave duplicates
    if categories["duplicate"]:
        pass
    else:
        list_of_found_filenames = []
        duplicates_removed_list = []
        for entry in trimmed_snaffler_list:
            try:
                if entry["fullname"] in list_of_found_filenames:
                    pass
                else:
                    list_of_found_filenames.append(entry['fullname'])
                    verbose_print(f"{OTHER}[!] Seen filename before: {DETAIL}{entry['fullname']}{RST}")
                    duplicates_removed_list.append(entry)
            except Exception as e:
                pass
        trimmed_snaffler_list = duplicates_removed_list
        verbose_print(f"{OTHER}[!] Snaffler list length after de-duplication: {DETAIL}{len(trimmed_snaffler_list)}{RST}")

    verbose_print(f"{OTHER}[!] Snaffler list length at end: {DETAIL}{len(trimmed_snaffler_list)}{RST}")
    verbose_print(f"")
    return sorted(trimmed_snaffler_list, key=lambda x: x["colour"])


def print_snaff_entries(snaffler_entries_list):

    for x in snaffler_entries_list:
        if x["colour"] == "BLACK":
            COLOUR = OTHER
        if x["colour"] == "RED":
            COLOUR = BAD
        if x["colour"] == "GREEN":
            COLOUR = GOOD
        if x["colour"] == "YELLOW":
            COLOUR = DETAIL
        if args.names:
            try:
                print(f"{INFO}x['fullname']")
                print("")
            except:
                pass
        else:
            print(f"{INFO}[*] Class:\n{COLOUR}{x['colour']}{RST}")
            try:
                print(f"{INFO}[*] File:\n{DETAIL}{x['fullname']}{RST}")
            except:
                pass
            try:
                print(f"{INFO}[*] Why:\n{OTHER}{x['why']}{RST}")
            except:
                pass
            try:
                print(f"{INFO}[*] Extra:\n{BAD}{x['extra']}{RST}")
            except:
                pass
            print("")
            print("")
    print("")
    print(f"{INFO}[*] Finished {DETAIL}({len(snaffler_entries_list)} items found{RST})")




# main
categories["input"] = args.input
banner(categories)

# check if we've got a json file or not
is_it_json, snaffler_data = check_snaff_file(args.input)
if is_it_json:
    print(f"{INFO}[*] Snaffler log is in JSON format")
    # print shares if wanted
    if categories["shares"]:
        get_snaff_shares_json(snaffler_data)
    snaffler_entries_list = get_snaff_files_json(snaffler_data)
else:
    print(f"{INFO}[*] Snaffler log is in standard format")
    # print shares if wanted
    if categories["shares"]:
        get_snaff_shares_other(args.input)
    snaffler_entries_list = get_snaff_files_other(args.input)

trimmed_snaffler_list = trim_snaff_entries(snaffler_entries_list, categories)
print_snaff_entries(trimmed_snaffler_list)

