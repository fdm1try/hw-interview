import email
import os
import re
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from imapclient import imap_utf7


RE_EMAIL_ADDRESS = re.compile(r'^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$')


class InvalidEmailAddress(Exception):
    def __str__(self):
        return 'Invalid email address!'


class NoRecipientSpecified(Exception):
    pass


class MailBox:
    """
    Этот класс предоставляет возможность получения и отправки писем,
    а также получения списка папок в электронном почтовом ящике.
    """
    def __init__(self, login: str, password: str,
                 smtp_server: str = 'smtp.gmail.com', imap_server: str = 'imap.gmail.com', use_ssl=True):
        """
        :param login: логином является e-mail адрес
        :param password: пароль к почтовому ящику
        :param smtp_server: адрес SMTP сервера в формате адрес:порт
        (порт можно не указывать, тогда будет установлен стандартный номер порта)
        :param imap_server: адрес IMAP сервера в формате адрес:порт
        :param use_ssl: использовать ли SSL
        """
        self.login = login.strip()
        if not RE_EMAIL_ADDRESS.match(self.login):
            raise InvalidEmailAddress
        self.use_ssl = use_ssl
        self.password = password
        smtp_parts = smtp_server.split(':')
        self.smtp_address = smtp_parts[0]
        self.smtp_port = int(smtp_parts[1]) if len(smtp_parts) > 1 else (587 if use_ssl else 25)
        imap_parts = imap_server.split(':')
        self.imap_address = imap_parts[0]
        self.imap_port = int(imap_parts[1]) if len(imap_parts) > 1 else (993 if use_ssl else 143)
        self._imap_client = None

    def __del__(self):
        if self._imap_client:
            try:
                self._imap_client.close()
                self._imap_client.logout()
            except Exception:
                pass

    def _get_imap_client(self) -> imaplib.IMAP4 | imaplib.IMAP4_SSL:
        if self._imap_client:
            return self._imap_client
        client_type = imaplib.IMAP4_SSL if self.use_ssl else imaplib.IMAP4
        self._imap_client = client_type(host=self.imap_address, port=self.imap_port)
        self._imap_client.login(user=self.login, password=self.password)
        return self._imap_client

    def send_message(self, subject: str, message_text: str, recipents: List[str]):
        """
        Отправляет письмо

        :param subject: Тема письма
        :param message_text: Текст письма
        :param recipents: список адресатов
        :return: None
        """
        if not len(recipents):
            raise NoRecipientSpecified()
        for recipient in recipents:
            if not RE_EMAIL_ADDRESS.match(recipient):
                raise InvalidEmailAddress(recipient)
        message = MIMEMultipart()
        message['From'] = self.login
        message['To'] = ', '.join(recipents)
        message['Subject'] = subject
        message.attach(MIMEText(message_text))
        client = smtplib.SMTP(self.smtp_address, self.smtp_port)
        client.ehlo()
        if self.use_ssl:
            client.starttls()
            client.ehlo()
        client.login(user=self.login, password=self.password)
        client.sendmail(from_addr=self.login, to_addrs=recipents, msg=message.as_string())
        client.quit()

    def get_labels(self) -> List[str]:
        """
        :return: Список папок почтового ящика
        """
        client = self._get_imap_client()
        resp_code, items = client.list()
        if resp_code != 'OK':
            return False
        if not items or not len(items):
            return None
        return [imap_utf7.decode(item).split('"')[-2] for item in items]

    def get_messages(self, label: str = 'INBOX', count: int = 0, search_criterion: str = 'ALL', sort_asc=False) -> \
            None | List[email.message.Message]:
        """
        Получает список сообщений в указанной папке

        :param label: имя папки
        :param count: количество писем
        :param search_criterion: критерий поиска
        :param sort_asc: сортирует письма от первого полученного к последнему.
        :return: Список электронных писем, в случае ошибки вернет False
        """
        client = self._get_imap_client()
        label = imap_utf7.encode(label)
        client.select(mailbox=label, readonly=True)
        resp_code, items = client.uid('search', None, search_criterion)
        if resp_code != 'OK':
            return False
        if not len(items):
            return []
        messages = []
        message_uids = items[0].split() if sort_asc else list(reversed(items[0].split()))
        for mail_uid in message_uids[:count] if count else message_uids:
            resp_code, data = client.uid('fetch', mail_uid, '(RFC822)')
            raw_email = data[0][1]
            messages.append(email.message_from_string(raw_email.decode()))
        return messages
