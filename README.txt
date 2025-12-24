*DISCLAIMER!* Anyone is available to use this application but it should only be used for personal projects where security is not a requirement. 

# MySQL Data View Application

## Description
Hello! Thank you for taking the time to check out my simple Python application. It allows you to find averages, insert and delete records, and view database tables. I designed it so you can use any MySQL database, not just a specific one. This project is currently being re-worked, where you can check out any of the recent changes in `beta`. 

## Set-Up:

### Prerequisites
- Any MySQL Database already set up
-  Python 3.12 or above (especially if you're not on Windows)
- Pip (Python package installer) to install `mysql.connector`

### Steps
1. After unzipping the folder, make sure your current working directory in the terminal contains `GUI.py`.

2. To run the source code yourself: Open a terminal, navigate to the Source Code Older and run:
	python GUI.py
## Usage

### Options
In File > Options, you are able to change the database's settings.

### Queries
You can use four types of queries in this database

#### View
Select this query and the table you'd like to view. The table's data will appear at the bottom of the window.

#### Average
Select this query and choose a table. You'll then select a numeric column to calculate its average.

#### Insert
Choose this query and select the table you'd like to insert a record into. A pop-up will display the table's attributes—just fill in the blanks and hit Submit.

#### Delete
Choose this query and select the table from which you'd like to delete a record. The app assumes the primary key and lets you input the key of the record to be deleted.

## Acknowledgements
This project was written for a class at New Mexico State University (C S 482) taught by Dr. Nagarkar. The database used was created for Project: Phase 1, and this project is an expansion of that work.

