import io
import random
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

# Константы цветов (RGB)
STEEL_BLUE = (70, 130, 180)
MEDIUM_SEA_GREEN = (60, 179, 113)
ORANGE = (255, 165, 0)
SLATE_BLUE = (106, 90, 205)
TOMATO = (255, 99, 71)
MEDIUM_PURPLE = (123, 104, 238)
DARK_SLATE_BLUE = (72, 61, 139)
CORNFLOWER_BLUE = (100, 149, 237)

# Константы для аватарки
DEFAULT_AVATAR_SIZE = (100, 100)
FONT_SIZE = 50
TEXT_COLOR = (255, 255, 255)  # белый


def generate_avatar(initial_letter, size=DEFAULT_AVATAR_SIZE):
    # Берём первую букву и переводим в верхний регистр
    if not initial_letter:
        first_letter = "?"
    else:
        first_letter = list(initial_letter)[0].upper()

    colors = [
        STEEL_BLUE,
        MEDIUM_SEA_GREEN,
        ORANGE,
        SLATE_BLUE,
        TOMATO,
        MEDIUM_PURPLE,
        DARK_SLATE_BLUE,
        CORNFLOWER_BLUE,
    ]
    bg_color = random.choice(colors)

    img = Image.new("RGB", size, color=bg_color)
    draw = ImageDraw.Draw(img)

    font_path = (
        Path(settings.BASE_DIR)
        / "static"
        / "fonts"
        / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
    )
    try:
        font = ImageFont.truetype(str(font_path), FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    # Центрируем букву
    bbox = draw.textbbox((0, 0), first_letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, first_letter, fill=TEXT_COLOR, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{first_letter}.png")
