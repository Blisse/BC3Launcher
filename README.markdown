<h1> README </h1>

<h2> BC3Launcher </h2>

Attempted to reproduce some of the features of Beyond Compare 3 [BC3]. However, I realized that
BC3 had much superior file comparison features, including speed and display, than I could make in 
my spare time.

Perhaps in the future, I will attempt to re-attempt the comparisons.

<h3> Includes </h3>

<ul>
<li> proto.pyw
<li> ptt.exe
<li> History
</ul>

<h3> Requirements </h3>

<ul>
<li> Python 2.7
<li> wxPython 64bit for Python 2.7
<li> Beyond Compare 3
</ul>

<h3> proto.pyw </h3>

This is the main application, built using wxPython. It has a window divided between the left and right panels with each having two further screens.

The top screens allow you to select the files you want to compare. There is a File button that opens up a dialog
for you to pick a file. The filepath in the text field for each panel is the path in question. <b> Both sides
must have a file before it can execute properly. Please only use .pdf or .txt files. I have not tested the application
using other file types. </b>

You can select a field using the file button, or double clicking on a file in the grid. Moving directories via the grid is not implemented.

<h3> Features </h3>

<h4> Launch files in Beyond Compare 3 </h4>

Simple enough. Launch the two selected files in Beyond Compare 3.

<h4> Load Files </h4>

Puts the two selected files' contents into the bottom screens.

<h4> In-line BC3 </h4>

Takes each bottom screens and loads them into Beyond Compare 3.

<h4> Remove Newlines </h4>

Removes all the newlines from the bottom screens.

<h4> Remove Dates </h4>

Removes all the dates from the bottom screens. <b> BETA. I cannot guarantee this will not remove SOME really coincidental lines. </b>

<h4> Clear </h4>

Clears the bottom screen.

<h4> One Duplicate </h4>

Removes one match from the bottom screens.

<h4> All Duplicates </h4>

Removes all matches from the bottom screens.



<h4> Set BC3 Path </h4>

If you've installed Beyond Compare 3 in a non-default directory, use this to select the new location of the BComp.exe file.

<h4> Set PTT Path </h4>

If you've moved the ptt.exe file, use this to select the new location of the ptt.exe file.


<h3> ptt.exe </h3>

This is a pdf-to-text tool taken from Beyond Compare 3. It's necessary so that the application can Load PDF Files.



<h2> About </h2>

If you have any concerns or improvements to suggest, please e-mail <a href="mailto:lai.victor.vl@gmail.com">lai.victor.vl@gmail.com</a> and I'll get back to you. Thanks.
