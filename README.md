# ESSU Attendance System with RFID
* made with django framework and esp32 for rfid processing
* login page
![alt text](https://github.com/CSSO-Linux-User-Group-ESSU/Attendance-with-ESP-RFID/blob/main/login_page.png?raw=true)
* main content
![alt text](https://github.com/CSSO-Linux-User-Group-ESSU/Attendance-with-ESP-RFID/blob/main/dashboard_page.png?raw=true)

# Getting Started and Installing

## 1.) Install the necessary libraries for the esp32 
#### Necessary libraries
```
<WiFi.h>
<HTTPClient.h>
<SPI.h>
<MFRC522.h>
<WebServer.h>
<ArduinoJson.h>
<EEPROM.h>
```
## 2.) Upload the code .ino into the esp32
## 3.) Run the .ino file in Arduino IDE to configure the esp32

## 4.) Clone repository

```bash
git clone https://github.com/CSSO-Linux-User-Group-ESSU/Attendance-with-ESP-RFID.git
```
## 5.) Go to Directory

```bash
cd Attendance-with-ESP-RFID
```
## 6.) Create Virtual Environment and activate

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
## 7.) Install requirements

```bash
pip install -r requirements.txt
```

## 8.) Setup MySQL database

```bash
mysql -u root -p
CREATE DATABASE database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
EXIT;
```
## 9.) Migrate and collectstatic

```bash
python manage.py makemigrations attendance_app
python manage.py makemigrations student_app
python manage.py migrate
python manage.py collectstatic
```

## 10.) Run server

```bash
python manage.py runserver
```
