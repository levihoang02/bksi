import html
from bs4 import BeautifulSoup

def decode_html(text, remove_tags=True):
    decoded_text = html.unescape(text)
    decoded_text = html.unescape(decoded_text)
    if remove_tags:
        decoded_text = BeautifulSoup(decoded_text, "html.parser").get_text()
    
    return decoded_text