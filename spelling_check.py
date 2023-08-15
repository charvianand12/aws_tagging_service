from rapidfuzz import fuzz, process
from textblob import TextBlob
from spellchecker import SpellChecker
from valid_keys import valid_keys


def check_spelling(input_item):
    corrected_words = []

    best_match = list(process.extractOne(input_item, valid_keys, scorer=fuzz.ratio))
    print(best_match)
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
