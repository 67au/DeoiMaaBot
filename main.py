#!/usr/bin/env python3

import argparse
import asyncio
import logging
import sys
from collections import defaultdict
from configparser import ConfigParser
from pathlib import Path
from typing import Union

from pyrogram import Client, filters, idle
from pyrogram.types import Message

sys.path.append('intel-map-client')

from IntelMapClient import AsyncClient, AsyncAPI
from IntelMapClient.errors import CookieError

PathType = Union[str, Path]

logger = logging.getLogger('DeoiMaaBot')
enter = '\n'


class ConfigProxy:

    def __init__(self, config_file: PathType):
        self._config = self._load_config(config_file)
        self.api_id = self._config.get('pyrogram', 'api_id')
        self.api_hash = self._config.get('pyrogram', 'api_hash')
        self.bot_token = self._config.get('pyrogram', 'bot_token', raw=True, fallback=None)
        self.admin = [int(i) for i in self._config.get('opts', 'admin').split(',')]

    def _load_config(self, config_file: PathType) -> ConfigParser:
        config = ConfigParser()
        config.read(config_file, encoding='utf8')
        return config


async def main():
    parser = argparse.ArgumentParser(description='DeoiMaaBot')
    parser.add_argument('--config', dest='config', metavar='FILEPATH', default='config.ini',
                        action='store', help='Configure file, default = \'config.ini\'', required=False)

    args = parser.parse_args()
    config_file = Path(args.config)
    if not config_file.exists():
        logger.error(f"Configure file ({str(config_file)}) not found")
        raise FileNotFoundError
    config = ConfigProxy(config_file)
    bot = Client(
        ':memory:',
        api_id=config.api_id,
        api_hash=config.api_hash,
        bot_token=config.bot_token,
    )
    admin = config.admin
    api = defaultdict(lambda: AsyncAPI(AsyncClient()))

    @bot.on_message(filters=filters.chat(admin) & filters.command('start'))
    async def start(client: Client, message: Message) -> None:
        if len(message.command) > 1:
            cookies = ' '.join(message.command[1:])
            try:
                await api[message.chat.id].client.connect(cookies)
                logger.debug(f'{message.chat.id} 登录成功')
                await message.reply('登录成功')
            except CookieError:
                logger.debug(f'{message.chat.id} 登录失败')
                await message.reply('登录失败')
        else:
            await message.reply(
                '**使用方式**\n'
                '/start `cookies` - 登录 IntelMap\n'
                '/clear - 退出 IntelMap 并清理 cookies\n'
                '/ping - 检测登录\n'
                '/redeem - 兑换 passcode\n'
                '/redeem_full - 兑换 passcode 并忽略无效部分\n'
            )

    @bot.on_message(filters=filters.chat(admin) & filters.command('clear'))
    async def clear(client: Client, message: Message) -> None:
        await api[message.chat.id].client.close()
        await message.reply('cookies 已经清理')

    @bot.on_message(filters=filters.chat(admin) & filters.command('ping'))
    async def ping(client: Client, message: Message) -> None:
        try:
            await api[message.chat.id].client.getGameScore()
            await message.reply('cookies 有效')
        except CookieError:
            await message.reply('cookies 无效')

    async def redeem_code(message: Message, passcode: str, no_fail: bool = False) -> tuple[list[str], list[str]]:
        redeemed = []
        failed = []
        for code in passcode:
            try:
                ok, result = await api[message.chat.id].redeemReward(code)
            except CookieError:
                await message.reply('Cookies 过期，中断兑换')
                return redeemed, failed
            if ok:
                reward, player = result
                redeemed.append(code)
                logger.debug(f'{code} 兑换成功')
                await message.reply(f'`{code}`\n\n`{str(reward)}`')
            else:
                failed.append(code)
                await message.reply(f'`{code}`\n\n`{result}`')
                if not no_fail:
                    break
            await asyncio.sleep(1)
        return redeemed, failed

    @bot.on_message(filters=filters.chat(admin) & filters.command('redeem'))
    async def redeem(client: Client, message: Message) -> None:
        if len(message.command) > 1:
            if not api[message.chat.id].client.is_login():
                await message.reply('**请按照 `/start` 的要求登陆**')
                return
            passcode = message.command[1:]
            redeemed, failed = await redeem_code(message, passcode)
            redeemed_txt = enter.join(redeemed) if any(redeemed) else None
            failed_txt = f'***发生错误***\n`{enter.join(failed)}`' if any(failed) else ''
            await message.reply(f'***成功兑换***\n`{redeemed_txt}`\n\n{failed_txt}')
        else:
            await message.reply('命令格式为 `/redeem code1 code2 ...`')

    @bot.on_message(filters=filters.chat(admin) & filters.command('redeem_full'))
    async def redeem(client: Client, message: Message) -> None:
        if len(message.command) > 1:
            if not api[message.chat.id].client.is_login():
                await message.reply('**请按照 `/start` 的要求登陆**')
                return
            passcode = message.command[1:]
            redeemed, failed = await redeem_code(message, passcode, no_fail=True)
            redeemed_txt = enter.join(redeemed) if any(redeemed) else None
            failed_txt = f'***发生错误***\n`{enter.join(failed)}`' if any(failed) else ''
            await message.reply(f'***成功兑换***\n`{redeemed_txt}`\n\n{failed_txt}')
        else:
            await message.reply('命令格式为 `/redeem_full code1 code2 ...`')

    async with bot:
        await idle()
        for a in api.values():
            await a.client.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    asyncio.run(main())
