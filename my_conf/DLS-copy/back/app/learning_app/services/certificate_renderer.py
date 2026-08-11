from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.pdfgen.canvas import Canvas


class CertificateRenderingError(ValueError):
    """Raised when a certificate cannot be rendered from the supplied data."""


@dataclass(frozen=True)
class _TextArea:
    left: float
    top: float
    right: float
    bottom: float
    center_y: float
    initial_font_size: int
    minimum_font_size: int
    max_lines: int
    leading_factor: float
    prefer_single_line: bool = False


class PdfCertificateRenderer:
    """Render a one-page PDF certificate without ORM or storage dependencies."""

    TEMPLATE_WIDTH = 1061
    TEMPLATE_HEIGHT = 1483
    TEMPLATE_ASPECT_RATIO_TOLERANCE = 0.005
    MAX_TEMPLATE_PIXELS = 25_000_000
    SUPPORTED_TEMPLATE_FORMATS = {"JPEG", "PNG"}

    TEXT_COLOR = (0, 38 / 255, 79 / 255)
    REGULAR_FONT_NAME = "DLS-Certificate-Montserrat-Regular"
    SEMIBOLD_FONT_NAME = "DLS-Certificate-Montserrat-SemiBold"
    FONT_DIRECTORY = Path(__file__).resolve().parent.parent / "assets" / "fonts"
    REGULAR_FONT_PATH = FONT_DIRECTORY / "Montserrat-Regular.ttf"
    SEMIBOLD_FONT_PATH = FONT_DIRECTORY / "Montserrat-SemiBold.ttf"

    RECIPIENT_AREA = _TextArea(
        left=120,
        top=790,
        right=941,
        bottom=870,
        center_y=830,
        initial_font_size=38,
        minimum_font_size=24,
        max_lines=2,
        leading_factor=1.15,
        prefer_single_line=True,
    )
    COURSE_AREA = _TextArea(
        left=120,
        top=970,
        right=941,
        bottom=1160,
        center_y=1065,
        initial_font_size=32,
        minimum_font_size=22,
        max_lines=3,
        leading_factor=1.2,
    )
    DATE_AREA = _TextArea(
        left=200,
        top=1370,
        right=861,
        bottom=1425,
        center_y=1398,
        initial_font_size=26,
        minimum_font_size=26,
        max_lines=1,
        leading_factor=1,
    )

    def render(
        self,
        *,
        template_bytes: bytes,
        recipient_name: str,
        course_title: str,
        completed_at: date,
    ) -> bytes:
        """Return a one-page certificate PDF as bytes."""
        recipient_name = self._normalize_required_text(
            recipient_name, "ФИО получателя"
        )
        course_title = self._normalize_required_text(
            course_title, "Название курса"
        )
        if not isinstance(completed_at, date) or isinstance(completed_at, datetime):
            raise CertificateRenderingError(
                "Дата прохождения должна быть календарной датой без времени."
            )

        self._register_fonts()
        self._ensure_font_supports_text(self.SEMIBOLD_FONT_NAME, recipient_name)
        self._ensure_font_supports_text(self.SEMIBOLD_FONT_NAME, course_title)

        date_text = f"Сертификат выдан {completed_at:%d.%m.%Y}"
        self._ensure_font_supports_text(self.REGULAR_FONT_NAME, date_text)

        template_image = self._load_template(template_bytes)
        try:
            return self._render_pdf(
                template_image=template_image,
                recipient_name=recipient_name,
                course_title=course_title,
                date_text=date_text,
            )
        finally:
            template_image.close()

    def _render_pdf(
        self,
        *,
        template_image: Image.Image,
        recipient_name: str,
        course_title: str,
        date_text: str,
    ) -> bytes:
        """Compose a validated template and prepared text into a PDF."""

        page_height = A4[1]
        scale = page_height / template_image.height
        page_width = template_image.width * scale
        output = BytesIO()
        pdf = Canvas(
            output,
            pagesize=(page_width, page_height),
            pageCompression=1,
        )
        pdf.setFillColorRGB(*self.TEXT_COLOR)
        pdf.drawImage(
            ImageReader(template_image),
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=True,
            mask="auto",
        )

        self._draw_fitted_text(
            pdf,
            text=recipient_name,
            area=self.RECIPIENT_AREA,
            font_name=self.SEMIBOLD_FONT_NAME,
            page_height=page_height,
            scale=scale,
        )
        self._draw_fitted_text(
            pdf,
            text=course_title,
            area=self.COURSE_AREA,
            font_name=self.SEMIBOLD_FONT_NAME,
            page_height=page_height,
            scale=scale,
        )
        self._draw_fitted_text(
            pdf,
            text=date_text,
            area=self.DATE_AREA,
            font_name=self.REGULAR_FONT_NAME,
            page_height=page_height,
            scale=scale,
        )

        pdf.showPage()
        pdf.save()
        return output.getvalue()

    @classmethod
    def _load_template(cls, template_bytes: bytes) -> Image.Image:
        if not isinstance(template_bytes, bytes) or not template_bytes:
            raise CertificateRenderingError(
                "Шаблон сертификата должен быть передан как непустые bytes."
            )

        try:
            with Image.open(BytesIO(template_bytes)) as source_image:
                image_format = source_image.format
                width, height = source_image.size
                if image_format not in cls.SUPPORTED_TEMPLATE_FORMATS:
                    raise CertificateRenderingError(
                        "Поддерживаются только PNG- и JPEG-шаблоны сертификата."
                    )
                if width * height > cls.MAX_TEMPLATE_PIXELS:
                    raise CertificateRenderingError(
                        "Шаблон сертификата имеет слишком большое разрешение."
                    )

                expected_ratio = cls.TEMPLATE_WIDTH / cls.TEMPLATE_HEIGHT
                actual_ratio = width / height
                relative_ratio_difference = (
                    abs(actual_ratio - expected_ratio) / expected_ratio
                )
                if relative_ratio_difference > cls.TEMPLATE_ASPECT_RATIO_TOLERANCE:
                    raise CertificateRenderingError(
                        "Пропорции шаблона сертификата не соответствуют макету."
                    )

                source_image.load()
                if source_image.mode in {"RGBA", "LA"} or "transparency" in source_image.info:
                    rgba_image = source_image.convert("RGBA")
                    rgb_image = Image.new("RGB", rgba_image.size, "white")
                    rgb_image.paste(rgba_image, mask=rgba_image.getchannel("A"))
                    return rgb_image
                return source_image.convert("RGB")
        except CertificateRenderingError:
            raise
        except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
            raise CertificateRenderingError(
                "Шаблон сертификата повреждён или не является изображением."
            ) from error

    def _register_fonts(self) -> None:
        self._register_font(
            font_name=self.REGULAR_FONT_NAME,
            font_path=self.REGULAR_FONT_PATH,
        )
        self._register_font(
            font_name=self.SEMIBOLD_FONT_NAME,
            font_path=self.SEMIBOLD_FONT_PATH,
        )

    @staticmethod
    def _register_font(*, font_name: str, font_path: Path) -> None:
        if font_name in pdfmetrics.getRegisteredFontNames():
            return
        if not font_path.is_file():
            raise CertificateRenderingError(
                f"Не найден файл шрифта сертификата: {font_path.name}."
            )
        try:
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
        except (OSError, TTFError, ValueError) as error:
            raise CertificateRenderingError(
                f"Не удалось загрузить шрифт сертификата: {font_path.name}."
            ) from error

    @staticmethod
    def _ensure_font_supports_text(font_name: str, text: str) -> None:
        font = pdfmetrics.getFont(font_name)
        char_to_glyph = getattr(font.face, "charToGlyph", {})
        unsupported_characters = sorted(
            {
                character
                for character in text
                if not character.isspace() and ord(character) not in char_to_glyph
            }
        )
        if unsupported_characters:
            unsupported_text = "".join(unsupported_characters)
            raise CertificateRenderingError(
                f"Шрифт сертификата не поддерживает символы: {unsupported_text}"
            )

    def _draw_fitted_text(
        self,
        pdf: Canvas,
        *,
        text: str,
        area: _TextArea,
        font_name: str,
        page_height: float,
        scale: float,
    ) -> None:
        lines, font_size, leading = self._fit_text(
            text=text,
            area=area,
            font_name=font_name,
            scale=scale,
        )
        center_x = ((area.left + area.right) / 2) * scale
        center_y = page_height - area.center_y * scale
        ascent, descent = pdfmetrics.getAscentDescent(font_name, font_size)
        block_height = ascent - descent + (len(lines) - 1) * leading
        baseline = center_y + block_height / 2 - ascent

        pdf.setFont(font_name, font_size)
        for line in lines:
            pdf.drawCentredString(center_x, baseline, line)
            baseline -= leading

    def _fit_text(
        self,
        *,
        text: str,
        area: _TextArea,
        font_name: str,
        scale: float,
    ) -> tuple[list[str], float, float]:
        max_width = (area.right - area.left) * scale
        max_height = (area.bottom - area.top) * scale
        allowed_line_counts = (
            (1, area.max_lines)
            if area.prefer_single_line and area.max_lines > 1
            else (area.max_lines,)
        )

        for allowed_lines in allowed_line_counts:
            for size_in_pixels in range(
                area.initial_font_size,
                area.minimum_font_size - 1,
                -1,
            ):
                font_size = size_in_pixels * scale
                lines = self._wrap_text(
                    text,
                    font_name=font_name,
                    font_size=font_size,
                    max_width=max_width,
                )
                if not lines or len(lines) > allowed_lines:
                    continue

                leading = font_size * area.leading_factor
                ascent, descent = pdfmetrics.getAscentDescent(font_name, font_size)
                block_height = ascent - descent + (len(lines) - 1) * leading
                if block_height <= max_height:
                    return lines, font_size, leading

        raise CertificateRenderingError(
            "Текст сертификата не помещается в предусмотренную область."
        )

    @staticmethod
    def _wrap_text(
        text: str,
        *,
        font_name: str,
        font_size: float,
        max_width: float,
    ) -> list[str] | None:
        lines: list[str] = []
        current_line = ""

        for word in text.split():
            if pdfmetrics.stringWidth(word, font_name, font_size) > max_width:
                return None
            candidate = f"{current_line} {word}".strip()
            if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
                current_line = candidate
                continue
            lines.append(current_line)
            current_line = word

        if current_line:
            lines.append(current_line)
        return lines

    @staticmethod
    def _normalize_required_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise CertificateRenderingError(f"{field_name} должно быть строкой.")
        normalized_value = " ".join(value.split())
        if not normalized_value:
            raise CertificateRenderingError(f"{field_name} не может быть пустым.")
        return normalized_value
