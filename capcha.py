from captcha.image import ImageCaptcha
from random import randint

def generate_captcha():
    image = ImageCaptcha(width=200, height=100)
    captcha_text = str(randint(1000, 9999))
    image.generate(captcha_text)
    return captcha_text, image.write(captcha_text, 'static/images/captcha.jpg')