"""WMO weather code → kullanıcı dostu Türkçe durum/açıklama.

Open-Meteo, WMO Weather interpretation codes kullanır:
https://open-meteo.com/en/docs
"""

from __future__ import annotations


def describe_weather_code(code: int) -> tuple[str, str]:
    """Return ``(status, description)`` for a WMO weather code.

    Bilinmeyen kodlarda güvenli bir varsayılan döner.
    """
    mapping: dict[int, tuple[str, str]] = {
        0: ("Açık", "Gökyüzü açık"),
        1: ("Çoğunlukla açık", "Çoğunlukla açık hava"),
        2: ("Parçalı bulutlu", "Parçalı bulutlu"),
        3: ("Kapalı", "Bulutlu / kapalı gökyüzü"),
        45: ("Sisli", "Sis"),
        48: ("Sisli", "Kırağılı sis"),
        51: ("Çisenti", "Hafif çisenti"),
        53: ("Çisenti", "Orta şiddette çisenti"),
        55: ("Çisenti", "Yoğun çisenti"),
        56: ("Dondurucu çisenti", "Hafif dondurucu çisenti"),
        57: ("Dondurucu çisenti", "Yoğun dondurucu çisenti"),
        61: ("Yağmurlu", "Hafif yağmur"),
        63: ("Yağmurlu", "Orta şiddette yağmur"),
        65: ("Yağmurlu", "Şiddetli yağmur"),
        66: ("Dondurucu yağmur", "Hafif dondurucu yağmur"),
        67: ("Dondurucu yağmur", "Şiddetli dondurucu yağmur"),
        71: ("Karlı", "Hafif kar"),
        73: ("Karlı", "Orta şiddette kar"),
        75: ("Karlı", "Şiddetli kar"),
        77: ("Kar taneleri", "Kar taneleri"),
        80: ("Sağanak", "Hafif sağanak yağış"),
        81: ("Sağanak", "Orta şiddette sağanak"),
        82: ("Sağanak", "Şiddetli sağanak"),
        85: ("Kar sağanağı", "Hafif kar sağanağı"),
        86: ("Kar sağanağı", "Şiddetli kar sağanağı"),
        95: ("Fırtınalı", "Gök gürültülü fırtına"),
        96: ("Fırtınalı", "Hafif dolu ile fırtına"),
        99: ("Fırtınalı", "Şiddetli dolu ile fırtına"),
    }
    return mapping.get(code, ("Bilinmiyor", f"WMO weather code {code}"))
