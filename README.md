CaterSearch is an application designed to cut down on lead generation time for catering companies. It is currently run from the command line, but the aim is to package it with dependencies for portability. 
It contains basic functionality to accept user input via a Tkinter window, create a list of Google Maps search URLs based on the input, and search HTML elements via Selenium and Beautiful Soup. 
Currently uses Firefox for Selenium options (should probably change to Chrome - bleh) and lacks a path to the Gecko Driver (not yet installed, since I may change dependencies.) 
Had some issues with the element selector returning an empty list when I used Beautiful Soup alone, hoping that once Selenium is configured this will resolve.
