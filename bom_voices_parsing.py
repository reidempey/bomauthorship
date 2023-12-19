from bs4 import BeautifulSoup
import csv
import re

keep_going = True
NULL_REF_REGEX = r'(?:\d )?\w+\.? 0:?\d{1,2}'
SCRIPTURE_REGEX = r'(?:\d\s)?\w+\.? \d{1,2}:\d{1,2}'
NAME_REGEX = r'\((\w+.?) »'

def robs_filter(tag):
    global keep_going  # allow this function to assign values to a global variable
    if keep_going and not (tag.name == 'p' and (tag.get('st') == 'Hd1' or 
                                                tag.get('st') == 'Hd2' or 
                                                tag.get('st') == 'Hd3' or
                                                tag.get('st') == 'Hd4' or
                                                tag.get('st') == 'h')):
        return True
    else:
        keep_going = False
        return False

def text_cleaner(text, null_regex=NULL_REF_REGEX, scripture_regex=SCRIPTURE_REGEX):
    # print(f"Text before cleaning: {text}")
    if not text or re.search(null_regex, text):
        return None
    cleaned_text = re.sub(scripture_regex, '', text, 1) # Remove the scripture reference
    # cleaned_text = text
    # print(f"Text after cleaning: {cleaned_text}")
    return cleaned_text


def name_cleaner(name, header):
    if header == "Hd1":
        if "(SON OF MORMON)" in name:
            return None
        else:
            return change_subscript(name.lower().capitalize())
    clean_name = re.match(NAME_REGEX, name).group(1)
    clean_name = change_subscript(clean_name)
    return clean_name


def change_subscript(name):
    if "₁" in name:
        name = name[:-1] + "1"
    if "₂" in name:
        name = name[:-1] + "2"
    return name

def grab_text_from_header(data, soup, header):

    # Find all sections with 'p' tags containing the text data
    sections = soup.find_all('p', st=header)
    sections_length = len(sections)
    print(f"Grabbed {sections_length} headers of type {header}.\nGrabbing siblings:\n")

    # Iterate through each section
    for i, section in enumerate(sections):
        if i % 50 == 0:
            print(f"Grabbing siblings of header number {i} of {sections_length}")
        # Extract the name from the section
        name = section.text.strip()
        name = name_cleaner(name, header)
        if not name:
            continue

        global keep_going
        keep_going = True
        siblings = section.find_next_siblings(robs_filter)

        # Extract sentences and append them to the data list along with the name
        for sibling in siblings:
            paragraph_text = sibling.get_text(strip=True)
            if not (cleaned_text := text_cleaner(paragraph_text)):
                continue # skip line if a non-BOM-text value or blank
            data.append([name, cleaned_text])


def main():
    # Your XML data here
    with open('VoiceOrder.etax', 'r', encoding="utf-8") as f:
        file = f.read() 

    # Parse the XML
    soup = BeautifulSoup(file, "xml")

    data = []
    HEADERS = ["Hd1", "Hd2", "Hd3", "Hd4"]

    for header in HEADERS:
        grab_text_from_header(data, soup, header)

    print(f"Total verses found: {len(data)}")
    # Write the data to a CSV file
    with open('output_full_final.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Name', 'Sentence'])

        for row in data:
            csv_writer.writerow(row)

    print("CSV file created successfully.")


if __name__ == "__main__":
    main()