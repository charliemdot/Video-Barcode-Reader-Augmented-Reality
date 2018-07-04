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
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60)

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

    # Scan the barcode
    pil = Image.fromarray(gray)
    width, height = pil.size
    raw = pil.tobytes()
    image = zbar.Image(width, height, 'Y800', raw)
    scanner.scan(image)

    # Loop over barcodes detected in the frame
    for symbol in image:
        #print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data

        # Extract the x1,y1 and x3,y3 coordinates from zbar to use for cv2 rectangle points
        coords = str(symbol.location)
        coords = coords.replace("(", "")
        coords = coords.replace(")", "")
        coords = [x.strip() for x in coords.split(',')]

        # Set more useful coords for CV2
        x1 = int(coords[0])
        y1 = int(coords[1])
        x2 = int(coords[4])
        y2 = int(coords[5])
        xWidth = abs(x2 - x1)
        yHeight = abs(y2 - y1)

        # Modify dimensions based on type of barcode displayed
        xModifier = 1
        yModifier = 1

        # if str(symbol.data) == "server1":
        xModifier = xWidth * 3
        yModifier = yHeight * 3

        # Expand layover icons as desired
        x2 += xModifier
        y2 += yModifier
        xWidth += xModifier
        yHeight += yModifier

        # Resize to maintain proper aspect ratio
        yHeight = int(xWidth * .46) # .46 is our averaged aspect ratio across all our overlays
        y2 = y1 + yHeight

        # Move overlay to desired location
        x1 = x1 - xWidth
        x2 = x2 - xWidth

        # Sample Output
        print(symbol.data)

        # Draw a rectangle around the QR codes
        #cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2) # Uncomment to draw the square
        try:
            # Resize and use the different icons based on device identified in barcode
            if symbol.data == "server1":
                resizedOverlay = cv2.resize(imgServerOne, (xWidth, yHeight), interpolation = cv2.INTER_AREA)
            elif symbol.data == "server2":
                resizedOverlay = cv2.resize(imgServerTwo, (xWidth, yHeight), interpolation = cv2.INTER_AREA)
            elif symbol.data == "server3":
                resizedOverlay = cv2.resize(imgServerThree, (xWidth, yHeight), interpolation = cv2.INTER_AREA)
            elif symbol.data == "server4":
                resizedOverlay = cv2.resize(imgServerFour, (xWidth, yHeight), interpolation = cv2.INTER_AREA)
            elif symbol.data == "laptop":
                resizedOverlay = cv2.resize(imgLaptop, (xWidth, yHeight), interpolation = cv2.INTER_AREA)
            elif symbol.data == "oven":
                resizedOverlay = cv2.resize(imgOven, (xWidth, yHeight), interpolation = cv2.INTER_AREA)
            elif symbol.data == "fridge":
                resizedOverlay = cv2.resize(imgFridge, (xWidth, yHeight), interpolation = cv2.INTER_AREA)
            elif symbol.data == "bulb":
                resizedOverlay = cv2.resize(imgBulb, (xWidth, yHeight), interpolation = cv2.INTER_AREA)

            # Support for transparency on png's
            alpha_s = resizedOverlay[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            # Add overlay graphic to frame
            for c in range(0, 3):
                output[y1:y2, x1:x2, c] = (alpha_s * resizedOverlay[:, :, c] +
                                          alpha_l * output[y1:y2, x1:x2, c])
        except:
            pass

    # Show visual output over current frame captured
    cv2.imshow("#init17", output)

    # Wait for the magic key
    keypress = cv2.waitKey(1) & 0xFF
    if keypress == ord('q'):
    	break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
