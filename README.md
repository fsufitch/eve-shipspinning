Ship Spinning Inc.
-----------------

This is a public for-reference version of the Ship Spinning Inc. project.

Ship Spinning Inc. was a slot machine minigame for the MMORPG [Eve Online](http://eveonline.com). It allowed players to gamble using in-game credits to win ships and other prizes. The process worked thus:

 1. Players donated credits to an in-game entity (corporation).
 * As a cron job, the Ship Spinning Inc. server used the game's [3rd party API](https://eveonline-third-party-documentation.readthedocs.org/en/latest/xmlapi/index.html) to detect such credit donations, assigning them to players' accounts.
 * The players could use these credits to trigger animated slot machines on the website. There was a variety of slot machines, each guaranteed to provide a return of 90%±5%, getting its data from a [3rd party game market API ](https://eve-central.com/home/develop.html).
 * When players won a prize, I received a notification and sent them their winnings in-game. The players also had an option to redeem the prize for market price plus 15% as game credit, to play more.

The slot machines were very successful and paid for themselves in no time, providing enjoyment for more than 1000 players. They were eventually shut down as I lost interest in Eve Online. 

I am now publishing its source code for reference/archival. Use it as you will. Enjoy!
