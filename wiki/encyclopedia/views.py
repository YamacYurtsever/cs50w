from django.shortcuts import render, redirect
from django.urls import reverse
from . import util
import random
import markdown2


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    if title in util.list_entries():
        content = markdown2.markdown(util.get_entry(title))
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": content
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error": "This entry doesn't exist."
        })


def search_results(request):
    if request.method == "POST":
        query = request.POST.get('q')

        if query in util.list_entries():
            return redirect(reverse('entry', args=[query]))

        resultEntries = []
        for entry in util.list_entries():
            if query in entry:
                resultEntries.append(entry)
        return render(request, "encyclopedia/search_results.html", {
            "entries": resultEntries
        })


def add(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title in util.list_entries():
            return render(request, "encyclopedia/error.html", {
                "error": "Encyclopedia entry already exists."
            })
        else:
            util.save_entry(title, content)
            return redirect(reverse("entry", args=[title]))
    else:
        return render(request, "encyclopedia/add.html")


def edit(request, title):
    if request.method == "POST":
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect(reverse("entry", args=[title]))
    else:
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })


def random_entry(request):
    entries = util.list_entries()
    entry = random.choice(entries)
    return redirect(reverse("entry", args=[entry]))
