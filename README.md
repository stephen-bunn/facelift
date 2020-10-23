<div style="background-color: #151320; padding: 1rem; margin-bottom: 1rem;">
  <img alt="Facelift" src="docs/source/_static/assets/images/facelift.png"/>
</div>

**A wrapper for decent face feature detection and basic face recognition.**

[![Supported Versions](https://img.shields.io/pypi/pyversions/facelift.svg)](https://pypi.org/project/facelift/)
[![Test Status](https://github.com/stephen-bunn/facelift/workflows/Test%20Package/badge.svg)](https://github.com/stephen-bunn/facelift)
[![Codecov](https://codecov.io/gh/stephen-bunn/facelift/branch/master/graph/badge.svg?token=xhhZQr8l76)](https://codecov.io/gh/stephen-bunn/facelift)
[![Documentation Status](https://readthedocs.org/projects/facelift/badge/?version=latest)](https://facelift.readthedocs.io/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

For more details please head over to our [documentation](https://facelift.readthedocs.io/).

```python
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
```

<div style="display: flex; justify-content: center;">
  <img alt="Basic Face Detection" src="docs/source/_static/assets/recordings/basic_face_detection.gif" />
</div>
