from num2words import num2words

def amount_in_bahttext(amount):
    return num2words(amount, to="currency", lang="th")
