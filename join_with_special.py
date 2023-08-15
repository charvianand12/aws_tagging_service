import re

input_string = "Hello:world/how:are|you"
delimiters = r'[/:.|]'  # Regular expression for multiple delimiters: / : . |

# Splitting the string into a list using the specified delimiters
string_list = re.split(delimiters, input_string)

print(string_list)  # Output: ['Hello', 'world', 'how', 'are', 'you']

# Joining the list back into a string using the same delimiters
output_string = ''.join([f"{s}{d}" for s, d in zip(string_list, re.findall(delimiters, input_string))]) + string_list[-1]
print(output_string)  # Output: "Hello/world:how.are|you"
