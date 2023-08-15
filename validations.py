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
    if int(best_match[1])>= 85:
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
  
        match_string = (text)
        
    # print(best_match[1])
    return match_string



def validate_tag_key(tag_key):

    key_pattern = r'^trhc:[a-z][a-z0-9:/.-]*$'
    # key_pattern = r'^[a-z][a-z0-9:/.-]*$'
    sp_chars = ["__"," ","&","_"]

    if re.match(key_pattern, tag_key) and " " not in tag_key:
        fetched_key = tag_key
    else:
        fetched_key = tag_key.strip()
        if fetched_key.startswith("trhc:") or fetched_key.startswith("accenture"):
            fetched_key=tag_key.lower()
        else:
            fetched_key="trhc:" + fetched_key.lower()
        
        for sp_char in sp_chars:
            if sp_char in fetched_key:
                if fetched_key.startswith(sp_char) or fetched_key.endswith(sp_char):
                    fetched_key=fetched_key.replace(sp_char,"")
                else:
                    fetched_key=fetched_key.replace(sp_char,"-")
    
    correct_key = check_spelling(fetched_key)
    return correct_key
                
def validate_tag_value(tag_value,tag_key):
    
    criticality_list = ["high","medium","low","critical"]
    idle_list = ["never","automatic","manual"]
    stage_list = ["development","staging","production","management","shared","beta","pre-production"]

    fetched_value = tag_value

    if ("@" in fetched_value) or (any(char.isdigit() for char in fetched_value)):
        correct_value = fetched_value

    elif ("_" in fetched_value):
        correct_value = fetched_value.replace("_","-")
        correct_value = correct_value.lower()

    elif (tag_key == "trhc:creation-ticket") or (tag_key == "trhc:initiative-epic"):
        correct_value = fetched_value
   
    else:
        fetched_value = fetched_value.lower()
        if tag_key == "trhc:criticality":
            best_match = list(process.extractOne(fetched_value, criticality_list, scorer=fuzz.ratio))
            correct_value = best_match[0]
 
        elif tag_key == "trhc:idle-shutdown":
            best_match = list(process.extractOne(fetched_value, idle_list, scorer=fuzz.ratio))
            correct_value = best_match[0]

        elif tag_key == "trhc:stage":
            best_match = list(process.extractOne(fetched_value, stage_list, scorer=fuzz.ratio))
            correct_value = best_match[0]

        else:
            correct_value = fetched_value.lower()
            

    # print(correct_value)
    return correct_value               
                                        
                                        
                                        