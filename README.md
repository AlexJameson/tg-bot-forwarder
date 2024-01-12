# Telegram Forwarding Bot (MVP)

This is a bot that allows forwarding messages from a group chat to a channel or another group chat. It is designed to create some kind of knowledge base in the target channel and can keep track of hashtags.

## Overview

This bot is built on top of the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library with features like asynchronicity introduced in v20+.

The main use-case is message forwarding. The bot has also several mechanics that allow you to add hashtags to label messages. The bot updates the last pinned message in the target channel to display the hashtag list and the count of each hashtag.

The bot uses TinyDB as a persistent storage for hashtags. It is not obligatory to use hashtags - you can utilize this bot just fo forwarding without any additional actions required.

## Installation and configuration

This bot was developed and tested on Ubuntu 22.04 with Python v3.10.6.

To run the bot, install two packages:

* `pip install python-telegram-bot`
* `pip install tinydb`

All secret data is stored in the configuration file with the following structure:

```
[secrets]
TELEGRAM_ACCESS_TOKEN = <token_value>
SECRET_CHANNEL_ID = <target_channel_id>
```

## Usage

To forward a message, reply to it with the `/repost` command. Each forwarded message is preceeded with another message that contains a link to the original message in the source chat.

This command also accepts a list of space-separated words as arguments. Note that each hashtag should be a single word without special symbols due to some bugs in the MarkdownV2 parsing engine. Prohibited symbols are the following: ```-_*[]()~`>#+=|{}.!```. The arguments are transformed to hashtags after forwarding. The bot adds the resulting hashtag list to the message with a link to the original message. You can do it as follows:

```
/repost tag1 tag2 anothertag
```

The bot will send the message with the content described below:

```
Go to message (link).
#tag1 #tag2 #anothertag
```

The bot automatically collects hashtags and updates their count in the last pinned message in the target chat/channel.
Note: Since this bot is an MVP, I haven't implemented capability to handle hashtags in the forwarded message itself. It is a useful feature but it didn't match the initial scenario.
