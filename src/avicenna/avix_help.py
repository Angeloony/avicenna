from importlib import resources
from pathlib import Path

# get the path to source in avicenna, from where we will import the instr file
def get_avicenna_rsc_path() -> Path:
    with resources.path('avicenna', 'rsc') as p:
        return Path(p)