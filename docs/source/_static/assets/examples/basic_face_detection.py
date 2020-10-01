from facelift import FullFaceDetector, iter_stream_frames
from facelift.render import draw_line
from facelift.window import opencv_window

detector = FullFaceDetector()
with opencv_window() as window:
    for frame in iter_stream_frames():
        for face in detector.iter_faces(frame):
            for feature, points in face.landmarks.items():
                frame = draw_line(frame, points)

        window.render(frame)
