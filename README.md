python-klikbca-parser
=====================

Fork of [python-klikbca-parser](https://github.com/rickyok/python-klikbca-parser) migrated to Python 3.

Parser untuk ambil balance dan transaksi dari klikbca personal

Cara penggunaan
---------------

```python
import bcaparser

bca = bcaparser.BCA_parser(username , password)

if bca.login():
	balance = bca.get_balance()
	transactions = bca.get_transactions()
	bca.logout()
	update_balance(conn , username , balance , process_notes(transactions) , pb_account)
```

Ide dan source PHP diambil dari website (Thanks bro)

http://www.randomlog.org/article/bca-parser/
