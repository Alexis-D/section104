#!/usr/bin/env python

from collections import defaultdict, namedtuple
from datetime import datetime
from decimal import Decimal
import itertools as it
import sys

from rich.console import Console
from rich.table import Table


Section104 = namedtuple('Section104', ['quantity', 'total_cost'])
# cost = per unit for BUY/SELL
# cost = total paid out for CAPRETURN/DIVIDEND
Event = namedtuple('Event', ['kind', 'date', 'quantity', 'cost', 'fees'])
TaxEvent = namedtuple('TaxEvent', ['date', 'symbol', 'value'])


events_by_symbol = defaultdict(list)
console = Console(highlight=False)

with open('trades.csv') as f:
    for line in f:
        event = line.strip()

        if not event or event.startswith('#'):
            continue

        event = event.split()
        event[1] = datetime.strptime(event[1], '%d/%m/%Y').date()
        event[3] = Decimal(event[3])
        event[4] = Decimal(event[4])

        if len(event) == 6:
            event[5] = Decimal(event[5])

        else:
            event.append(0)

        symbol = event[2]
        del event[2]
        event = Event(*event)

        if (event.kind == 'DIVIDEND' and
                symbol in ['GB00B5B74F71', 'GB00BD3RZ475']):
            console.print(
                    'Do not list dividend for income funds (%s)!' % symbol,
                    style='bold red')
            sys.exit(1)

        events_by_symbol[symbol].append(event)

tax_events = []
section104s = {}

for symbol, value in events_by_symbol.items():
    ordered = sorted(value, key=lambda event: event.date)

    for i, event in enumerate(ordered):
        if event.kind == 'SELL':
            for future_event in ordered[i+1:]:
                duration = future_event.date - event.date

                if duration.days <= 30 and future_event.kind == 'BUY':
                    console.print(
                            '[bold red]This _only_ supports section 104 holdings:\n%s\n%s\n%s[/]' %
                            (event, future_event, duration))
                    sys.exit(2)

    section104 = Section104(Decimal(0), Decimal(0))

    for event in ordered:
        if event.kind == 'BUY':
            section104 = Section104(
                section104.quantity + event.quantity,
                section104.total_cost + event.quantity * event.cost +
                event.fees
            )

        elif event.kind == 'SELL':
            tax_event = TaxEvent(
                    event.date,
                    symbol,
                    event.quantity * (
                        event.cost -
                        (section104.total_cost / section104.quantity)
                    ) - event.fees
            )
            tax_events.append(tax_event)

            console.print(
                    'Disposed of [cyan]%s[/] units of [bold]%s[/] held in section 104' % (
                    event.quantity,
                    symbol
                    ))
            console.print('  gain/loss: %s * (%.2f - %.2f) - %s = [bold cyan]%.2f[/]' % (
                event.quantity,
                event.cost,
                section104.total_cost / section104.quantity,
                event.fees,
                tax_event.value
                ))
            console.print()

            section104 = Section104(
                section104.quantity - event.quantity,
                section104.total_cost - event.quantity * (
                    section104.total_cost / section104.quantity)
            )

        elif event.kind == 'CAPRETURN':
            section104 = Section104(
                section104.quantity,
                section104.total_cost - event.cost
            )

        elif event.kind == 'DIVIDEND':
            section104 = Section104(
                section104.quantity,
                section104.total_cost + event.cost
            )

        else:
            console.print(
                    'Unknown event type %s' % event.kind,
                    style='bold red')
            sys.exit(3)

    section104s[symbol] = section104

table = Table(title='[bold]Current section 104 holdings[/]')

table.add_column('Symbol', style='bold')
table.add_column('Quantity', justify='right', style='cyan')
table.add_column('Total cost', justify='right', style='cyan')
table.add_column('Per unit cost', justify='right', style='bold cyan')

for symbol, section104 in sorted(
        section104s.items(),
        key=lambda x: x[1].total_cost,
        reverse=True):
    if section104.quantity:
        table.add_row(
                symbol,
                str(section104.quantity),
                '%.2f' % section104.total_cost,
                '%.2f' % (section104.total_cost / section104.quantity))

console.print(table)

def tax_year(tax_event):
    date = tax_event.date

    if date.month < 4:
        return '%d/%d' % (date.year - 1, date.year)
    elif date.month > 4:
        return '%d/%d' % (date.year, date.year + 1)
    else:
        if date.day <= 5:
            return '%d/%d' % (date.year - 1, date.year)
        else:
            return '%d/%d' % (date.year, date.year + 1)

console.print()
console.print('Tax year summaries:', style='bold')
console.print()

ordered_tax_events = sorted(tax_events, key=lambda tax_event: tax_event.date)
for tax_year, tax_events in it.groupby(ordered_tax_events, key=tax_year):
    tax_events = list(tax_events)
    title = '[bold]%s: [cyan]%.2f[/][/]' % (
        tax_year,
        sum(tax_event.value for tax_event in tax_events))

    table = Table(title=title)

    table.add_column('Date', style='bold')
    table.add_column('Symbol', style='bold')
    table.add_column('Gain/Loss', justify='right', style='bold cyan')

    for tax_event in tax_events:
        table.add_row(
                str(tax_event.date),
                tax_event.symbol,
                '%.2f' % tax_event.value)

    console.print(table)
    console.print()
