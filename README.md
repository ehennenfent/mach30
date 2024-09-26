# mach30
GCode library for using Python as CAM

### TODO:
- [ ] Tool offset changes should include a Z move
- [ ] And maybe we don't need so many G49's?
- [ ] Figure out what's going on with mode changes
- [ ] Abstracting away tool changes might make this simpler
- [ ] Figure out a convenient way to work in G53
- [ ] warn for failure to change feedrate when changing tools


* 1 override per group
* canned cycles & overrides are context managers 
* restore the motion group after canned cycle
* set mode initially, override after

00 - motion
01 - motion
02 - motion
03 - motion
04 - nonmodal
17 - plane
20 - units
21 - units
28 - nonmodal
40 - cutter compensation
41 - cutter compensation
42 - cutter compensation
43 - tool offset
49 - tool offset
53 - nonmodal
54 - coordinate system
80 - canned cycle
81 - canned cycle
82 - canned cycle
83 - canned cycle
84 - canned cycle
90 - distance mode
91 - distance mode 
98 - canned cycle return mode
99 - canned cycle return mode

