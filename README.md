These are a series of programs inspired by the basic functionality of the [prodigy](http://prodi.gy/) system modified to use keyboard entry and the terminal-based `curses` library. They have been used in various phases of the Political Instability Task Force New Generation Event Coder project (2021-2022) and the formats have gradually morphed away from `prodigy` but should be fairly easy to figure out/modify.

## plovigy-mark
A lightweight program that duplicates the basic functionality of the "mark" function in the [prodigy](http://prodi.gy/) system using the same input and output formats; output is saved to a file which is coder- and time-stamped rather than to a database.

### Note March-2020: 

Somehow I'd missed the existance of the Python `curses` library when writing this, and that would
be a much better way to implement it, as well as removing the need for the constant use of `return`

## To run program:

```
python3 plovigy-mark.py <filename> <coder>
```

where  `<filename>` is the file to annotate; `<coder>` is typically the coder initials ("PLV" is the default). The file *plovigy_testfile_0105.jsonl* is sample input.

### Example

```
python3 plovigy-mark.py verify_test0105_02.jsonl PAS
```

Output file will have a name of the format `plovigy-eval.PAS-180105-171558.txt`

## Key commands

| key | effect |
:---: | ---
a | accept
1 | accept
x | reject
2 | reject
space | ignore (useful if entering ' ', a, x from lower left of keyboard)
\` | ignore (useful if entering \`, 1, 2 from top row of keyboard)
0 |  ignore (useful if entering 0, 1, 2 from numerical keypad)
return | accept, reject, or ignore depending on setting 
c | add "comment" to "meta" in output record: program prompts for text
d | toggle <return> between accept/reject/ignore (initial value is "accept")
m | toggle  display of the "meta" information
\- | go back one record in buffer
\+ | go forward one record in buffer without recoding
q | quit 

At present, key commands except for the default `return` must be followed by `return`.

## Some usage notes

1. Toggling the `return` option substantially increases the speed at which one can annotate in situations where one hits a sequence of cases which are either usually right, usually wrong or usually irrelevant.

2. Input is not case-sensitive. 

3. Cases are saved in a temporary buffer before being written: this currently holds 8 entries (probably beyond the capacity of your working memory) but can be changed using the global BUFFER_SIZE. This can be navigated using the +/- keys; to change the annonated "answer" value use the accept/reject/ignore options.

4. In the normal forward flow, a comment ('C' key) needs to be added *before* adding the annotation since after an annotation is added, the program moves to the next record. Comments can be added by going backwards in the buffer.

5. The file FILEREC_NAME -- currently set to "plovigy.filerecs.txt" -- keeps track of the location in the file, so if you quit and restart, you will be returned to the last uncoded record in the file.

6. The file *plover_reference.html* is a reference to the PLOVER ontology and has some suggestions for doing annotation; it can be opened in a browser or from [this link](http://eventdata.parusanalytics.com/data.dir/plover_reference.html).

5. *plovigy_testfile_0105.jsonl* is set up for annotating the primary PLOVER event but, with different data preparation, this could be -- and in the future will be -- changed so that the program can be used for the annotation of the source or target actors, or the PLOVER mode or context of the event. We have a set of programs which extract the most frequently-used patterns for the [PETRARCH-1](https://github.com/openeventdata/petrarch2) and [PETRARCH-2](https://github.com/openeventdata/petrarch) programs (see [this presentation](http://eventdata.parusanalytics.com/presentations.dir/Schrodt.RIDIR.PETRARCH.slides.pdf)) and then convert these to the `prodigy/plovigy` format, but at the moment these are fairly ad hoc: still, if you might find them useful, contact schrodt735@gmail.com. 

## What's the point?

This program was developed to do simple annotation -- that is, simply determining whether a coding was correct, incorrect, or the text should not have been coded -- on the records coded into the [PLOVER](https://github.com/openeventdata/PLOVER) system (hence the name) by several different automated event data coding programs, simply presenting the text and the assigned category without any additional markup. While `prodigy` is way cool, it involves considerable overhead, and we are looking for something that could run, say, on a cheap little Ubuntu burner laptop on, say, a trans-Atlantic flight. As it happens, the simplicity of the interface also means that one can classify cases very quickly.

## Programming Notes

1. There are obviously work-arounds -- see StackOverflow -- that would allow the program to respond immediately to any key, without the `return`, though so far I haven't found this sufficiently irritating to bother including that feature: in fact having to use two keys before doing anything except annotating with the default seems useful.

2. I'm guessing in the appropriate Python framework, it would be easy to get this running on a smart phone: again, it's really lightweight. This is left as an exercise.


## Acknowledgments
This program was developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

This program has been successfully run under Mac OS 10.13.2 and Ubuntu 16.04; it is standard Python 3.5
and so also should run in Windows. Not that I can see any reason you'd want to run Windows.

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

# plovigy-PITF

## plovigy-PITF-DEDI.py

A subset of `plovigy-mark.py` which uses the PITF-DEDI jsonl format—see the file `plovigy-DEDI-input-sample.jsonl` for a sample of the input—and mostly does simple accept/reject classification without
any other options, though it does allow dates to be moved forward and back. This also does quite a bit of autocoding: see the sample files `autocodes-DEDI.txt` and `autocodes-202212-DEDI.txt`. Requires `utilDEDI.py` 

DEDI is an internal PITF data set on protests which is derived from the government version of the ICEWS event data. `plovigy-PITF-DEDI.py` is just one piece of an extended pipeline used in this production but has been *extensively* used for several years and I've got more documentation for the program if that would be helpful.

## plovigy-PITF-annotate.py

Radical simplification of `plovigy-PITF-DEDI.py` to work with the PITF PLOVER/NGEC human annotations. The more complex `actor-annot-lite` replaces this for annotation purposes, but this forms the basis for the later `plovigy-NGEC` programs.
  
## actor-annot-lite.py/documentation
  
A Python program for annotating event files with sentence segmentation, actor, recipient, and location spans. It is designed to use minimal machine resources—in the Macintosh OS-X system—it takes about 6Mb of memory versus the 350Mb required for a single Google Chrome web page—and does not require connection to a server. The program is implemented using the C/Python `ncurses` terminal emulation and uses a small set of keyboard commands rather than a mouse, and is designed to run on a laptop. Like on an airplane.

# November 2022

## plovigy-NGEC-context.py
plovigy for selecting cases either from the Release data (.json suffix) or from the cases selected by assess_context.py(.txt suffix). Writes to the training-case format: see internal commenting for additional details

## plovigy-NGEC-review.py/.documentation.pdf
plovigy for additional annotating of event training cases and documentation for same. 

