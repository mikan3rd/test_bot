
import re

text = '''
SMILE
SWEET
SISTER
SADISTIC
SURPRISE
SERVICE
SUPER A.I

https://t.co/KYySnjWhTO

#KizunaAI https://t.co/abcdefg https://t.co/uSzNKqU2JI'''

length = len(text)
print(length)

url_list = re.findall('https://t.co/\S*', text)
print(url_list)
text = text[:-(len(url_list[-1]))]
print(text)


# over_len = length - 125

# if over_len > 0:
#     url_list = re.findall('https://t.co/\S*', text)
#     print(url_list)
#     text = text[:-(over_len + len(url_list[-1]))] + "... " + url_list[-1]
#     text = re.sub('(http|#|@)\S*\.\.\.', '...', text)

#     print(text)
