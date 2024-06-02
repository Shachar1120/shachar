# import the opencv library
import cv2

# define a video capture object
# the 0 means first camera or webcam. VideoCapture(1): Means second camera or webcam

#vid = cv2.VideoCapture(0, cv2.CAP_DSHOW) # an object that capture a video from the camera

while (True):

    # Capture the video frame
    # by frame

    # read function-returns the specified number of bytes from the file.
    #Default is -1 which means the whole file.

    ret, frame = vid.read()

    # Display the resulting frame
    # cv2.imshow(window_name-name of the window in which image to be displayed. , image-he image that is to be displayed.)

    cv2.imshow('frame', frame)
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()


# Destroy all the windows
cv2.destroyAllWindows()
