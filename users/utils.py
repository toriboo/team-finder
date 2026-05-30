import io
import random
from pathlib import Path
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


def generate_avatar(initial_letter, size=(100, 100)):
	# Берём первую букву и переводим в верхний регистр
	if not initial_letter:
		first_letter = '?'
	else:
		first_letter = list(initial_letter)[0].upper()

	colors = [
		(70, 130, 180), (60, 179, 113), (255, 165, 0), (106, 90, 205),
		(255, 99, 71), (123, 104, 238), (72, 61, 139), (100, 149, 237)
	]
	bg_color = random.choice(colors)
	text_color = (255, 255, 255)

	img = Image.new('RGB', size, color=bg_color)
	draw = ImageDraw.Draw(img)

	font_path = (Path(
		settings.BASE_DIR) / 'static' / 'fonts' /
				 'Neue_Haas_Grotesk_Display_Pro_75_Bold.otf')
	try:
		font = ImageFont.truetype(str(font_path), 50)
	except Exception:
		font = ImageFont.load_default()

	# Центрируем букву
	bbox = draw.textbbox((0, 0), first_letter, font=font)
	text_width = bbox[2] - bbox[0]
	text_height = bbox[3] - bbox[1]
	position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
	draw.text(position, first_letter, fill=text_color, font=font)

	buffer = io.BytesIO()
	img.save(buffer, format='PNG')
	return ContentFile(buffer.getvalue(), name=f'avatar_{first_letter}.png')
