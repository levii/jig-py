import enum


class Color(enum.Enum):
    # https://graphviz.org/doc/info/colors.html#svg
    White = "white"
    Black = "black"
    Darkgray = "darkgray"
    LightGray = "lightgray"
    Red = "red"
    Blue = "blue"
    Green = "green"
    Yellow = "yellow"
    Purple = "purple"
    Teal = "teal"
    Navy = "navy"


class PenWidth(enum.Enum):
    Normal = "normal"
    Bold = "bold"
    Thin = "thin"

    @classmethod
    def to_size(cls, penwidth: "PenWidth") -> str:
        return {
            PenWidth.Normal: "1.0",
            PenWidth.Bold: "3.0",
            PenWidth.Thin: "0.5",
        }.get(penwidth, "1.0")
