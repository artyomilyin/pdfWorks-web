from django.shortcuts import render


def homepage(request):
    return render(request,
                  'website/homepage.html',
                  {'section': 'merge'})


def merge(request):
    return render(request,
                  'website/merge.html',
                  {'section': 'merge'})


def split(request):
    if request.method == "POST":
        print("it's POST!")
        print(request)
    return render(request,
                  'website/split.html',
                  {'section': 'split'})


def offline(request):
    return render(request,
                  'website/offline.html',
                  {'section': 'offline'})
