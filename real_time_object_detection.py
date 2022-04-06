# USAGE

# импортируем необходимые пакеты
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2

# создаем аргумент parse и анализируем аргументы
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# инициализируем список меток классов, которым был обучен MobileNet SSD
# определить, а затем сгенерировать набор цветов ограничивающей рамки для каждого класса
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# загружаем нашу сериализованную модель с диска
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# инициализируем видеопоток, даем сенсору камеры прогреться,
# и инициализируем счетчик FPS
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()

# зацикливаем кадры из видеопотока
while True:
	# захватить кадр из потокового видеопотока и изменить его размер
	# иметь максимальную ширину 400 пикселей
	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# получить размеры фрейма и преобразовать его в блоб
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
		0.007843, (300, 300), 127.5)
	
	# передать блоб по сети и получить обнаружения и
	# предсказания
	net.setInput(blob)
	detections = net.forward()

	# цикл по обнаружениям
	для  я  в  нп . arange ( 0 , обнаружение . shape [ 2 ]):
		# извлечь достоверность (т.е. вероятность), связанную с
		# предсказание
		confidence = detections[0, 0, i, 2]

		# отфильтровать слабые обнаружения, убедившись, что `доверие`
		# больше, чем минимальная достоверность
		if confidence > args["confidence"]:
			# извлечь индекс метки класса из
			# `detections`, затем вычислить (x, y)-координаты точки
			# ограничивающая рамка для объекта
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# рисуем предсказание на кадре
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
			
	# показываем выходной кадр
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# если была нажата клавиша `q`, выйти из цикла
	if key == ord("q"):
		break

	# обновить счетчик FPS
	fps.update()

# останавливаем таймер и отображаем информацию о FPS
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# сделать небольшую очистку
cv2.destroyAllWindows()
vs.stop()
