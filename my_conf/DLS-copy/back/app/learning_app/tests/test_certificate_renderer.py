import re
from datetime import date, datetime
from io import BytesIO

from django.test import SimpleTestCase
from PIL import Image

from app.learning_app.services.certificate_renderer import (
    CertificateRenderingError,
    PdfCertificateRenderer,
)


class PdfCertificateRendererTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.renderer = PdfCertificateRenderer()

    def test_render_returns_one_page_pdf_with_embedded_fonts(self):
        pdf_bytes = self.renderer.render(
            template_bytes=self._make_template(),
            recipient_name="Иванов Иван Иванович",
            course_title="Основы безопасной работы",
            completed_at=date(2026, 8, 5),
        )

        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertEqual(len(re.findall(rb"/Type\s*/Page(?!s)", pdf_bytes)), 1)
        self.assertIn(b"Montserrat-Regular", pdf_bytes)
        self.assertIn(b"Montserrat-SemiBold", pdf_bytes)

    def test_render_handles_cyrillic_and_long_course_title(self):
        pdf_bytes = self.renderer.render(
            template_bytes=self._make_template(),
            recipient_name="Александр Константинович Петров-Сидоров",
            course_title=(
                "Организация безопасной эксплуатации производственных объектов "
                "и предупреждение чрезвычайных ситуаций"
            ),
            completed_at=date(2026, 12, 31),
        )

        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_render_accepts_repeated_whitespace(self):
        pdf_bytes = self.renderer.render(
            template_bytes=self._make_template(),
            recipient_name="  Иванов   Иван\nИванович  ",
            course_title="  Основы    обучения  ",
            completed_at=date(2026, 8, 5),
        )

        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_render_rejects_non_image_template(self):
        with self.assertRaisesMessage(
            CertificateRenderingError,
            "Шаблон сертификата повреждён",
        ):
            self.renderer.render(
                template_bytes=b"not-an-image",
                recipient_name="Иванов Иван Иванович",
                course_title="Основы обучения",
                completed_at=date(2026, 8, 5),
            )

    def test_render_rejects_wrong_template_proportions(self):
        with self.assertRaisesMessage(
            CertificateRenderingError,
            "Пропорции шаблона сертификата",
        ):
            self.renderer.render(
                template_bytes=self._make_template(size=(1000, 1000)),
                recipient_name="Иванов Иван Иванович",
                course_title="Основы обучения",
                completed_at=date(2026, 8, 5),
            )

    def test_render_rejects_blank_snapshot(self):
        with self.assertRaisesMessage(
            CertificateRenderingError,
            "ФИО получателя не может быть пустым",
        ):
            self.renderer.render(
                template_bytes=self._make_template(),
                recipient_name="  ",
                course_title="Основы обучения",
                completed_at=date(2026, 8, 5),
            )

    def test_render_rejects_datetime_instead_of_calendar_date(self):
        with self.assertRaisesMessage(
            CertificateRenderingError,
            "календарной датой без времени",
        ):
            self.renderer.render(
                template_bytes=self._make_template(),
                recipient_name="Иванов Иван Иванович",
                course_title="Основы обучения",
                completed_at=datetime(2026, 8, 5, 12, 30),
            )

    def test_render_rejects_unbreakable_text_that_does_not_fit(self):
        with self.assertRaisesMessage(
            CertificateRenderingError,
            "Текст сертификата не помещается",
        ):
            self.renderer.render(
                template_bytes=self._make_template(),
                recipient_name="Иванов Иван Иванович",
                course_title="А" * 400,
                completed_at=date(2026, 8, 5),
            )

    @staticmethod
    def _make_template(size=(1061, 1483), image_format="PNG") -> bytes:
        output = BytesIO()
        image = Image.new("RGB", size, "white")
        image.save(output, format=image_format)
        image.close()
        return output.getvalue()
