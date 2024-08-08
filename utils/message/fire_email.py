import os
from string import Template

import requests
from django.conf import settings


class FireEmail(object):
    def __init__(self, action: str, to_email: str, **kwargs):
        self.action = action
        self.from_name = kwargs.get("from_name", "hintmatrix")
        self.from_email = kwargs.get("from_email", settings.DEFAULT_FROM_EMAIL)
        self.to_email = to_email
        self.subject = None
        self.body_txt = None
        self.body_html = None
        self.reply_to = kwargs.get("reply_to", "support@hintmatrix.com")
        self.placeholder_data = kwargs.get("placeholder_data", dict())

        template_dir = os.path.dirname(os.path.realpath(__file__))
        template_dir += "/fire_email_templates/"
        print(template_dir)
        self.subject_path = kwargs.get(
            "subject_path", f"{template_dir}{self.action}_subject.txt")

        self.body_path_html = kwargs.get(
            "body_path_html", f"{template_dir}{self.action}_body.html")

        self.body_path_txt = kwargs.get(
            "body_path_txt", f"{template_dir}{self.action}_body.txt")

    def get_subject(self):
        if not self.subject:
            with open(self.subject_path) as fob:
                self.subject = fob.read()

        return self.subject

    def get_body_html(self):
        if not self.body_html:
            with open(self.body_path_html) as fob:
                self.body_html = fob.read()

        return self.body_html

    def get_body_txt(self):
        if not self.body_txt:
            with open(self.body_path_txt) as fob:
                self.body_txt = fob.read()

        return self.body_txt

    @staticmethod
    def prepare_template(txt, **kwargs):
        t = Template(txt)
        return t.substitute(**kwargs)

    def shoot_email(self, data: dict) -> bool:
        """
        :param data: to fill template's placeholder.
        :return: boolean
        """
        data.update(self.placeholder_data)

        try:
            subject = self.prepare_template(self.get_subject(), **data)
            txt_message = self.prepare_template(self.get_body_txt(), **data)
            html_message = self.prepare_template(self.get_body_html(), **data)
            # sender = self.from_email
            recipient = self.to_email.split(",")

            # is_fire = send_mail(
            #     subject=subject, message=txt_message, from_email=sender,
            #     recipient_list=recipient, html_message=html_message)
            # send("Your Subject", "youremail@yourdomain.com",
            #      "Your Company Name",
            #      "recipient1@gmail.com;recipient2@gmail.com",
            #      "<h1>Html Body</h1>",
            #      "Text Body", True)

            is_fire = send(
                subject=subject,
                ee_from=self.from_email, from_name=self.from_name,
                to=recipient, body_html=html_message, body_text=txt_message,
                is_transactional=True)

            if is_fire:
                return True
        except Exception as e:
            print(69, e.__str__())

        return False


class ApiClient:
    apiUri = 'https://api.elasticemail.com/v2'
    apiKey = settings.ELASTICEMAIL_API_KEY

    @staticmethod
    def request(method, url, data):
        data['apikey'] = ApiClient.apiKey
        if method == 'POST':
            result = requests.post(ApiClient.apiUri + url, data=data)
        elif method == 'PUT':
            result = requests.put(ApiClient.apiUri + url, data=data)
        elif method == 'GET':
            attach = ''
            for key in data:
                attach = attach + key + '=' + data[key] + '&'
            url = url + '?' + attach[:-1]
            result = requests.get(ApiClient.apiUri + url)

        json_my = result.json()
        print(json_my)

        if json_my['success'] is False:
            return json_my['error']

        return json_my['data']


def send(subject, ee_from, from_name, to, body_html, body_text,
         is_transactional):
    return ApiClient.request('POST', '/email/send', {
        'subject': subject,
        'from': ee_from,
        'fromName': from_name,
        'to': to,
        'bodyHtml': body_html,
        'bodyText': body_text,
        'isTransactional': is_transactional})
