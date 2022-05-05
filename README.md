# Baby foot VAR

This software is a way to see replays of your great, totally controlled, table football goals using automatic infrared ball detection and your smartphone.

## Principle

The principle is to detect when the ball goes into the goal using a infrared distance sensor which will tell a computer that there was a goal. The computer, which is connected to a smartphone that acts as a webcam, then recovers the last 10 seconds (more or less this is up to you) to save them and display them back to the players.

## Table of contents
[**1. Requirements**](#1-requirements)  
[**2. Instructions**](#2-instructions)  
[**3. For NTNU usage**](#3-ntnu-gløshaugen-foosbal)  
[**4. Troubleshooting**](#4-troubleshooting)

___

## 1. Requirements

### For the manual replays

1. A working laptop (works on windows haven't tested the other ones)
2. At least one smartphone with a camera
3. A table soccer and some friends

### For the automatic replays 

4. All of the above
5. A fairly simple circuit with :
	- Arduino Nano (or any arduino really)
	- 2 IR sensors (I've used [these](https://www.christians-shop.de/IR-Infrared-Obstacle-and-Distance-Sensor-Flying-Fish))
	- Cables (roughly 3-4 meters) to be able to position the IR sensors nicely in the goals.

## 2. Instructions

### 2.1 Software Installation

 1. Clone the repo
	`git clone https://github.com/Wolgamonox/baby_foot_var.git`
 2. Create a virtual environment with the required packages
	```
	cd .\baby_foot_var\
	py -m venv venv
	.\venv\Scripts\activate
	```
	```
	pip install -r requirements.txt
	```
3. You'll also need a working [VLC](https://www.videolan.org/vlc/) installation.
4. To launch the program just use this command : 
`py main.py`
To connect more than one camera you'll need to call the program with the desired number of cameras (up to 3)
`py main.py -c <number_of_cameras>`

###  2.2 Install droidcam on the smartphone
Install droidcam app on your smartphone (available for [Android](https://play.google.com/store/apps/details?id=com.dev47apps.droidcam) and [iOS](https://apps.apple.com/us/app/droidcam-webcam-obs-camera/id1510258102)). It's free.

### 2.3 Usage
In order to connect the smartphone(s), they'll have to be on the same wifi network as the computer. Open the droidcam app on the smartphone(s) and add the IP address shown on the phone using the "Connect Webcam(s)" button in the program.

****
If you don't have the arduino part, you can still use the replay


## 3. NTNU Gløshaugen foosbal
This was developped while in an exchange at NTNU in Trondheim and the table located in Sentralbygg is equipped with sensors/arduino setup aswell as a stand for the camera.

You can put your phone on the strings on the ceiling and you just have to connect the arduino (under the foosball table) and your computer with a micro-USB to USB cable and click on the "Detector connection status" text in the bottom left. The indicator should turn green once the sensors are connected.



## 4. Troubleshooting

- **Problem :** The goals are detected when they should not.
  - Check if the ball is still in the goal, don't forget to remove the ball while the replay is playing to avoid multiple detections.
  - Check if the sensor has the right sensibility:
    - it should not send signal when there is no ball
    - and should send signal when the boal is rested at the end of the goal.
- **Problem :** The phone camera is not connecting.
  - Check if the phone and the computer are on the same wifi network.
  - Check you entered the right IP address in the program.