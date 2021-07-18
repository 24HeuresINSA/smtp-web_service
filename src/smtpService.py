import smtplib
import ssl
import email.mime.multipart
import email.mime.text
import os
import json
import dns.resolver
import re
import multiprocessing


class SmtpSender:
    def __init__(self, sender_email, sender_password, receiver_email, subject, body):
        self.port = 465  # smtp server port
        self.smtpServer = "smtp.gmail.com"  # smtp server host
        self.senderEmail = sender_email  # From email
        self.senderPassword = sender_password  # From email password for smtp connection
        self.receiverEmail = receiver_email  # Receiver email list
        self.subject = subject  # Email subject
        self.body = body  # Email body
        self.EMAIL_REGEX = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        self.emailCheckList = self.fastVerifyEmails()  # List of bool to know wrong emails
        # self.emailCheckList = [self.verifyEmail(mail) for mail in self.receiverEmail] # List of bool to know wrong emails
        self.message = self.messageCrafter()  # The generating mail

    def __str__(self):
        return self.message.as_string()

    def messageCrafter(self):
        """
        Generate the email from
        self.senderEmail
        self.cleanWrongEmails()
        self.subject
        self.body
        :return:
        """
        message = email.mime.multipart.MIMEMultipart("alternative")
        message["From"] = self.senderEmail
        message["Bcc"] = ";".join([mail for mail in self.cleanWrongEmails()])
        message["Subject"] = self.subject
        message.attach(email.mime.text.MIMEText(self.body, "html"))
        return message

    def verifyEmail(self, mail):
        """
        Function to verify if the mail is correct
        First, check the structure with self.EMAIL_REGEX
        Second, check if the domain have a MX record
        :param mail: mail to check
        Example : "foo@bar.net"
        :return: boolean if mail is correct or not
        """
        if re.match(self.EMAIL_REGEX, mail):
            try:
                dns.resolver.resolve(mail[mail.find('@') + 1:], rdtype=dns.rdatatype.MX)
                return True
            except (dns.resolver.NoAnswer, dns.resolver.Timeout):
                return False

    def fastVerifyEmails(self):
        """
        Multiprocessing implementation of self.verifyEmail
        Take list of self.receiverEmail
        :return: list of boolean if mail is correct or not
        """
        pool = multiprocessing.Pool()
        result = pool.map(self.verifyEmail, self.receiverEmail)
        return result

    def cleanWrongEmails(self):
        """
        Clean the list of the wrong emails
        Take list of self.receiverEmail
             list of boolean self.emailCheckList
        :return: list without wrong emails
        """
        return [self.receiverEmail[index] for index in range(len(self.receiverEmail)) if self.emailCheckList[index]]

    def getWrongEmails(self):
        """
        Get the wrong email in self.receiverEmail list
        :return: list of wrong emails
        """
        return [self.receiverEmail[index] for index in range(len(self.receiverEmail)) if not self.emailCheckList[index]]

    def sendEmail(self):
        """
        Connect to smtp sever then send email
        :return: string to say if mail is send or not
        """
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtpServer, self.port, context=context) as server:
            try:
                server.login(self.senderEmail, self.senderPassword)
            except smtplib.SMTPAuthenticationError as e:
                return "SMTP authentication error... \n \n" + str(e)
            server.send_message(self.message)
        return "Email sent !"


if __name__ == '__main__':
    credentials = json.loads(os.getenv("CREDENTIALS"))
    for account in credentials.items():
        if account[0] == "overbookd@24heures.org":
            accountEmail = account[0]
            accountPassword = account[1]
        else:
            raise ValueError("No valid account")

    _mail = SmtpSender(accountEmail,
                       accountPassword,
                       ["titouanjoseph@gmail.com", "titouanjoseph@hotmail.fr", "foo@bar.net"],
                       "Test de mail groupe",
                       "Bonjour monde")
    print(_mail.cleanWrongEmails())
    print(_mail.getWrongEmails())
    print(_mail)
    # _mail.sendEmail()
