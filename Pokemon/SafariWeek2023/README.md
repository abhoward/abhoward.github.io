# Safari Week 2023

## **Description**
As a long-time shiny hunter, I've always wanted to see aggregated shiny stats for the shiny hunting community as a whole, but I never really thought such a thing would be possible. First, you'd need a place where everyone posts their shinies, and then you'd need to be able to extract the data from it in some way. I initially considered trying to get data from an online shiny counter like [Shiny Hunt](https://www.shinyhunt.com/) but I pretty quickly shot that down given how many shiny hunters use their own offline counter. The ideal source, in my mind, would be to get data for shiny hunts off of Twitter, since thats where most shiny hunters post their shiny Pokemon. However, I would need some way to determine that a tweet is about a shiny hunt to begin with; I can't just simply pull every single tweet. Furthermore, the format of hunters' tweets are all over the place; sometimes they include the name of the Pokemon and the number of encounters, but sometimes they only post the name OR the number of encounters, and other times they don't even post anything except a picture with the some simple text like "I GOT IT"! Given these challenges there's no way we can use Twitter to source the data...right?

Enter OpenAI.

My initial theory was that I could just simply send the text of the tweet to ChatGPT, ask it to pull the number of encounters and name of the Pokemon in the tweet, and call it a day. That theory was pretty quickly shot out of the window when I realized just how many edge cases there were. Take [this tweet](https://twitter.com/YourFriedBread/status/1665508135933444098) for example: there's two shinies Exeggcutes in the tweet, but ChatGPT might think the name of the Pokemon is "Eggs" and it might only pull one of the two encounter numbers, if at all. [Here's another example](https://twitter.com/k9742850/status/1664340125617373184), this time in Japanese: ChatGPT can't recognize the name very easily, and it might sometimes pull the number "4" instead of "1391" as the number of encounters. I quickly realized that ChatGPT is just simply too generalized for this hyper-specific use case. After coming to this conclusion, I gave up using AI models to extract data and wrote up an extremely complicated hard-coded method to extract data from each hunters tweet, but given that I had to assume a very specific format it only worked for ~15% of all tweets, which just wouldn't work. After giving up on THAT, I vented to a friend about these challenges, and he told me to look into [fine-tuning](https://platform.openai.com/docs/guides/fine-tuning). I had no idea this was a thing, but after researching it further, I realized this would be _perfect_ for my use case. I can take OpenAI's generalized text model (Davinci) and tune it to become a shiny-Pokemon-tweet extraction MACHINE. Thus, I manually classified ~250 tweets myself (training data viewable [here](https://github.com/abhoward/abhoward.github.io/blob/main/data/Pokemon/davinci_training_data_prepared.jsonl)) and gave that to OpenAI, creating a customized AI model that can pull two pieces of information from a tweet: the shiny Pokemon's name and how many encounters it took to find the shiny in the format <pokemon_name>: <number_of_encounters>. If a tweet doesn't contain the name of a shiny Pokemon, it simply returns "No Pokemon found", and if it doesn't contain an encounter number it returns "0". Here are some examples of how well it did:

- https://twitter.com/AmpsDark/status/1666866526631366657 resulted in "Rhyhorn: 20884" 
  - Correct! 
- https://twitter.com/Canned_Wolfmeat/status/1666881224567029785 resulted in "No Pokemon found"
  - Correct given the text doesn't mention any specific Pokemon or encounters
- https://twitter.com/Joesby07/status/1666896353731960859 resulted in "Magneton: 0"
  - Correct! Pokemon name was found but no encounters were given
- https://twitter.com/CaptionCats/status/1667194630268387328 resulted in "Girafarig: 980 and Exeggcute: 1172"
  - Correct! This was one of the most impressive extractions to me: not only was it able to pull two separate shinies from one tweet, but it also recognized that "Egg" corresponds to "Exeggcute". Crazy!
- https://twitter.com/TheDailySpinda/status/1666444624611647489 resulted in "Spinda: 0"
  - Incorrect but understandable why it got confused here

As you can see, the model works surprisingly well! It still isn't perfect but I'm confident that it can get better as I give it more and more data to fine-tune it. If you're reading this and you're a shiny hunter, please consider formatting your tweets similarly to the first tweet listed above! It'll help raise the model extract data from your tweets more accurately!

### **Credits**
- [Matt Brandl](https://twitter.com/TheAbsol) for organizing and coordinating Safari Week 
- [Msikma](https://msikma.github.io/pokesprite/) for the shiny Pokemon icons used in the chart below
- [Tweepy](https://www.tweepy.org/) for making a great, easy to use Tweet scraper for Python
- [OpenAI](https://openai.com/) for creating our AI overlords
- [Highcharts](https://www.highcharts.com/) for their super pretty visualizations

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