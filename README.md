# Beta402 - DocHub


Beta402 or DocHub is a website, written in django. It's main goal is to provide a space for students (for now form the [ULB](http://ulb.ac.be) univeristy) to collaborate, help each other and distribute old exams and exercices.

There is a [live instance of DocHub](http://dochub.be) hosted by [UrLab](http://urlab.be) and the [Cercle Informatique](http://cerkinfo.be).

## Screenshots

![](https://github.com/urlab/beta402/blob/master/.meta/screen-1.png)
![](https://github.com/urlab/beta402/blob/master/.meta/screen-2.png)
![](https://github.com/urlab/beta402/blob/master/.meta/screen-3.png)

## Tech

### Dependencies

You'll need everything that is in requirements.txt (don't worry, pip will do it for you).

You will also need to install GraphicsMagick (the binary 'gm') and LibreOffice/OpenOffice + unoconv (you need the binary 'unoconv') using your distribution packages.

For exemple on Debian/Ubuntu

    sudo apt-get install graphicsmagick unoconv python-dev

Or on Fedora

    sudo dnf install GraphicsMagick unoconv python-devel

### Installation

    # Install dependencies then
    make install database

### Run

    honcho start

Then go http://localhost:8000/

There will already be 2 users in the database, both with `test` as a password:
   - $(USER) : your username on your machine
   - blabevue

### Reset

    make cleandata database


### Misc


Add another user to the db

    ./manage.py createuser

## Testing

Run only fast tests (total time < 2 sec) : not testing actual file conversions

    py.test -k "not slow"

Run all tests (~20 sec)

    py.test

## Contribute !


Come by #urlab on freenode or just fork this repo and send a patch !


## License


Copyright 2012 - 2015, Cercle Informatique ASBL. All rights reserved.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This software was made by hast, C4, iTitou at UrLab, ULB's hackerspace


[_Woop woop_](https://www.youtube.com/watch?v=z13qnzUQwuI)

