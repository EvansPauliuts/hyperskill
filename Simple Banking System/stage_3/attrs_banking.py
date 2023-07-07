import random

from attrs import field, define, Factory
from sqlite3 import Connection, Cursor, connect
from typing import TypeVar

TGenerateCard = TypeVar('TGenerateCard', bound='GenerateCard')
TBankAccount = TypeVar('TBankAccount', bound='BankAccount')
TDatabase = TypeVar('TDatabase', bound='Database')

FIXED_DIGITS = 10
INN = 400_000


def luhn_checksum(card_number: int) -> int:
    digits = [int(d) for d in str(card_number)]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)

    for digit in even_digits:
        checksum += sum(int(d) for d in str(2 * digit))

    return checksum % 10


def is_luhn_valid(card_number: int) -> bool:
    return luhn_checksum(card_number) == 0


@define
class GenerateCard:
    number: str = field(init=False)
    pin: str = field(init=False)
    def __attrs_post_init__(self: TGenerateCard) -> TGenerateCard:
        while True:
            create_card_num = f'{INN}{random.randrange(1111111111, 9999999999, FIXED_DIGITS)}'

            if is_luhn_valid(int(create_card_num)):
                self.number = create_card_num
                self.pin = f'{random.randrange(1111, 9999, 4)}'
                break

        return self


@define(slots=True, frozen=True)
class BankAccount:
    __card: GenerateCard = field(default=Factory(GenerateCard))
    __balance: int = field(default=0)

    @property
    def balance(self: TBankAccount) -> int:
        return self.__balance

    @property
    def get_account(self: TBankAccount) -> GenerateCard:
        return self.__card


@define
class Database:
    conn: Connection = connect('card.s3db')
    cur: Cursor = field(factory=conn.cursor)

    def __attrs_post_init__(self: TDatabase) -> TDatabase:
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS card "
            "(id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)"
        )
        return self

    def create(self: TDatabase, card_item: BankAccount) -> TDatabase:
        self.cur.execute("INSERT INTO card VALUES (NULL, ?, ?, ?)", (
            card_item.get_account.number, card_item.get_account.pin, card_item.balance,
        ))
        self.conn.commit()
        return self

    def read(self: TDatabase, number: str, pin: str) -> tuple | None:
        self.cur.execute("SELECT * FROM card WHERE number = (?) AND pin = (?)", (
            number, pin,
        ))
        rows = self.cur.fetchone()
        return rows or None


if __name__ == '__main__':
    card = None
    bank_account = None
    db = Database()
    is_flag = True

    while is_flag:
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')

        check_number = int(input())

        if check_number == 1:
            print('\nYour card has been created')
            card = GenerateCard()
            bank_account = BankAccount(card)
            print(bank_account)
            db.create(bank_account)

            print(f'Your card number:\n{card.number}')
            print(f'Your card PIN:\n{card.pin}\n')

            continue

        elif check_number == 2:
            card_n = input('\nEnter your card number:\n')
            card_p = input('Enter your PIN:\n')

            bank_account_db = db.read(card_n, card_p)

            print(
                '\nYou have successfully logged in!\n' if bank_account_db else
                '\nWrong card number or PIN!\n'
            )

            if bank_account_db:
                _, _, _, card_balance = bank_account_db

                while True:
                    print('1. Balance')
                    print('2. Log out')
                    print('0. Exit')

                    check_d = int(input())

                    if check_d == 1:
                        print(f'\nBalance: {card_balance}\n')
                        continue
                    elif check_d == 2:
                        print('You have successfully logged out!\n')
                        break
                    elif check_d == 0:
                        is_flag = False
                        break

            else:
                continue

        elif check_number == 0:
            is_flag = False

    db.cur.close()
    print('\nBye!')
