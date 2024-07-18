import math
import scipy.io.wavfile
from statistics import mode
import sys


code_map = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
}


class MorseDecoder:
    TOLERANCE = 5

    def __init__(self, path):
        self.path = path
        self.spacing = set()
        self.tones = []
        self.chunks = []

    def analyze(self):
        """Analyze the waveform and pick out tone and spacing values"""
        _, waveform = scipy.io.wavfile.read(self.path)
        space = mode(waveform)
        counter = 0
        spacer = 0

        for idx, value in enumerate(waveform, 1):
            if value == space:
                spacer += 1
            else:
                if spacer > self.TOLERANCE:
                    self.spacing.add(round(spacer, -1))
                    self.chunks.append(spacer)
                spacer = 0
                counter += 1
            if counter > 1 and (value == space and waveform[idx + 1] == space):
                self.chunks.append(len(waveform[idx - counter : idx]))
                self.tones.append(len(waveform[idx - counter : idx]))
                counter = 0
                spacer = 0

    def decode(self):
        self.analyze()
        tone_space, letter_space, word_space = self._get_spacing_values(self.spacing)
        translation = []
        current_letter = ""
        max_tone = max(self.tones, default=0)
        min_tone = min(self.tones, default=0)
        for chunk in self.chunks:
            if self._is_within_threshold(chunk, tone_space):
                continue
            if self._is_within_threshold(chunk, word_space):
                if current_letter:
                    translation.append(self._get_code_value(current_letter))
                translation.append(" ")
                current_letter = ""
            elif self._is_within_threshold(chunk, letter_space):
                translation.append(self._get_code_value(current_letter))
                current_letter = ""
            elif self._is_within_threshold(chunk, max_tone):
                current_letter += "-"
            elif self._is_within_threshold(chunk, min_tone):
                current_letter += "."

        if current_letter:
            translation.append(self._get_code_value(current_letter))
        translation = "".join(translation)
        print(f"Translation: {translation}")

    def _get_spacing_values(self, spacing):
        """Extract tone, letter, and word spacing values."""
        spacing = sorted(spacing)
        tone_space = spacing[0] if len(spacing) > 0 else 0
        letter_space = spacing[1] if len(spacing) > 1 else 0
        word_space = spacing[2] if len(spacing) > 2 else 0
        return tone_space, letter_space, word_space

    def _is_within_threshold(self, value, reference):
        """Check if the value is within +/- 5 of the reference."""
        return reference - self.TOLERANCE < value < reference + self.TOLERANCE

    def _get_code_value(self, code):
        return code_map.get(code, "?")


def main():
    path = sys.argv[1]
    decoder = MorseDecoder(path)
    decoder.decode()


if __name__ == "__main__":
    main()
