# SMTP Web Service

This web service permit to simply send mail with http post request  

## How to lunch

### With source

Define 2 env var : 

|Name|Description|Value example|
|----|-----------|-------------|
|KEY|API key for x-api-key|SecretKey|
|CREDENTIALS|json with mail and password to smtp login|{"mail@24heures.org":"password", "mail2@24heures.org":"pass"}|

```bash
python3 webServer.py
```

### With docker

Create a ``.env`` file like the ``.env.example``

```bash
docker build --tag smtpWebService .
docker run -p 5000:5000 --env-file .env smtpWebService
```

## How to use

You can GET ``/`` to display a short explication of usages

There is this entry point : 

- ``/sendemail`` : a POST http request take json data like ``doc/sendemail.json``
- ``/verifyemail`` : a POST http request take list date like ``doc/verifyemail.json``
- ``/getemaillist`` : a GET http request return list of available sender mails
- ``/version`` : a GET http request return the current version
