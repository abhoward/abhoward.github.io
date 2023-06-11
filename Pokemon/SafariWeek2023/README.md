# Safari Week 2023

## **[Shiny Pokemon Encounters](safariweek2023-mon-counts.html "Click to view graph in full"){:target="_blank"}**
##### Features Drilldowns

### Preview:
<div class="iframe-container">
  <iframe src="safariweek2023-mon-counts.html" width="100%" frameborder="0" loading="lazy" scrolling="no" title="Shiny Pokemon Encounters" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen> </iframe>
  <br>
</div>

## **[Encounter Histogram](safariweek2023-encounters.html "Click to view graph in full"){:target="_blank"}**

### Preview:
<div class="iframe-container">
  <iframe src="safariweek2023-encounters.html" width="100%" frameborder="0" loading="lazy" scrolling="no" title="Encounter Histogram" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen> </iframe>
  <br>
</div>

## **Description**
As a long-time shiny Pokemon hunter and full-time Analytics Engineer, I've always thought it would be interesting to see aggregated statistics for shiny hunting community events. Thus, for Safari Week 2023, I challenged myself to create a visualization that displays easily digestible information about people's shiny hunts, such as which Pokemon they shiny hunted and how many encounters it took for them to find the shiny. Since the shiny hunting community's main source of communication is Twitter, I used [Tweepy](https://www.tweepy.org/), a Python wrapper that accesses Twitter's API, to extract everyone's shiny hunts. In order to determine which tweets to extract, I pulled tweets that contained the hashtags "#safariweek" or "#safariweek2023". Of course this is not perfect as it may exclude tweets containing valid shinies (but were posted without the appropriate hashtag), but the tradeoff is probably worth it as we also exclude shinies that were found _during_ Safari Week but are _not_ actual safari shinies. Another limitation of this is that the Twitter API only allows applications to extract tweets from the last seven days. Since I had started this project on June 6th, I missed some safari shinies that people had found before May 31st. Furthermore, I included tweets containing the hashtag "#safariweek" on June 11th (I had previously limited my query to only "#safariweek2023" tweets) which in turn means I may be missing tweets from before June 4th that used the hashtag "#safariweek" but not "#safariweek2023". 

Once I had extracted these tweets, I looked through them and realized that the people within the shiny hunting community have _VERY_ different ways of tweeting about their shinies! Some people include the Pokemon name and number of encounters, but a lot of people don't include either piece (or even both pieces) of information. Therefore, instead of creating a harad coded text extraction program, I decided to utilize [OpenAI's text model Davinci](https://platform.openai.com/docs/models/gpt-3-5) to extract the information I wanted out of these tweets. After performing some initial extractions, I quickly realized the model was too generalized to do a good job with this hyper-specific use-case. Thus I used [fine-tuning](https://platform.openai.com/docs/guides/fine-tuning) to further train the model; by giving it a [dataset](https://github.com/abhoward/abhoward.github.io/blob/main/data/Pokemon/davinci_training_data_prepared.jsonl) that I had manually classified, thereby "teaching" the model what exactly I wanted it to do. You can see some examples of the model's extraction efforts below:

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Shiny Rhyhorn in LeafGreen after 20,884 RE&#39;s! Caught after 1 ball! My 2nd shiny of safari week.<a href="https://twitter.com/hashtag/SafariWeek2023?src=hash&amp;ref_src=twsrc%5Etfw">#SafariWeek2023</a> <a href="https://twitter.com/hashtag/SafariWeek?src=hash&amp;ref_src=twsrc%5Etfw">#SafariWeek</a> <a href="https://t.co/1zg4pv58R2">pic.twitter.com/1zg4pv58R2</a></p>&mdash; Dark Amps (@AmpsDark) <a href="https://twitter.com/AmpsDark/status/1666866526631366657?ref_src=twsrc%5Etfw">June 8, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
- Extracted information: "Rhyhorn: 20884" &rarr; Correct!

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Second shiny of <a href="https://twitter.com/hashtag/safariweek2023?src=hash&amp;ref_src=twsrc%5Etfw">#safariweek2023</a>, managed to actually record this one fully this time <a href="https://t.co/daFEK4VHob">pic.twitter.com/daFEK4VHob</a></p>&mdash; CannedWolfMeat (@Canned_Wolfmeat) <a href="https://twitter.com/Canned_Wolfmeat/status/1666881224567029785?ref_src=twsrc%5Etfw">June 8, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
- Extracted information: "No Pokemon found" &rarr; Correct given that the text doesn't mention any specific Pokemon or encounters

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Yesterday we were able to find this majestic Magneton! <a href="https://twitter.com/hashtag/safariweek2023?src=hash&amp;ref_src=twsrc%5Etfw">#safariweek2023</a> <a href="https://t.co/wupgnwbFTQ">pic.twitter.com/wupgnwbFTQ</a></p>&mdash; Joesby (@Joesby07) <a href="https://twitter.com/Joesby07/status/1666896353731960859?ref_src=twsrc%5Etfw">June 8, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
- Extracted information: "Magneton: 0" &rarr; Correct! Pokemon name was found but no encounters were given

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">SAFARI WEEK BB! 1hr in and I caught a Shiny Lapras and Fail a Shiny Abra! What is my luck tonight!!!<a href="https://twitter.com/hashtag/safariweek2023?src=hash&amp;ref_src=twsrc%5Etfw">#safariweek2023</a> &amp; <a href="https://twitter.com/pkmnpride?ref_src=twsrc%5Etfw">@pkmnpride</a><a href="https://t.co/YHUTv3vU2A">https://t.co/YHUTv3vU2A</a> <a href="https://t.co/TF3r98MLUA">pic.twitter.com/TF3r98MLUA</a></p>&mdash; Sentyal | PokéTuber (@Sentyal) <a href="https://twitter.com/Sentyal/status/1664869189193195521?ref_src=twsrc%5Etfw">June 3, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
- Extracted information: "Lapras: 0 and Abra: 0" &rarr; Correct! The model successfully extracted two Pokemon from one tweet!

<blockquote class="twitter-tweet"><p lang="en" dir="ltr"><a href="https://twitter.com/hashtag/safariweek2023?src=hash&amp;ref_src=twsrc%5Etfw">#safariweek2023</a> hunters, time for a Safari Week check in!!<br><br>I’ll go first:<br><br>Total Encounters: 12,616<br>Wins:0<br>Fails:1<br>Most recent Shiny: Riolu, 6224<br><br>Targets: Riolu, exeggcute, Pinsir, chansey, anything in Emerald.<a href="https://twitter.com/hashtag/shinypokemon?src=hash&amp;ref_src=twsrc%5Etfw">#shinypokemon</a> <a href="https://twitter.com/hashtag/shiny?src=hash&amp;ref_src=twsrc%5Etfw">#shiny</a> <a href="https://twitter.com/hashtag/pokemon?src=hash&amp;ref_src=twsrc%5Etfw">#pokemon</a></p>&mdash; gr3atScotty (@gr3atscotty) <a href="https://twitter.com/gr3atscotty/status/1667624161915863040?ref_src=twsrc%5Etfw">June 10, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
- Extracted information: "Riolu: 6224" &rarr; Correct! Somehow the model did not get confused by the 12626 encounter number, instead opting for the correct number 6224

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Spinda is chilling in the irl safari. <br><br>Shout out to those of us who hunted for safari week and came up short. It&#39;s still great to hunt alongside the community!<a href="https://twitter.com/hashtag/spinda?src=hash&amp;ref_src=twsrc%5Etfw">#spinda</a> <a href="https://twitter.com/hashtag/safariweek2023?src=hash&amp;ref_src=twsrc%5Etfw">#safariweek2023</a> <a href="https://t.co/oNSajELZdI">pic.twitter.com/oNSajELZdI</a></p>&mdash; The Daily Spinda (@TheDailySpinda) <a href="https://twitter.com/TheDailySpinda/status/1666444624611647489?ref_src=twsrc%5Etfw">June 7, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
- Extracted information: "Spinda: 0" &rarr; Incorrect but understandable why it got confused here

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">My wife found her first 8192 shiny today! Welcome Puff Daddy♀ who will be very loved. She doesn&#39;t have twitter but with <a href="https://twitter.com/hashtag/safariweek2023?src=hash&amp;ref_src=twsrc%5Etfw">#safariweek2023</a> wrapping up she wanted me to share with everyone. <a href="https://twitter.com/hashtag/pokemon?src=hash&amp;ref_src=twsrc%5Etfw">#pokemon</a> <a href="https://twitter.com/hashtag/ShinyPokemon?src=hash&amp;ref_src=twsrc%5Etfw">#ShinyPokemon</a> <a href="https://t.co/maFgkHlnca">pic.twitter.com/maFgkHlnca</a></p>&mdash; Beanhurst (@beanhurstpkmn) <a href="https://twitter.com/beanhurstpkmn/status/1667459159942635520?ref_src=twsrc%5Etfw">June 10, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
- Extracted information: "Puff Daddy: 8192" &rarr; Incorrect; Puff Daddy is (unfortunately) not a valid Pokemon name, and 8192 is not the correct number of encounters. This should have been "No Pokemon found: 0"

As you can see, the model does a surprisingly (and scarily?) good job at extracting the information I need! Of course the model is not perfect, and as such I've had to manually go through some of the extractions and update them to more accurately align with the tweet text. However, if the tweet is formatted in a straightforward way, the model will accurately extract data almost 100% of the time. Note that a straightforward format for a tweet is something [like this](https://twitter.com/norainthefuture/status/1666463331790782464), where the tweet is in English, Pokemon name is easily identifiable, and the encounter number is close to the Pokemon name and/or a phrase designating the number of encounters (i.e. "encounters", "REs", "RAs", etc). If you notice any incorrect information in the chart(s) above, or if you'd like a tweet included in the chart(s), please feel free to fill out the form below.

After this data has been extracted and cleaned, I did a couple of data transformations to it to make it more digestible for Highcharts to consume. You can find the script where I do all of these data extractions, cleans, transformations, and more [here](https://github.com/abhoward/abhoward.github.io/blob/main/scripts/pokemon/shiny_pokemon_tweet_scraper.py).

My future goals for this project is to continue training the model so that it can be used to extract other pieces of information, such as the game the Pokemon was hunted on, or if the shiny hunter successfully caught the Pokemon or not. I'd also like to create more ways to visualize shiny hunters' efforts, so if you have any ideas or would like to see something specific don't hesitate to reach out (Twitter DMs usually work best)!

### **[Request Form](https://docs.google.com/forms/d/e/1FAIpQLSeeM-nSVhPH26QaUweYJ2r2nH7ApT2Fe3gzslMFX_Oph-cWWw/viewform?usp=sf_link "Click to view form in full"){:target="_blank"}**
<div class="iframe-container">
  <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSeeM-nSVhPH26QaUweYJ2r2nH7ApT2Fe3gzslMFX_Oph-cWWw/viewform?embedded=true" width="100%" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
  <br>
</div>

### **Credits**
- [Matt Brandl](https://twitter.com/TheAbsol) for organizing and coordinating Safari Week 
- [Msikma](https://msikma.github.io/pokesprite/) for the shiny Pokemon icons used above
- [Tweepy](https://www.tweepy.org/) for making a great, easy to use Tweet scraper for Python
- [OpenAI](https://openai.com/) for creating our AI overlords
- [Highcharts](https://www.highcharts.com/) for their super pretty visualizations
- ✨ The shiny Pokemon community for being awesome (and for tweeting their shinies) ✨