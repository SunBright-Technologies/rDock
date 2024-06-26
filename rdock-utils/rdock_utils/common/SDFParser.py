# Standard Library
import itertools
import logging
from io import StringIO
from typing import Any, Generator, Iterable, TextIO

logger = logging.getLogger("SDParser")


class FastSDMol:
    def __init__(self, lines: list[str], data: dict[str, str]) -> None:
        self.lines = lines
        self.data = data

    @classmethod
    def read(cls, source: TextIO) -> "FastSDMol | None":
        lines: list[str] = []
        data: dict[str, str] = {}
        terminator_found = False
        for line in source:
            if line.startswith("$$$$"):
                terminator_found = True
                break
            if not line.startswith(">"):
                lines.append(line)
                continue

            # dealing with fields
            field_name = cls.parse_field_name(line)
            field_value = source.readline()
            if field_value.startswith("$$$$"):
                terminator_found = True
                logger.warning(
                    f"found end of molecule {lines[0]} while looking for field {field_name} value."
                    " defaulting to empty string."
                )
                data[field_name] = ""
                break
            data[field_name] = field_value.strip("\n")
            discard_line = source.readline()
            if discard_line.startswith("$$$$"):
                terminator_found = True
                logger.warning(f"found end of molecule {lines[0]} while expecting empty line after field {field_name}")
                break

        if not terminator_found and all(line.strip() == "" for line in lines):
            return None

        if len(lines) >= 4:
            return cls(lines, data)

        # if we've reached this point, we have an invalid molecule
        raise ValueError(f"invalid molecule: {lines}")

    @staticmethod
    def parse_field_name(field_line: str) -> str:
        field_start = field_line.find("<") + 1
        field_end = field_line.find(">", 1)
        return field_line[field_start:field_end]

    @staticmethod
    def str_field(field_name: str, field_value: Any) -> str:
        return f">  <{field_name}>\n{field_value}\n\n"

    def __repr__(self) -> str:
        str_io = StringIO()
        self.write(str_io)
        return str_io.getvalue()

    def __str__(self) -> str:
        return f"<Molecule {self.lines[0]}>"

    def write(self, dest: TextIO) -> None:
        dest.writelines(self.lines)
        for field_name, field_value in self.data.items():
            dest.write(self.str_field(field_name, field_value))
        dest.write("$$$$\n")

    def get_field(self, field_name: str) -> str | None:
        if field_name.startswith("_TITLE"):
            line_number = int(field_name[-1]) - 1
            if 0 <= line_number < min(len(self.lines), 3):
                return self.lines[line_number].strip()
            return None
        return self.data.get(field_name, None)

    def set_title(self, title: str, line_index: int = 0) -> None:
        if line_index > 2:
            raise ValueError("line index must be 0, 1, or 2")
        self.lines[line_index] = title + ("" if title.endswith("\n") else "\n")

    @property
    def title(self) -> str:
        return self.lines[0].strip()


def read_molecules(file: TextIO) -> Generator[FastSDMol, None, None]:
    while True:
        try:
            mol = FastSDMol.read(file)
            if mol is None:
                break
            yield mol
        except ValueError as e:
            logger.warning(f"error reading molecule: {e}")


def read_molecules_from_all_inputs(inputs: Iterable[TextIO]) -> Iterable[FastSDMol]:
    return itertools.chain.from_iterable(read_molecules(source) for source in inputs)


def molecules_with_progress_log(molecules: Iterable[FastSDMol], count: int = 1000) -> Iterable[FastSDMol]:
    for i, molecule in enumerate(molecules):
        if i % count == 0:
            logger.info(f"read {i} molecules")

        yield molecule
