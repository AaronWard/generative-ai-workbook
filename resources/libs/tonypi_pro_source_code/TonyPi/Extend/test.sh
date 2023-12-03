#!/bin/bash
pid=$(ps -elf|grep AthleticsPerform.py|grep -v grep|grep -v sh |awk '{print $4}')
kill -9 $pid


