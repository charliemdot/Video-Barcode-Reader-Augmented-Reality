# --- Receptor APP Developed By: Charles Markovich @ 2017 --- #

# KNOWN ISSUE: (occasonal crash due to the following)
# Traceback (most recent call last):
#  File "opencv-qrcode.py", line 116, in <module>
#    alpha_l * output[y1:y2, x1:x2, c])
# ValueError: operands could not be broadcast together with shapes (149,324) (149,0)

import cv2
import zbar
import qrtools
from PIL import Image

# Facial recognition dependancies
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

# Utility Method
def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

# Capture video as frames
cv2.namedWindow("#init17 Receptor App")
cap = cv2.VideoCapture(1)
#cap.set(cv2.CV_CAP_PROP_FPS, 60)

# Initialize barcode scanning
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

# Load our overlay icon images
imgPath = '/Users/charlesmarkovich/Projects/receptor_vr_project/icons/'
imgLogo = cv2.imread(imgPath + 'logo-receptor.png', -1)
imgServerOne = cv2.imread(imgPath + 'node-server1.png', -1)
imgServerTwo = cv2.imread(imgPath + 'node-server2.png', -1)
imgServerThree = cv2.imread(imgPath + 'node-server3.png', -1)
imgServerFour = cv2.imread(imgPath + 'node-server4.png', -1)
imgLaptop = cv2.imread(imgPath + 'node-laptop.png', -1)
imgOven = cv2.imread(imgPath + 'node-oven.png', -1)
imgFridge = cv2.imread(imgPath + 'node-refrigerator.png', -1)
imgBulb = cv2.imread(imgPath + 'node-smartbulb.png', -1)
imgMobileNone = cv2.imread(imgPath + 'node-mobile-none.png', -1)
imgMobile1 = cv2.imread(imgPath + 'node-mobile-low1.png', -1)
imgMobile2 = cv2.imread(imgPath + 'node-mobile-low2.png', -1)
imgMobileHigh = cv2.imread(imgPath + 'node-mobile-high.png', -1)
imgMobileCritical = cv2.imread(imgPath + 'node-mobile-critical.png', -1)

# Place our logo
resizedLogo = cv2.resize(imgLogo, (400, 100), interpolation = cv2.INTER_AREA)

# Capture frames from the camera
while True:
    faceCounter = 0

    if not cap.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass

    ret, output = cap.read()
    if not ret:
	    continue

    # Black and white version of frame for app parsing
    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY, dstCn=0)

    # Facial detection
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw overlays on discovered faces
    for (x, y, w, h) in faces:
        # Ensure we only init face counter to a range of 1 through 5
        faceCounter += 1
        if faceCounter > 5:
            faceCounter = 1

        #print "faceCounter is: ", faceCounter

        #cv2.rectangle(output, (x, y), (x+w, y+h), (255,0,255), 1) # Uncomment to draw rectangle around face

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = output[y:y+h, x:x+w]

        # Set more useful coords for CV2
        x1 = x
        y1 = y
        x2 = x + w
        y2 = y + h

        # Resize to maintain proper aspect ratio
        h = int(w * .46) # .46 is our averaged aspect ratio across all our overlays
        y2 = y1 + h

        # Move overlay to desired location
        y1 = y1 - (2 * h)
        y2 = y2 - (2 * h)

        try:
            # Apply different icons randomly for show purposes ONLY!
            if faceCounter == 1:
                resizedOverlay = cv2.resize(imgMobileNone, (w, h), interpolation = cv2.INTER_AREA)
            if faceCounter == 2:
                resizedOverlay = cv2.resize(imgMobile1, (w, h), interpolation = cv2.INTER_AREA)
            if faceCounter == 3:
                resizedOverlay = cv2.resize(imgMobile2, (w, h), interpolation = cv2.INTER_AREA)
            if faceCounter == 4:
                resizedOverlay = cv2.resize(imgMobileHigh, (w, h), interpolation = cv2.INTER_AREA)
            if faceCounter == 5:
                resizedOverlay = cv2.resize(imgMobileCritical, (w, h), interpolation = cv2.INTER_AREA)

            # Support for transparency on png's
            alpha_s = resizedOverlay[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            # Add overlay graphic to frame
            for c in range(0, 3):
                output[y1:y2, x1:x2, c] = (alpha_s * resizedOverlay[:, :, c] + alpha_l * output[y1:y2, x1:x2, c])

            # Show visual output over current frame captured
            cv2.imshow("#init17", output)
        except:
            pass

    # Wait for the magic key
    keypress = cv2.waitKey(1) & 0xFF
    if keypress == ord('q'):
    	break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
