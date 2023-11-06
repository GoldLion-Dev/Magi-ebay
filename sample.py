from cx_Freeze import setup, Executable

setup(
    name="setup",
    version="1.0",
    description="Description of Your Script",
    executables=[Executable("setup.py",base="Win32GUI")]
)

