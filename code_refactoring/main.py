from code_refactoring.mail_box import MailBox

EMAIL_LOGIN = 'login@gmail.com'
EMAIL_PASSWORD = 'qwerty'
EMAIL_HEADER_FILTER = None

if __name__ == '__main__':
    subject = 'Subject'
    message = 'Message'
    recipients = ['vasya@email.com', 'petya@email.com']
    mail_box = MailBox(login=EMAIL_LOGIN, password=EMAIL_PASSWORD)
    # send message
    mail_box.send_message(subject=subject, message_text=message, recipents=recipients)
    # recieve
    folders = mail_box.get_labels()
    criterion = f'(HEADER Subject "{EMAIL_HEADER_FILTER}")' if EMAIL_HEADER_FILTER else 'ALL'
    emails = mail_box.get_messages(count=1, search_criterion=criterion)
    email_message = emails[0] if len(emails) else None
    # end receive

