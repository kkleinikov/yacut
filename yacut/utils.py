import random
import string

from yacut.constants import SHORTENED_ID_LENGTH
from yacut.models import URLMap


def get_unique_short_id(length=SHORTENED_ID_LENGTH):
    chars = string.ascii_letters + string.digits
    while True:
        new_id = ''.join(random.choices(chars, k=length))
        if not URLMap.query.filter_by(short=new_id).first():
            return new_id
