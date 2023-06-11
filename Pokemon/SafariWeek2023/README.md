# Safari Week 2023

## **[Shiny Pokemon Encounters](safariweek2023-mon-counts.html "Click to view graph in full"){:target="_blank"}**
##### Features Drilldowns

### Preview:
<div class="iframe-container">
  <iframe src="safariweek2023-mon-counts.html" width="100%" frameborder="0" loading="lazy" scrolling="no" title="Shiny Pokemon Encounters" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen> </iframe>
</div>

## **[Encounter Histogram](safariweek2023-encounters.html "Click to view graph in full"){:target="_blank"}**

### Preview:
<div class="iframe-container">
<iframe src="safariweek2023-encounters.html" width="100%" frameborder="0" loading="lazy" scrolling="no" title="Encounter Histogram" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen> </iframe>
</div>

## **Description**
As a long-time shiny Pokemon hunter and full-time Analytics Engineer, I've always thought it would be interesting to see aggregated statistics for shiny hunting community events. Thus, for Safari Week 2023, I challenged myself to create a visualization that displays easily digestible information about people's shiny hunts, such as which Pokemon they shiny hunted and how many encounters it took for them to find the shiny. Since the shiny hunting community's main source of communication is Twitter, I used [Tweepy](https://www.tweepy.org/), a Python wrapper that accesses Twitter's API, to extract everyone's shiny hunts. In order to determine which tweets to extract, I pulled tweets that contained the hashtags "#safariweek" or "#safariweek2023". Of course this is not perfect as it may exclude tweets containing valid shinies (but were posted without the appropriate hashtag), but the tradeoff is probably worth it as we also exclude shinies that were found _during_ Safari Week but are _not_ actual safari shinies. Another limitation of this is that the Twitter API only allows applications to extract tweets from the last seven days. Since I had started this project on June 6th, I missed some safari shinies that people had found before May 31st. Furthermore, I included tweets containing the hashtag "#safariweek" on June 11th (I had previously limited my query to only "#safariweek2023" tweets) which in turn means I may be missing tweets from before June 4th that used the hashtag "#safariweek" but not "#safariweek2023". 

Once I had extracted these tweets, I looked through them and realized that the people within the shiny hunting community have _VERY_ different ways of tweeting about their shinies! Some people include the Pokemon name and number of encounters, but a lot of people don't include either piece (or even both pieces) of information. Therefore, instead of creating a harad coded text extraction program, I decided to utilize [OpenAI's text model Davinci](https://platform.openai.com/docs/models/gpt-3-5) to extract the information I wanted out of these tweets. After performing some initial extractions, I quickly realized the model was too generalized to do a good job with this hyper-specific use-case. Thus I used [fine-tuning](https://platform.openai.com/docs/guides/fine-tuning) to further train the model; by giving it a [dataset](https://github.com/abhoward/abhoward.github.io/blob/main/data/Pokemon/davinci_training_data_prepared.jsonl) that I had manually classified, thereby "teaching" the model what exactly I wanted it to do. You can see some examples of the model's extraction efforts below:

- https://twitter.com/AmpsDark/status/1666866526631366657 -> "Rhyhorn: 20884" 
  - Correct! 
- https://twitter.com/Canned_Wolfmeat/status/1666881224567029785 -> "No Pokemon found"
  - Correct given the text doesn't mention any specific Pokemon or encounters
- https://twitter.com/Joesby07/status/1666896353731960859 -> "Magneton: 0"
  - Correct! Pokemon name was found but no encounters were given
- https://twitter.com/Sentyal/status/1664869189193195521/photo/1 -> "Lapras: 0 and Abra: 0"
  - Correct! The model successfully extracted two Pokemon from one tweet!
- https://twitter.com/gr3atscotty/status/1667624161915863040 -> "Riolu: 6224"
  - Correct! Somehow the model did not get confused by the 12626 encounter number, instead opting for the correct number 6224
- https://twitter.com/TheDailySpinda/status/1666444624611647489 -> "Spinda: 0"
  - Incorrect but understandable why it got confused here
- https://twitter.com/beanhurstpkmn/status/1667459159942635520 -> "Puff Daddy: 8192" 
  - Incorrect; Puff Daddy is (unfortunately) not a valid Pokemon name, and 8192 is not the correct number of encounters. This should have been "No Pokemon found: 0"

As you can see, the model does a surprisingly (and scarily?) good job at extracting the information I need! Of course the model is not perfect, and as such I've had to manually go through some of the extractions and update them to more accurately align with the tweet text. However, if the tweet is formatted in a straightforward way, the model will accurately extract data almost 100% of the time. Note that a straightforward format for a tweet is something [like this](https://twitter.com/norainthefuture/status/1666463331790782464), where the tweet is in English, Pokemon name is easily identifiable, and the encounter number is close to the Pokemon name and/or a phrase designating the number of encounters (i.e. "encounters", "REs", "RAs", etc). If you notice any incorrect information in the chart(s) above, or if you'd like a tweet included in the chart(s), please feel free to fill out the form below.

After this data has been extracted and cleaned, I did a couple of data transformations to it to make it more digestible for Highcharts to consume. You can find the script where I do all of these data extractions, cleans, transformations, and more [here]().

My future goals for this project is to continue training the model so that it can be used to extract other pieces of information, such as the game the Pokemon was hunted on, or if the shiny hunter successfully caught the Pokemon or not. I'd also like to create more ways to visualize shiny hunters' efforts, so if you have any ideas or would like to see something specific don't hesitate to reach out (Twitter DMs usually work best)!

### **[Request Form](**https://docs.google.com/forms/d/e/1FAIpQLSeeM-nSVhPH26QaUweYJ2r2nH7ApT2Fe3gzslMFX_Oph-cWWw/viewform?usp=sf_link "Click to view form in full"){:target="_blank"}**
<div class="iframe-container">
  <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSeeM-nSVhPH26QaUweYJ2r2nH7ApT2Fe3gzslMFX_Oph-cWWw/viewform?embedded=true" width="100%" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
</div>

### **Credits**
- [Matt Brandl](https://twitter.com/TheAbsol) for organizing and coordinating Safari Week 
- [Msikma](https://msikma.github.io/pokesprite/) for the shiny Pokemon icons used above
- [Tweepy](https://www.tweepy.org/) for making a great, easy to use Tweet scraper for Python
- [OpenAI](https://openai.com/) for creating our AI overlords
- [Highcharts](https://www.highcharts.com/) for their super pretty visualizations
- ✨ The shiny Pokemon community for being awesome (and for tweeting their shinies) ✨