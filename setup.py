import sys
from cx_Freeze import setup, Executable

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(
        name='marquee_renderer',
        version="0.1",
        description="Renders Marquees",
        executables=[Executable('marquee_renderer.py', base=base)]
        )
