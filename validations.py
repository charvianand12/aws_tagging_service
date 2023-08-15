import re
from rapidfuzz import fuzz, process

# from textblob import TextBlob
# from spellchecker import SpellChecker
from valid_keys import valid_keys


def check_spelling(input_item):
    # corrected_words = []

    best_match = list(process.extractOne(input_item, valid_keys, scorer=fuzz.ratio))
    # print(best_match)
    match_string = None
    if int(best_match[1]) >= 79:
        match_string = best_match[0]
    else:
        text = input_item[5:]
        # spell = SpellChecker()
        # words = text.split("-")

        # for word in words:
        #     if spell.unknown([word]):
        #         corrected_word = spell.correction(word)
        #     else:
        #         corrected_word = word

        #     if (fuzz.ratio(word, corrected_word))>95:
        #         corrected_words.append(corrected_word)
        #     else:
        #         corrected_words.append(word)

        # # corrected_words = [spell.correction(word) if spell.unknown([word]) else word for word in words]
        # corrected_text = '-'.join(corrected_words)

        # print("Original Text:", text)
        # print("Corrected Text:", corrected_text)

        match_string = text

    # print(best_match[1])
    return match_string


def validate_tag_key(tag_key):
    key_pattern = r"^trhc:[a-z][a-z0-9:/.-]*$"
    # key_pattern = r'^[a-z][a-z0-9:/.-]*$'
    sp_chars = ["__", " ", "&", "_"]

    if re.match(key_pattern, tag_key) and " " not in tag_key:
        # print("pattern matched")
        fetched_key = tag_key
    else:
        # print("pattern not matched")
        fetched_key = tag_key.strip()
        if fetched_key.startswith("trhc:") or fetched_key.startswith("accenture"):
            fetched_key = tag_key.lower()
        else:
            fetched_key = "trhc:" + fetched_key.lower()

        for sp_char in sp_chars:
            if sp_char in fetched_key:
                if fetched_key.startswith(sp_char) or fetched_key.endswith(sp_char):
                    fetched_key = fetched_key.replace(sp_char, "")
                else:
                    fetched_key = fetched_key.replace(sp_char, "-")

    correct_key = check_spelling(fetched_key)
    return correct_key


def validate_tag_value(tag_value):
    fetched_value = tag_value.lower()
    return fetched_value

    # key_pattern = r'^trhc:[a-z][a-z0-9:/.-]*$'
    # # key_pattern = r'^[a-z][a-z0-9:/.-]*$'
    # sp_chars = ["__"," ","&","_"]

    # if re.match(key_pattern, tag_key) and " " not in tag_key:
    #     # print("pattern matched")
    #     fetched_key = tag_key
    # else:
    #     # print("pattern not matched")
    #     fetched_key = tag_key.strip()
    #     if fetched_key.startswith("trhc:") or fetched_key.startswith("accenture"):
    #         fetched_key=tag_key.lower()
    #     else:
    #         fetched_key="trhc:" + fetched_key.lower()

    #     for sp_char in sp_chars:
    #         if sp_char in fetched_key:
    #             if fetched_key.startswith(sp_char) or fetched_key.endswith(sp_char):
    #                 fetched_key=fetched_key.replace(sp_char,"")
    #             else:
    #                 fetched_key=fetched_key.replace(sp_char,"-")

    # correct_value = check_spelling(fetched_value)
    # return correct_value
