from dataclasses import dataclass


@dataclass
class HFModelInfo:

    model_id: str

    author: str

    sha: str

    private: bool

    disabled: bool


@dataclass
class HFFile:

    path: str

    size: int


@dataclass
class HFRepository:

    info: HFModelInfo

    files: list[HFFile]