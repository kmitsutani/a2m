from a2m.outputs.mail import (
        SmtpMailSender,
        GmailSmtpSender,
)

method_dict =dict(
    smtp=SmtpMailSender,
    gmail_smtp=GmailSmtpSender,
)
