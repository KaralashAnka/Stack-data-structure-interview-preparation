# Задание 1: Реализация класса Stack
from typing import Any, Optional, List
import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Stack:
    """Реализация стека (LIFO - Last In First Out)"""

    def __init__(self) -> None:
        """Инициализация пустого стека"""
        self._items: List[Any] = []

    def is_empty(self) -> bool:
        """Проверка стека на пустоту.

        Returns:
            bool: True если стек пуст, False иначе
        """
        return len(self._items) == 0

    def push(self, item: Any) -> None:
        """Добавляет новый элемент на вершину стека.

        Args:
            item: элемент для добавления
        """
        self._items.append(item)

    def pop(self) -> Any:
        """Удаляет верхний элемент стека.

        Returns:
            Верхний элемент стека

        Raises:
            IndexError: если стек пуст
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> Any:
        """Возвращает верхний элемент стека, не удаляя его.

        Returns:
            Верхний элемент стека

        Raises:
            IndexError: если стек пуст
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def size(self) -> int:
        """Возвращает количество элементов в стеке.

        Returns:
            int: количество элементов
        """
        return len(self._items)


# Задание 2: Проверка сбалансированности скобок
def is_balanced_brackets(brackets_string: str) -> str:
    """Проверяет сбалансированность скобок в строке.

    Args:
        brackets_string (str): строка со скобками

    Returns:
        str: "Сбалансировано" или "Несбалансировано"
    """
    brackets_stack = Stack()

    # Словарь соответствия открывающих и закрывающих скобок
    brackets_pairs = {
        '(': ')',
        '[': ']',
        '{': '}'
    }

    # Множество открывающих скобок
    opening_brackets = set(brackets_pairs.keys())
    # Множество закрывающих скобок
    closing_brackets = set(brackets_pairs.values())

    for char in brackets_string:
        # Если символ - открывающая скобка
        if char in opening_brackets:
            brackets_stack.push(char)
        # Если символ - закрывающая скобка
        elif char in closing_brackets:
            # Если стек пуст, значит нет соответствующей открывающей скобки
            if brackets_stack.is_empty():
                return "Несбалансировано"

            # Проверяем, соответствует ли закрывающая скобка последней открывающей
            last_opening = brackets_stack.pop()
            if brackets_pairs[last_opening] != char:
                return "Несбалансировано"

    # Если в стеке остались элементы, значит есть незакрытые скобки
    if not brackets_stack.is_empty():
        return "Несбалансировано"

    return "Сбалансировано"


# Задание 3: Рефакторинг кода для работы с почтой
class EmailClient:
    """Класс для работы с электронной почтой через Gmail"""

    GMAIL_SMTP_SERVER = "smtp.gmail.com"
    GMAIL_IMAP_SERVER = "imap.gmail.com"
    SMTP_PORT = 587

    def __init__(self, login: str, password: str) -> None:
        """Инициализация клиента электронной почты.

        Args:
            login (str): email адрес
            password (str): пароль от email
        """
        self.login = login
        self.password = password

    def send_email(self, recipients: List[str], subject: str, message: str) -> bool:
        """Отправка email сообщения.

        Args:
            recipients (list): список получателей
            subject (str): тема письма
            message (str): текст сообщения

        Returns:
            bool: True если отправка успешна, False иначе
        """
        try:
            # Создание сообщения
            msg = MIMEMultipart()
            msg['From'] = self.login
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(message))

            # Подключение к SMTP серверу
            smtp_server = smtplib.SMTP(self.GMAIL_SMTP_SERVER, self.SMTP_PORT)

            # Идентификация себя серверу
            smtp_server.ehlo()

            # Включение TLS шифрования
            smtp_server.starttls()

            # Повторная идентификация как зашифрованное соединение
            smtp_server.ehlo()

            # Авторизация
            smtp_server.login(self.login, self.password)

            # Отправка сообщения
            smtp_server.sendmail(self.login, recipients, msg.as_string())

            # Закрытие соединения
            smtp_server.quit()

            return True

        except Exception as exception:
            print(f"Ошибка при отправке email: {exception}")
            return False

    def receive_email(self, header: Optional[str] = None) -> Optional[email.message.Message]:
        """Получение email сообщений.

        Args:
            header (str, optional): заголовок для поиска. Если None, получает все письма

        Returns:
            email.message.Message или None: последнее email сообщение или None при ошибке
        """
        try:
            # Подключение к IMAP серверу
            mail = imaplib.IMAP4_SSL(self.GMAIL_IMAP_SERVER)

            # Авторизация
            mail.login(self.login, self.password)

            # Получение списка папок
            mail.list()

            # Выбор папки входящих
            mail.select("inbox")

            # Критерий поиска
            if header:
                criterion = f'(HEADER Subject "{header}")'
            else:
                criterion = 'ALL'

            # Поиск писем
            search_result, data = mail.uid('search', None, criterion)

            if not data or not data[0]:
                print('Письма с указанным заголовком не найдены')
                mail.logout()
                return None

            # Получение последнего письма
            email_uids = data[0].split()
            if not email_uids:
                print('Не найдено ни одного письма')
                mail.logout()
                return None

            latest_email_uid = email_uids[-1]
            fetch_result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')

            if not email_data or not email_data[0]:
                print('Ошибка при получении письма')
                mail.logout()
                return None

            # Парсинг сырого email
            raw_email = email_data[0][1]
            if isinstance(raw_email, bytes):
                raw_email = raw_email.decode('utf-8')

            email_message = email.message_from_string(raw_email)

            # Закрытие соединения
            mail.logout()

            return email_message

        except Exception as exception:
            print(f"Ошибка при получении email: {exception}")
            return None


# Тестирование решений
if __name__ == '__main__':
    print("=== Тестирование Stack ===")

    # Создание и тестирование стека
    test_stack = Stack()

    print(f"Стек пуст: {test_stack.is_empty()}")  # True
    print(f"Размер стека: {test_stack.size()}")  # 0

    # Добавление элементов
    test_stack.push(1)
    test_stack.push(2)
    test_stack.push(3)

    print(f"Размер стека: {test_stack.size()}")  # 3
    print(f"Верхний элемент: {test_stack.peek()}")  # 3
    print(f"Удаленный элемент: {test_stack.pop()}")  # 3
    print(f"Размер стека: {test_stack.size()}")  # 2

    print("\n=== Тестирование проверки скобок ===")

    # Тестовые случаи для проверки скобок
    test_cases = [
        "(((([{}]))))",  # Сбалансировано
        "[([])((([[[]]])))]{()}",  # Сбалансировано
        "{{[()]}}",  # Сбалансировано
        "}{",  # Несбалансировано
        "{{[(])]}}",  # Несбалансировано
        "[[{())}]",  # Несбалансировано
        "",  # Сбалансировано (пустая строка)
        "()[]{}"  # Сбалансировано
    ]

    for test_case in test_cases:
        test_result = is_balanced_brackets(test_case)
        print(f"'{test_case}' -> {test_result}")

    print("\n=== Пример использования EmailClient ===")
    print("Для использования EmailClient:")
    print("1. Создайте экземпляр: client = EmailClient('your_email@gmail.com', 'your_password')")
    print("2. Отправьте письмо: client.send_email(['recipient@email.com'], 'Subject', 'Message')")
    print("3. Получите письма: email_msg = client.receive_email('Subject')")
    print("\nВнимание: Для Gmail требуется использование App Password вместо обычного пароля!")

    # Пример создания клиента (без реальных данных)
    # email_client = EmailClient('your_email@gmail.com', 'your_app_password')
    # send_success = email_client.send_email(['recipient@email.com'], 'Test Subject', 'Test Message')
    # received_email_message = email_client.receive_email('Test Subject')