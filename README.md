# ESSU Attendance System with RFID
* made with django framework and esp32 for rfid processing

![alt text](https://github.com/CSSO-Linux-User-Group-ESSU/Attendance-with-ESP-RFID/blob/main/my_page.png?raw=true)

# Getting Started and Instaling
## Clone repository

```bash
git clone https://github.com/CSSO-Linux-User-Group-ESSU/Attendance-with-ESP-RFID.git
```
## Go to Directory

```bash
cd Attendance-with-ESP-RFID
```
## Create Virtual Environment and activate

On Linux/Mac
```bash
python -m venv venv
source venv/bin/activate
```
On Windows
```bash
python -m venv venv
venv\Scripts\activate
```
## Install requirements

```bash
pip install -r requirements.txt
```
## Migrate and collectstatic

```bash
python manage.py makemigrations attendance_app
python manage.py makemigrations student_app
python manage.py migrate
python manage.py collectstatic
```

## Run server

```bash
python manage.py runserver
```
