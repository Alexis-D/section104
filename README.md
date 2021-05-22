# `section104.py`

[CGTCalculator.com](http://www.cgtcalculator.com/) is great but doesn't support for equalization/accumulation funds.
[cgtcalc](https://github.com/mattjgalloway/cgtcalc) is great but doesn't support [partial disposals](https://github.com/mattjgalloway/cgtcalc/blob/6acd7b5a9bb51242ef8840adfc69adecbb0c528d/Sources/CGTCalcCore/Calculator/Calculator.swift#L175).

Thankfully all my (fund) holdings are currently held in section 104, hence this script to compute my capital gains.

Should you use this, please do so at your own risk, this has not been tested aside from my own portfolio, and I'm not an
accountant. Hopefully HMRC will own day come up with a tool that makes it easy for everyone to accurately and simply
compute their capital gains.

This reads trades from a `trades.csv` file that roughly follow the `cgtcalc` format.

This is lacking a ton of features that might matter to you:

* Not carrying loss over
* No support for same day trades
* No bed and breakfast support (<=30 days sell/buy)
* No stock split/unsplit
* No tests!
* Doesn't account for HMRC rounding rules (assuming there are some)

Known to ~work~ run with Python 3.9 (+`pip install -r requirements.txt`).

## Sample output

`trades.csv`:

```
BUY 05/12/2020 GB00B41YBW71 500 4.7012 2
SELL 28/11/2019 GB00B41YBW71 2000 4.6702 12.5
BUY 28/08/2018 GB00B41YBW71 1000 4.1565 12.5
BUY 01/03/2018 GB00B41YBW71 1000 3.6093 2
```

```
2019-11-08: Disposed of 2000 units of GB00B41YBW71 held in section 104
  gain/loss: 2000 * (4.67 - 3.89) - 12.5 = 1547.60

              Current section 104 holdings
┏━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Symbol       ┃ Quantity ┃ Total cost ┃ Per unit cost ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ GB00B41YBW71 │      500 │    2352.60 │          4.71 │
└──────────────┴──────────┴────────────┴───────────────┘

Tax year summaries:

           2019/2020: 1547.60
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Date       ┃ Symbol       ┃ Gain/Loss ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 2019-11-28 │ GB00B41YBW71 │   1547.60 │
└────────────┴──────────────┴───────────┘
```
