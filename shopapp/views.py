from timeit import default_timer

from django.http import HttpRequest
from django.shortcuts import render


def schop_index(reguest: HttpRequest):
    prodocts = [
        ('Laptop', 1999),
        ('Desktop', 3555),
        ('Smartphone', 876),
    ]
    context = {
        'time_running': default_timer(),
        'prodocts': prodocts,
    }
    return render(reguest, 'shopapp/shop_index.html', context=context)
