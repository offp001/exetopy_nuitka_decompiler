
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXETOPYHH = ROOT / "test" / "exetopyh.py"
PYCDC_DIR = ROOT / "src" / "pycdc"


def status(message):
    print(f"[exetopy(nuitka)] {message}", flush=True)


def find_output(exe, previous):
    candidates = [
        path for path in exe.parent.glob(f"UNPACKED_{exe.stem}_*")
        if path.is_dir() and path.resolve() not in previous
    ]

    if not candidates:
        return None

    return max(candidates, key=lambda path: path.stat().st_mtime)


def unique_destination(path):
    if not path.exists():
        return path

    index = 2
    while True:
        candidate = path.with_name(f"{path.name}_{index}")
        if not candidate.exists():
            return candidate
        index += 1


def find_tool(name):
    bundled = [
        PYCDC_DIR / name,
        PYCDC_DIR / "build" / name,
        PYCDC_DIR / "bin" / name
    ]

    for path in bundled:
        if path.is_file():
            return str(path)

    if PYCDC_DIR.is_dir():
        matches = [
            path for path in PYCDC_DIR.rglob(name)
            if path.is_file()
        ]

        if matches:
            return str(matches[0])

    system_tool = shutil.which(name)

    if system_tool:
        return system_tool

    raise FileNotFoundError(
        f"cant find {name} in {PYCDC_DIR}"
    )


def run_EXETOPYHH(exe):
    if not EXETOPYHH.is_file():
        raise FileNotFoundError(
            f"cant find exetopyh: {EXETOPYHH}"
        )

    previous = {
        path.resolve()
        for path in exe.parent.glob(f"UNPACKED_{exe.stem}_*")
        if path.is_dir()
    }

    log_path = exe.parent / f".{exe.stem}_EXETOPYHH.log"

    status("starting exetopyh")

    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.run(
            [sys.executable, str(EXETOPYHH), str(exe)],
            cwd=exe.parent,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False
        )

    output = find_output(exe, previous)

    if output is None:
        status("cant create exetopyh folder.")
        status(f"log: {log_path}")
        raise RuntimeError(
            f"exetopyh failed, return code: {process.returncode}"
        )

    destination = unique_destination(
        exe.parent / f"{exe.stem}_decompiled"
    )

    output.rename(destination)

    shutil.move(
        str(log_path),
        str(destination / "exetopyh.log")
    )

    status(f"exetopyh completed: {destination.name}")

    if process.returncode != 0:
        status(f"exetopyh return code: {process.returncode}")
        status(f"log: {destination / 'exetopyh.log'}")

        raise RuntimeError(
            "exetopyh finished with errors"
        )

    return destination


def convert_pyc(output):
    pycdc = find_tool("pycdc")
    pycdas = find_tool("pycdas")

    status(f"pycdc: {pycdc}")
    status(f"pycdas: {pycdas}")

    pyc_files = sorted(output.rglob("*.pyc"))

    if not pyc_files:
        status("no .pyc file.")
        return []

    converted = []

    status(f"{len(pyc_files)} .pyc files found.")

    for index, pyc in enumerate(pyc_files, 1):
        status(f"converting: {index}/{len(pyc_files)} - {pyc.name}")

        source_file = pyc.with_suffix(".py")
        assembly_file = pyc.with_suffix(".pyasm")

        try:
            source = subprocess.run(
                [pycdc, str(pyc)],
                capture_output=True,
                text=True,
                errors="replace",
                check=False
            )

            assembly = subprocess.run(
                [pycdas, str(pyc)],
                capture_output=True,
                text=True,
                errors="replace",
                check=False
            )

            if source.stdout:
                source_file.write_text(
                    source.stdout,
                    encoding="utf-8",
                    errors="replace"
                )

            if assembly.stdout:
                assembly_file.write_text(
                    assembly.stdout,
                    encoding="utf-8",
                    errors="replace"
                )

            if source.returncode == 0 and source.stdout:
                converted.append(source_file)
            else:
                status(f"PyCDC error: {pyc.name}")

            if assembly.returncode != 0:
                status(f"PyCDAS error: {pyc.name}")

        except OSError as error:
            status(f"convert error: {error}")

    return converted


def main():
    parser = argparse.ArgumentParser(
        prog="exetopy",
        description="Nuitka executable decompiler"
    )

    parser.add_argument("exe", help="exe file")
    args = parser.parse_args()

    exe = Path(args.exe).expanduser().resolve()

    if not exe.is_file():
        status(f"cant find exe: {exe}")
        return 1

    try:
        output = run_EXETOPYHH(exe)
        converted = convert_pyc(output)

        status(f"converted files: {len(converted)}")

        if converted:
            main_file = max(
                converted,
                key=lambda path: path.stat().st_size
            )

            status(f"main file: {main_file.relative_to(output)}")
        else:
            status("cant find main python file.")

        status(f"output folder: {output}")
        return 0

    except KeyboardInterrupt:
        status("terminated process by user")
        return 130

    except Exception as error:
        status(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
