#
#
#    ▄▄▄▄▄▄▄▄     ▄▄       ▄▄▄▄    ▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄      ▄▄▄▄    ▄▄▄▄▄▄▄▄ ▄▄      ▄▄    ▄▄
#    ▀▀▀▀▀███    ████    ▄█▀▀▀▀█   ▀▀▀██▀▀▀  ██▀▀▀▀▀▀  ██▀▀▀▀█▄  ▄█▀▀▀▀█   ▀▀▀██▀▀▀ ██      ██   ████
#        ██▀     ████    ██▄          ██     ██        ██    ██  ██▄          ██    ▀█▄ ██ ▄█▀   ████
#      ▄██▀     ██  ██    ▀████▄      ██     ███████   ██████▀    ▀████▄      ██     ██ ██ ██   ██  ██
#     ▄██       ██████        ▀██     ██     ██        ██             ▀██     ██     ███▀▀███   ██████
#    ███▄▄▄▄▄  ▄██  ██▄  █▄▄▄▄▄█▀     ██     ██▄▄▄▄▄▄  ██        █▄▄▄▄▄█▀     ██     ███  ███  ▄██  ██▄
#    ▀▀▀▀▀▀▀▀  ▀▀    ▀▀   ▀▀▀▀▀       ▀▀     ▀▀▀▀▀█▀▀  ▀▀         ▀▀▀▀▀       ▀▀     ▀▀▀  ▀▀▀  ▀▀    ▀▀
#                                                █▄▄
#

# Standardowe biblioteki
import asyncio
import re
from typing import Optional

# Zewnętrzne biblioteki
import discord

# Wewnętrzne importy
from src.classes.constants import Constants
from src.handlers.logging import logiKonsoli
from src.helpers.helpers import (
    ograniczReagowanie,
    ograniczUsuwanie,
    ograniczWysyłanie,
    pobierzSzczęśliweNumerkiNaDzień
)

async def wyślijNumerki(
    kanał: discord.TextChannel,
    identyfikatorSerwera: int,
    informacjeDodatkowe: str,
    szkoła: str = ""
) -> None:
    """
    Wysyła aktualizacje z szczęśliwymi numerkami dla danego dnia do konkretnego kanału tekstowego Discord.

    Args:
        kanał (discord.TextChannel): Kanał tekstowy Discord, na który zostaną wysłane wiadomości.
        identyfikatorSerwera (int): ID serwera Discord.
        informacjeDodatkowe (str): Tekst informacji dodatkowych nad zastépstwami.
        aktualneWpisyZastępstw (Optional[list[tuple[str, list[str]]]]): Lista zastępstw (nie jest używana).
        szkoła (str): Identyfikator szkoły do pobrania szczęśliwych numerków.
    """

    def wyodrębnijDzień(tekst: str) -> Optional[str]:
        """
        Wyodrębnia datę w formacie DD.MM z tekstu informacji dodatkowych.

        Args:
            tekst (str): Tekst zawierający informacje dodatkowe.

        Returns:
            Optional[str]: Data w formacie DD.MM lub None.
        """
        dopasowanie = re.search(r'\b(\d{1,2})\.(\d{1,2})\b', tekst)
        if dopasowanie:
            dzień = dopasowanie.group(1).zfill(2)
            miesiąc = dopasowanie.group(2).zfill(2)
            return f"{dzień}.{miesiąc}"
        return None

    opis = (
        "**Szczęśliwe numerki:**"
        f"\n{informacjeDodatkowe}"
    )

    try:
        dzień = wyodrębnijDzień(informacjeDodatkowe)

        if not dzień or not szkoła:
            logiKonsoli.warning(
                f"Brak dnia lub szkoły dla serwera o ID {identyfikatorSerwera}. Szczęśliwe numerki nie mogą być wysłane."
            )
            return

        szczesliweNumerki = pobierzSzczęśliweNumerkiNaDzień(szkoła, dzień)

        if szczesliweNumerki:
            embed = discord.Embed(
                title="**Szczęśliwe numerki!**",
                description=opis,
                color=Constants.KOLOR
            )

            embed.add_field(
                name="Szczęśliwe numerki",
                value=", ".join(str(numerek) for numerek in szczesliweNumerki),
                inline=False
            )

            embed.set_footer(text=Constants.KRÓTSZA_STOPKA)
            ostatniaWiadomość = await ograniczWysyłanie(kanał, embed=embed)

            if ostatniaWiadomość:
                await ograniczReagowanie(ostatniaWiadomość, "❤️")
        else:
            embed = discord.Embed(
                title="**Brak szczęśliwych numerków**",
                description=opis,
                color=Constants.KOLOR
            )

            embed.add_field(
                name="Informacja",
                value="Dla tego dnia nie zostały znalezione szczęśliwe numerki.",
                inline=False
            )

            embed.set_footer(text=Constants.KRÓTSZA_STOPKA)
            await ograniczWysyłanie(kanał, embed=embed)

    except discord.DiscordException as e:
        logiKonsoli.exception(
            f"Wystąpił błąd podczas wysyłania wiadomości do serwera o ID {identyfikatorSerwera}. Więcej informacji: {e}"
        )
    except Exception as e:
        logiKonsoli.exception(
            f"Wystąpił nieoczekiwany błąd podczas wysyłania wiadomości do serwera o ID {identyfikatorSerwera}. Więcej informacji: {e}"
        )