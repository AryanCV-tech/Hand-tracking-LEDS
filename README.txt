==============================================================================
 HAND TRACKING FINGER COUNTER WITH ARDUINO LED CONTROL
==============================================================================

Author: Arian Amid
Tech:   Python, OpenCV, MediaPipe, PySerial, Arduino Uno


------------------------------------------------------------------------------
 1. ABOUT THE PROJECT
------------------------------------------------------------------------------

This project uses a webcam to detect a human hand in real time, work out
which fingers are raised, and show the result on screen. It can also send
the result to an Arduino Uno, which lights up one LED for each raised finger.

Example: if you raise only your index finger, only the second LED turns on.
If you open your whole hand, all five LEDs turn on. If you make a fist or no
hand is visible, all LEDs turn off.

This is a learning project built to practice computer vision, Python, and
communication between a computer and a microcontroller.


------------------------------------------------------------------------------
 2. FEATURES
------------------------------------------------------------------------------

- Real-time hand detection from a webcam
- Draws the 21 hand landmarks on the video
- Detects which of the 5 fingers are raised
- Shows the number of raised fingers on the video window
- Sends the finger pattern to an Arduino over USB (serial)
- Arduino turns on one LED per raised finger
- Press "q" to quit


------------------------------------------------------------------------------
 3. HOW IT WORKS
------------------------------------------------------------------------------

STEP 1 - Capture
  OpenCV reads one frame at a time from the webcam.

STEP 2 - Hand landmark detection
  Each frame is converted from BGR to RGB and passed to MediaPipe's
  HandLandmarker. It returns 21 landmark points for the hand (wrist,
  knuckles, finger joints and fingertips). Each point has an x and y
  position between 0 and 1, which are multiplied by the frame width and
  height to get pixel positions for drawing.

STEP 3 - Finger counting (my own logic)
  - Index, middle, ring and pinky: a finger is "raised" when its fingertip
    is higher on the screen (smaller y value) than the joint two landmarks
    below it. Tips: 8, 12, 16, 20. Joints: 6, 10, 14, 18.
  - Thumb: the thumb moves sideways, so x is compared instead. The thumb
    counts as "raised" when its tip (landmark 4) is farther from the base of
    the pinky (landmark 17) than the thumb joint (landmark 3).

STEP 4 - Build a message
  The result is turned into a 5-character text pattern, one character per
  finger in this order: thumb, index, middle, ring, pinky.
    1 = finger raised
    0 = finger down
  Examples:
    10000 -> only the thumb
    00100 -> only the middle finger
    11111 -> open hand
    00000 -> fist / no hand

STEP 5 - Send to Arduino
  Python sends the pattern plus a newline character over USB serial at
  9600 baud. The pattern is only sent when it changes, to avoid flooding the
  Arduino with identical messages.

STEP 6 - Arduino controls the LEDs
  The Arduino reads each message and sets LED 1 to 5 HIGH or LOW to match
  the five characters.


------------------------------------------------------------------------------
 4. THE MODEL FILE (hand_landmarker.task)
------------------------------------------------------------------------------

This project uses "hand_landmarker.task", a pretrained model bundle from
Google's MediaPipe Hand Landmarker. It is not code and not a script. It
contains two neural network models:

  1. A palm detector that finds where the hand is in the image.
  2. A hand landmark model that predicts the 21 landmark points.

The model was trained by Google and was NOT trained by me. The model only
gives landmark positions. The finger counting logic, the serial
communication and the Arduino code were written by me.

The model file is not included in this repository. Download it from:

  https://storage.googleapis.com/mediapipe-models/hand_landmarker/
  hand_landmarker/float16/1/hand_landmarker.task

(This is one single link. Remove the line breaks when you paste it.)

Place the file in the same folder as the Python script, or write its full
path in the code.


------------------------------------------------------------------------------
 5. REQUIREMENTS
------------------------------------------------------------------------------

SOFTWARE
  - Python 3 (a version supported by MediaPipe)
  - opencv-python
  - mediapipe
  - pyserial
  - Arduino IDE (to upload the Arduino sketch)

Install the Python libraries with:

  pip install opencv-python mediapipe pyserial

NOTE: the package is named "pyserial", but in code you write "import serial".
Do not install a package named just "serial". That is a different package.

HARDWARE
  - Computer with a webcam
  - Arduino Uno and USB cable
  - 5 LEDs
  - 5 resistors (about 220 ohm)
  - Breadboard and jumper wires


------------------------------------------------------------------------------
 6. WIRING
------------------------------------------------------------------------------

Do not use digital pins 0 and 1. The Arduino Uno uses them for USB serial
communication.

  LED   Finger    Arduino pin
  ---   ------    -----------
  1     Thumb     2
  2     Index     3
  3     Middle    4
  4     Ring      5
  5     Pinky     6

Wire each LED like this:

  Digital pin --> 220 ohm resistor --> LED long leg (+)
                                       LED short leg (-) --> GND

All the LED short legs can share one GND rail on the breadboard.


------------------------------------------------------------------------------
 7. SETUP AND USAGE
------------------------------------------------------------------------------

1. Wire the LEDs as shown above.

2. Open the Arduino sketch in the Arduino IDE and upload it to the Arduino
   Uno. Then close the Serial Monitor (only one program can use the port
   at a time).

3. Download hand_landmarker.task (see section 4) and put it next to the
   Python script.

4. Find your Arduino's port:
     Windows:  Arduino IDE -> Tools -> Port (for example COM5)
     Linux:    usually /dev/ttyACM0
     Mac:      usually /dev/cu.usbmodemXXXX

5. In the Python script, change the port name here to your port:

     arduino = serial.Serial("COM5", 9600)

6. Run the Python script:

     python your_script_name.py

7. Show your hand to the webcam. The finger count appears on the video and
   the LEDs follow your fingers. Press "q" to quit. When you quit, all LEDs
   are turned off.

If you have no Arduino, you can still use the finger counter by removing
the serial lines from the Python script.


------------------------------------------------------------------------------
 8. SERIAL PROTOCOL
------------------------------------------------------------------------------

  Baud rate: 9600
  Message:   5 characters of '0' or '1' followed by a newline ('\n')
  Order:     thumb, index, middle, ring, pinky
  Example:   "10110\n" -> thumb, middle and ring raised

Python and Arduino must use the same baud rate.


------------------------------------------------------------------------------
 9. KNOWN LIMITATIONS
------------------------------------------------------------------------------

- It works best when the hand is upright and the palm or back of the hand
  faces the camera. Sideways or upside-down hands give wrong results,
  because the finger check compares vertical positions.
- Thumb detection is the least reliable part, because it depends on the
  angle of the hand to the camera.
- Only one hand is tracked (num_hands = 1).
- Poor lighting can make the count flicker.


------------------------------------------------------------------------------
 10. TROUBLESHOOTING
------------------------------------------------------------------------------

"Unable to open file at hand_landmarker.task"
  Python cannot find the model file. Check that the name is exactly
  hand_landmarker.task (not .task.txt), and use the full path if needed,
  for example r"C:\Users\name\Desktop\hand_landmarker.task".

"Access denied" or "could not open port"
  Another program is using the port, usually the Arduino IDE Serial Monitor.
  Close it and run the script again.

Wrong LED turns on
  Check that the LED order matches the table in section 6, and that the pin
  list in the Arduino sketch matches your wiring.

Nothing happens on the Arduino
  Check the port name and make sure both sides use 9600 baud. Make sure the
  Arduino sketch was uploaded before running Python.

No camera window
  If the webcam cannot be opened, the program ends immediately. Try a
  different camera index (1 instead of 0) or check that no other app is
  using the webcam.


------------------------------------------------------------------------------
 11. FUTURE IDEAS
------------------------------------------------------------------------------

- Control a 3D-printed robotic hand with servo motors, so it raises the same
  fingers as the user. The Python code can stay the same, only the Arduino
  code changes from LEDs to servos.
- Add gesture names (for example "Fist", "Open hand").
- Track two hands.
- Make the thumb detection more reliable for different hand angles.


------------------------------------------------------------------------------
 12. CREDITS
------------------------------------------------------------------------------

- MediaPipe Hand Landmarker by Google (hand detection model and library)
- OpenCV (camera, drawing and display)
- PySerial (serial communication between Python and Arduino)
- Arduino (microcontroller platform)
