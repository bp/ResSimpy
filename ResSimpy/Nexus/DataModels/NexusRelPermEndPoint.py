"""Class for Nexus relative permeability endpoints data storage."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from ResSimpy.RelPermEndPoint import RelPermEndPoint


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
