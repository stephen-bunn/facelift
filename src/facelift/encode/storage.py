# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

import concurrent.futures
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, Generator, Iterator, List, Optional, Tuple

import attr
import numpy

from ..types import Face
from .resnet import BaseResnetEncoder

DEFAULT_GUESS_MAX_WORKERS = 8


@attr.s
class FaceCollection:
    encoder: BaseResnetEncoder = attr.ib()
    encodings: Dict[str, List[numpy.ndarray]] = attr.ib(default=attr.Factory(dict))

    def push(self, name: str, face_encoding: numpy.ndarray) -> List[numpy.ndarray]:
        if name not in self.encodings:
            self.encodings[name] = []

        self.encodings[name].append(face_encoding)
        return self.encodings[name]

    def pop(self, name: str) -> Optional[numpy.ndarray]:
        return self.encodings.pop(name)

    def drop(self, name: str) -> List[numpy.ndarray]:
        original = self.encodings[name]
        del self.encodings[name]
        return original

    def clear(self, name: str) -> List[numpy.ndarray]:
        original = self.encodings[name]
        self.encodings[name].clear()
        return original

    def iter_scores(
        self, face_encoding: numpy.ndarray, tolerance: float
    ) -> Generator[Tuple[str, float], None, None]:
        if len(self.encodings) <= 0:
            yield from []

        for face_name, known_encodings in self.encodings.items():
            score = self.encoder.score_encoding(
                face_encoding, known_encodings, tolerance=tolerance
            )
            if score is not None:
                yield (face_name, score)

    def iter_scores_threaded(
        self,
        face_encoding: numpy.ndarray,
        tolerance: float,
        max_workers: int = DEFAULT_GUESS_MAX_WORKERS,
    ) -> Generator[Tuple[str, float], None, None]:
        if len(self.encodings) <= 0:
            yield from []

        with ThreadPoolExecutor(max_workers=max_workers) as thread_executor:
            score_futures = {
                thread_executor.submit(
                    self.encoder.score_encoding,
                    face_encoding,
                    known_encodings,
                    tolerance=tolerance,
                ): face_name
                for face_name, known_encodings in self.encodings.items()
            }

            for future in concurrent.futures.as_completed(score_futures):
                score = future.result()
                if score is not None:
                    yield (score_futures[future], score)

    def iter_guesses(
        self,
        face_encoding: numpy.ndarray,
        tolerance: float,
        use_workers: bool = False,
        max_workers: int = DEFAULT_GUESS_MAX_WORKERS,
    ) -> Optional[Iterator[Tuple[numpy.ndarray, float]]]:
        score_generator = (
            self.iter_scores_threaded(face_encoding, tolerance, max_workers=max_workers)
            if use_workers
            else self.iter_scores(face_encoding, tolerance)
        )

        return reversed(sorted(score_generator, key=lambda result: result[-1]))
