import cv2
import datetime
import mediapipe as mp
import pygame

# Initialize mediapipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Set up pygame for playing the alarm sound
pygame.mixer.init()
pygame.mixer.music.load('alarm.mp3')  # Replace with your alarm sound file path

# Define the alarm time (set this to a specific time for actual use)
alarm_time = datetime.datetime.now() + datetime.timedelta(seconds=10)  # 10 seconds from now for testing

cap = cv2.VideoCapture(0)  # Start video capture from the camera

alarm_active = False

def detect_position(landmarks):
    # Use keypoints like nose, shoulders, hips, and ankles to determine if lying down
    nose_y = landmarks[mp_pose.PoseLandmark.NOSE].y
    left_hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
    right_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y
    left_ankle_y = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y
    right_ankle_y = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y

    # Calculate average hip and ankle positions for easier comparison
    avg_hip_y = (left_hip_y + right_hip_y) / 2
    avg_ankle_y = (left_ankle_y + right_ankle_y) / 2

    # Compare the positions to determine if the body is lying down
    if nose_y < avg_hip_y and abs(avg_hip_y - avg_ankle_y) < 0.2:
        # If the nose is above the hips, and hips and ankles are roughly aligned, consider lying down
        return "lying"
    else:
        return "sitting_or_standing"

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video frame.")
            break

        # Convert the frame to RGB for mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(frame_rgb)
        
        if result.pose_landmarks:
            # Draw the pose landmarks on the frame for visual feedback
            mp.solutions.drawing_utils.draw_landmarks(
                frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Get the detected position
            position = detect_position(result.pose_landmarks.landmark)
            print(f"Detected position: {position}")

            if datetime.datetime.now() >= alarm_time and not alarm_active:
                print("Alarm time reached. Starting alarm.")
                pygame.mixer.music.play(-1)  # Loop the alarm sound
                alarm_active = True

            if alarm_active:
                if position == "sitting_or_standing":
                    print("Position changed to sitting/standing. Stopping alarm.")
                    pygame.mixer.music.stop()
                elif position == "lying":
                    if not pygame.mixer.music.get_busy():
                        print("Person is lying again. Restarting alarm.")
                        pygame.mixer.music.play(-1)  # Restart the alarm if lying down again

        # Press 'q' to stop the alarm completely
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

        # Display the video frame with landmarks
        cv2.imshow('Alarm System', frame)

finally:
    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.music.stop()
