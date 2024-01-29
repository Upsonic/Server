#!/bin/bash

service nginx start

upsonic_on_prem api --host=0.0.0.0 --port=3000