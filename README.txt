Hello and thank you for choosing DjangoMaintained HealthNet.
HealthNet is a web based program that helps keep track of the 
hospital you are currently a patient at. It records your schedule,
prescriptions, doctors, and recent visits information.

The following are requirements to use HealthNet:
    1) Computer
    2) Internet Access
    3) Email
    4) Insurance
    5) Phone Number

The HealthNet program is all web based. You can visit the website
by going to "https://www.djangomaintained.com". Please note, the
https:// is required for security reasons as opposed to http://.

If you would like to run it locally, then you must run the following commands
in the HealthNet directory:

    python manage.py syncdb
    python manage.py populatedb
    python manage.py runserver

Once you are on the homepage, it should redirect you to a login page.
If you have an existing account, please login, otherwise proceed to
the next steps.

If you do not have an existing account, then click on "Sign Up". This
will bring you to a page to fill out some information. Complete the
form and create your account. You should now be able to login with the
information just created.

For demonstration purposes, we provide an existing account for you.
Email: admin
Password: SuperSecurePassword1234

The home page is currently just a form with your information in it.
This is going to change as we progress through the releases.

The schedule is currently set with a date/time picker. You can request 
the amount of time and doctor to have your appointment with. Once filled
out, you can add the appointment. It will show up in a schedule table 
below.

The prescriptions page has a table similar to the schedule table. However,
only a doctor can add prescriptions, so the patient can only view this table.

System logs is just a record of changes/views from a person. 

Lastly, there is a Sign Out button in the top right corner to securely log 
your account out.

We have everything for Release 1 presented.
