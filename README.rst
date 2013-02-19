Chucks
======

Chucks - a framework for developing technical courseware.

It evolved out of some tools I use to teach Django classes. It's also inspired
by the way `David Beazley`__ organizes and presents his training material.

__ http://dabeaz.com/

**This probably won't work for anyone but me**, but I'm sharing it in just in
case anyone else finds it fun.

It's organized around a few concepts:

A **module** is a bit of courseware, one "section". In my use, these are
typically 30-60 minute segments, but it really could be anything. Modules
consist of:

* A slide deck, written with Keynote.
* Code snippets for the deck that get included into the slides.
* Some exercises, as reST documents.
* Solutions to the exercise, as Python code.
* Tests for the code snippets, exercises, and solutions.

A **course** is a particular class, created by cobbling together a bunch of
modules in a particular order. The idea is that you've got a library of modules
that you build up over time, and when you give a course you piece it together
from the set of modules you've got available. A bit like Django's
app/project concepts (shocking, I know). A course is really just a config
document consisting of:

* An outline of modules that comprise the course.
* Authentication info (if hosting, see below).

Given a course, Chucks will build:

* A single slide deck, made by joining all the decks from each module.
* Handouts for students - a PDF document of all the slides.
* A bunch of HTML documents for the exercises and solutions.

Here's an example: an `Intro to Django from OSCON 2012`__.

__ http://training.revsys.com/oscon2012/

A **library** is the top-level container for a Chucks "setup" consisting of a
bunch of modules and a bunch of courses. It doeesn't actually have to exist,
but it's a nice convienience for holding everything together.

Libraries include a WSGI app, so you can just give students a URL (and maybe
user/pass) where they can find a course. This app's written to run easily
on Heroku, but with minimal effort you could probably host it anywhere.
Courses may also be deployed seperately.

