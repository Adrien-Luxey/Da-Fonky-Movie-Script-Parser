# Da Fonky Movie Script Parser

## What is it for?

To parse movie scripts found online (in HTML) as JSON.

Indeed, movie scripts are always displayed in a certain format, but not in a way that would be intelligible for a computer program for later studies (stylometry, for instance).

The goal of this program is to create a JSON file from your movie script, differentiating the following types of text: character, speech, stage direction, and location.

Here are some movie scripts databases: http://www.imsdb.com , http://www.script-o-rama.com/table.shtml , ... go find your own... 

## Why did you do this?

My friend Pierre Peigné-Leroy needed to parse movie scripts to make some stylometry on it, as part of his Master Thesis in Philosophy. With a good dataset, a lot can be observed by looking only at the text of our cult movies!

## How does it work?

First of all, we try to find the movie script in the given page. In essence, we look for the first \<pre\> tag, since movie scripts are most often located inside this DOM element.

Once we went through the introduction, we count the number of leading spaces at each line, ask the user for this line's type, and assume that all others lines with this amount of leading spaces must be of the same type. It is a big assumption, but it seems to work nicely most of the time.

Active learning, baby!

Contributions welcome etc etc.

No licence at the moment, but I hereby declare that you can use, modify and sell my script if you feel like it.


Adrien

