# Shark Tracking Drone Ground Station Documentation

## Overview
This document provides an overview of the Ground Station for the Shark Tracking Drone system, designed for real-time tracking and analysis of sharks, integrating temperature data and shark detections.

## Interface Snapshot
![Ground Station Interface](https://github.com/robertfobrien/UAV-shark-tracking-ground-station/assets/20687631/af1cf086-6edb-4a9e-b199-6c668a4d6636)

## Features
- **Shark Detection**: Detect shark locations using algorithms from drone feeds.
- **Temperature Mapping**: View real-time temperature data.
- **Dynamic Mapping**: Navigate the drone's flight path and monitor shark activities.

## Installation
Clone the repository to your local environment:

```bash
git clone https://github.com/robertfobrien/UAV-shark-tracking-ground-station.git
```

## Usage 
Connect to the HolyBro 2.4GHz reciever and change the video source in "stream_interface.py" to the correct rtsp stream (commented inside the file)
