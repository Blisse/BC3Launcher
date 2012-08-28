<h1> README </h1>

<h2> BC3Launcher </h2>

Attempted to reproduce some of the features of Beyond Compare 3 [BC3]. However, I realized that
BC3 had much superior file comparison features, including speed and display, than I could make in 
my spare time.

Perhaps in the future, I will attempt to re-attempt the comparisons.

<h3> History </h3>

The History folder contains all my scripting attempts to copy BC3's features. They can be 
run in single or batch format. I thought this was enough, but it's a tad too difficult to run.

So I decided to use wxPython, an extension of wxWindows, to create a proper user interface.

<h3> proto </h3>

proto.pyw is my launcher program for BC3. It requires Python 2.7 to run properly, as long as wxPython.
It is my finished product, which is nice to look at, but I could make some improvements, especially on 
my remove duplicates algorithm. 

The main reason I made this program was the extra two text boxes at the bottom, which can find any duplicate
lines in the two text boxes and remove them. It is a specific requirement for some of the reports that
this program was used to run.