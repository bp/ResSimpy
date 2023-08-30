from __future__ import annotations
from dataclasses import dataclass
from abc import ABC
from typing import Optional


@dataclass
class RelPermEndPoint(ABC):
    __swl: Optional[float] = None
    __swr: Optional[float] = None
    __swu: Optional[float] = None
    __sgl: Optional[float] = None
    __sgr: Optional[float] = None
    __sgu: Optional[float] = None
    __swro: Optional[float] = None
    __sgro: Optional[float] = None
    __sgrw: Optional[float] = None
    __krw_swro: Optional[float] = None
    __krw_swu: Optional[float] = None
    __krg_sgro: Optional[float] = None
    __krg_sgu: Optional[float] = None
    __kro_swl: Optional[float] = None
    __kro_swr: Optional[float] = None
    __kro_sgl: Optional[float] = None
    __kro_sgr: Optional[float] = None
    __krw_sgl: Optional[float] = None
    __krw_sgr: Optional[float] = None
    __krg_sgrw: Optional[float] = None
    __sgtr: Optional[float] = None
    __sotr: Optional[float] = None

    def __init__(self, swl: Optional[float] = None, swr: Optional[float] = None, swu: Optional[float] = None,
                 sgl: Optional[float] = None, sgr: Optional[float] = None, sgu: Optional[float] = None,
                 swro: Optional[float] = None, sgro: Optional[float] = None, sgrw: Optional[float] = None,
                 krw_swro: Optional[float] = None, krw_swu: Optional[float] = None, krg_sgro: Optional[float] = None,
                 krg_sgu: Optional[float] = None, kro_swl: Optional[float] = None, kro_swr: Optional[float] = None,
                 kro_sgl: Optional[float] = None, kro_sgr: Optional[float] = None, krw_sgl: Optional[float] = None,
                 krw_sgr: Optional[float] = None, krg_sgrw: Optional[float] = None, sgtr: Optional[float] = None,
                 sotr: Optional[float] = None) -> None:
        self.__swl = swl
        self.__swr = swr
        self.__swu = swu
        self.__sgl = sgl
        self.__sgr = sgr
        self.__sgu = sgu
        self.__swro = swro
        self.__sgro = sgro
        self.__sgrw = sgrw
        self.__krw_swro = krw_swro
        self.__krw_swu = krw_swu
        self.__krg_sgro = krg_sgro
        self.__krg_sgu = krg_sgu
        self.__kro_swl = kro_swl
        self.__kro_swr = kro_swr
        self.__kro_sgl = kro_sgl
        self.__kro_sgr = kro_sgr
        self.__krw_sgl = krw_sgl
        self.__krw_sgr = krw_sgr
        self.__krg_sgrw = krg_sgrw
        self.__sgtr = sgtr
        self.__sotr = sotr

    def to_dict(self) -> dict[str, Optional[float]]:
        attribute_dict: dict[str, Optional[float]] = {
            'swl': self.__swl,
            'swr': self.__swr,
            'swu': self.__swu,
            'sgl': self.__sgl,
            'sgr': self.__sgr,
            'sgu': self.__sgu,
            'swro': self.__swro,
            'sgro': self.__sgro,
            'sgrw': self.__sgrw,
            'krw_swro': self.__krw_swro,
            'krw_swu': self.__krw_swu,
            'krg_sgro': self.__krg_sgro,
            'krg_sgu': self.__krg_sgu,
            'kro_swl': self.__kro_swl,
            'kro_swr': self.__kro_swr,
            'kro_sgl': self.__kro_sgl,
            'kro_sgr': self.__kro_sgr,
            'krw_sgl': self.__krw_sgl,
            'krw_sgr': self.__krw_sgr,
            'krg_sgrw': self.__krg_sgrw,
            'sgtr': self.__sgtr,
            'sotr': self.__sotr,
        }
        return attribute_dict
