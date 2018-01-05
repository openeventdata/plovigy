# plodigy-mark
A lightweight program that duplicates the basic functionality of the "mark" function in the [prodigy](http://prodi.gy/) system using the same input and output formats; output is saved to a file which is coder- and time-stamped rather than to a database.

## To run program:

```
python3 plodigy-mark.py <filename> <coder>
```

where  `<filename>` is the file to annotate; `<coder>` is typically the coder initials ("PLD" is the default). The file *plodigy_testfile_0105.jsonl* is sample input.

## Key commands

| key | key  | effect |
:---: | :---: | ---
0 | space | ignore
1 | a | accept
2 |x | reject
3 |z | toggles the display of the "meta" information
4 |d | toggle <return> between accept/reject (default is "accept")
` ` |return | accept or reject depending on setting 
` ` |q | quit 

At present, key commands except for the default `return` must be followed by `return`.

## Some usage notes

1. Toggling the `return` option substantially increases the speed at which one can annotate in situations where one hits a sequence of cases which are either usually right or usually wrong.

2. Input is not case-sensitive 

3. The file FILEREC_NAME -- currently set to "plodigy.filerecs.txt" -- keeps track of the location in the file, so if you quit and restart, you will be returned to the last uncoded record in the file.

4. The file *plover_reference.html* is a reference to the PLOVER ontology and has some suggestions for doing annotation; it can be opened in a browser.

## What's the point?

This program was developed to do simple annotation on the records coded into the [PLOVER](https://github.com/openeventdata/PLOVER) system (hence the name) by several different automated event data coding programs, simply presenting the text and the assigned category without any additional markup. While `prodigy` is way cool, it involves considerable overhead, and we are looking for something that could run, say, on a cheap little Ubuntu burner laptop on, say, a trans-Atlantic flight. As it happens, the simplicity of the interface also means that one can classify cases very quickly.

## Programming Notes

1. There are obviously work-arounds -- see StackOverflow -- that would allow the program to respond immediately to any key, without the `return`, though so far I haven't found this sufficiently irritating to bother including that feature.

2. Unlike `prodigy`, the program currently does not have the ability to go backwards: saving the results to a buffer rather than immediately writing them to a file would also be a very straightforward feature to add. 

3. I'm guessing in the appropriate Python framework, it would be easy to get this running on phone: again, it's really lightweight. This is left as an exercise.


## Acknowledgments
This program was developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

This program has been successfully run under Mac OS 10.13.2; it is standard Python 3.5
so it should also run in Unix or Windows. 

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

