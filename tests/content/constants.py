# -*- encoding: utf-8 -*-
# Copyright (c) 2020 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""Contains testing constants related to content testing."""

from typing import Dict, List, Union

SAMPLE_MAGIC: Dict[str, Dict[str, Union[str, List[str], bytes]]] = {
    "mp4": {
        "type": "video",
        "mimetypes": ["video/mp4"],
        "buffer": bytearray.fromhex(
            "00 00 00 20 66 74 79 70 69 73 6F 6D 00 00 02 00 69 73 6F 6D 69 73 6F 32 "
            "61 76 63 31 6D 70 34 31 00 00 00 08 66 72 65 65 00 A0 1D 54 6D 64 61 74 "
            "01 06 54 20 4C 6A 13 06 02 C1 80 B0 A0 4C 35 0A 0D 82 82 50 A0 4C 22 97 "
            "3A DD D4 AE 6F 55 2A 4E 78 BC 91 56 A9 C6 F5 71 46 4D 04 34 99 ED 77 D3 "
            "D7 97 E5 6C F8 69 DD A7 EA E3 B0 F4 F8 6F 86 BE CD 91 73 A6 87 F7 CD 7A "
            "C2 F8 FC 2F 65 9E EA DB A2 E4 61 07 FA 0C 95 82 47 9C EE 79 87 6A E1 57 "
            "2D 26 7B 78 BD 77 F0 8A F8 3E 1C F4 7F 49 FD 8E A7 36 F1 76 DD 75 D9 6A "
            "3B DD C7 70 1F 6B 14 23 A2 3D BA 4B 9E 5A 4F 2E 61 C4 79 79 0A 2D 77 28 "
            "F4 FF E7 DA 98 B6 23 53 C5 52 70 74 3C 7B 99 DA BF 5A 33 38 78 74 9F 94 "
            "D4 78 D7 5B E9 1B D5 C9"
        ),
    },
    "avi": {
        "type": "video",
        "mimetypes": ["video/avi", "video/msvideo", "video/x-msvideo"],
        "buffer": bytearray.fromhex(
            "52 49 46 46 96 05 7F 00 41 56 49 20 4C 49 53 54 DE 22 00 00 68 64 72 6C "
            "61 76 69 68 38 00 00 00 6A 04 01 00 28 A0 00 00 00 00 00 00 10 09 00 00 "
            "61 07 00 00 00 00 00 00 02 00 00 00 00 00 10 00 40 01 00 00 F0 00 00 00 "
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4C 49 53 54 E0 10 00 00 "
            "73 74 72 6C 73 74 72 68 38 00 00 00 76 69 64 73 4D 50 34 32 00 00 00 00 "
            "00 00 00 00 00 00 00 00 01 00 00 00 0F 00 00 00 00 00 00 00 61 07 00 00 "
            "42 26 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 40 01 F0 00 73 74 72 66 "
            "28 00 00 00 28 00 00 00 40 01 00 00 F0 00 00 00 01 00 18 00 4D 50 34 32 "
            "00 84 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4A 55 4E 4B "
            "18 10 00 00 04 00 00 00"
        ),
    },
    "flv": {
        "type": "video",
        "mimetypes": ["video/x-flv"],
        "buffer": bytearray.fromhex(
            "46 4C 56 01 05 00 00 00 09 00 00 00 00 12 00 01 68 00 00 00 00 00 00 00 "
            "02 00 0A 6F 6E 4D 65 74 61 44 61 74 61 08 00 00 00 10 00 08 64 75 72 61 "
            "74 69 6F 6E 00 40 5F 7F 9D B2 2D 0E 56 00 05 77 69 64 74 68 00 40 74 00 "
            "00 00 00 00 00 00 06 68 65 69 67 68 74 00 40 6E 00 00 00 00 00 00 00 0D "
            "76 69 64 65 6F 64 61 74 61 72 61 74 65 00 40 68 6A 00 00 00 00 00 00 09 "
            "66 72 61 6D 65 72 61 74 65 00 40 2E 00 00 00 00 00 00 00 0C 76 69 64 65 "
            "6F 63 6F 64 65 63 69 64 00 40 00 00 00 00 00 00 00 00 0D 61 75 64 69 6F "
            "64 61 74 61 72 61 74 65 00 40 5F 40 00 00 00 00 00 00 0F 61 75 64 69 6F "
            "73 61 6D 70 6C 65 72 61 74 65 00 40 E5 88 80 00 00 00 00 00 0F 61 75 64 "
            "69 6F 73 61 6D 70 6C 65"
        ),
    },
    "mkv": {
        "type": "video",
        "mimetypes": ["video/x-matroska"],
        "buffer": bytearray.fromhex(
            "1A 45 DF A3 A3 42 86 81 01 42 F7 81 01 42 F2 81 04 42 F3 81 08 42 82 88 "
            "6D 61 74 72 6F 73 6B 61 42 87 81 04 42 85 81 02 18 53 80 67 01 00 00 00 "
            "00 4A EE CB 11 4D 9B 74 C1 BF 84 FE 32 4C 82 4D BB 8B 53 AB 84 15 49 A9 "
            "66 53 AC 81 8C 4D BB 8B 53 AB 84 16 54 AE 6B 53 AC 81 DC 4D BB 8C 53 AB "
            "84 12 54 C3 67 53 AC 82 01 A9 4D BB 8D 53 AB 84 1C 53 BB 6B 53 AC 83 4A "
            "E8 C2 EC 01 00 00 00 00 00 00 3D 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "15 49 A9 66 CB BF 84 82 13 08 F7 2A D7 B1 83 0F 42 40 4D 80 8D 4C 61 76 "
            "66 35 38 2E 34 32 2E 31"
        ),
    },
    "mov": {
        "type": "video",
        "mimetypes": ["video/quicktime"],
        "buffer": bytearray.fromhex(
            "00 00 00 14 66 74 79 70 71 74 20 20 00 00 02 00 71 74 20 20 00 00 00 08 "
            "77 69 64 65 00 DB CA 13 6D 64 61 74 00 00 02 9F 06 05 FF FF 9B DC 45 E9 "
            "BD E6 D9 48 B7 96 2C D8 20 D9 23 EE EF 78 32 36 34 20 2D 20 63 6F 72 65 "
            "20 31 35 35 20 2D 20 48 2E 32 36 34 2F 4D 50 45 47 2D 34 20 41 56 43 20 "
            "63 6F 64 65 63 20 2D 20 43 6F 70 79 6C 65 66 74 20 32 30 30 33 2D 32 30 "
            "31 38 20 2D 20 68 74 74 70 3A 2F 2F 77 77 77 2E 76 69 64 65 6F 6C 61 6E "
            "2E 6F 72 67 2F 78 32 36 34 2E 68 74 6D 6C 20 2D 20 6F 70 74 69 6F 6E 73 "
            "3A 20 63 61 62 61 63 3D 31 20 72 65 66 3D 33 20 64 65 62 6C 6F 63 6B 3D "
            "31 3A 30 3A 30 20 61 6E 61 6C 79 73 65 3D 30 78 33 3A 30 78 31 31 33 20 "
            "6D 65 3D 68 65 78 20 73"
        ),
    },
    "mpg": {
        "type": "video",
        "mimetypes": ["video/mpeg"],
        "buffer": bytearray.fromhex(
            "00 00 01 BA 21 00 01 00 01 A1 9C 6D 00 00 01 BB 00 0C A1 9C 6D 04 21 FF "
            "E0 E0 E6 C0 C0 20 00 00 01 E0 07 DC 31 00 03 7B B1 11 00 03 5F 91 00 00 "
            "01 B3 14 00 F0 23 FF FF E0 18 00 00 01 B5 14 8A 00 01 00 00 00 00 01 B8 "
            "00 08 00 40 00 00 01 00 00 0F FF F8 00 00 01 B5 8F FF F3 41 80 00 00 01 "
            "01 2B F8 7D 29 48 8B 94 A5 22 2E 52 94 88 B9 4A 52 22 E5 29 48 8B 94 A5 "
            "22 2E 52 94 88 B9 4A 52 22 E5 29 48 8B 94 A5 22 2E 52 94 88 B9 4A 52 22 "
            "E5 29 48 8B 94 A5 22 2E 52 94 88 B9 4A 52 22 E5 29 48 8B 94 A5 22 2E 52 "
            "94 88 B9 4A 52 22 00 00 01 02 2B F8 7D 2E C8 20 FF 30 03 E0 45 FF 91 40 "
            "13 13 41 34 00 EA 81 07 FB 00 34 38 06 E0 94 00 65 80 0C 2C C0 C1 60 12 "
            "24 02 2F 3B E5 D2 DC 80"
        ),
    },
    "ogv": {
        "type": "video",
        "mimetypes": ["video/ogg"],
        "buffer": bytearray.fromhex(
            "4F 67 67 53 00 02 00 00 00 00 00 00 00 00 04 EA 22 F2 00 00 00 00 93 C5 "
            "74 35 01 2A 80 74 68 65 6F 72 61 03 02 01 00 14 00 0F 00 01 40 00 00 F0 "
            "00 00 00 00 00 19 00 00 00 01 00 00 01 00 00 01 00 00 00 00 B0 C0 4F 67 "
            "67 53 00 02 00 00 00 00 00 00 00 00 51 AE 61 FD 00 00 00 00 B9 35 01 16 "
            "01 1E 01 76 6F 72 62 69 73 00 00 00 00 02 44 AC 00 00 FF FF FF FF 00 F4 "
            "01 00 FF FF FF FF B8 01 4F 67 67 53 00 00 00 00 00 00 00 00 00 00 04 EA "
            "22 F2 01 00 00 00 EF B5 F8 52 0E 3F FF FF FF FF FF FF FF FF FF FF FF FF "
            "90 81 74 68 65 6F 72 61 0D 00 00 00 4C 61 76 66 35 38 2E 34 32 2E 31 30 "
            "31 01 00 00 00 1F 00 00 00 65 6E 63 6F 64 65 72 3D 4C 61 76 63 35 38 2E "
            "38 30 2E 31 30 30 20 6C"
        ),
    },
    "webm": {
        "type": "video",
        "mimetypes": ["video/webm"],
        "buffer": bytearray.fromhex(
            "1A 45 DF A3 9F 42 86 81 01 42 F7 81 01 42 F2 81 04 42 F3 81 08 42 82 84 "
            "77 65 62 6D 42 87 81 02 42 85 81 02 18 53 80 67 01 00 00 00 00 C0 80 4F "
            "11 4D 9B 74 BB 4D BB 8B 53 AB 84 15 49 A9 66 53 AC 81 8C 4D BB 8B 53 AB "
            "84 16 54 AE 6B 53 AC 81 C3 4D BB 8C 53 AB 84 12 54 C3 67 53 AC 82 12 0A "
            "4D BB 8D 53 AB 84 1C 53 BB 6B 53 AC 83 C0 7D 7E EC 01 00 00 00 00 00 00 "
            "43 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 15 49 A9 66 "
            "B2 2A D7 B1 83 0F 42 40 4D 80 8D 4C 61 76 66 35 38 2E 34 32 2E 31 30 31 "
            "57 41 8D 4C 61 76 66 35"
        ),
    },
    "wmv": {
        "type": "video",
        "mimetypes": ["video/x-ms-asf", "video/x-ms-wmv"],
        "buffer": bytearray.fromhex(
            "30 26 B2 75 8E 66 CF 11 A6 D9 00 AA 00 62 CE 6C F7 02 00 00 00 00 00 00 "
            "06 00 00 00 01 02 A1 DC AB 8C 47 A9 CF 11 8E E4 00 C0 0C 20 53 65 68 00 "
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 73 23 "
            "5B 00 00 00 00 00 00 80 3E D5 DE B1 9D 01 4A 07 00 00 00 00 00 00 E0 EE "
            "06 4D 00 00 00 00 20 E9 2D 4B 00 00 00 00 1C 0C 00 00 00 00 00 00 02 00 "
            "00 00 80 0C 00 00 80 0C 00 00 40 01 05 00 B5 03 BF 5F 2E A9 CF 11 8E E3 "
            "00 C0 0C 20 53 65 9C 00 00 00 00 00 00 00 11 D2 D3 AB BA A9 CF 11 8E E6 "
            "00 C0 0C 20 53 65 06 00 6E 00 00 00 EA CB F8 C5 AF 5B 77 48 84 67 AA 8C "
            "44 FA 4C CA 6E 00 00 00 00 00 00 00 02 00 00 00 01 00 1A 00 03 00 04 00 "
            "00 00 41 00 73 00 70 00"
        ),
    },
    "3g2": {
        "type": "video",
        "mimetypes": ["video/3gpp2"],
        "buffer": bytearray.fromhex(
            "00 00 00 1C 66 74 79 70 33 67 32 61 00 01 00 00 33 67 32 61 69 73 6F 6D "
            "69 73 6F 32 00 00 00 08 66 72 65 65 00 3A EA EE 6D 64 61 74 DE 02 00 4C "
            "61 76 63 35 38 2E 38 30 2E 31 30 30 00 42 31 87 20 F9 03 90 7C 83 80 00 "
            "00 01 B3 00 10 07 00 00 01 B6 10 60 91 82 3D B7 F1 B6 DF C6 DB 7F 1B 6D "
            "FC 6D B7 F1 B6 DF C6 DB 7F 1B 6D FC 6D B7 F1 B6 DF C6 DB 7E 00 00 8B 21 "
            "30 50 40 0D 03 D5 10 96 9A 8C E8 48 8C 11 C4 AB 3B 07 EC 72 0A C1 93 BE "
            "2C AB 5C BD 96 CE 2F CB 4E 94 54 DF 67 7B C6 E4 5F D4 61 16 42 6D 0A 33 "
            "E1 6D 12 9A 40 DD A3 27 33 74 0C 1F 8E 81 E1 7F EF 68 63 42 45 28 06 84 "
            "09 A5 94 76 9A 7D 65 BB 7A BA 22 08 6D 4C 9A DF AA ED 66 F2 71 1D AB C8 "
            "32 46 26 16 84 21 D2 68"
        ),
    },
    # FIXME: .3gp media is being detected as application/octet-stream on Ubuntu's
    # libmagic installation. This could either be due to an old version of libmagic in
    # CI or not enough bytes in this sample to detect 3gp. This sample size DOES work
    # for a new libmagic (file) installation on MacOS which is why these tests pass
    # locally for me currently. They also pass currently on a WSL2 Ubuntu fresh install
    # of libmagic which points to the likelyhood of it being an older version of
    # libmagic being present in CI
    # "3gp": {
    #     "type": "video",
    #     "mimetypes": ["video/3gpp"],
    #     "buffer": bytearray.fromhex(
    #         "00 00 00 1C 66 74 79 70 33 67 70 34 00 00 02 00 33 67 70 34 69 73 6F 6D "
    #         "69 73 6F 32 00 00 00 08 66 72 65 65 00 2E 80 BA 6D 64 61 74 3C 91 17 16 "
    #         "BE 66 79 E1 E0 01 E7 AF F0 00 00 00 80 00 00 00 00 00 00 00 00 00 00 00 "
    #         "00 00 00 00 00 00 80 02 08 03 26 20 20 20 21 FF FF 31 01 01 01 0F FF F9 "
    #         "88 08 08 08 7F FF CC 40 40 40 43 FF FE 62 02 02 02 1F FF F3 10 10 10 10 "
    #         "FF FF 98 80 80 80 87 FF FC C4 04 04 04 3F FF E6 20 20 20 21 FF FF 31 01 "
    #         "01 01 0F FF F9 88 08 08 08 7F FF AC 86 03 01 C4 0C 00 CF C4 60 60 3B 82 "
    #         "05 02 7F 07 34 08 6E 03 01 D8 0C 00 8F E2 98 0C 07 98 91 90 1C 6F E6 A5 "
    #         "65 C0 7B E3 AF AA FE FB F6 67 72 D0 70 BF 97 C2 10 96 A6 6E E0 FF D0 76 "
    #         "5D 40 84 E3 2B B2 D9 F6"
    #     ),
    # },
    "jpeg": {
        "type": "image",
        "mimetypes": ["image/jpeg"],
        "buffer": bytearray.fromhex(
            "FF D8 FF E0 00 10 4A 46 49 46 00 01 01 00 00 01 00 01 00 00 FF DB 00 84 "
            "00 09 06 07 0D 07 07 0D 07 07 0D 0D 07 07 07 07 0D 07 07 07 07 0D 0F 08 "
            "09 07 0D 20 11 16 16 20 11 15 15 18 1C 28 20 18 1A 25 1B 15 15 21 31 21 "
            "31 29 37 2E 2E 2E 17 1F 33 38 33 2C 37 28 2D 2E 2B 01 0A 0A 0A 0D 0D 0D "
            "10 0D 0D 1A 2B 1D 1F 1D 2D 2B 2D 2B 2B 2B 2D 2D 2B 2B 2B 2B 2D 2D 2B 2B "
            "2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 37 "
            "37 2B 2B 2B 2B 2B 2B 2B 2B 2B FF C0 00 11 08 00 E1 00 E1 03 01 22 00 02 "
            "11 01 03 11 01 FF C4 00 19 00 01 01 01 01 01 01 00 00 00 00 00 00 00 00 "
            "00 00 02 01 00 03 06 07 FF C4 00 18 10 01 01 01 01 01 00 00 00 00 00 00 "
            "00 00 00 00 00 00 01 02"
        ),
    },
    "png": {
        "type": "image",
        "mimetypes": ["image/png"],
        "buffer": bytearray.fromhex(
            "89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52 00 00 02 00 00 00 02 00 "
            "08 06 00 00 00 F4 78 D4 FA 00 00 20 00 49 44 41 54 78 9C ED DD 7F 94 D6 "
            "F5 75 E0 F1 B7 48 08 25 94 B2 94 A5 84 A5 2E 25 2C B5 84 B2 C6 25 1E C2 "
            "BA 76 6A 5C 6B AC 35 D6 58 F3 C3 98 68 AC 35 D6 5A EB 5A EB E6 B8 AE 5F "
            "8F EB BA 6E EA 71 BB 49 1A 8D 89 31 9A 58 63 8C 12 6B 08 21 D4 CE 12 96 "
            "43 29 87 65 29 4B 09 A5 94 C3 B2 94 22 A1 D3 E9 74 3A 9D 4C 26 FB C7 9D "
            "A7 CF 00 C3 F0 CC 33 CF F3 7C BE 3F DE AF 73 72 B6 9B 18 B8 BB 85 B9 F7 "
            "7B 3F F7 73 3F 20 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 "
            "49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 26 "
            "E6 AC D4 01 48 92 A4 06"
        ),
    },
    "gif": {
        "type": "image",
        "mimetypes": ["image/gif"],
        "buffer": bytearray.fromhex(
            "47 49 46 38 39 61 6B 03 1F 02 87 00 00 EC F2 B6 A3 B2 24 FB D3 EA 93 0C "
            "5B 41 47 11 CD 27 9B DE 5B 6C 01 9B D0 03 3A 4D 01 90 C1 58 76 CA 75 62 "
            "BE 7E 89 1D AF BF 27 EB 22 96 D5 8D 52 48 C7 F3 CB DA 4A 02 70 95 0F 51 "
            "6A 0A 09 09 4E 55 13 A2 0E 63 6A 6B 33 F5 8B C8 8A 97 1F 8F 97 4E CE B5 "
            "3F 1A 44 53 89 8D 2F 71 7C 1A C7 D0 76 24 BA EC 23 1F 20 29 A8 D3 14 14 "
            "14 ED 50 AB 5A 62 16 5B 0A 38 8A DB F7 B0 3B A7 B0 2B 91 DC 12 86 69 0B "
            "41 85 0C 52 A7 B1 53 B4 8D 3D 3E 08 27 22 1D 1E 29 2C 0B F7 A7 D5 8A 5C "
            "37 10 11 07 B0 0F 6C 00 A6 DE 76 2D 3C D0 A8 44 1C 1F 09 E4 ED 95 12 68 "
            "87 08 6B 8C 08 7C A2 B0 63 4B 4C 09 30 10 57 71 70 73 52 E6 2B 83 DB 1D "
            "95 CD 11 7E 15 5C 81 EA"
        ),
    },
    "webp": {
        "type": "image",
        "mimetypes": ["image/webp"],
        "buffer": bytearray.fromhex(
            "52 49 46 46 C4 4E 00 00 57 45 42 50 56 50 38 20 B8 4E 00 00 30 76 02 9D "
            "01 2A 80 07 E8 03 3E 6D 36 9A 49 A4 23 22 A2 20 D3 C8 50 80 0D 89 67 6E "
            "FC 3E B9 FE 4A 47 62 AA BF A9 FE E7 FB 77 E1 E3 1F F9 63 F3 BF DF BF 72 "
            "BF B7 FB E1 59 5F CA FF 72 FD 9D EC D3 B9 EE B3 FD 94 F5 08 F3 7F D4 3F "
            "E4 7F 6D FC 8C F9 9B FE 37 FE 17 F6 CF F3 BF 04 7F 52 FF D1 FF 05 FB FF "
            "F4 03 FA D5 FF 3F D2 8F F6 F7 DC 67 EE DF FD 6F 60 BF D6 BF C5 FF EB FF "
            "2B EF 25 FE 8F FF 0F FA CF 74 FF D8 BF D6 7E D5 FF B8 F9 03 FE 85 FD D3 "
            "FF 1F E7 FF C6 AF B1 5F ED 8F FF 1F 70 BF E8 3F EF 7F F7 FA E7 FE DD FC "
            "29 7F 61 FF 75 FF CF FD B7 FB EF FF FF 44 7F B3 9F FC 7D 80 3F FC FB 5D "
            "FF 00 FF CF D6 EF D4 EF"
        ),
    },
}
