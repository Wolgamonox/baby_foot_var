# Baby foot VAR

This software is a way to see replays of your great, totally controlled, table football goals using automatic infrared ball detection and your smartphone.

## Principle

The principle is to detect when the ball goes into the goal using a infrared distance sensor which will tell a computer that there was a goal. The computer, which is connected to a smartphone that acts as a webcam, then recovers the last 10 seconds (more or less this is up to you) to save them and display them back to the players.

## Requirements

### 1) For the manual replays

1. A working laptop (works on windows haven't tested the other ones)
2. At least one smartphone with a camera
3. A table soccer and some friends

### 2) For the automatic replays 

4. All of the above
5. A fairly simple circuit with :
	- Arduino Nano (or any arduino really)
	- 2 IR sensors (I've used [these](https://www.christians-shop.de/IR-Infrared-Obstacle-and-Distance-Sensor-Flying-Fish))
	- Cables (roughly 3-4 meters) to be able to position the IR sensors nicely in the goals.

## Instructions

### 1) Software Installation

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
3. You'll also need a working [VLC installation](https://www.videolan.org/vlc/).
4. To launch the program just use this command : 
`py main.py`
To connect more than one camera you'll need to call the program with the desired number of cameras (up to 3)
`py main.py -c <number_of_cameras>`

###  2) Install droidcam on the smartphone
Install droidcam app on your smartphone (available for Android and iOS). It's free.

### 3) Usage
In order to connect the smartphone(s), they'll have to be on the same wifi network as the computer. Open the droidcam app on the smartphone(s) and add the IP address shown on the phone using the "Connect Webcam(s)" button in the program.
