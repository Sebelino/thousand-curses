#!/usr/bin/env python

"""
Encoding/decoding functions.

An encoding function maps a bytestring to a unicode string.
A decoding function maps a unicode string to a bytestring.

Encoders/decoders are bijective -- each encoder has a inverse decoder function,
and vice versa.
"""

import os
import yaml
from abc import ABC, abstractmethod


package_dir = os.path.dirname(os.path.abspath(__file__))


def read_yaml(path):
    """ YAML -> Dictionary. """
    stream = open(path, 'r', encoding='utf8')
    dct = yaml.load(stream)
    return dct


class Codec(ABC):
    @classmethod
    @abstractmethod
    def encode(cls, s):
        raise NotImplementedError("Encoder for {0} not implemented.".format(cls.__name__))

    @classmethod
    @abstractmethod
    def decode(cls, bytestr):
        raise NotImplementedError("Decoder for {0} not implemented.".format(cls.__name__))


class Hexify(Codec):
    def encode(s):
        return bytes([int(s[i:i+2], base=16) for i in range(len(s))])

    def decode(bytestr):
        return "".join(("0"+hex(n)[2:])[-2:].upper() for n in bytestr)


class HexifySpaces(Codec):
    def encode(s):
        return bytes([int(b, base=16) for b in s.split()])

    def decode(bytestr):
        return " ".join(Hexify.decode(bytes([n])) for n in bytestr)


class ASCII(Codec):

    def decode(bytestr):
        return "".join(chr(b) for b in bytestr)


class MonospaceASCIIByte(Codec):
    """ Like ASCII, but replaces any unprintable and non-monospace character
    with some other (non-ascii) monospace character. """

    def decode(bytestr):
        b = bytestr[0]
        replacements = list(range(2**8, 2**9))
        if not chr(b).isprintable():
            return chr(replacements[b])
        return chr(b)


class MonospaceASCII(Codec):

    def decode(bytestr):
        return "".join(MonospaceASCIIByte.decode(bytes([b])) for b in bytestr)


class MajinTenseiIIByte(Codec):
    """ Bytestrings of length 1 """

    hexmap = os.path.join(package_dir, "resources/hexmap.yaml")
    transliter = read_yaml(hexmap)

    def decode(bytestr):
        return MajinTenseiIIByte.transliter[bytestr[0]]


class Mt2GarbageTextPair(Codec):

    def decode(bytestr):
        garbage = "".join(MonospaceASCIIByte.decode(bytes([b])) for b in
                          bytestr[1::2])
        text = "".join(MajinTenseiIIByte.decode(bytes([b])) for b in bytestr[::2])
        return garbage+text


names = {
    "Hexify": Hexify,
    "HexifySpaces": HexifySpaces,
    "ASCII": ASCII,
    "MonospaceASCIIByte": MonospaceASCIIByte,
    "MonospaceASCII": MonospaceASCII,
    "MajinTenseiIIByte": MajinTenseiIIByte,
    "Mt2GarbageTextPair": Mt2GarbageTextPair,
}
