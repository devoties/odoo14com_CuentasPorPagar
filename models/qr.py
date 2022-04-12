import cv2
import os
from wand.image import Image as wi

PDFfile = wi(filename="C:\pdf\archivo.pdf", resolution=400)
Images = PDFfile.convert('png')
ImageSequence = 1

for img in PDFfile.sequence:
    Image = wi(image=img)
    Image.save(filename="Image" + str(ImageSequence) + ".png")
    ImageSequence += 1

    # read the QRCODE image
image = cv2.imread("image1.png")
# initialize the cv2 QRCode detector
qrCodeDetector = cv2.QRCodeDetector()
# detect and decode
decodedText, points, straight_qrcode = qrCodeDetector.detectAndDecode(image)
# points is the output array of vertices of the found QR code quadrangle
# straight qrcode
# if there is a QR code
if points is not None:
    # QR Code detected handling code

    print('Decoded data: ' + decodedText)
    nrOfPoints = len(points)
    print('Number of points:  ' + str(nrOfPoints))
    points = points[0]
    for i in range(len(points)):
        pt1 = [int(val) for val in points[i]]
        pt2 = [int(val) for val in points[(i + 1) % 4]]
        cv2.line(image, pt1, pt2, color=(255, 0, 0), thickness=3)

    print('Successfully saved')
    cv2.imshow('Detected QR code', image)
    cv2.imwrite('Generated/extractedQrcode.png', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("QR code not detected")
    # display the image with lines
    # length of bounding box