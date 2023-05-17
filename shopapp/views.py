from timeit import default_timer

from django.contrib.auth.models import Group
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


def groups_list(request: HttpRequest):
    context = {
        'groups': Group.objects.prefetch_related('permissions').all(),
    }
    return render(request, 'shopapp/groups_list.html', context=context)
