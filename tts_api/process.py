import argparse
import hashlib
import io
import logging
import sys
import time
import typing
import uuid
import wave
from pathlib import Path

from synthesize import Synthesizer

sample_rate = 0
cache_dir = False

def startmodel() -> None:
    global sample_rate
    config_path = False#'model/config.json'
    model_path  = False#'model'
    cache_dir   = False
    vocoder_path = False#'model/vocoder'
    vocoder_config_path = False#'model/vocoder/config.json'
    if not model_path:
        model_dir = Path("/app/model")
        #_LOGGER.debug("Looking for TTS model checkpoint in %s", model_dir)
        for checkpoint_path in model_dir.glob("*.pth.tar"):
            model_path = checkpoint_path
            break
    else:
        model_path = Path(model_path)
        model_dir = model_path.parent

    assert (
        model_path and model_path.is_file()
    ), f"No TTS model checkpoint ({model_path})"

    if not config_path:
        config_path = model_dir / "config.json"

    assert config_path and config_path.is_file(), f"No TTS config file ({config_path})"

    # Determine vocoder checkpoint/config paths
    if not vocoder_path:
        vocoder_dir = Path("/app/model/vocoder")
        if vocoder_dir.is_dir():
            #_LOGGER.debug("Looking for vocoder model checkpoint in %s", vocoder_dir)
            for checkpoint_path in vocoder_dir.glob("*.pth.tar"):
                vocoder_path = checkpoint_path
                break
    else:
        vocoder_path = Path(vocoder_path)
        vocoder_dir = vocoder_path.parent

    #if vocoder_config_path:
        #assert (
        #    vocoder_config_path.is_file()
        #), f"No vocoder model checkpoint ({vocoder_config_path})"

    if not vocoder_config_path:
        vocoder_config_path = vocoder_dir / "config.json"

    # assert (
    #     vocoder_config_path and vocoder_config_path.is_file()
    # ), f"No vocoder config file ({vocoder_config_path})"

    synthesizer = Synthesizer(
        config_path=config_path,
        model_path=model_path,
        use_cuda=False,
        vocoder_path=vocoder_path,
        vocoder_config_path=vocoder_config_path,
    )
    synthesizer.load()
    sample_rate = synthesizer.sample_rate
    return synthesizer


def text_to_wav(synthesizer,text: str) -> bytes:
       # _LOGGER.debug("Text: %s", text)

        wav_bytes: typing.Optional[bytes] = None
        cached_wav_path: typing.Optional[Path] = None

        if cache_dir:
            # Check cache first
            sentence_hash = hashlib.md5()
            sentence_hash.update(text.encode())
            cached_wav_path = cache_dir / f"{sentence_hash.hexdigest()}.wav"

            if cached_wav_path.is_file():
                _LOGGER.debug("Loading WAV from cache: %s", cached_wav_path)
                wav_bytes = cached_wav_path.read_bytes()

        if not wav_bytes:
            #_LOGGER.info("Synthesizing (%s char(s))...", len(text))
            start_time = time.time()

            # Synthesize each line separately.
            # Accumulate into a single WAV file.
            with io.BytesIO() as wav_io:
                with wave.open(wav_io, "wb") as wav_file:
                    wav_file.setframerate(sample_rate)
                    wav_file.setsampwidth(2)
                    wav_file.setnchannels(1)

                    for line_index, line in enumerate(text.strip().splitlines()):
                      #  _LOGGER.debug(
                      #      "Synthesizing line %s (%s char(s))",
                      #      line_index + 1,
                      #      len(line),
                      #  )
                        line_wav_bytes = synthesizer.synthesize(line)
                      #  _LOGGER.debug(
                      #      "Got %s WAV byte(s) for line %s",
                      #      len(line_wav_bytes),
                      #      line_index + 1,
                      #  )

                        # Open up and add to main WAV
                        with io.BytesIO(line_wav_bytes) as line_wav_io:
                            with wave.open(line_wav_io) as line_wav_file:
                                wav_file.writeframes(
                                    line_wav_file.readframes(line_wav_file.getnframes())
                                )

                wav_bytes = wav_io.getvalue()

            end_time = time.time()

           # _LOGGER.debug(
           #     "Synthesized %s byte(s) in %s second(s)",
           #     len(wav_bytes),
           #     end_time - start_time,
           # )

            # Save to cache
            if cached_wav_path:
                cached_wav_path.write_bytes(wav_bytes)

        return wav_bytes