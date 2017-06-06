import csv
import argparse
import time
import math

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='+', type=argparse.FileType('r'))
    args = parser.parse_args()

    transactions = []
    for f in args.infile:
        for line in csv.DictReader(f):
            #print line
            # The single line has a gross payment and a fee payment, so we need to split those apart
            tstamp = time.strptime('{\xef\xbb\xbf"Date"} {Time}'.format(**line), '%d/%m/%Y %H:%M:%S')

            # This is the "gross" payment
            transactions.append((
                tstamp,
                'Paypal - {Type} {Invoice Number} From {Name} {From Email Address}'.format(**line),
                line['Gross'].replace(',', '')
            ))

            if line['Fee'] != '0.00':
                transactions.append((
                    tstamp,
                    'Paypal - {Type} Fee {Invoice Number} From {Name} {From Email Address}'.format(**line),
                    line['Fee'].replace(',', '')
                ))

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
