import soxbindings
import soundfile as sf 
import numpy as np 
import tempfile
import pytest
import subprocess

INPUT_FILES = [
    'tests/data/input.wav',
]

def sox(args):
    if args[0].lower() != "sox":
        args.insert(0, "sox")
    else:
        args[0] = "sox"

    try:
        process_handle = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        out, err = process_handle.communicate()
        #out = out.decode("utf-8")
        err = err.decode("utf-8")

        status = process_handle.returncode

        return status, out, err

    except OSError as error_msg:
        logger.error("OSError: SoX failed! %s", error_msg)
    except TypeError as error_msg:
        logger.error("TypeError: %s", error_msg)
    return 1, None, None

@pytest.mark.parametrize("input_file", INPUT_FILES)
def test_read(input_file):
    sox_data, sox_rate = soxbindings.read(input_file)
    sf_data, sf_rate = sf.read(input_file, always_2d=True)

    assert np.allclose(sox_data, sf_data)
    assert sox_rate == sf_rate

@pytest.mark.parametrize("input_file", INPUT_FILES)
def test_write(input_file):
    sox_data, sox_rate = soxbindings.read(input_file)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp:
        soxbindings.write(tmp.name, sox_data, sox_rate)

        sf_data, sf_rate = sf.read(tmp.name, always_2d=True)
        sox_data_2, _ = soxbindings.read(tmp.name)

        assert np.allclose(sox_data, sf_data)
        assert np.allclose(sox_data, sox_data_2)

with open('tests/subset.txt', 'r') as f:
    COMMANDS = f.readlines()
    COMMANDS = [c.rstrip() for c in COMMANDS]

@pytest.mark.parametrize("command", COMMANDS)
def test_against_sox(command):
    status, out, err = sox(command.split())
    
    if 'output.wav' in command:
        cmd_sox_data, sr = soxbindings.read('tests/data/output.wav')
        py_sox_data, sr = soxbindings.sox(command)
        assert np.allclose(cmd_sox_data, py_sox_data)
        