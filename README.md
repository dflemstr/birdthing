# `birdthing`

A hacky set of scripts for continuously monitoring and photographing birds outside of my kitchen window.

The code has a bunch of hard-coded constants inline that are tailored for my use-case and I haven't focused on making
things tweakable.

# Setup

Use a Raspberry Pi 4, and get an Adafruit Servo Hat, install a pan/tilt jig via two servos (servo 0 is pan and servo 1
is tilt), and mount a Raspberry Pi camera on top (I used the HQ version).  You should also get a Coral Edge TPU device
for accelerating the deep learning model prediction.

# Running

Use poetry to run:

```shell
$ poetry run birdthing -t bird
```

You can select various objects to track, I used a deep learning model that supports a bunch of different objects, see
`--help` for the full list.  Here's a snapshot:

```
person|bicycle|car|motorcycle|airplane|bus|train|truck|boat|traffic light|fire hydrant|stop sign|parking meter|bench|bird|cat|dog|horse|sheep|cow|elephant|bear|zebra|giraffe|backpack|umbrella|handbag|tie|suitcase|frisbee|skis|snowboard|sports ball|kite|baseball bat|baseball glove|skateboard|surfboard|tennis racket|bottle|wine glass|cup|fork|knife|spoon|bowl|banana|apple|sandwich|orange|broccoli|carrot|hot dog|pizza|donut|cake|chair|couch|potted plant|bed|dining table|toilet|tv|laptop|mouse|remote|keyboard|cell phone|microwave|oven|toaster|sink|refrigerator|book|clock|vase|scissors|teddy bear|hair drier|toothbrush
```

# Licenses

Heavily based on the `rpi-deep-pantilt` pip package which is licensed under:

```text
MIT License

Copyright (c) 2019, Leigh Johnson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```