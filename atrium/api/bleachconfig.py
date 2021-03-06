import bleach

ALLOWED_TAGS = bleach.ALLOWED_TAGS + [
    'div', 'span', 's', 'u', 'img', 'br'
]

ALLOWED_STYLES = bleach.ALLOWED_STYLES + [
    'font-weight', 'font-family', 'font-size'
]

ALLOWED_ATTRIBUTES = bleach.ALLOWED_ATTRIBUTES
ALLOWED_ATTRIBUTES['*'] = ['style']
ALLOWED_ATTRIBUTES['img'] = ['src', 'alt']
