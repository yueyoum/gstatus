# gstatus

## Intro

I using git, But our team not using GitLab or even gitweb.
Just the `git init --bare`. 

I wanna see git log in a browser, which shows the `origin` git log.

So, I spend about 3 hours make this simple tool, 
**No root required**,  I can using it anywhere.

## Usage

	git clone https://github.com/yueyoum/gstatus.git
	cd gstatus

	virtualenv env
	source env/bin/activate

	pip install -r requirements.txt
	python gstatus.py [GIT REPO PATH] [WEB LISTEN PORT]

the follow two argument are required

*	**GIT REPO PATH**  is your git repo root path
*	**WEB LISTEN PORT**

## Screenshot

![gstatus](http://i1297.photobucket.com/albums/ag23/yueyoum/gg_zpsc3d3d43b.png)


*	left bar shows the git commit info. contains date, author, and log
*	click one git commit in left bar, the diff info will shown at the right area
