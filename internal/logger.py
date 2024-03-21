import datetime

from colorama import Fore


class Logger:
    @staticmethod
    def info(content: str) -> None:
        print(
            f'{Fore.LIGHTBLACK_EX}[{datetime.datetime.now().strftime("%I:%M:%S %p")}] {Fore.GREEN}{content}{Fore.RESET}'
        )

    @staticmethod
    def error(content: str) -> None:
        print(
            f'{Fore.LIGHTBLACK_EX}[{datetime.datetime.now().strftime("%I:%M:%S %p")}] {Fore.RED}{content}{Fore.RESET}'
        )

    @staticmethod
    def inp(content: str) -> str:
        return (
            f'{Fore.LIGHTBLACK_EX}[{datetime.datetime.now().strftime("%I:%M:%S %p")}] {Fore.CYAN}{content}{Fore.RESET}'
        )