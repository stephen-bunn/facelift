# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the available builtin face encoders.

The included encoders will handle the necessary steps to take a given frame and
detected face to generate an encoding that can be used for future recognition.
I highly recommend that you use the :class:`~.detect.BasicFaceDetector` if attempting to
encode faces as it is lightweight and other detectors don't provide any added benefit to
face recognition.

Examples:
    >>> from facelift.capture import iter_media_frames
    >>> from facelift.detect import BasicFaceDetector
    >>> from facelift.encode import BasicFaceEncoder
    >>> detector = BasicFaceDetector()
    >>> encoder = BasicFaceEncoder()
    >>> for frame in iter_media_frames(MEDIA_FILEPATH):
    ...     for face in detector.iter_faces(frame):
    ...         face_encoding = encoder.get_encoding(frame, face)


.. important::
    Faces detected from the :class:`~.detect.FullFaceDetector` cannot be encoded as the
    model this detector uses is trained by a third party and not able to be processed by
    ``dlib``'s default ResNet model.
    Please only use faces detected using the :class:`~.detect.BasicFaceDetector` or the
    :class:`~.detect.PartialFaceDetector` for building face encodings.

    I would **highly** recommend that you use the :class:`~.detect.BasicFaceDetector` in
    all cases where you are performing encoding.
    The trained detection model for this basic detector is ~5MB whereas the
    alternative is >90MB.
    Using a heavier model will cause slowdown when simply trying to recognize multiple
    faces in a single frame.

Attributes:
    DEFAULT_ENCODING_JITTER (int):
        The default amount of jitter to apply to produced encodings.
    DEFAULT_ENCODING_PADDING (float):
        The default padding expected to exist around the detected face frame.
"""

import abc
from functools import lru_cache
from math import inf
from pathlib import Path
from typing import List, Optional

import dlib
import numpy

from .constants import DLIB_RESNET_ENCODER_V1_MODEL_NAME, ENCODERS_DIRPATH
from .types import Encoder, Encoding, Face, FaceFeature, Frame

DEFAULT_ENCODING_JITTER = 0
DEFAULT_ENCODING_PADDING = 0.25


@lru_cache()
def get_encoder(model_filepath: Path) -> Encoder:
    """Build an encoder for the given ``dlib`` ResNet model.

    Args:
        model_filepath (~pathlib.Path):
            The path to the encoder model

    Raises:
        FileNotFoundError: If the given model filepath does not exist

    Returns:
        :class:`~.types.Encoder`: The encoder to use for encoding face frames
    """

    if not model_filepath.is_file():
        raise FileNotFoundError(f"No such file {model_filepath!s} exists")

    return dlib.face_recognition_model_v1(model_filepath.as_posix())


class BaseEncoder(abc.ABC):
    """An abstract encoder class that each encoder should inherit from.

    Raises:
        NotImplementedError: If the ``model_filepath`` property is not implemented
    """

    @abc.abstractproperty
    def model_filepath(self) -> Path:  # pragma: no cover
        """Property filepath to the encoding model that should be used for encoding.

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """

        raise NotImplementedError(
            f"{self.__class__.__qualname__!s} has no associated encoding model"
        )

    def get_encoding(
        self,
        frame: Frame,
        face: Face,
        jitter: int = DEFAULT_ENCODING_JITTER,
        padding: float = DEFAULT_ENCODING_PADDING,
    ) -> Encoding:
        """Calculate the encoding for a given frame and detected face.

        Examples:
            >>> from facelift.capture import iter_media_frames
            >>> from facelift.detect import BasicFaceDetector
            >>> from facelift.encode import BasicFaceEncoder
            >>> detector = BasicFaceDetector()
            >>> encoder = BasicFaceEncoder()
            >>> for frame in iter_media_frames(MEDIA_FILEPATH):
            ...     for face in detector.iter_faces(frame):
            ...         face_encoding = encoder.get_encoding(frame, face)

        Args:
            frame (:attr:`~.types.Frame`):
                The frame the face was detected in
            face (:class:`~.types.Face`):
                The detected face from the given frame
            jitter (int, optional):
                The amount of jitter to apply during encoding.
                This can help provide more accurate encodings for frames containing
                the same face.
                Defaults to :attr:`~.encode.DEFAULT_ENCODING_JITTER`.
            padding (float, optional):
                The amount of padding to apply to the face frame during encoding.
                Defaults to :attr:`~.encode.DEFAULT_ENCODING_PADDING`.

        Returns:
            Encoding: The encoding of the provided face for the given frame
        """

        encoder = get_encoder(self.model_filepath)
        return numpy.array(
            encoder.compute_face_descriptor(
                frame,
                face.raw,
                num_jitters=jitter,
                padding=padding,
            )
        )

    def score_encoding(
        self,
        source_encoding: Encoding,
        known_encodings: List[Encoding],
    ) -> float:
        """Score a source encoding against a list of known encodings.

        .. important::
            This score is the average Euclidian distance between the given encodings.
            So the most similar encodings will result in a score closest to ``0.0``.

            If no encodings are given, then we will default to using :data:`math.inf`
            as it is the greatest distance from ``0.0`` that we can define.

        Examples:
            >>> from facelift.capture import iter_media_frames
            >>> from facelift.detect import BasicFaceDetector
            >>> from facelift.encode import BasicFaceEncoder
            >>> detector = BasicFaceDetector()
            >>> encoder = BasicFaceEncoder()
            >>> # A list of previously encoded faces for a single person
            >>> KNOWN_FACES = [...]
            >>> for frame in iter_media_frames(MEDIA_FILEPATH):
            ...     for face in detector.iter_faces(frame):
            ...         face_encoding = encoder.get_encoding(frame, face)
            ...         score = encoder.score_encoding(face_encoding, KNOWN_FACES)

        Args:
            source_encoding (:attr:`~.types.Encoding`):
                The unknown encoding we are attempting to score.
            known_encodings (List[:attr:`~.types.Encoding`]):
                A list of known encodings we are scoring against.
                These encodings should all encodings from a single person's face.

        Returns:
            float:
                The score of a given encoding against a list of known encodings.
                This value should be greater than 0.0 (lower is better).
        """

        if len(known_encodings) <= 0:
            return inf

        return numpy.sum(
            [numpy.linalg.norm(known - source_encoding) for known in known_encodings]
        ) / len(known_encodings)


class BasicFaceEncoder(BaseEncoder):
    """Encode faces detected by the :class:`~.detect.BasicFaceDetector`.

    This face encoder *can* handle faces detected by both the
    :class:`~.detect.BasicFaceDetector` and the :class:`~.detect.PartialFaceDetector`.
    However, you should likely only ever be encoding faces for recognition from the
    lightest model available (:class:`~.detect.BasicFaceDetector`).

    .. important::
        This encoder **can not** handle faces detected using the
        :class:`~.detect.FullFaceDetector`.
        If we determine we are using a face detected by this detector, the
        :meth:`~.BasicFaceEncoder.get_encoding` method will raise a :class:`ValueError`.
    """

    model_filepath: Path = ENCODERS_DIRPATH.joinpath(DLIB_RESNET_ENCODER_V1_MODEL_NAME)

    def get_encoding(
        self,
        frame: Frame,
        face: Face,
        jitter: int = DEFAULT_ENCODING_JITTER,
        padding: float = DEFAULT_ENCODING_PADDING,
    ) -> numpy.ndarray:
        """Calculate the encoding for a given frame and detected face.

        Examples:
            >>> from facelift.capture import iter_media_frames
            >>> from facelift.detect import BasicFaceDetector
            >>> from facelift.encode import BasicFaceEncoder
            >>> detector = BasicFaceDetector()
            >>> encoder = BasicFaceEncoder()
            >>> for frame in iter_media_frames(MEDIA_FILEPATH):
            ...     for face in detector.iter_faces(frame):
            ...         face_encoding = encoder.get_encoding(frame, face)

        Args:
            frame (:attr:`~.types.Frame`):
                The frame the face was detected in
            face (:class:`~.types.Face`):
                The detected face from the given frame
            jitter (int, optional):
                The amount of jitter to apply during encoding.
                This can help provide more accurate encodings for frames containing
                the same face.
                Defaults to :attr:`~.encode.DEFAULT_ENCODING_JITTER`.
            padding (float, optional):
                The amount of padding to apply to the face frame during encoding.
                Defaults to :attr:`~.encode.DEFAULT_ENCODING_PADDING`.

        Raises:
            ValueError:
                When the given face was detected with the
                :class:`~.detect.FullFaceDetector`.

        Returns:
            Encoding: The encoding of the provided face for the given frame
        """

        if FaceFeature.FOREHEAD in face.landmarks:
            raise ValueError(
                f"{self.__class__.__qualname__!r} cannot encode features detected "
                "with the 'FullFaceDetector'"
            )

        return super().get_encoding(frame, face, jitter=jitter, padding=padding)
