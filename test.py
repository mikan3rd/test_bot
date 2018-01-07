
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

#KizunaAI #キズナアイ @aichan_nel https://t.co/uSzNKqU2JI'''

length = len(text)

print(length)

over_len = length - 125

if over_len > 0:
    url_list = re.findall('https://t.co/.*', text)
    print(url_list)
    text = text[:-(over_len + len(url_list[-1]))] + "... " + url_list[-1]
    print(text)
