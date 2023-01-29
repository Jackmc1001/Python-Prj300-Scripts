import cv2
from datetime import datetime

cam_port = 0
image_name= datetime.now().strftime('%Y_%m_%d_%H_%M_%S')


cam = cv2.VideoCapture(cam_port)

# reading the input using the camera
result, image = cam.read()

# If image will detect without any error,
# show result
if result:

 # showing result, it take frame name and image
 # output
    cv2.imshow(image_name, image)

# saving image in local storage
    cv2.imwrite(image_name+".png", image)

# If keyboard interrupt occurs, destroy image
# window
    cv2.waitKey(0)
    
    cv2.destroyWindow(image_name)
    cam.release()

# If captured image is corrupted, moving to else part
else:
    print("No image detected. Please! try again")

