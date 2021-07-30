# Ravelry Harry Potter Knitting Crochet House Cup (HPKCHC) Post Analyser

## General

This python tool is written to analyse a forum page on ravelry and all submitted projects will be extracted. The saved content from the post is shonw below:

1. The user name with link to profile page on ravelry
2. the link to the project post,
3. the post id,
4. the date of the post,
5. the house,
6. if possible the project,
7. if possible the type of crafting and
8. the number of loved tags

All information to the submitted projects are exported to a *.csv file*. Then the tool generates a message written in markdown to cheer all users of one house how submitted a project. The house can be selected in the settings.

## Manual

The steps to use this tool are the following:

1. Unfortunately, the page in ravelry must be saved, because the ravelry forum is password protected. Open the page in your browser and press **STRG + S** or right click and show source code. Copy everything and paste it into an empty *.html* file.
	- One trick is to manipulate the url of the page. At the end of the url is the range of the posts. Normally all posts are devided into 25 posts per page. But if you enter 1-50 in example, the first 50 posts are displayed on the page.
2. Copy the *settings.example.json* file and name it *settings.json*. Within change the data. (The file can be opened with any text editor.)
	- **sHouse** is Hogwarts house you want to cheer. (But in the exported *.csv* file all projects from any house are listed)
	- **pagePath** is the path in your file system to the saved ravelry page (step 1)
	- **url** is the base url of the page you want to analyse. This is needed to setup the links to the project posts. Please delete the information after the last slash (/) with the post range. 
	- **startPost** is the post number you want to start with. For example, if you write 21, all posts before post 21 will be ignored.
	- **endPost** is similar to startPost. All post after the given number will be ignored. If you want to analyse all post to the end of the page, you can write -1.
	- **author** is the name to sign the cheer message.
3. Don't forget to save the settings.
4. Execute the *run.py* file. At least 2 files are saved in the same folder:
	- *message.md* is the message post to cheer to the submitters from the selected house. If a project is marked with at least 5 'loves', it will be higlighted.
	- And *submittedProjects.csv* contains all projects from each house.
	- If at least one post can't be interpretated, an *error.txt* file is exported with the html code of this post.
5. At the end, save time with this tool and enjoy crafting.

## Annotations

Unfortunately, there are some issues as well. 
1. A submitted project is identified by the tags *Name:* and *House:* like explaned in the beginning of the page. If someone ignores this and don't used to write that, the post can't be found by this tool.
2. The project and the type of crafting is interpretated by some key words. These keywords are stored in *categories.json*. If the keyword are not used in the post, the project and the type of crafting can't be identified.
