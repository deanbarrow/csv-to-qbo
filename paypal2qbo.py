import csv
import argparse
import time
import math
from decimal import Decimal

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='+', type=argparse.FileType('r'))
    args = parser.parse_args()
    total = 0
    transactions = []
    for f in args.infile:
        for line in csv.DictReader(f):
            tstamp = time.strptime('{\xef\xbb\xbf"Date"} {Time}'.format(**line), '%d/%m/%Y %H:%M:%S')
            line['Gross'] = line['Gross'].replace(',','')

            # Ignore all other currencies as Paypal will convert to a single transaction inclusive of transaction and exchange fees
            if line['Currency'] == 'GBP':

                if line['Type'] == 'Account Hold for Open Authorisation':
                    #transactions.append((tstamp, 'Sent: Account Hold for Open Authorisation', line['Gross']))
                    continue

                elif line['Type'] == 'Reversal of General Account Hold':
                    #transactions.append((tstamp, 'Refund: Reversal of General Account Hold', line['Gross']))
                    continue

                elif line['Type'] == 'Payment Reversal':
                    transactions.append((tstamp, 'Reversal: Reversal of dispute', line['Gross']))

                elif line['Type'] == 'Cancellation of Hold for Dispute Resolution':
                    transactions.append((tstamp, 'Reversal: Reversal of dispute', line['Gross']))

                elif line['Type'] == 'Hold on Balance for Dispute Investigation':
                    transactions.append((tstamp, 'Sent: Dispute reclaim for {Invoice Number}', line['Gross']))

                elif line['Type'] == 'General Withdrawal':
                    transactions.append((tstamp, 'Transfer: Paypal to bank account', line['Gross']))

                elif line['Type'] in ['General Credit Card Deposit', 'Bank Deposit to PP Account (Obsolete)', 'General Credit Card Withdrawal']:
                    transactions.append((tstamp, 'Transfer: Bank account to Paypal', line['Gross']))

                elif line['Type'] == 'Payment Refund':
                    transactions.append((tstamp, 'Refund: Payment for {Invoice Number} From {Name} {From Email Address}'.format(**line), line['Gross']))
                    if line['Fee'] != '0.00':
                        transactions.append((tstamp, 'Refund: Fee {Invoice Number} From {Name} {From Email Address}'.format(**line), line['Fee']))

                elif line['Type'] in ['Website Payment', 'General Currency Conversion', 'Pre-approved Payment Bill User Payment', 'eBay Auction Payment', 'Express Checkout Payment', 'General Payment']:
                    if float(line['Gross']) > 0:
                        transactions.append((tstamp, 'Received: {Invoice Number} From {Name} {From Email Address}'.format(**line), line['Gross']))
                    else:
                        transactions.append((tstamp, 'Sent: {Invoice Number} From {Name} {From Email Address}'.format(**line), line['Gross']))

                    if line['Fee'] != '0.00':
                        transactions.append((tstamp, 'Sent: Fee {Invoice Number} From {Name} {From Email Address}'.format(**line), line['Fee']))

                else:
                    transactions.append((tstamp, 'REVIEW: {Invoice Number} From {Name} {From Email Address}'.format(**line), line['Gross']))
                    if line['Fee'] != '0.00':
                        transactions.append((tstamp, 'REVIEW: Fee {Invoice Number} From {Name} {From Email Address}'.format(**line), line['Fee']))
                    print 'Review transaction ID {Transaction ID} {Type}'.format(**line)

                #Basic error checking, ensure Paypal balance matches transaction balance
                total = Decimal(total) + Decimal(line['Gross']) + Decimal(line['Fee'])
                if Decimal(total) != Decimal(line['Balance'].replace(',','')):
                    print "Error: balances are not equal, please check"
                    print total, line['Gross'], line['Fee'], line['Balance'], line['Transaction ID']
                    exit()

    for filenum in range(0, int(math.ceil(len(transactions) / 1000.0))):
        with open('PaypalQuickBooksOutput%d.csv' % (filenum + 1), 'w') as f:
            i = 0
            writer = csv.DictWriter(f, fieldnames=['Date', 'Description', 'Amount'])
            writer.writeheader()

            for txn in sorted(transactions, key=lambda l: time.mktime(l[0])):
                if i == 999:
                    continue
                writeline = {
                    'Date': time.strftime('%d/%m/%Y', txn[0]),
                    'Description': txn[1],
                    'Amount': txn[2]
                }
                writer.writerow(writeline)
                transactions.remove(txn)
                i += 1

            if i == 999:
                continue

if __name__ == '__main__':
    main()
