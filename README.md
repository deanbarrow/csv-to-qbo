csv-to-qbo
==========

Converts CSV exports from Paypal to a CSV format that QuickBooks Online understands.

Paypal Download
---------------

1. In your Paypal account, browse to the Reports → Activity Download page.
2. Select the "Comma Delimeted - Balance Affecting Payments" format and either download a time range or use the Last Download to Present option. Either way, you'll end up with a CSV file (probably called `Download.csv`).

Convert
-------

1. Run `python paypal2qbo.py Download.csv` (note that if you have multiple CSV files from Paypal you can add specify them all). The script will output a file named `PaypalQuickBooksOutput[num].csv`. If the number of transactions are greater than 999 it will create multiple output files as QBO only allows CSV imports of up to 1000 lines (headers + 999 transactions).

QuickBooks Online Upload
------------------------

1. In your Quickbooks Online account, go to the account you want to import transactions into.
2. Click the arrow next to the "Update" button in the upper right and select "File Upload".
3. Click the Browse button and find the `QuickBooksOutput.csv` file generated above.

Other
=====

Forked from https://github.com/iandees/csv-to-qbo
Tested and working with UK Paypal/Quickbooks accounts.