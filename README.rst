Chucks
======

Chucks - a framework for developing technical courseware.

It evolved out of some tools I used to teach Django classes. It's also heavily
inspired by the way `David Beazley`__ organizes and presents his Python
training material.

__ http://dabeaz.com/

It's organized around a couple of concepts:

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

Finally, Chucks includes a WSGI app, so you can just give students a URL (and
maybe user/pass) where they can find all the above. This app's written to run
easily on Heroku, but with minimal effort you could probably host it anywhere.

Installation
------------

``pip install chucks``, natch.

Creating modules
----------------

First, create a module with ``chucks module <name>``. This creates a
skeleton module in a new directory named ``<name>``. Inside this directory, XXX.

Testing modules
---------------

``chucks test <module>``.

Creating courses
----------------

``chucks course <coursename>`` -- interactive, creates ``<coursename>.yaml``.

Building courses
----------------

``chucks build course.yaml``

Deploying
---------

``chucks deploy`` - deploy everything onto Heroku, asking for creds if needed.

``chucks deploy course.yaml`` - just deploy the given course.
