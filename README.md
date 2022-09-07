# Ravelry Harry Potter Knitting Crochet House Cup (HPKCHC) Post Analyser

## General

This python tool is written to analyse a forum page on ravelry and all submitted projects will be extracted. The saved content from the post is shown below:

1. The user name
2. the course id,
3. the post id,
4. the date of the post,
5. the house,
6. if possible the project,
7. if possible the type of crafting

All information to the submitted projects are stored in a database. The script will be executed every day and all submissions from last day can be send as a mail to trackers. The trackers with there email addresses are also stored in the database. Information to the courses are stored in the database as well.

## Annotations

Unfortunately, there are some issues as well. 
1. A submitted project is identified by the tags *Name:* and *House:*. There are some rules to find submissions with inproper tags, but there are limits. *rawenclav* would not be identified as *ravenclaw*.
2. The project and the type of crafting is interpretated by some key words. These keywords are stored in *categories.json*. If the keyword are not used in the post, the project and the type of crafting can't be identified.
