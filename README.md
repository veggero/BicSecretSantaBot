# BicSecretSantaBot
Il bot non ufficiale per il Secret Santa del Breaking Italy Club

## Requirements
Il bot funziona basandosi sulla libreria [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).
Per installarla:
``` pip install pyTelegramBotAPI``` 
Le istruzioni si basano sull'idea che tu sia su una piattaforma Linux.

## Running the bot
Per provare il bot, ti conviene creare un tuo bot seguendo le istruzioni del [BotFather](https://telegram.me/BotFather).
Successivamente:
- esegui lo script `init_files.sh`, questo inizializzerà tre file vuoti: `api_token.csv`, `assignemnts.json` e `registered_users.json`.
- copia il token di autenticazione del tuo bot e incollalo nel file `api_token.csv`.
- `python ss_bot.py`

## Contributions
Per contribuire, puoi guardare le [open issues](https://github.com/CarolinaBianchi/BicSecretSantaBot/issues) ed aprire una Pull Request. Puoi anche aprire un'issue se trovi un bug.
