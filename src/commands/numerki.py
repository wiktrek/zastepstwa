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
import contextlib
from datetime import datetime

# Zewnętrzne biblioteki
import discord

# Wewnętrzne importy
from src.classes.commands import WidokGłówny
from src.classes.constants import Constants
from src.handlers.configuration import konfiguracja, blokadaKonfiguracji
from src.helpers.helpers import pobierzSzczęśliweNumerkiNaDzień
from src.handlers.logging import (
	logiKonsoli,
	logujPolecenia
)

def ustaw(bot: discord.Client) -> None:
	"""
	Rejestruje polecenie `/numerki` w drzewie bota.

	Args:
		bot (discord.Client): Instancja klienta Discord, do której dodawane jest polecenie.
	"""

	@bot.tree.command(
		name="numerki",
		description="Wyświetl dzisiejsze szczęśliwe numerki"
	)

	async def numerki(interaction: discord.Interaction) -> None:
		"""
		Wyświetla szczęśliwe numerki dla danej szkoły.

		Args:
			interaction (discord.Interaction): Obiekt interakcji wywołujący polecenie.
		"""

		try:
			embed = discord.Embed(
				title="**Szczęśliwe numerki**",
				color=Constants.KOLOR
			)
			identyfikatorSerwera = str(interaction.guild.id) if interaction.guild else "01"
			async with blokadaKonfiguracji:
				szkola = konfiguracja.get("serwery", {}).get(identyfikatorSerwera, {}).get("szkoła", "01")
			szczesliweNumerki = pobierzSzczęśliweNumerkiNaDzień(szkola, datetime.today().strftime('%d.%m'))
			if szczesliweNumerki:
				embed.add_field(
					name="Numerki:",
					value=", ".join(str(numerek) for numerek in szczesliweNumerki)
				)
			else:
				embed.add_field(
					name="Brak szczęśliwych numerków",
					value=("Skontaktuj się z Administratorem bota.")
				)
			embed.set_footer(text=Constants.KRÓTSZA_STOPKA)
			await interaction.response.send_message(embed=embed)
			logujPolecenia(interaction, sukces=True)
		except Exception as e:
			logujPolecenia(interaction, sukces=False, wiadomośćBłędu=str(e))
			logiKonsoli.exception(
				f"Wystąpił błąd podczas wywołania polecenia „/numerki”. Więcej informacji: {e}"
			)
			with contextlib.suppress(Exception):
				if not interaction.response.is_done():
					await interaction.response.send_message(
						"Wystąpił błąd. Spróbuj ponownie lub skontaktuj się z administratorem bota.",
						ephemeral=True
					)
				else:
					await interaction.followup.send(
						"Wystąpił błąd. Spróbuj ponownie lub skontaktuj się z administratorem bota.",
						ephemeral=True
					)