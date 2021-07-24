import os
import unittest
import webServer
import json


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = webServer.app.test_client()
        self.credentials = json.loads(os.getenv("CREDENTIALS"))
        self.headers = {'x-api-key': os.getenv('KEY')}

    def tearDown(self):
        pass

    def testMainPage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testVersion(self):
        versionFile = open("version", 'r')
        version = versionFile.read()
        versionFile.close()
        response = self.app.get('/version')
        self.assertEqual(response.data.decode("utf-8"), version)

    def testApiKey(self):
        response = self.app.get('/getemaillist')
        self.assertEqual(response.status_code, 401)

    def testGetemaillist(self):
        emailList = list(self.credentials.keys())
        response = self.app.get('/getemaillist',
                                headers=self.headers)
        self.assertEqual(json.loads(response.data.decode('utf-8')), emailList)

    def testVerifyemailWithNoneValidType(self):
        response = self.app.post('/verifyemail',
                                 headers=self.headers,
                                 data="string")
        self.assertEqual(response.status_code, 400)

    def testVerifyemail(self):
        emailList = ["test@24heures.org", "foo@bar.net"]
        returnList = ["foo@bar.net"]
        response = self.app.post('/verifyemail',
                                 headers=self.headers,
                                 json=emailList)
        self.assertEqual(json.loads(response.data.decode('utf-8')), returnList)


class SendEmailTest(unittest.TestCase):
    def setUp(self):
        self.app = webServer.app.test_client()
        self.credentials = json.loads(os.getenv("CREDENTIALS"))
        self.headers = {'x-api-key': os.getenv('KEY')}
        self.data = {
            "From": "overbookd@24heures.org",
            "To": [
                "mail@domain.fr",
                "foo@bar.net"
            ],
            "Subject": "Testing mail",
            "Body": "Hello world"
        }

    # executed after each test
    def tearDown(self):
        pass

    def testWithoutFrom(self):
        body = self.data.copy()
        body.pop("From")
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=body)
        self.assertEqual(response.status_code, 400)

    def testWithNoneValidFrom(self):
        body = self.data.copy()
        body["From"] = "test@24heures.org"
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=body)
        self.assertEqual(response.status_code, 400)

    def testWithoutTo(self):
        body = self.data.copy()
        body.pop("To")
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=body)
        self.assertEqual(response.status_code, 400)

    def testWithoutSubject(self):
        body = self.data.copy()
        body.pop("Subject")
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=body)
        self.assertEqual(response.status_code, 400)

    def testWithoutBody(self):
        body = self.data.copy()
        body.pop("Body")
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=body)
        self.assertEqual(response.status_code, 400)

    def testWithWrongEmails(self):
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=self.data)
        self.assertEqual(response.status_code, 400)

    def testCorrect(self):
        body = self.data.copy()
        body["To"] = ["admin@cicorella.net"]
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "Email sent !")

    def testInvalidCreds(self):
        body = self.data.copy()
        body["To"] = ["admin@cicorella.net"]
        webServer.credentials["overbookd@24heures.org"] = "password"
        response = self.app.post('/sendemail',
                                 headers=self.headers,
                                 json=body)
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
