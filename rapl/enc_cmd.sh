#!/bin/sh
echo 555555 | sudo -S ./codecs/hhi-vvc-codec/encoder/vvencFFapp -c ./configs/hhi-vvc-codec/randomaccess_medium.cfg -i ./sequences/CLASS_C/RaceHorses_416x240_30.yuv -wdt 416 -hgt 240 -b ./bin/hhi-vvc-codec/randomaccess_medium.cfg/CLASS_C/RaceHorses_416x240_30_QP_22_hhi-vvc-codec.bin -o ./rec_yuv/hhi-vvc-codec/randomaccess_medium.cfg/CLASS_C/RaceHorses_416x240_30_QP_22_hhi-vvc-codec.yuv -fr 30 -fs 0 -f 5 -q 40

