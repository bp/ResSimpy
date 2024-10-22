"""Class for Nexus relative permeability endpoints data storage."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from ResSimpy.DataModelBaseClasses.RelPermEndPoint import RelPermEndPoint


@dataclass
class NexusRelPermEndPoint(RelPermEndPoint):
    """Class for Nexus relative permeability endpoints data storage."""
    def __init__(self, swl: Optional[float] = None, swr: Optional[float] = None, swu: Optional[float] = None,
                 sgl: Optional[float] = None, sgr: Optional[float] = None, sgu: Optional[float] = None,
                 swro: Optional[float] = None, sgro: Optional[float] = None, sgrw: Optional[float] = None,
                 krw_swro: Optional[float] = None, krw_swu: Optional[float] = None, krg_sgro: Optional[float] = None,
                 krg_sgu: Optional[float] = None, kro_swl: Optional[float] = None, kro_swr: Optional[float] = None,
                 kro_sgl: Optional[float] = None, kro_sgr: Optional[float] = None, krw_sgl: Optional[float] = None,
                 krw_sgr: Optional[float] = None, krg_sgrw: Optional[float] = None, sgtr: Optional[float] = None,
                 sotr: Optional[float] = None) -> None:
        """Initialises the NexusRelPermEndPoint class.

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
        super().__init__(swl=swl, swr=swr, swu=swu, sgl=sgl, sgr=sgr, sgu=sgu, swro=swro, sgro=sgro,
                         sgrw=sgrw, krw_swro=krw_swro, krw_swu=krw_swu, krg_sgro=krg_sgro, krg_sgu=krg_sgu,
                         kro_swl=kro_swl, kro_swr=kro_swr, kro_sgl=kro_sgl, kro_sgr=kro_sgr, krw_sgl=krw_sgl,
                         krw_sgr=krw_sgr, krg_sgrw=krg_sgrw, sgtr=sgtr, sotr=sotr)

    @staticmethod
    def nexus_mapping() -> dict[str, tuple[str, type]]:
        """Returns a dictionary of mapping from nexus keyword to attribute name."""
        nexus_mapping: dict[str, tuple[str, type]] = {
            'SWL': ('swl', float),
            'SWR': ('swr', float),
            'SWU': ('swu', float),
            'SGL': ('sgl', float),
            'SGR': ('sgr', float),
            'SGU': ('sgu', float),
            'SWRO': ('swro', float),
            'SGRO': ('sgro', float),
            'SGRW': ('sgrw', float),
            'KRW_SWRO': ('krw_swro', float),
            'KRW_SWU': ('krw_swu', float),
            'KRG_SGRO': ('krg_sgro', float),
            'KRG_SGU': ('krg_sgu', float),
            'KRO_SWL': ('kro_swl', float),
            'KRO_SWR': ('kro_swr', float),
            'KRO_SGL': ('kro_sgl', float),
            'KRO_SGR': ('kro_sgr', float),
            'KRW_SGL': ('krw_sgl', float),
            'KRW_SGR': ('krw_sgr', float),
            'KRG_SGRW': ('krg_sgrw', float),
            'SGTR': ('sgtr', float),
            'SOTR': ('sotr', float),
        }
        return nexus_mapping
