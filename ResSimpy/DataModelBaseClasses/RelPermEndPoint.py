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
        """Initialises the RelPermEndPoint class.

        Args:
            swl (Optional[float], optional): the lowest water saturation value. Defaults to None.
            swr (Optional[float], optional): the residual water saturation value. Defaults to None.
            swu (Optional[float], optional): the maximum water saturation. Defaults to None.
            sgl (Optional[float], optional): the minimum gas saturation value (Ordinarily the value is
                zero). Defaults to None.
            sgr (Optional[float], optional): the residual gas saturation value. Defaults to None.
            sgu (Optional[float], optional): the maximum gas saturation. Defaults to None.
            swro (Optional[float], optional): the water saturation value at residual oil. Defaults to None.
            sgro (Optional[float], optional): the gas saturation value at residue oil saturation. Defaults
                to None.
            sgrw (Optional[float], optional): the gas saturation at residual water saturation. Defaults
                to None.
            krw_swro (Optional[float], optional): the relative permeability to water at the residual
                oil saturation. Defaults to None.
            krw_swu (Optional[float], optional): the relative permeability to water at the maximum
                water saturation. Defaults to None.
            krg_sgro (Optional[float], optional): the relative permeability to gas at the residual
                oil saturation. Defaults to None.
            krg_sgu (Optional[float], optional): the relative permeability to gas at the maximum gas
                saturation. Defaults to None.
            kro_swl (Optional[float], optional): the relative permeability to oil at the minimum water
                saturation. Defaults to None.
            kro_swr (Optional[float], optional): the relative permeability to oil at the residual water
                saturation. Defaults to None.
            kro_sgl (Optional[float], optional): the relative permeability to oil at the minimum gas
                saturation. Defaults to None.
            kro_sgr (Optional[float], optional): the relative permeability to oil at the residual gas
                saturation. Defaults to None.
            krw_sgl (Optional[float], optional): the relative permeability to water at the minimum gas
                saturation. Defaults to None.
            krw_sgr (Optional[float], optional): the relative permeability to water at the residual gas
                saturation. Defaults to None.
            krg_sgrw (Optional[float], optional): the relative permeability to gas at the residual water
                saturation. Defaults to None.
            sgtr (Optional[float], optional): the maximum trapped gas saturation. Defaults to None.
            sotr (Optional[float], optional): the maximum trapped oil saturation. Defaults to None.
        """
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
        """Returns a dictionary mapping keys to types (usually of type list)."""
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
