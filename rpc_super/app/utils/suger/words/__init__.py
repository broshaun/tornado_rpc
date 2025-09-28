import os
import base64
import re
import wrapt


WORDS = os.path.dirname(__file__) + "/pub_banned_words.txt"

with open(WORDS) as f:
    data = ""
    for i in f:
        data += base64.b64decode(i).decode().replace("\n","|")
    else:
        P = re.compile(data)

@wrapt.decorator
def filter_word(wrapped, instance, args, kwargs):
    '屏蔽敏感词语装饰器'
    for k, v in kwargs.items():
        if isinstance(v, str):
            kwargs[k] = P.sub(r'*',v)
    return wrapped(*args, **kwargs)
    


# @filter_word
# def test1(a):
#     print(a)

# test1(a="习近平")
