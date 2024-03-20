import cv2
import numpy as np
import yolov5_model
import time
from datetime import datetime
# /Users/robertobrien/Documents/Thesis/Code/mavlinkage.py
import mavlinkage
import os


# create a VideoCapture object to receive the video stream
# webcam: 
# 0 

#rtsp: 
# 'rtsp://192.168.43.1:8554/fpv_stream'

#video on computer: 
# '/Users/robertobrien/Documents/example-shark-vid.mov'
cap = cv2.VideoCapture('/Users/robertobrien/Documents/example-shark-vid.mov')

# object detection mdoel retrieval
model = yolov5_model.get_model()
model.eval()

#connect to the mavlink
mav_connection = mavlinkage.open_mavlink_connection("192.168.43.1:14550")
print("Mavlink connection: " + str(mav_connection))

#returns an array of all file names on the camera, sorted
def listdir(path):
    return sorted(os.listdir(path))

cv2.namedWindow('Video Stream', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Video Stream', 2560, 1280)  # Increase the window size for better visibility

debug_photos = listdir("/Users/robertobrien/Documents/Thesis/Code/validate")[1:]

frame = None
total_proc_time = 0
total_proc_n = 0
avg_proc_time = -1
period = 0.01466

result = cv2.VideoWriter('detection_video.avi',  
                         cv2.VideoWriter_fourcc(*'MJPG'), 
                         np.round(1/period,0), (3676, 1150)) 

print()

while True:
    try:
        ret, frame = cap.read()

        if not ret:
            break

        original_frame = frame.copy()

        latitude = -1 
        longitude = -1  
        altitude = -1  
        # If we have a connection 
        if mav_connection is not None:
            gps_info = mavlinkage.read_latest_gps_info(mav_connection)
            latitude = gps_info["latitude"]
            longitude = gps_info["longitude"]
            altitude = gps_info["altitude"] 

        results = yolov5_model.infer(model,frame)
        total_proc_n += 1
        results.print()
        print(results.pandas().xyxy[0])  # im1 predictions (pandas))
        proccess_time = np.round(np.sum(np.array(results.t)),2)
        print("proccess_time: ", proccess_time)
        total_proc_time += proccess_time
        avg_proc_time = np.round(total_proc_time / total_proc_n,2)
        print("average proccess_time: " , avg_proc_time)
        print()
        #['ims', 'pred', 'names', 'files', 'times', 'xyxy', 'xywh', 'xyxyn', 'xywhn', 'n', 't', 's', '__module__', '__init__', '_run', 'show', 'save', 'crop', 'render', 'pandas', 'tolist', 'print', '__len__', '__str__', '__repr__', '__dict__', '__weakref__', '__doc__', '__slotnames__', '__hash__', '__getattribute__', '__setattr__', '__delattr__', '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__', '__new__', '__reduce_ex__', '__reduce__', '__subclasshook__', '__init_subclass__', '__format__', '__sizeof__', '__dir__', '__class__']

        #show just the cropped images
        #if len(results.crop()) > 0:
        #    cv2.imshow('crop', results.crop()[0]['im'])

        # set threshold
        inference = np.squeeze(results.render())
        # convert it to the correct color channels
        inference = cv2.cvtColor(inference, cv2.COLOR_RGB2BGR)


        combined_frame = np.hstack((original_frame, inference))

        gps_info_bar = np.zeros((120, combined_frame.shape[1], 3), dtype=np.uint8)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        font_color = (255, 255, 255)  # white
        font_thickness = 2

        text = f'Latitude: {latitude:.6f}, Longitude: {longitude:.6f}, Altitude: {altitude:.2f}'
        cv2.putText(gps_info_bar, text, (10, 40), font, font_scale, font_color, font_thickness)
        cv2.putText(gps_info_bar, str(datetime.now()), (10, 70), font, font_scale, font_color, font_thickness)
        cv2.putText(gps_info_bar, "Proccess time: " + str(proccess_time)+ "ms", (600, 70), font, font_scale, font_color, font_thickness)
        cv2.putText(gps_info_bar, "Avg. Proccess time: " + str(avg_proc_time) + "ms", (1200, 70), font, font_scale, font_color, font_thickness)

        final_frame = np.vstack((combined_frame, gps_info_bar))

        cv2.imshow('Video Stream', final_frame)
        cv2.imwrite("recent_frame.jpg", final_frame)

        result.write(final_frame) 

        print("Frame shape: " + str(final_frame.shape))
        print("Just processed frame #" + str(total_proc_n))
        print("############################################")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
        time.sleep(period) #we don't need to be running this so quickly
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt. Closing windows")
        cap.release()
        cv2.destroyAllWindows()
        break

# Release the VideoCapture when done
cap.release()
cv2.destroyAllWindows()
