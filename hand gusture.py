import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# Capture Video
cap = cv2.VideoCapture(0)

# Initialize drawing canvas
canvas = np.zeros((480, 640, 3), dtype=np.uint8)

# Previous finger tip position
prev_tip = None

# Drawing color
color = (255, 255, 255)  # White

# Button positions
color_button_pos = (10, 400, 50, 50)
erase_button_pos = (70, 400, 50, 50)

# Button press status
color_button_pressed = False
erase_button_pressed = False

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Convert the BGR image to RGB.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
            )
            
            # Get index finger tip position
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_tip_x = int(index_tip.x * image.shape[1])
            index_tip_y = int(index_tip.y * image.shape[0])
            
            # Draw on canvas if index finger is extended
            if index_tip.y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y:
                if prev_tip is not None:
                    cv2.line(canvas, prev_tip, (index_tip_x, index_tip_y), color, 5)
                prev_tip = (index_tip_x, index_tip_y)
            else:
                prev_tip = None
            
            # Check if color button is pressed
            if (color_button_pos[0] < index_tip_x < color_button_pos[0] + color_button_pos[2] and
                color_button_pos[1] < index_tip_y < color_button_pos[1] + color_button_pos[3]):
                if not color_button_pressed:
                    color_button_pressed = True
                    if color == (255, 255, 255):  # White
                        color = (0, 0, 255)  # Red
                    elif color == (0, 0, 255):  # Red
                        color = (0, 255, 0)  # Green
                    elif color == (0, 255, 0):  # Green
                        color = (255, 0, 0)  # Blue
                    elif color == (255, 0, 0):  # Blue
                        color = (255, 255, 0)  # Yellow
                    elif color == (255, 255, 0):  # Yellow
                        color = (255, 165, 0)  # Orange
                    else:  # Orange
                        color = (255, 255, 255)  # White
            else:
                color_button_pressed = False
            
            # Check if erase button is pressed
            if (erase_button_pos[0] < index_tip_x < erase_button_pos[0] + erase_button_pos[2] and
                erase_button_pos[1] < index_tip_y < erase_button_pos[1] + erase_button_pos[3]):
                if not erase_button_pressed:
                    erase_button_pressed = True
                    canvas[:] = 0
                    prev_tip = None
            else:
                erase_button_pressed = False

    # Draw buttons on the original video
    cv2.rectangle(image, (color_button_pos[0], color_button_pos[1]), (color_button_pos[0] + color_button_pos[2], color_button_pos[1] + color_button_pos[3]), color, -1)
    cv2.putText(image, "Color", (color_button_pos[0] + 5, color_button_pos[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
    
    cv2.rectangle(image, (erase_button_pos[0], erase_button_pos[1]), (erase_button_pos[0] + erase_button_pos[2], erase_button_pos[1] + erase_button_pos[3]), (0, 0, 0), -1)
    cv2.putText(image, "Erase", (erase_button_pos[0] + 5, erase_button_pos[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # Display canvas on a black screen
    black_screen = np.zeros((480, 640, 3), dtype=np.uint8)
    black_screen = cv2.addWeighted(black_screen, 1, canvas, 1, 0)
    
    # Display both the original video and the black screen with drawing
    cv2.imshow('Original Video', cv2.flip(image, 1))
    cv2.imshow('Drawing Screen', cv2.flip(black_screen, 1))
    
    if cv2.waitKey(5) & 0xFF == 27:
        break
hands.close()
cap.release()
cv2.destroyAllWindows()
#harish
