import re

line = '你 好'

regex_str = "(你\S好)"
match_obj = re.match(regex_str,line)
if match_obj:
    print(match_obj.group(1))
