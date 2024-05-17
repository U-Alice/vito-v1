import cv2
import time
import sqlite3

def generate_uid():
    uid = int(round(time.time() * 1000))
    return uid

face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
time.sleep(1)

try: 
    conn = sqlite3.connect('customer_faces_Data.db')
    c = conn.cursor()
except sqlite3.Error as e:
    print("Sqlite error : ", e)

try:
    c.execute('''CREATE TABLE IF NOT EXISTS customers(id INTEGER RPIMARY KEY AUTO INCREMENT, customer_uid TEXT, customer_name TEXT, image_path TEXT)''')
    print("Table customers created successfully")
except sqlite3.Error as e:
    print("Sqlite error : ", e)



customer_name = input('Enter your full name: ')
customer_uid = generate_uid()


print('Get ready for your shot!!')
time.sleep(2)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

display_window = cv2.namedWindow("Dataset generating....")
start_time = time.time()
interval = 500
current_time = start_time
image_count = 0 

while True:
    ret, image = camera.read()
    if not ret:
        break
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x, y, w, h) in faces:
        # Draw rectangle around the face
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Check if enough time has passed to capture an image and if image count is less than 100
        if (time.time() - current_time) * 1000 >= interval and image_count < 50:
            # Save the captured image into the datasets folder
            cv2.imwrite(f"dataset/data.{customer_uid}.{int(time.time() * 1000)}.jpg", gray[y:y + h, x:x + w])
            current_time = time.time()
            image_count += 1

            try:
                c.execute("INSERT INTO customers(customer_uid, customer_name, image_path) VALUES(?, ?, ?)", (customer_uid, customer_name, f"dataset/data.{customer_uid}.{int(time.time() * 1000)}.jpg"))
                conn.commit()
                print("Image saved to database successfully")
            except sqlite3.Error as e:
                print("Sqlite error : ", e)

        cv2.imshow("Dataset Generating...", image)

    # To stop taking video, press 'q' key or if image count reaches 100
    if cv2.waitKey(1) & 0xFF == ord('q') or image_count >= 50:
        break

# Release the camera and close all windows
camera.release()
cv2.destroyAllWindows()
