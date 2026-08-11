"""
Утилиты для форматирования текста перед отправкой в Telegram.
"""

from bs4 import BeautifulSoup
import re

# Список тегов, поддерживаемых Telegram в режиме HTML
# https://core.telegram.org/bots/api#html-style
TELEGRAM_ALLOWED_TAGS = [
    "b",
    "strong",  # bold
    "i",
    "em",  # italic
    "u",  # underline - Officially, 'ins' might be better for new content, but 'u' is common.
    "s",
    "strike",
    "del",  # strikethrough
    "tg-spoiler",  # spoiler
    "a",  # link
    "code",  # inline fixed-width code
    "pre",  # pre-formatted fixed-width code block
    "tg-emoji",  # custom emoji
]


def clean_html_for_telegram(html_text: str) -> str:
    """
    Очищает HTML-строку, оставляя только теги, поддерживаемые Telegram,
    и преобразуя некоторые общие теги (например, <p>) в соответствующее форматирование.

    :param html_text: Исходная HTML-строка.
    :return: Очищенная строка, готовая для отправки в Telegram с parse_mode="HTML".
    """
    if not html_text:
        return ""

    soup = BeautifulSoup(html_text, "html.parser")

    # Обработка <p> тегов: заменяем на их содержимое + два переноса строки
    for p_tag in soup.find_all("p"):
        content = p_tag.decode_contents()  # Получаем внутреннее содержимое как строку
        if p_tag.get_text(strip=True):  # Если тег <p> не пустой
            p_tag.replace_with(content + "\n\n")
        else:
            p_tag.replace_with("\n\n")  # Если пустой, просто добавляем отступ

    # Обработка <br> тегов: заменяем на перенос строки
    for br_tag in soup.find_all("br"):
        br_tag.replace_with("\n")

    # Удаляем или преобразуем другие неподдерживаемые теги
    for tag in soup.find_all(True):  # True находит все теги
        if tag.name not in TELEGRAM_ALLOWED_TAGS:
            # Просто удаляем тег, оставляя его содержимое
            tag.unwrap()
        elif tag.name == "a":
            # Для ссылок <а> убеждаемся, что есть href, иначе удаляем тег
            if not tag.has_attr("href") or not tag["href"].strip():
                tag.unwrap()
            else:
                # Экранируем кавычки в URL, если они есть (хотя это редкость и плохая практика)
                tag["href"] = tag["href"].replace('"', "%22").replace("'", "%27")
        elif tag.name == "strong":
            tag.name = "b"  # Заменяем <strong> на <b>
        elif tag.name == "em":
            tag.name = "i"  # Заменяем <em> на <i>
        elif tag.name in ["strike", "del"]:
            tag.name = "s"  # Заменяем <strike> и <del> на <s>
        # Для <pre> можно добавить обработку lang атрибута, если нужно

    # Удаляем лишние пробелы и переносы строк в начале и конце,
    # а также заменяем множественные переносы на два (максимум для абзацев)
    cleaned_text = str(soup).strip()

    # Заменяем три и более переноса строки на два
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text


# Добавляем функцию пагинации
DEFAULT_PAGE_SIZE = (
    4000  # Максимальный размер сообщения в Telegram около 4096, берем с запасом
)


def paginate_text(
    text: str, page_number: int, page_size: int = DEFAULT_PAGE_SIZE
) -> tuple[str, int, int]:
    """
    Разбивает длинный текст на страницы для Telegram.
    Старается не разрывать слова и учитывает HTML-теги (очень упрощенно).

    :param text: Исходный текст (предполагается, что он уже прошел clean_html_for_telegram).
    :param page_number: Номер запрашиваемой страницы (1-индексированный).
    :param page_size: Максимальный размер страницы.
    :return: Кортеж (текст_страницы, текущая_страница, всего_страниц).
             Если запрошенная страница выходит за пределы, текст_страницы будет None.
    """
    if not text:
        return "", 1, 1

    parts = []
    current_pos = 0
    while current_pos < len(text):
        end_pos = current_pos + page_size
        if end_pos >= len(text):
            parts.append(text[current_pos:])
            break

        # Ищем ближайший подходящий разрыв (пробел, перенос строки) с конца
        # или конец HTML-тега, если он попадает на границу
        actual_end_pos = -1
        # Поиск пробела или переноса строки
        possible_breaks = [
            text.rfind(" ", current_pos, end_pos),
            text.rfind("\n", current_pos, end_pos),
        ]
        possible_breaks = [p for p in possible_breaks if p != -1]
        if possible_breaks:
            actual_end_pos = max(possible_breaks)

        # Попытка найти конец тега, если он близко к границе (очень упрощенно)
        # Это больше для того, чтобы не обрезать открытый тег
        closing_tag_pos = text.rfind(">", current_pos, end_pos)
        if closing_tag_pos != -1 and closing_tag_pos > actual_end_pos:
            # Если нашли закрывающий тег после последнего пробела/переноса, но до конца среза
            # и если есть открывающий тег, который он может закрывать в этом чанке
            opening_tag_pos = text.rfind("<", current_pos, closing_tag_pos)
            if (
                opening_tag_pos != -1 and text[opening_tag_pos + 1] != "/"
            ):  # Убедимся, что это не закрывающий тег
                # Проверим, что между открывающим и закрывающим тегами нет других открывающих без закрывающих
                temp_chunk = text[opening_tag_pos : closing_tag_pos + 1]
                open_tags = temp_chunk.count("<") - temp_chunk.count("</")
                if (
                    open_tags <= 1
                ):  # Позволяем один незакрытый тег, если он начался в этом чанке
                    actual_end_pos = closing_tag_pos + 1

        if (
            actual_end_pos == -1 or actual_end_pos <= current_pos
        ):  # Если не нашли пробел/перенос или закрывающий тег
            actual_end_pos = end_pos  # Режем как есть

        parts.append(text[current_pos:actual_end_pos])
        current_pos = actual_end_pos

    total_pages = len(parts)
    if not 1 <= page_number <= total_pages:
        return "Страница не найдена.", page_number, total_pages  # Или None

    return parts[page_number - 1].strip(), page_number, total_pages
