# HealthNet

HealthNet is a web-based program that helps hostpitals keep track of
everything they need for management. It records patients' and doctors'
schedules, prescriptions, admissions, discharges, and provides rich
statistics for administrators.

To effectively use HealthNet, a computer with internet access is
required. Account creation requires valid insurance information.

The HealthNet program is all web-based. You can visit the current
development website [Here](https://www.djangomaintained.com).

## Installation

If you are running HealthNet on your local machine, run the following
commands:

```bash
python manage.py syncdb
python manage.py populatedb
python manage.py runserver
```

## Usage

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
    Password: p@ssword

    Doctor:
    Email: turk@sacredheart.org
    Password: p@ssword

    Nurse:
    Email: carla@sacredheart.org
    Password: p@ssword

    Patient:
    Email: duwayne@theroc-johnson.com
    Password: p@ssword

The Home tab displays a dashboard for easy daily use. This displays a
welcome message, a notification of unread messages (if any), and a list of upcoming appointments, and a list of
prescriptions (if the user is a patient).

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
any of them will display the conversation. The "Send Message" button is used to send
a new message. Messages can be sent between one or multiple users, except between
patients only.

Admins can view two additional tabs: System and Add User.

The System tab displays a list of system statistics and all
logged system activity.

The Users tab is used to view the doctors, nurses, and patients in the
system.

## Contributors

Project Manager: 
[Harlan Haskins: harlan@harlanhaskins.com](https://github.com/harlanhaskins)

Test Liason:
Stefani Grimaldi: sg4780@rit.edu
