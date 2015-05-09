Thank you for choosing DjangoMaintained: HealthNet!
HealthNet is a web-based program that helps keep track of the 
hospital you are currently a patient at. It records your schedule,
prescriptions, doctors, and recent visits information.

To effectively use HealthNet, a computer with internet access is
required. Account creation requires valid insurance information.

The HealthNet program is all web-based. You can visit the website
by going to "https://www.djangomaintained.com". Please note that the
"https://" is required for security reasons as opposed to "http://".

If you are running HealthNet on your local machine, run the following
commands:
python manage.py syncdb
python manage.py populatedb
python manage.py runserver

Once you are on the homepage, it should redirect you to a login page.

If you have an existing account, please login, otherwise proceed to
the next steps.

If you do not have an existing account, then click on "Sign Up". This
will bring you to a page to fill out some basic information. Complete the
form and create your account. You should now be able to login with the
information just created.

For demonstration purposes, we provide an existing account of each type 
for you:

Admin:
Email: admin
Password: SuperSecurePassword1234

Doctor:
Email: turk@sacredheart.org
Password: SuperSecurePassword1234

Nurse:
Email: carla@sacredheart.org
Password: SuperSecurePassword1234

Patient:
Email: duwayne@theroc-johnson.com
Password: SuperSecurePassword1234

The Home tab displays a dashboard for easy daily use. This displays a 
welcome message, a notification for new messages (if there are any),
a list of upcoming appointments, and a list of prescriptions (if the
user is a patient).

The Schedule tab displays a list of upcoming appointments as well as a list of
past appointments. The "Add Appointment" button at the top of the page is
only available to patients, doctors, and admins. It prompts for a date, time,
duration, and a choice of patient (if you are a doctor) or a choice of doctor
(if you are a patient). Appointments can be edited or deleted by patients,
doctors, or admins if needed.

The Prescriptions tab displays a list of active prescriptions. A given patient
will only be able to see their prescriptions. Doctors are able to view, edit,  
and remove prescriptions of all patients. Nurses can view prescriptions of 
patients from their hospital.

The Medical Information tab displays the patient's basic profile information and 
medical information. The "Export" button is used to export the medical information
into a readable file that can be saved to the user's computer, and is only 
available to patients. It displays a security warning before exporting the file.

The Messages tab displays a list of active conversations the user is in. Selecting
any of them will display the conversation. The "Send Message" is used to send a new
message. Messages can be sent between any two types of users, except between patients.

Admins can view two additional tabs: System Log and Add User.

The System Log tab displays a list of all logged system activity.

The Add User tab is used to add doctors, nurses, and other admins to the system.

For questions, please contact:

Project Manager:
Harlan Haskins: harlan@harlanhaskins.com
Test Liason:
Stefani Grimaldi: sg4780@rit.edu