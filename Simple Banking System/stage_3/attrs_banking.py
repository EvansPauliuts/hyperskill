import random

from attrs import make_class, field, define, Factory
from sqlite3 import Connection, Cursor, connect

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


CardAccount = make_class(
    'CardAccount',
    {
        'id': field(type=int),
        'number': field(type=str),
        'pin': field(type=str),
        'balance': field(type=int),
    }
)


@define
class GenerateCard:
    number: str = field(init=False)
    pin: str = field(init=False)
    def __attrs_post_init__(self):
        while True:
            create_card_num = f'{INN}{random.randrange(1111111111, 9999999999, FIXED_DIGITS)}'

            if is_luhn_valid(int(create_card_num)):
                self.number = create_card_num
                self.pin = f'{random.randrange(1111, 9999, 4)}'
                break


@define(slots=True, frozen=True)
class BankAccount:
    __card: GenerateCard = field(default=Factory(dict))
    __balance: int = field(default=0)

    @property
    def balance(self) -> int:
        return self.__balance

    @property
    def get_account(self) -> GenerateCard:
        return self.__card


@define
class Database:
    conn: Connection = connect('card.s3db')
    cur: Cursor = field(factory=conn.cursor)

    def __attrs_post_init__(self):
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS card "
            "(id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)"
        )

    def create(self, card: BankAccount) -> None:
        self.cur.execute("INSERT INTO card VALUES (NULL, ?, ?, ?)", (
            card.get_account.number, card.get_account.pin, card.balance
        ))
        self.conn.commit()

    def read(self, number: str, pin: str) -> CardAccount | None:
        self.cur.execute(f"SELECT * FROM card WHERE number = {number} AND pin = {pin}")
        rows = self.cur.fetchone()
        return CardAccount(*rows) if rows else None


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
                while True:
                    print('1. Balance')
                    print('2. Log out')
                    print('0. Exit')

                    check_d = int(input())

                    if check_d == 1:
                        print(f'\nBalance: {bank_account_db.balance}\n')
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
