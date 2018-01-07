
import re

text = '''あけましておめでとうございますლ(´ڡ`ლ)✨
バーチャルYouTuberキズナアイです！🤗
住所を知ってる友達がいなくて切なくなったりしたけど、こうしてみんなに届ければいいじゃないかと気づいた私、やっぱり今年も天才でした！🤩🤩… https://t.co/0twyLqxbhB'''

length = len(text)

print(length)

over_len = length - 125

if over_len > 0:
    url_list = re.findall('https://t.co/.*', text)
    urls = ' '.join(url_list)
    text = text[:-(over_len + len(urls))] + "... " + urls
    print(text)
    print(len(text))
