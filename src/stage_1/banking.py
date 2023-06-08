import random
from dataclasses import dataclass

FIXED_DIGITS = 10
INN = 400_000


@dataclass(frozen=True)
class CheckCardAccount:
    number: str
    pin: str


@dataclass
class Account:
    def __post_init__(self):
        self.number = f'{INN}{random.randrange(1111111111, 9999999999, FIXED_DIGITS)}'
        self.pin = f'{random.randrange(1111, 9999, 4)}'


class BankAccount:
    def __init__(self, account: Account) -> None:
        self.__account = account
        self.__balance = 0

    @property
    def balance(self):
        return self.__balance

    def __eq__(self, other: Account) -> bool:
        return (self.__account.number, self.__account.pin) == (
            other.number, other.pin
        )


if __name__ == '__main__':
    account_card = None
    bank_account = None
    is_flag = True

    while is_flag:
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')

        check_number = int(input())

        if check_number == 1:
            print('\nYour card has been created')
            account_card = Account()
            bank_account = BankAccount(account_card)

            print(f'Your card number:\n{account_card.number}')
            print(f'Your card PIN:\n{account_card.pin}\n')
            continue

        elif check_number == 2:
            card_n = input('\nEnter your card number:\n')
            card_p = input('Enter your PIN:\n')

            bank_account_valid = bank_account != CheckCardAccount(card_n, card_p)

            print(
                '\nWrong card number or PIN!\n' if bank_account_valid else
                '\nYou have successfully logged in!\n'
            )

            if not bank_account_valid:
                while True:
                    print('1. Balance')
                    print('2. Log out')
                    print('0. Exit')

                    check_d = int(input())

                    if check_d == 1:
                        print(f'\nBalance: {bank_account.balance}\n')
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

    print('\nBye!')
