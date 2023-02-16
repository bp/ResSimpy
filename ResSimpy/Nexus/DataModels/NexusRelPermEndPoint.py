from dataclasses import dataclass
from typing import Optional
from ResSimpy.RelPermEndPoint import RelPermEndPoint


@dataclass
class NexusRelPermEndPoint(RelPermEndPoint):
    def __init__(self, swl: Optional[float] = None, swr: Optional[float] = None, swu: Optional[float] = None,
                 sgl: Optional[float] = None, sgr: Optional[float] = None, sgu: Optional[float] = None,
                 swro: Optional[float] = None, sgro: Optional[float] = None, sgrw: Optional[float] = None,
                 krw_swro: Optional[float] = None, krw_swu: Optional[float] = None, krg_sgro: Optional[float] = None,
                 krg_sgu: Optional[float] = None, kro_swl: Optional[float] = None, kro_swr: Optional[float] = None,
                 kro_sgl: Optional[float] = None, kro_sgr: Optional[float] = None, krw_sgl: Optional[float] = None,
                 krw_sgr: Optional[float] = None, krg_sgrw: Optional[float] = None, sgtr: Optional[float] = None,
                 sotr: Optional[float] = None, ):
        super().__init__(swl=swl, swr=swr, swu=swu, sgl=sgl, sgr=sgr, sgu=sgu, swro=swro, sgro=sgro,
                         sgrw=sgrw, krw_swro=krw_swro, krw_swu=krw_swu, krg_sgro=krg_sgro, krg_sgu=krg_sgu,
                         kro_swl=kro_swl, kro_swr=kro_swr, kro_sgl=kro_sgl, kro_sgr=kro_sgr, krw_sgl=krw_sgl,
                         krw_sgr=krw_sgr, krg_sgrw=krg_sgrw, sgtr=sgtr, sotr=sotr, )
